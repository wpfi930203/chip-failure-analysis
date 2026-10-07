# -*- coding: utf-8 -*-
"""install.py —— 把 chip-fa-analysis 从工作区源目录安装到用户级技能目录，并做逐文件 SHA256 校验。

设计要点（都是踩过坑后加的）：
  * 用 `os.path.join` 逐段拼路径：PowerShell 三参数 `Join-Path` 曾静默失败，
    导致 icons/ tools/ 共 5 个文件没被拷过去，靠哈希校验才发现。
  * 绝不递归删除任何目录：只做覆盖拷贝，多出来的文件只报告、不动。
  * 拷完立即重跑 `sync_meta.py`，因为界面重装会覆盖 `_user_meta.json`。
  * 最后逐文件 SHA256 比对，并额外用 `verify_meta.py` 校验展示名/图标链路。

用法：
    python tools/install.py                 # 默认 源 -> C:\\Users\\<user>\\.workbuddy\\skills\\chip-fa-analysis
    python tools/install.py --dest <dir>    # 指定目标
    python tools/install.py --check         # 只校验，不拷贝
"""
import hashlib
import io
import os
import shutil
import subprocess
import sys

SRC = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SKILL_NAME = "chip-fa-analysis"
DEFAULT_DEST = os.path.normpath(os.path.join(os.path.expanduser("~"), ".workbuddy", "skills", SKILL_NAME))
SUBDIRS = ("references", "icons", "tools")
TOP_FILES = ("SKILL.md", "test-prompts.json")
# `_user_meta.json` 两侧必然不同（iconLocalPath 是各自目录的绝对路径），故不参与拷贝与哈希对账，
# 由 sync_meta.py 各自生成。
IGNORED = ("_user_meta.json",)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def collect(root):
    """返回 {相对路径: 绝对路径}，覆盖顶层文件与全部子目录（保持扁平结构）。"""
    items = {}
    for n in TOP_FILES:
        p = os.path.join(root, n)
        if os.path.isfile(p):
            items[n] = p
    for sub in SUBDIRS:
        d = os.path.join(root, sub)
        if not os.path.isdir(d):
            continue
        for n in sorted(os.listdir(d)):
            p = os.path.join(d, n)
            if os.path.isfile(p) and n not in IGNORED:
                items[os.path.join(sub, n)] = p
    return items


def main():
    src = SRC
    dest = DEFAULT_DEST
    if "--dest" in sys.argv:
        dest = os.path.normpath(sys.argv[sys.argv.index("--dest") + 1])
    only_check = "--check" in sys.argv

    print("SRC : %s" % src)
    print("DEST: %s" % dest)
    print("MODE: %s\n" % ("check only" if only_check else "copy + verify"))

    src_files = collect(src)
    if not src_files:
        print("!! 源目录没有可安装文件，退出")
        return 2

    if not only_check:
        for sub in ("",) + SUBDIRS:
            d = os.path.join(dest, sub) if sub else dest
            os.makedirs(d, exist_ok=True)
        for rel, p in sorted(src_files.items()):
            shutil.copy2(p, os.path.join(dest, rel))

    # 逐文件校验
    ok, bad = [], []
    for rel, p in sorted(src_files.items()):
        t = os.path.join(dest, rel)
        if not os.path.isfile(t):
            bad.append((rel, "MISSING"))
            continue
        if sha256(p) == sha256(t):
            ok.append(rel)
        else:
            bad.append((rel, "DIFF"))

    print("MATCH %d / %d" % (len(ok), len(src_files)))
    for rel, why in bad:
        print("  !! %-9s %s" % (why, rel))

    # 目标里多出来的文件（只报告，不删除）
    extra = []
    for sub in ("",) + SUBDIRS:
        d = os.path.join(dest, sub) if sub else dest
        if not os.path.isdir(d):
            continue
        for n in sorted(os.listdir(d)):
            p = os.path.join(d, n)
            if not os.path.isfile(p):
                continue
            rel = os.path.join(sub, n) if sub else n
            if rel not in src_files and os.path.basename(rel) not in IGNORED:
                extra.append(rel)
    if extra:
        print("\n目标目录中多出的文件（未处理，请人工确认）：")
        for rel in extra:
            print("  ? %s" % rel)

    # 重刷 meta（界面重装会覆盖 _user_meta.json）
    if not only_check:
        for d in (dest, src):
            subprocess.run([sys.executable, os.path.join(dest, "tools", "sync_meta.py"), "--target", d],
                           check=False)
        print()
        subprocess.run([sys.executable, os.path.join(dest, "tools", "verify_meta.py")], check=False)

    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
