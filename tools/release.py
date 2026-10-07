# -*- coding: utf-8 -*-
"""release.py —— 一键发版：校验 → 推送 main 与标签 → 用 CHANGELOG 建 GitHub Release。

设计为**自包含**：仓库路径、owner/repo 全部从本文件位置与 git remote 推导，
不依赖任何仓库外文件。可放在任意 clone 里直接跑。

用法：
    python tools/release.py --check              # 只体检，不改动任何东西
    python tools/release.py                      # 正式发版
    python tools/release.py --token-file /path/to/token
    GH_TOKEN=xxx python tools/release.py         # 也可用环境变量
    python tools/release.py --create-repo        # 远端仓库不存在时自动新建（需 repo 权限）
    python tools/release.py --force-with-lease   # 远端已领先时覆盖推送

token 取值优先级：--token-file > 环境变量 GH_TOKEN > <仓库根>/.gh_token
token 权限：classic PAT 需 `repo`；fine-grained 需 Contents:Read/write（+ Administration:Read/write 才能建仓）
安全：--token-file 指向的文件在成功后会被删除；环境变量方式不做删除。
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

API = "https://api.github.com"
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_TOKEN_FILE = os.path.join(REPO_DIR, ".gh_token")


# ---------------------------------------------------------------- 基础工具
def git(args, check=True):
    p = subprocess.run(["git"] + args, cwd=REPO_DIR,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
    out = p.stdout.decode("utf-8", "replace")
    if check and p.returncode != 0:
        print(out)
        raise SystemExit("!! git %s 失败（exit %d）" % (" ".join(args[:2]), p.returncode))
    return p.returncode, out


def api(method, path, token, payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "chip-fa-analysis-release")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            body = r.read().decode("utf-8", "replace")
            return r.status, (json.loads(body) if body.strip() else {}), dict(r.headers)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(body), dict(e.headers)
        except Exception:
            return e.code, {"raw": body[:400]}, dict(e.headers)
    except urllib.error.URLError as e:
        return 0, {"network_error": str(e.reason)}, {}


# ---------------------------------------------------------------- 仓库推导
def parse_remote():
    _, url = git(["remote", "get-url", "origin"], check=False)
    url = url.strip()
    m = re.search(r"github\.com[:/]+([^/]+)/(.+?)(?:\.git)?$", url)
    if not m:
        raise SystemExit("!! 无法从 origin 解析 owner/repo：%r" % url)
    return m.group(1), m.group(2), url


def current_version():
    _, out = git(["describe", "--tags", "--abbrev=0"], check=False)
    tag = out.strip()
    tag = tag if tag.startswith("v") else "v" + tag
    return tag if len(tag) > 1 else None


def changelog_section(version):
    p = os.path.join(REPO_DIR, "CHANGELOG.md")
    if not os.path.isfile(p):
        return ""
    t = io.open(p, encoding="utf-8").read()
    m = re.search(r"(?ms)^## \[%s\].*?(?=^## \[|\Z)" % re.escape(version), t)
    return m.group(0).strip() if m else ""


def git_with_token(token, args):
    """token 经临时 credential helper 注入：不写 .git/config、不进 argv、不进日志。"""
    env = dict(os.environ, GH_TOKEN_FOR_PUSH=token, GIT_TERMINAL_PROMPT="0")
    helper = '!f(){ echo username=x-access-token; echo password="$GH_TOKEN_FOR_PUSH"; };f'
    p = subprocess.run(
        ["git", "-c", "credential.helper=", "-c", "credential.helper=" + helper] + args,
        cwd=REPO_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    out = p.stdout.decode("utf-8", "replace")
    if p.returncode != 0:
        print(out)
        raise SystemExit("!! git %s 失败（exit %d）" % (args[0], p.returncode))
    return out


# ---------------------------------------------------------------- 主流程
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只体检，不推送")
    ap.add_argument("--token-file", default=None)
    ap.add_argument("--create-repo", action="store_true", help="远端不存在时自动建仓")
    ap.add_argument("--force-with-lease", action="store_true", help="远端领先时覆盖推送")
    a = ap.parse_args()

    owner, repo, url = parse_remote()
    tag = current_version()
    ver = tag[1:] if tag else None
    print("=" * 68)
    print("仓库：%s/%s" % (owner, repo))
    print("远端：%s" % url)
    print("版本：%s" % (tag or "（无标签，请先 git tag -a）"))
    print("模式：%s" % ("体检（--check）" if a.check else "正式发版"))
    print("=" * 68)

    if not tag:
        return 2

    # 工作区干净检查
    _, dirty = git(["status", "--porcelain"], check=False)
    if dirty.strip():
        print("!! 工作区不干净，先提交：")
        print(dirty.strip()[:600])
        if not a.check:
            return 2
    else:
        print("[1] 工作区干净")

    # 标签必须指向 HEAD
    _, head = git(["rev-parse", "HEAD"], check=False)
    _, tags = git(["rev-parse", "%s^{commit}" % tag], check=False)
    on_head = head.strip() == tags.strip()
    print("[2] 标签 %s %s HEAD" % (tag, "指向" if on_head else "**不**指向"))
    if not on_head:
        print("    → 请先 git tag -a 到当前提交，或 git checkout 到标签所在提交。")
        if not a.check:
            return 2

    # token
    token = None
    if a.token_file:
        if not os.path.isfile(a.token_file):
            print("!! 找不到 token 文件：%s" % a.token_file)
            return 2
        token = io.open(a.token_file, encoding="utf-8").read().strip()
    elif os.environ.get("GH_TOKEN"):
        token = os.environ["GH_TOKEN"].strip()
    elif os.path.isfile(DEFAULT_TOKEN_FILE):
        token = io.open(DEFAULT_TOKEN_FILE, encoding="utf-8").read().strip()

    print("[3] token：%s" % ("已读取（长度 %d，不回显）" % len(token) if token else "未提供"))

    remote_has_main = False
    if token:
        st, me, hdr = api("GET", "/user", token)
        if st != 200:
            print("!! token 校验失败 HTTP %s：%s" % (st, me))
            return 2
        print("    身份：%s     scope：%s" % (me.get("login"), hdr.get("X-OAuth-Scopes") or "（fine-grained）"))
        if me.get("login") != owner:
            print("!! 身份与 remote owner 不符（%s != %s）" % (me.get("login"), owner))
            return 2

        st, info, _ = api("GET", "/repos/%s/%s" % (owner, repo), token)
        if st == 200:
            print("[4] 远端仓库存在（private=%s, default=%s）"
                  % (info.get("private"), info.get("default_branch")))
        elif st == 404 and a.create_repo and not a.check:
            st2, r2, _ = api("POST", "/user/repos", token, {
                "name": repo, "private": False, "auto_init": False,
                "has_issues": True, "has_wiki": False})
            if st2 not in (200, 201):
                print("!! 建仓失败 HTTP %s：%s" % (st2, r2))
                return 2
            print("[4] 已新建远端仓库：%s" % r2.get("html_url"))
        elif st == 404:
            print("[4] 远端仓库不存在（要自动建仓请加 --create-repo）")
        else:
            print("!! 查询仓库失败 HTTP %s：%s" % (st, info))
            return 2
    else:
        print("[4] 无 token，跳过仓库查询与 Release")

    rc, out = git(["ls-remote", "--heads", "origin", "main"], check=False)
    remote_has_main = (rc == 0) and bool(out.strip())
    print("[5] 远端 main：%s" % ("已存在" if remote_has_main else "为空"))

    if a.check:
        print("\n体检结束，未做任何改动。")
        return 0

    if not token:
        return 2

    if remote_has_main:
        print("[6] git fetch + push（%s）…" % ("force-with-lease" if a.force_with_lease else "常规"))
        if a.force_with_lease:
            git_with_token(token, ["push", "--force-with-lease", "origin", "main"])
        else:
            git_with_token(token, ["push", "origin", "main"])
    else:
        print("[6] git push -u origin main …")
        git_with_token(token, ["push", "-u", "origin", "main"])

    print("[7] git push --tags …")
    git_with_token(token, ["push", "origin", "--tags"])

    st, _, _ = api("GET", "/repos/%s/%s/git/ref/tags/%s" % (owner, repo, tag), token)
    print("[8] 远端标签 %s：%s" % (tag, "OK" if st == 200 else "未找到（HTTP %s）" % st))

    st, rel, _ = api("GET", "/repos/%s/%s/releases/tags/%s" % (owner, repo, tag), token)
    if st == 200:
        print("[9] Release %s 已存在，跳过" % tag)
    else:
        body = changelog_section(ver) or ("见 CHANGELOG.md 的 %s 章节" % tag)
        st2, r2, _ = api("POST", "/repos/%s/%s/releases" % (owner, repo), token, {
            "tag_name": tag, "name": "%s — 芯片失效分析 Skill" % tag,
            "body": body, "draft": False, "prerelease": False})
        print("[9] 创建 Release：%s" % ("OK" if st2 in (200, 201) else "失败 HTTP %s %s" % (st2, r2)))
        if st2 in (200, 201):
            print("    %s" % r2.get("html_url"))

    # 删除 token 文件（仅当 token 来自文件；环境变量方式不动）
    tf = a.token_file or (DEFAULT_TOKEN_FILE if os.path.isfile(DEFAULT_TOKEN_FILE) else None)
    if tf and not os.environ.get("GH_TOKEN"):
        try:
            os.remove(tf)
            print("[10] 已删除 token 文件 %s" % tf)
        except Exception as e:
            print("[10] !! 删除 token 文件失败：%s（请手工删除）" % e)

    print("\n完成：https://github.com/%s/%s/releases/tag/%s" % (owner, repo, tag))
    return 0


if __name__ == "__main__":
    sys.exit(main())
