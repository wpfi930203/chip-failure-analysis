# 芯片 + 裂纹 —— skill 图标设计说明

> **文件**：`icons/logo.png`（200×200 PNG）+ `icons/logo.svg`（矢量源）
> **生成**：`tools/make_icon.py`（纯 Pillow 手绘矢量，**不调用任何图像生成 API**，积分消耗 0）
> **复核**：`tools/preview_icon.py` 生成「2× 原图 + 32/40/64/100/200px 缩略条」对照图
> **引用方式**：`_user_meta.json` 的 `iconLocalPath`（**绝对路径**）。见第六节——frontmatter 里的 `icon:` / `displayName:` 会被主机静默丢弃，不生效（2026-10-07 拆 `app.asar` 实测）。
> **刷新**：`tools/sync_meta.py`（写 meta）+ `tools/install.py`（拷贝并校验）+ `tools/verify_meta.py`（按主机真实代码路径复核）

---

## 一、为什么是「芯片 + 裂纹」而不是纯芯片

图标要传递的是**这个 skill 到底管什么**。芯片 = 领域；芯片上带裂纹 = **失效分析**。
少了裂纹，它就只是一枚通用 IC 图标，和"芯片设计""芯片制造"无法区分；
带了裂纹，"坏了、并且要把坏在哪找出来"这层语义在 40px 就成立。

| 候选图形 | 判断 |
|---|---|
| 纯芯片（无裂纹） | ❌ 泛用于任何芯片相关 skill，无区分度 |
| 放大镜 + 芯片 | ⚠️ 32px 下放大镜手柄会糊成一条斜线，反而像裂纹 |
| 波形 / 频谱 | ❌ 语义偏"测试/信号"，不表示"失效机理" |
| ⚡ 闪电 | ❌ 泛用于"电力/警示"，易被读成"过压"单一含义 |
| **芯片 + 裂纹 + 裂纹源点** | ✅ 领域明确 + 动作明确（裂纹源定位是 FA 的第一步），且与本机其他 skill 图标不撞形不撞色 |

## 二、图形语义拆解

```
        ▮ ▮ ▮ ▮        ← 四面引脚（QFP 封装俯视，无歧义的"芯片"符号）
    ▮  ┌────────┐  ▮
    ▮  │ ▓▓▓▓▓▓ │  ▮    ← 浅色封装体（模塑料）
    ▮  │ ▓╱▓▓▓● │  ▮    ← 深色裸片（die）
    ▮  │ ▓▓╱▓▓▓ │  ▮       橙色折线 = 脆性断裂裂纹
    ▮  └────────┘  ▮       ● 高光点  = 裂纹源（origin）
        ▮ ▮ ▮ ▮
```

| 元素 | 颜色 | 语义 | 设计作用 |
|---|---|---|---|
| 底 | `#0E3A44`→`#06222B` | — | 深青蓝渐变，与 `lean-production-expert` 的深海军蓝、linkfox 的品牌色**都不撞色** |
| 引脚 ×16 | `#A8DFE9` | 引线 / 封装 | 一眼可数=16，规则排布传达"规整的工程对象" |
| 封装体 | `#EAF7FA` + `#86CFDE` 描边 | 模塑料封装 | 最亮的大色块，稳定视觉重心 |
| 裸片 die | `#12525F`→`#0A3641` | 芯片本体 | 深色内嵌方块，制造"封装体 / 芯片本体"两层结构 |
| 裂纹 | `#FF7A45` | 脆性断裂 | 与青底**互补色**，32px 下仍是画面唯一暖色 → 视线第一落点 |
| 裂纹源点 | `#FF7A45` + `#FFD2B8` 芯 | 裂纹起源 | 对应技能里"断口判读 / 裂纹源分析"的动作 |

## 三、迭代记录（依据渲染后目视复核）

| 版本 | 复核发现 | 修法 |
|---|---|---|
| v1 | 语义正确，但 **32px 下裂纹糊成一个橙色团块**（线宽 7 + 起点圆点 r=11 粘连） | 线宽 7→6，裂纹源点 r 11→9.5 / 高光芯 4→3.2 |
| **v2（当前）** | 40px 起裂纹可辨为**斜向折线**（而非团块），32px 保留"芯片 + 橙色斜痕"的辨识度 | — |

> **教训沿用精益屋图标那一条**：图标不能"画完就交"。`make_icon.py` 一次同时输出 PNG 与 SVG，
> 改完必须跑 `preview_icon.py` **把图读回来看**——本次第一版就是靠缩略条复核才发现 32px 糊团。

## 四、技术规格

| 项 | 值 |
|---|---|
| 输出尺寸 | 200×200 px（对齐本机其他 skill app icon 规格） |
| 格式 | PNG（`optimize=True`）+ SVG 矢量源，二者结构一一对应 |
| 抗锯齿 | 4× 超采样（800×800）→ LANCZOS 降采样 |
| 圆角 | 底板 rx=44（边长 22%）；封装体 rx=12；引脚 rx=3 |
| 最小可辨识尺寸 | **约 32 px**（skill 列表通常 ≥40 px，64 px 以上折线细节完整） |
| 透明通道 | 无（底板不透明，任意背景色下都不会"发灰"） |
| 版权 | 原创矢量，无版权风险 |

## 五、如何修改

```bash
PY="C:/Users/fiona/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
T="D:/BaiduNetdiskDownload/失效分析/outputs/芯片失效分析/skills/chip-fa-analysis/tools"

# 改配色 / 结构 → 编辑 make_icon.py 顶部颜色常量或 CRACK_PATH / PIN_CENTERS 坐标
"$PY" "$T/make_icon.py"      # 输出 icons/logo.png + icons/logo.svg
"$PY" "$T/preview_icon.py"   # 输出复核对照图到 _tools/_icon_preview.png
```

> 改 `make_icon.py` 时注意：`SVG` 常量是手写矢量，**必须与绘图代码同步修改**，
> 否则 PNG 与 SVG 会不一致（两者共用 `CRACK_PATH` / `PIN_CENTERS` 等常量作为单一事实源）。

## 六、显示名与图标的生效机制（拆 `app.asar` 实测，2026-10-07）

**结论：SKILL.md 的 frontmatter 写 `displayName:` 和 `icon:` 都没用。** 真正生效的是技能目录下的
`_user_meta.json`。

证据链（`C:\Program Files\WorkBuddy\resources\app.asar`）：

| 环节 | 函数 | 事实 |
|---|---|---|
| ② 读 meta | `readInstalledSkillMeta(dir)` | 按序找 `_skillhub_meta.json` → `_marketplace_meta.json` → `_knot_meta.json` → `_builtin_market_meta.json` → **`_user_meta.json`**，取**第一个存在的** |
| ③ 解析 SKILL.md | `asSkillFrontmatter(data)` | 白名单只有 `name` / `description` / `description_zh` / `description_en` / `when-to-use` / `allowed-tools` / `disable` / `disable-model-invocation` / `user-invocable` / `license` → **`displayName`、`icon` 被丢弃** |
| ④ 组装 | `parseSkillFile()` | `name = meta?.name \|\| frontmatter.name \|\| dirName`；`iconUrl = (meta.iconLocalPath 存在 ? toLocalFileUrl(...) : meta.iconSource)` |
| ⑤ 取显示名 | `getInstalledSkillDisplayName()` | 中文环境 `display_name_zh \|\| skill.name \|\| …`，而 `display_name_zh` 无人赋值 → **落到 ③ 的 `name`，即 `_user_meta.json.name`** |
| ⑥ 卡片 | `installedSkillToCardProps()` → `SkillAvatar` | `skillIconUrl = resolveIconUrl(skill.iconUrl, skill.iconSource)`；有 `iconUrl` 就渲染 `<img src="local-file:///...">`，否则退回首字母头像 |

所以 `_user_meta.json` 里两个字段是必需的：

```json
{
  "name": "芯片失效分析 Skill",
  "iconLocalPath": "C:\\Users\\fiona\\.workbuddy\\skills\\chip-fa-analysis\\icons\\logo.png"
}
```

三条硬约束：

1. **`iconLocalPath` 必须是绝对路径且文件真实存在**——主机做 `fs.existsSync()` 判定，写相对路径等于没写。
2. **不要改 `frontmatter.name`**。运行期身份（agent-cli 的 `skill.name`、`settings.json` 的
   `skillOverrides` 键）都用 `frontmatter.name || 目录名`，保持 `chip-fa-analysis` 才能让
   `/chip-fa-analysis` 与开关继续工作；中文名只放在 `_user_meta.json.name` 里。
3. **通过界面「导入技能 / 重装」会覆盖 meta**。`installSkillByPath()` 会先 `rm -rf` 目标目录，
   再写一份只有 `{name, installedAt, source:"userImport"}` 的 `_user_meta.json`——
   显示名与图标都会丢。识别到这种情况就跑一次 `tools/sync_meta.py` 补回来。

排查顺序：`verify_meta.py` 打印 `skillIconUrl` 为 `local-file:///...` 且图标文件 PNG 签名 `= 是`，
即链路通；若界面仍未刷新，重启 WorkBuddy 让主进程重新扫描技能目录。
