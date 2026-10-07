# -*- coding: utf-8 -*-
"""
verify_meta.py — 按 WorkBuddy 真实代码路径，模拟解析已安装技能的展示名与图标。
对应 asar 中的：
  readInstalledSkillMeta()  -> 依次找 _skillhub_meta.json / _marketplace_meta.json /
                               _knot_meta.json / _builtin_market_meta.json / _user_meta.json
  parseSkillFile()          -> name = meta.name || frontmatter.name || dirName
                               iconUrl = metaIconLocalPath ? toLocalFileUrl(...) : metaIconRemoteUrl
  getInstalledSkillDisplayName() -> zh: display_name_zh || skill.name || ...
  installedSkillToCardProps()    -> skillIconUrl = resolveIconUrl(skill.iconUrl, skill.iconSource)
  SkillAvatar                    -> 有 iconUrl 就 <img src>，否则首字母头像
"""
import io, json, os, re, sys

META_CANDIDATES = [
    "_skillhub_meta.json",
    "_marketplace_meta.json",
    "_knot_meta.json",
    "_builtin_market_meta.json",
    "_user_meta.json",
]
SCHEME_RE = re.compile(r"^(https?|local-file|file)://", re.I)


def read_installed_skill_meta(skill_dir):
    for c in META_CANDIDATES:
        p = os.path.join(skill_dir, c)
        if os.path.exists(p):
            try:
                return json.load(io.open(p, encoding="utf-8")), c
            except Exception:
                return None, c
    return None, None


def to_local_file_url(abs_path):
    """win32 分支：local-file:///<backslash -> slash>"""
    return "local-file:///" + abs_path.replace("\\", "/")


def parse_frontmatter(raw):
    m = re.match(r"^---\r?\n([\s\S]*?)\r?\n---", raw)
    return m.group(1) if m else ""


def fm_field(fm, key):
    m = re.search(r"^%s:\s*(.+)$" % re.escape(key), fm, re.M)
    return m.group(1).strip() if m else None


def resolve_icon_url(*candidates):
    for raw in candidates:
        t = (raw or "").strip()
        if SCHEME_RE.match(t):
            return t
    return None


def check(skill_dir):
    print("=" * 78)
    print("SKILL DIR:", skill_dir)
    print("=" * 78)
    ok = True

    meta, meta_file = read_installed_skill_meta(skill_dir)
    if meta is None:
        print("  [X] meta: 未找到任何 meta 文件 -> 展示名会回落到 frontmatter.name（英文 slug），图标无")
        return False
    print("  [.] meta 命中文件 : %s   (优先级第 %d 位)"
          % (meta_file, META_CANDIDATES.index(meta_file) + 1))

    md = os.path.abspath(skill_dir)
    dir_name = os.path.basename(md)
    skill_md = os.path.join(md, "SKILL.md")
    raw = io.open(skill_md, encoding="utf-8").read()
    fm = parse_frontmatter(raw)
    fm_name = fm_field(fm, "name")

    # --- 展示名 ---
    name = (meta.get("name") if isinstance(meta.get("name"), str) and meta["name"] else None) \
        or fm_name or dir_name
    print("  [%s] 展示名 name      : %r" % ("V" if name else "X", name))
    print("        frontmatter.name = %r  (仅回落用，未改动则 override key 不受影响)" % fm_name)

    # --- 描述 ---
    desc = meta.get("description_zh") or fm_field(fm, "description")
    print("  [%s] description_zh   : %s" % ("V" if meta.get("description_zh") else "!", (desc or "")[:70] + "..."))

    # --- 图标 ---
    icon_local = meta.get("iconLocalPath")
    meta_icon_local = None
    if isinstance(icon_local, str) and icon_local and os.path.exists(icon_local):
        meta_icon_local = icon_local
    icon_remote = None
    if isinstance(meta.get("iconSource"), str) and re.match(r"^https?://", meta["iconSource"], re.I):
        icon_remote = meta["iconSource"]

    icon_url = to_local_file_url(meta_icon_local) if meta_icon_local else icon_remote
    if icon_local and not meta_icon_local:
        print("  [X] iconLocalPath     : %r  <-- 文件不存在，被丢弃" % icon_local)
        ok = False
    print("  [%s] iconLocalPath   : %s" % ("V" if meta_icon_local else "X", icon_local))

    card_icon = resolve_icon_url(icon_url, dir_name)
    print("  [%s] skillIconUrl    : %s" % ("V" if card_icon else "X", card_icon))
    if card_icon:
        size = os.path.getsize(meta_icon_local)
        with open(meta_icon_local, "rb") as f:
            sig = f.read(8)
        is_png = sig.startswith(b"\x89PNG")
        print("        图标文件 %d bytes, PNG签名=%s -> SkillAvatar 会渲染 <img>"
              % (size, "是" if is_png else "否"))
        if not is_png:
            ok = False
    else:
        print("        -> SkillAvatar 会退回首字母头像")
        ok = False

    # --- frontmatter 里写了但主机不读的字段（提示用） ---
    for f in ("icon", "displayName"):
        v = fm_field(fm, f)
        if v:
            print("  [i] frontmatter.%s = %r  (主机不读取此字段，实际生效的是 _user_meta.json)" % (f, v))

    print("  >>> %s" % ("PASS 图标与中文名都会显示" if ok else "FAIL"))
    return ok


if __name__ == "__main__":
    dirs = sys.argv[1:] or [
        r"C:\Users\fiona\.workbuddy\skills\chip-fa-analysis",
        r"D:\BaiduNetdiskDownload\失效分析\outputs\芯片失效分析\skills\chip-fa-analysis",
    ]
    results = [check(d) for d in dirs]
    print()
    print("TOTAL: %d/%d PASS" % (sum(results), len(results)))
