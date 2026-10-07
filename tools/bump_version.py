# -*- coding: utf-8 -*-
"""bump_version.py —— 一次改完技能包里所有版本号（单一事实源同步）。

版本号出现在 4 个源文件里，任何一处漏改都会让 SKILL.md / test-prompts.json /
README / _user_meta.json 的版本打架（本项目真实踩过：SKILL.md 改了、test-prompts.json 漏改）：

  1. SKILL.md             frontmatter `version:`
  2. test-prompts.json    顶层 `version` + 每个模块条目的 `version`
  3. tools/sync_meta.py   常量 VERSION（决定生成出来的 _user_meta.json.version）
  4. README.md            shields 版本徽章 + "当前 **x.y.z**"

用法（在技能根目录执行）：
    python tools/bump_version.py 5.0.3          # 改 4 个源文件
    python tools/bump_version.py                # 只打印当前版本分布，不改动
"""
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = sys.argv[1] if len(sys.argv) > 1 else None

F_SKILL = os.path.join(BASE, "SKILL.md")
F_TESTS = os.path.join(BASE, "test-prompts.json")
F_META = os.path.join(BASE, "tools", "sync_meta.py")
F_README = os.path.join(BASE, "README.md")


def current_versions():
    t = io.open(F_SKILL, encoding="utf-8").read()
    m = re.search(r"(?m)^version:\s*(\S+)\s*$", t)
    skill_v = m.group(1) if m else "?"
    j = json.load(io.open(F_TESTS, encoding="utf-8"))
    tests_v = {j.get("version")}
    for v in (j.get("modules") or {}).values():
        if isinstance(v, dict):
            tests_v.add(v.get("version"))
    t = io.open(F_META, encoding="utf-8").read()
    m = re.search(r'(?m)^VERSION\s*=\s*"([^"]*)"', t)
    meta_v = m.group(1) if m else "?"
    readme_v = "?"
    if os.path.isfile(F_README):
        t = io.open(F_README, encoding="utf-8").read()
        m = re.search(r"badge/version-([0-9][^-\s)]*)", t)
        readme_v = m.group(1) if m else "?"
    return skill_v, sorted(x for x in tests_v if x), meta_v, readme_v


def main():
    skill_v, tests_v, meta_v, readme_v = current_versions()
    print("当前版本：")
    print("  SKILL.md           : %s" % skill_v)
    print("  test-prompts.json  : %s" % ", ".join(tests_v))
    print("  tools/sync_meta.py : %s" % meta_v)
    print("  README.md          : %s" % readme_v)

    if TARGET is None:
        print("\n（未给目标版本，仅查询。用法：python tools/bump_version.py 5.0.3）")
        return 0

    if not re.match(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.\-]+)?$", TARGET):
        print("\n!! 版本号格式应为 MAJOR.MINOR.PATCH[-rc.N]，实际：%s" % TARGET)
        return 2

    # 1) SKILL.md
    t = io.open(F_SKILL, encoding="utf-8").read()
    t2, n1 = re.subn(r"(?m)^version:\s*\S+\s*$", "version: " + TARGET, t, count=1)
    io.open(F_SKILL, "w", encoding="utf-8", newline="\n").write(t2)

    # 2) test-prompts.json
    j = json.load(io.open(F_TESTS, encoding="utf-8"))
    n2 = 0
    if "version" in j:
        j["version"] = TARGET
        n2 += 1
    for v in (j.get("modules") or {}).values():
        if isinstance(v, dict) and "version" in v:
            v["version"] = TARGET
            n2 += 1
    io.open(F_TESTS, "w", encoding="utf-8", newline="\n").write(
        json.dumps(j, ensure_ascii=False, indent=2) + "\n")

    # 3) sync_meta.py
    t = io.open(F_META, encoding="utf-8").read()
    t2, n3 = re.subn(r'(?m)^VERSION\s*=\s*"[^"]*"', 'VERSION = "%s"' % TARGET, t, count=1)
    io.open(F_META, "w", encoding="utf-8", newline="\n").write(t2)

    # 4) README.md（徽章 + 正文「当前 x.y.z」）
    n4 = 0
    if os.path.isfile(F_README):
        t = io.open(F_README, encoding="utf-8").read()
        t, k1 = re.subn(r"(badge/version-)[0-9][^-\s)]*", r"\g<1>" + TARGET, t)
        t, k2 = re.subn(r"(当前\s*\*\*)[0-9]+\.[0-9]+\.[0-9]+[^*]*(\*\*)",
                        r"\g<1>" + TARGET + r"\g<2>", t)
        n4 = k1 + k2
        io.open(F_README, "w", encoding="utf-8", newline="\n").write(t)

    print("\n已改到 %s：" % TARGET)
    print("  SKILL.md           : %d 处" % n1)
    print("  test-prompts.json  : %d 处" % n2)
    print("  tools/sync_meta.py : %d 处" % n3)
    print("  README.md          : %d 处" % n4)
    print("\n下一步：更新 CHANGELOG.md → python tools/install.py → python tools/verify_meta.py")
    return 0 if (n1 and n2 and n3) else 1


if __name__ == "__main__":
    sys.exit(main())
