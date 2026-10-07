# Changelog

本文件记录本技能包的所有重要变更。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

版本号语义：

- **MAJOR** — 知识体系重构、模块编号重排、破坏性变更（如分体技能合并为单技能）
- **MINOR** — 新增知识模块 / 新增主题
- **PATCH** — 内容修订、打包方式、文档、图标、元数据等不影响知识结构的变更

---

## [5.0.3] - 2026-10-07

### Added
- `tools/release.py` — **自包含一键发版脚本**：owner/repo 从 `git remote` 推导、仓库路径从脚本自身
  位置推导，不依赖任何仓库外文件。串联「体检 → 建仓 → 推送 main → 推标签 → 用 CHANGELOG 建 Release」，
  并可幂等重跑。`--check` 只体检不改动；`--create-repo` 自动建仓；`--force-with-lease` 覆盖推送。
  token 经**临时 credential helper** 注入，不落 `.git/config`、不进 argv 与日志；文件方式读取时成功后自动删除。
- `VERSIONING.md` 第七节 — 远程仓库信息、clone 目录名硬约束、克隆后必做 `sync_meta.py`，
  以及 `github.com:443` 不可达（沙箱/受限网络）时的三种处理路径。
- `.gitignore` 新增凭据拦截段：`.gh_token` / `.gh_token.*` / `*.token` / `.env`。

### Changed
- 版本号统一至 5.0.3（`SKILL.md` / `test-prompts.json` / `tools/sync_meta.py`）。
- `VERSIONING.md` 发版流程第 5–6 步改用 `tools/release.py`，并补该脚本的能力表与选型理由；
  标签表补 `v5.0.3` 行、注明每个标签同时对应一个 Release。
- 4 处版本号一致性改由 `tools/bump_version.py` 批量维护（历史上曾漏改 `test-prompts.json`）。

### Notes
- **本仓库自 v5.0.2 起的 git 历史与标签**。v1.0.0–v5.0.1 的演进只存在于 `CHANGELOG.md`
  （早期以"直接改写工作区文件"的方式迭代，文件快照不可追溯），**未补打指向当前提交的标签**。
- v5.0.3 是本仓库的**第二个标签**，同时用于验证 `tools/release.py` 全链路可用。

---

## [5.0.2] - 2026-10-07

### Fixed
- **修复「技能图标与中文名不显示」**。根因：WorkBuddy 桌面端的 frontmatter 白名单不含
  `displayName` 与 `icon`，且本技能是直接写文件安装的、目录下没有 meta 文件，导致
  展示名回落到英文目录名、图标回落到首字母头像。
  修法：新增 `_user_meta.json`（`name` 中文展示名 + `iconLocalPath` 绝对路径 + `description_zh`）。

### Added
- `tools/sync_meta.py` — 生成/刷新 `_user_meta.json`，沿用既有 `installedAt` 以便两侧对账。
- `tools/verify_meta.py` — 按 WorkBuddy 真实代码路径模拟解析，打印展示名 / `iconUrl` / PNG 签名。
- `tools/install.py` — 一键：拷贝 → 刷 meta → 逐文件 SHA256 校验 → 自动复核；目标目录多余文件只报告不删除。
- `VERSIONING.md` — 版本策略与发版流程。
- 仓库工程文件：`README.md`、`CHANGELOG.md`、`LICENSE`、`.gitignore`、`.gitattributes`。

### Changed
- 版本号统一至 5.0.2（`SKILL.md` / `test-prompts.json`(23 处) / `tools/sync_meta.py` 同步）。
- `icons/README.md` 增第六节，记录 frontmatter 无效、`_user_meta.json` 生效的完整证据链与三条硬约束。

---

## [5.0.1] - 2026-10-07

### Added
- **技能图标**：`icons/logo.png`（200×200）+ `icons/logo.svg`（矢量源）+ `icons/README.md`（设计说明）。
  图形语义 = 芯片（四面 16 引脚 + 封装体 + 裸片）+ 裂纹 + 裂纹源实心点——芯片给领域，
  裂纹给"失效分析"，裂纹源点对应"断口判读 / 裂纹源定位"这一 FA 第一动作。
- `tools/make_icon.py`（纯 Pillow 手绘，确定性、零外部 API）与 `tools/preview_icon.py`
  （输出 2× 原图 + 32/40/64/100/200px 缩略条，用于渲染后目视复核）。

### Changed
- `MARKETPLACE_LISTING.md` 由上架时的 v3.0.0/12 模块重写为 **v5.0.0/25 模块**：
  短文案 A/B 重写、"能帮你做什么"按五大主题重组、典型提问补 4 条、来源表补 IMA 四类源及等级、
  诚实边界从 5 条扩到 9 条。
- 图标迭代：v1（线宽 7、源点 r=11）在 32 px 下裂纹糊成橙团 → v2（线宽 6、源点 r=9.5）40 px 起可辨为斜向折线。

---

## [5.0.0] - 2026-10-02

### Added
- **模块 23 `reliability-test-matrix.md`** — 可靠性试验四维矩阵（项目 × 条件 × 激发机理 × 标准号）、
  HTOL 时长—年限换算、THB / HAST / PCT 三选一判据、从缺陷反查应做试验速用表。
- **模块 24 `app-level-mechanisms.md`** — 应用级与封装界面机理：锡枝晶 ECM 完整链与"自愈"解释、
  EOS 六类来源、器件级 HBM/MM/CDM vs 系统级 IEC 61000-4-2、Au-Al 柯肯达尔与 Ni 阻挡层、
  减薄裂片 100–150 μm 临界厚度、SOA/EAS/dv/dt。
- **模块 25 `fa-practice-tools.md`** — FA 实操：五步交付物、委托接样 10 要点、手段选型反查表、
  6 个可复用判读案例。
- `test-prompts.json` 扩至 22 组模块条目（新增正例 20 / 诱饵 6 / 边界 9）。

### Changed
- 重写 `references/kb-index.md`：7 个 IMA 订阅库盘点、五主题覆盖矩阵、跨库去重与冲突裁决四级优先级。
- `INDEX.md` / `COVERAGE_AND_LIMITS.md` / `PUBLISH_REPORT.md` 三份顶层文档同步至 v5.0.0。

### Known limitations
- 逐条核验后，7 个订阅库中**仅库 3「芯片应用失效分析」原文可取**，且仅限公众号/网页类条目；
  库 1/4/6/7 全部 `can_fetch_content=false`，库 5 为空库。故模块 23/24/25 均为 **L2 源**，
  不得作为认证唯一依据。已在 `SKILL.md` B 段固化为禁令：**禁止宣称「7 库已全部蒸馏完毕」**。

---

## [4.2.0] - 2026-10-01

### Added
- **模块 22 `case-atlas.md`** — 失效模式图谱与中英判读术语：PFA/DPA/CA/FA/EA 五类活动分工、
  仿冒翻新八类识别、失效四级分类、爆米花六步链 / 分层四界面 / 开裂四型递进表、
  键合缺陷中英术语表、"X-ray 查不出开路"纪律、EOS vs ESD 判别表。

---

## [4.1.0] - 2026-10-01

### Added
- **模块 21 `fa-desk-reference.md`** — ASM Desk Reference 7th Ed. (2019, L1) 精要：
  封装 FA 实战五步（每步附误判风险）、故障隔离选型与**定量分辨率表**
  （LIT 几 µK / TDR ~1 mm vs **EOTPR <10 µm** / LADA-SDL / PEM 三类发射 / MFI / LVP / 3D-LIT）。

---

## [4.0.0] - 2026-10-01

### Added
- **模块 19 `power-device-reliability.md`** — 功率器件可靠性试验与寿命建模（IPFA 2019 教程，L1.5）：
  磨损/异常条件/在线监测三层次、ALT 设计、寿命模型族（Coffin-Manson / 改进 C-M /
  Norris-Landzberg / Bayerer / Semikron）、LESIT 曲线、键合线 lift-off 在线监测。
- **模块 20 `kb-index.md`** — IMA 订阅库盘点与覆盖地图。

### Changed
- **知识体系重构为五大主题**：元器件基础 / 可靠性与测试标准 / 失效机理 / 分析流程与方法 /
  预防闭环与案例；模块地图改为「编号索引 + 主题视图」双视图。
- 跨库合并去重，冲突按四级源优先级裁决。

---

## [3.3.0] - 2026-10-01

### Added
- **模块 18 `report-template.md`** — 失效分析报告模板：12 节逐项填空、**工序/环节定位表**
  （晶圆/封装/测试/包装/应用/可靠性六区）、**仪器手段速查矩阵**（15 种 + 破坏性标注）、
  **接样确认清单 12 项**、三格式输出规范（对话框简要 / HTML / PDF）。

---

## [3.2.0] - 2026-10-01

### Added
- **模块 17 `standards-jesd22.md`** — JESD22 一手标准速查：湿热族（A101/A110/A118/A102）、
  温循与热冲击（A104/A106/A105）、功率器件偏置寿命（A108F 的 HTFB/HTRB/HTGB）、
  功率循环（A122A vs A105D）、J-STD-020E MSL 定量表与分层判据。

> 本版升级中曾出现**同一文件并行编辑竞态**（4 处并行 Edit 只落盘 1 处，版本号未改上），
> 已改为串行编辑并在项目记忆中立规。

---

## [3.1.0] - 2026-10-01

### Added
- **模块 13–16** — 蒸馏 IMA 个人知识库存量文章：
  `standards.md`（考核项目—条件—判据总表、AEC-Q/JESD22 地图、Precon）、
  `accel-models.md`（六大加速模型 + 13 种机理 Ea 速查）、
  `bonding-practice.md`（键合定量专题）、
  `mechanism-modern.md`（HCI/TDDB/NBTI/可动离子/EM）。

---

## [3.0.0] - 2026-10-01

### Changed
- **破坏性重构**：把 v2.0.0 的 13 个分体技能（1 hub + 12 原子）**合并为单一技能**
  `chip-fa-analysis`，结构改为 `SKILL.md` 总纲 + `references/` 12 模块。
  合并理由：分体版跨技能路由成本高、术语与判据重复、不便整体分发与版本管理。

---

## [2.0.0] - 2026-10-01

### Added
- 继续蒸馏另外 4 本专著（典型案例集、可靠性专著 ×2、失效分析基础第 2 版），
  合成后形成 **13 个技能**（1 hub + 12 原子），模块涵盖 procedure / electrical /
  localization / sample-prep / characterization / stress-test / mechanism / prevention /
  closed-loop / reasoning / hermeticity / reliability-stats。

---

## [1.0.0] - 2026-10-01

### Added
- 首个版本：以仓颉蒸馏流水线（整书理解 → 五路提取 → 三重验证 → RIA++ 构造 → 知识卡片 →
  索引 → 压力测试 → 发布）蒸馏《电子元器件失效分析技术》，产出 `chip-fa-*` 系列技能。
