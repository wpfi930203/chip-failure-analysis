# 版本管理规范 · Versioning

本仓库采用**语义化版本 + 单一事实源 + 强制一致性校验**的方式管理版本。

当前版本：**5.0.2**

---

## 一、版本号语义

`MAJOR.MINOR.PATCH`

| 位 | 何时 +1 | 例子 |
|---|---|---|
| **MAJOR** | 知识体系重构、模块编号重排、破坏性变更 | v2.0.0 → v3.0.0（13 个分体技能合并为单技能，模块从"技能"改为"references 文件"，编号体系完全重排） |
| **MINOR** | 新增知识模块 / 新增主题，向后兼容 | v4.1.0 → v4.2.0（新增模块 22 `case-atlas.md`） |
| **PATCH** | 内容修订、打包方式、文档、图标、元数据，不动知识结构 | v5.0.1 → v5.0.2（修复图标与中文名不显示） |

预发布版本若需要，用 `-rc.N` 后缀（如 `5.1.0-rc.1`），**不**单独打正式标签。

---

## 二、单一事实源：版本号出现在 4 个地方，必须一致

| 位置 | 字段 | 作用 |
|---|---|---|
| `SKILL.md` | frontmatter `version:` | 技能包自述版本；agent 读取 |
| `test-prompts.json` | 顶层 `version` + 每个模块条目 `version` | 测试集与源模块的版本对齐 |
| `tools/sync_meta.py` | 常量 `VERSION` | 决定 `_user_meta.json.version`（界面显示的版本） |
| `_user_meta.json` | `version` | **生成物，不入库**；由 `sync_meta.py` 写出 |

手工改多处极易漏改（本项目就发生过 `SKILL.md` 改了、`test-prompts.json` 没改的情况），
因此**一律用脚本批量改**：

```bash
python tools/bump_version.py 5.0.3    # 见下方"发版流程"
```

---

## 三、发版流程

```bash
# 0) 前置：工作区干净
git status

# 1) 批量同步版本号（SKILL.md / test-prompts.json / sync_meta.py 三处一次改完）
python tools/bump_version.py 5.0.3
python tools/bump_version.py            # 不带参数 = 只查询当前版本分布

# 2) 更新 CHANGELOG.md：在最新版本上方插入新章节（Keep a Changelog 格式）
#    Added / Changed / Fixed / Removed / Known limitations

# 3) 同步安装到用户级并**逐文件 SHA256 校验**（顺带重刷 _user_meta.json）
python tools/install.py

# 4) 复核展示名与图标链路
python tools/verify_meta.py            # 期望 2/2 PASS

# 5) 提交 + 打标签
git add -A
git commit -m "chore(release): v5.0.3"
git tag -a v5.0.3 -m "v5.0.3"
git push origin main --tags
```

### 发版前检查清单

- [ ] 4 处版本号一致（`grep -n '5\.0\.[0-9]' SKILL.md test-prompts.json tools/sync_meta.py`）
- [ ] `CHANGELOG.md` 已加入对应版本章节，且注明**来源等级**与**新增/未闭合缺口**
- [ ] `python tools/install.py` 输出 `MATCH n / n` 且 `BAD = 0`
- [ ] `python tools/verify_meta.py` 输出 `PASS`
- [ ] 新增模块已在 `SKILL.md` 的**模块地图**与**主题视图**两处登记
- [ ] 新增模块已在 `test-prompts.json` 补正例 / 诱饵 / 边界三组用例
- [ ] 涉及新来源时，已在 `references/kb-index.md` 与 `README.md` 来源表登记**源等级**
- [ ] 未闭合缺口未被悄悄"补白"（无来源的内容宁缺勿造）

---

## 四、分支与提交约定

| 分支 | 用途 |
|---|---|
| `main` | 始终可发布；每个 release tag 都指向 `main` 上的提交 |
| `feat/<主题>` | 新增知识模块（如 `feat/module-26-latchup`） |
| `fix/<问题>` | 内容勘误、工具修复 |

提交信息用 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/) 前缀：

```
feat(module-26): 新增闩锁（Latch-up）专节
fix(module-17): 修正 A108F 的 HTGB 偏置条件
chore(release): v5.0.3
docs(readme): 补充 clone 目录名说明
tools(install): 修正三参数 Join-Path 静默失败
```

---

## 五、标签与发布

- 标签一律**附注标签**（`git tag -a`），命名 `v<版本号>`，如 `v5.0.2`。
- 每个标签对应 `CHANGELOG.md` 中同名章节，内容保持一一对应。
- **本仓库 git 历史自 v5.0.2 起**。v1.0.0–v5.0.1 的演进过程记录在
  `CHANGELOG.md` 中，但**没有对应的 git 标签**——早期版本是在本仓库创建前、
  以"直接改写工作区文件"的方式迭代的，其文件快照已不可追溯。
  为免误导，这里**不**为历史版本补打指向当前提交的标签。

| 版本 | 记录位置 |
|---|---|
| v1.0.0 → v5.0.1 | 仅 `CHANGELOG.md`（无 git 标签） |
| **v5.0.2** | `CHANGELOG.md` + git 附注标签 `v5.0.2`（本仓库首个标签） |
| v5.0.3 及之后 | `CHANGELOG.md` + git 附注标签，按上方流程发版 |

---

## 六、不入库清单

以下内容**禁止提交**，原因见括号：

| 路径 | 原因 |
|---|---|
| `_user_meta.json` | 含**本机绝对路径**（`iconLocalPath`），跨机器无意义 |
| `_skillhub_meta.json` / `_marketplace_meta.json` / `_knot_meta.json` / `_builtin_market_meta.json` | 市场/企业安装态，属本地状态 |
| `__pycache__/`、`*.pyc` | 构建产物 |
| `_icon_preview.png` | `preview_icon.py` 的复核产物，可随时重生成 |

已在 `.gitignore` 中固化。
