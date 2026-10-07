# -*- coding: utf-8 -*-
"""生成/刷新技能的 `_user_meta.json`（WorkBuddy 桌面端真正读取显示名与图标的位置）。

背景（2026-10-07 实测自 app.asar）：
  1. `asSkillFrontmatter()` 的 frontmatter 白名单只有
     name / description / description_zh / description_en / when-to-use /
     allowed-tools / disable / disable-model-invocation / user-invocable /
     license / examples_zh / examples_en
     → **`displayName` 与 `icon:` 会被静默丢弃**，写在 SKILL.md 里不生效。
  2. 显示名走`getInstalledSkillDisplayName()`：
     zh → `display_name_zh || skill.name || display_name || slug`
     而 `parseSkillFile()` 返回的 `name = meta?.name || frontmatter.name || dirName`
     → **`_user_meta.json` 的 `name` 才是中文名的唯一来源**。
  3. 图标走 `iconUrl = metaIconLocalPath ? toLocalFileUrl(...) : metaIconRemoteUrl`：
     - `iconLocalPath` 必须是**绝对路径**且文件存在（existsSync 判定，相对路径无效）
     - `iconSource` 只有匹配 `^https?://` 才被当远程图
     → 本地图标只能靠 `iconLocalPath`。
  4. 运行期身份不受影响：agent-cli 与 `overrideKey` 都用 `frontmatter.name`，
     所以把 meta.name 改成中文不会破坏 `/chip-fa-analysis` 的调用与开关。

用法：
    python tools/sync_meta.py            # 同时刷新工作区源目录与用户级安装目录
    python tools/sync_meta.py --target <skill_dir>   # 只刷指定目录
"""
import json
import io
import os
import sys
import time

DISPLAY_NAME = "芯片失效分析 Skill"
DISPLAY_NAME_EN = "Chip Failure Analysis Skill"
SLUG = "chip-fa-analysis"
VERSION = "5.0.2"
DESCRIPTION_ZH = ("芯片/半导体器件失效分析专家。25 个模块覆盖五大主题：元器件基础、可靠性与测试标准、"
                  "失效机理、分析流程与方法、预防闭环与案例。含 11 步程序、故障隔离定量分辨率、"
                  "可靠性试验四维矩阵、应用级机理（锡枝晶/EOS/ESD/键合退化）、功率器件寿命建模、"
                  "FMEA/FTA/SPC、FRACAS 归零，并输出 12 节分析报告。")

DEFAULT_TARGETS = [
    r"D:\BaiduNetdiskDownload\失效分析\outputs\芯片失效分析\skills\chip-fa-analysis",
    r"C:\Users\fiona\.workbuddy\skills\chip-fa-analysis",
]
ICON_REL = os.path.join("icons", "logo.png")


def build_meta(skill_dir, installed_at=None):
    icon_abs = os.path.normpath(os.path.join(skill_dir, ICON_REL))
    meta = {
        "name": DISPLAY_NAME,
        "display_name": DISPLAY_NAME_EN,
        "slug": SLUG,
        "version": VERSION,
        "installedAt": installed_at if installed_at is not None else int(time.time() * 1000),
        "source": "userImport",
        "description_zh": DESCRIPTION_ZH,
        # 本地图标：必须是绝对路径，且文件真实存在
        "iconLocalPath": icon_abs,
        # 防止自动更新/迁移覆盖用户手工维护的 meta
        "userModified": True,
    }
    return meta


def read_installed_at(d):
    """沿用已有 installedAt，保证工作区源目录与用户级副本字节一致（便于 SHA256 对账）。"""
    p = os.path.join(d, "_user_meta.json")
    if not os.path.exists(p):
        return None
    try:
        v = json.load(io.open(p, encoding="utf-8")).get("installedAt")
        return int(v) if isinstance(v, (int, float)) else None
    except Exception:
        return None


def main():
    targets = DEFAULT_TARGETS
    if "--target" in sys.argv:
        i = sys.argv.index("--target")
        targets = [sys.argv[i + 1]]

    for d in targets:
        if not os.path.isdir(d):
            print("SKIP (no such dir): %s" % d)
            continue
        icon_abs = os.path.normpath(os.path.join(d, ICON_REL))
        icon_ok = os.path.isfile(icon_abs)
        meta = build_meta(d, read_installed_at(d))
        if not icon_ok:
            meta.pop("iconLocalPath", None)
            meta["iconSource"] = "letter:auto"   # 兜底：退回首字母头像
        path = os.path.join(d, "_user_meta.json")
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
        print("%-72s icon=%s" % (path, "OK " + icon_abs if icon_ok else "MISSING -> letter:auto"))


if __name__ == "__main__":
    main()