# 芯片失效分析 Skill · Chip Failure Analysis

> 一个可直接装进 WorkBuddy 的**芯片/半导体器件失效分析**技能包：25 个模块 · 五大主题 · 12 节报告模板。
> 从「这颗芯片为什么烧了」一路问到「问题出在哪个工序、该用什么仪器、报告怎么写、怎么闭环」。

[![version](https://img.shields.io/badge/version-5.0.2-blue)](CHANGELOG.md)
[![modules](https://img.shields.io/badge/modules-25-brightgreen)](SKILL.md)
[![lang](https://img.shields.io/badge/lang-中文-red)]()
[![license](https://img.shields.io/badge/license-代码%20MIT%20%2F%20内容见%20LICENSE-lightgrey)](LICENSE)

---

## 它解决什么问题

失效分析（FA）的难点从来不是"不知道有哪些仪器"，而是**顺序和判据**：

- 现象一堆，但不知道该先电测还是先定位；
- 知道该开封，但不知道用哪种开封法、会不会把证据毁掉；
- 现象齐了，判不出是 EOS 还是 ESD、是键合脱落还是柯肯达尔空洞；
- 结论写了，但说不清是"猜测"还是"能站住的结论"；
- 报告交了，但没定位到工序环节，产线不知道改哪里。

这个技能把上述判断固化成**可检索的模块 + 明确的判据 + 强制向用户确认的接样流程**。

## 五大主题 / 25 个模块

| 主题 | 模块 |
|---|---|
| **① 元器件基础与工艺背景** | `sample-prep`（开封/剥层/切片/FIB/减薄）、`characterization`（OM/SEM/TEM/AFM/X-ray/SAM/AES/SIMS/XPS/FTIR） |
| **② 可靠性与测试标准** | `standards`（考核项目—条件—判据总表）、`standards-jesd22`（JESD22 一手速查：湿热族/温循/功率偏置寿命 A108F/MSL）、`reliability-test-matrix`（项目×条件×机理×标准号四维）、`accel-models`（六大加速模型 + 13 种机理 Ea 速查）、`reliability-stats`（四分布/威布尔/MTTF/抽样）、`hermeticity`（泄漏率/粗检/氦质谱细检） |
| **③ 失效机理** | `mechanism`（模式—机理反查、九类核心机理、功率器件六类特化、ESD 专节）、`mechanism-modern`（HCI/TDDB/NBTI/可动离子/EM）、`app-level-mechanisms`（锡枝晶 ECM、EOS 六类来源、HBM/MM/CDM vs IEC 61000-4-2、Au-Al 柯肯达尔、减薄裂片临界厚度、SOA/EAS/dv/dt）、`bonding-practice`（键合定量专题）、`power-device-reliability`（功率循环/寿命模型族/Bayerer/lift-off 在线监测） |
| **④ 分析流程与方法** | `procedure`（11 步作业单）、`electrical`、`localization`（光探测/EBT/磁显微/红外热像 + 分辨率量级）、`fa-desk-reference`（故障隔离定量分辨率：TDR ~1 mm vs EOTPR <10 µm）、`reasoning`（断口六项任务/裂纹源判读）、`fa-practice-tools`（五步交付物 + 委托接样 10 要点 + 手段选型反查表 + 可复用案例） |
| **⑤ 预防闭环与案例** | `prevention`（FMEA 十步 / FTA 最小割集 / SPC 控制图）、`closed-loop`（FRACAS 归零/四 M）、`case-atlas`（PFA/DPA/CA/FA/EA 分工、仿冒翻新八类、爆米花/分层/开裂递进表、键合缺陷中英术语表、EOS vs ESD 判别）、`report-template`（12 节报告 + 工序六区定位表 + 15 种仪器矩阵 + 接样确认 12 项 + 三种输出格式）、`kb-index`（知识库盘点与覆盖地图） |

完整模块地图与"何时读哪个模块"见 [`SKILL.md`](SKILL.md)。

## 快速开始

### 装到 WorkBuddy（用户级）

```bash
git clone https://github.com/wpfi930203/chip-failure-analysis.git \
  ~/.workbuddy/skills/chip-fa-analysis          # 注意：目录名必须是 chip-fa-analysis
cd ~/.workbuddy/skills/chip-fa-analysis
python tools/sync_meta.py                        # 生成 _user_meta.json（中文名 + 图标）
python tools/verify_meta.py                      # 校验展示名与图标链路
```

重启 WorkBuddy，技能面板即出现「芯片失效分析 Skill」与芯片图标。

> **为什么不能直接克隆成 `chip-failure-analysis` 目录？**
> 技能的运行期身份取 `SKILL.md` 的 `frontmatter.name`（= `chip-fa-analysis`），
> 但**目录名**会影响 `frontmatter.name` 缺失时的回落与 `overrideKey` 稳定性。
> 一律用 `chip-fa-analysis` 作为目录名，最省事。

### 日常调用

```
/chip-fa-analysis MOS 金线键合脱落，可能是什么因素导致的
/chip-fa-analysis 脱板就好了、加大电流又恢复，这是什么机理
/chip-fa-analysis 帮我出一份失效分析报告
```

技能在接样阶段会**先按 12 项清单向你确认信息**（失效阶段 / 批次聚集性 / 封装形态 / 已做检测 / 应用环境 …），
再给分析方案——避免在信息不足时给出看似完整实则空洞的结论。

## 目录结构

```
chip-fa-analysis/
├── SKILL.md                 总纲：四层目标、三条铁律、11 步程序、模块地图、跨库去重与冲突裁决
├── test-prompts.json        22 组模块触发测试（正例 / 诱饵 / 边界），含防误用用例
├── references/              25 个知识模块（模块地图见 SKILL.md）
├── icons/                   logo.png（200×200）+ logo.svg（矢量源）+ README.md（设计说明）
├── tools/                   可复现工具链（见下）
├── CHANGELOG.md             版本历史
├── VERSIONING.md            版本策略与发版流程
└── LICENSE                  许可与来源声明
```

### tools/ 工具链

| 脚本 | 作用 |
|---|---|
| `make_icon.py` | 纯 Pillow 手绘生成 `icons/logo.png` + `logo.svg`（确定性，无外部 API） |
| `preview_icon.py` | 输出「2× 原图 + 32/40/64/100/200px 缩略条」对照图，用于**渲染后目视复核** |
| `sync_meta.py` | 生成 `_user_meta.json`：中文展示名 + 图标绝对路径 |
| `verify_meta.py` | 按 WorkBuddy 真实代码路径模拟解析，打印展示名 / iconUrl / PNG 签名 |
| `install.py` | 一键：拷贝 → 刷 meta → 逐文件 SHA256 校验 → 自动复核；多出的文件只报告不删除 |
| `bump_version.py` | 一次改完 4 处版本号（防漏改）；不带参数则只查询版本分布 |

## 一个必须知道的坑：WorkBuddy 不读 frontmatter 的 `displayName` / `icon`

在 WorkBuddy 桌面端，`SKILL.md` 的 frontmatter 白名单只有
`name / description / description_zh / description_en / when-to-use / allowed-tools / disable / disable-model-invocation / user-invocable / license`。
**写 `displayName:` 和 `icon:` 会被静默丢弃。**

真正生效的是技能目录下的 `_user_meta.json`：

| 环节 | 取值 |
|---|---|
| 展示名 | `parseSkillFile()` 的 `name = meta?.name \|\| frontmatter.name \|\| 目录名`，中文环境最终落到 `meta.name` |
| 图标 | `iconUrl = (meta.iconLocalPath 存在 ? localFileUrl : meta.iconSource)`，`iconLocalPath` 必须是**绝对路径且文件存在** |

所以本仓库 **不提交 `_user_meta.json`**（每台机器的绝对路径不同），改为 clone 后跑一次
`python tools/sync_meta.py` 现场生成。完整证据链见 [`icons/README.md`](icons/README.md) 第六节。

另有两条硬约束：

1. **`frontmatter.name` 不要改成中文**——agent-cli 的 `skill.name` 与 `settings.json` 的 `skillOverrides` 键都用它，改了会断掉 `/技能名` 调用与开关。
2. **界面「导入 / 重装」会 `rm -rf` 目标目录并覆盖 `_user_meta.json`**，中文名与图标会丢；重跑 `tools/sync_meta.py` 即可。

## 来源与诚实边界

**来源分级**（`L1` 一手标准/手册 > `L1.5` 翻译版 > `L2` 二手文章）：

| 等级 | 来源 |
|---|---|
| L1 | 专著 5 本（《电子元器件失效分析技术》、典型案例集、可靠性专著 2 本、失效分析基础第 2 版）· ASM Desk Reference 7th Ed. (2019) · JEDEC JESD22 系列（A101/A102/A104/A105/A106/A108F/A109B/A110/A118/A122A）· IPC/J-STD-020E |
| L1.5 | IPFA 2019 功率器件可靠性教程 · 部分标准翻译版 |
| L2 | 半导体行业公众号与技术文章（应用级机理、试验矩阵、FA 实操三者主要来自此层） |

**边界（不掩饰）**：

- **模块 23/24/25 主要来自 L2 工程经验层**，可用于工程参考与快速定位，**不得作为认证或判定的唯一依据**；涉认证请回到 `standards-jesd22.md` 与标准原文。
- **七本 IMA 订阅知识库的原文可取性受限**，实际只有部分条目可取（详见 `references/kb-index.md`）；本仓库**不声称**已完整覆盖这些库。
- **三个缺口未闭合**：① MIL-STD-883 M1014 检漏限值 ② AEC-Q 全系试验矩阵 ③ Desk Reference 的 EOS/ESD 判据章。
- **OCR 数字不可靠**：源自扫描版专著的数值均经交叉比对，个别表格数值可能存在 OCR 误差，关键判定请回查原书。
- 图片来源图集未纳入。

## 许可

- **代码**（`tools/*.py`）：MIT，见 [`LICENSE`](LICENSE)。
- **知识内容**（`SKILL.md`、`references/*`、`test-prompts.json`）：**蒸馏自第三方版权作品**，版权归原出处所有，此处仅作学习与研究用途，**禁止商业使用**；如需商用请自行取得原著作权人授权。详见 [`LICENSE`](LICENSE)。

## 版本管理

版本号语义化（`MAJOR.MINOR.PATCH`），当前 **5.0.2**。
版本号在 `SKILL.md`、`test-prompts.json`、`tools/sync_meta.py`、`_user_meta.json` 四处同步，
改版一律用脚本保证一致。策略与发版流程见 [`VERSIONING.md`](VERSIONING.md)，历史见 [`CHANGELOG.md`](CHANGELOG.md)。
