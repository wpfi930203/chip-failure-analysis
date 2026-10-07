# 模块 21 · FA 案头手册精要（ASM Desk Reference 第7版）

> **源**：*Microelectronics Failure Analysis Desk Reference*, 7th Edition（2019）
> 编：Tejinder Gandhi；出版：ASM International；学会：EDOFAS（Electronic Device Failure Analysis Society）
> **源等级**：**L1 一手权威**——国际 FA 领域标准案头手册，各章由该技术领域一线专家撰写。
> 本模块只收**可迁移的方法与判据**（技术选型、空间/灵敏度量级、流程纪律），不复制图集。

## R · 原文锚点

> As tester contact issues and intermittency are very common, the failing electrical signature must be confirmed in the lab, even for the "simple" opens and shorts associated with package failures. IV curves should be collected as they provide much more insight into what is wrong with the device.
>
> ——Gandhi & Silva, "Package Failure Analysis: Flow and Technique", p.10

> With 30–40 ps rise time of the TDR instrument and with dielectric constant 4 of FR4 material, spatial resolution of TDR is about 1 mm. …While this distance is acceptable for cables and PCB, it is too large to be useful for most package applications. In response, EOTPR was developed. …Spatial resolutions of less than 10 µm have been obtained.
>
> ——同章，Fault Isolation 段

> To improve the signal to noise ratio, a lock-in signal is used to simultaneously toggle the failure and the thermograph's heat signature collecting hardware. This technique allows the detection of temperature modulation of few µK.
>
> ——同章，IR Lock-In Thermography 段

---

## I · 骨架：手册的九段知识结构（本技能各模块的映射）

| Section | 主题 | 对应本技能模块 |
|---|---|---|
| **1** | Failure Analysis Process and Management（晶圆级流程、封装 FA 流程、CSP 挑战、板级无损、实验室管理） | 1 procedure、3 localization、18 report-template |
| **2** | Incoming Inspection Tools（光学显微、X-ray、**声学显微 SAM**） | 5 characterization |
| **3** | Fault Isolation（Scan 诊断驱动 FA、**磁场成像 MFI**、**TDR/EOTPR/TDT**、正/背面制样、**硅基光子发射**、激光 FA 物理、**热探测**、**3D Lock-in 热像**、**LADA/SDL**、**激光电压探针 LVP**、CAD 导航） | **3 localization（本模块主补）** |
| **4** | Device and Circuit Characterization | 2 electrical |
| **5** | FIB Technique and Circuit Edit | 4 sample-prep |
| **6** | Physical Analysis | 4 sample-prep、5 characterization |
| **7** | Memory Failure Analysis | 2 electrical（存储器专项） |
| **8** | Special Applications of FA | 视器件类型分散 |
| **9** | Fundamental Topics（电子学基础、**IC 测试方法概述**、**EOS 与 ESD 区分**、**可靠性与质量基础**、术语定义） | 7 mechanism、12 reliability-stats |

**使用原则**：本模块不是手册的替代品，而是**索引 + 关键判据提取**。需要图集、设备参数、完整案例时，回到手册原书（Desk Reference 7th Ed., ASM 2019）。

---

## A1 · 封装失效分析实战流程（Section 1 章例，可直接照搬到方案里）

手册给的是一个**可复制的五步链路**，每一步都有"为什么必须在这步做"的理由：

| 步 | 动作 | 手段 | 这一步回答什么 / 纪律 |
|---|---|---|---|
| ① | **非破坏成像** | **SAM（扫描声学显微）** | 找内部分层、空洞、裂纹。手册强调：内部裂纹**常被误判为机械制样引入的假象**——所以**裂纹必须在制样前用 SAM 先记录**，否则无法区分"真缺陷"与"制样损伤" |
| ② | **背面/衬底红外检查** | **IR 显微**（低掺杂硅对红外透明） | 对暴露衬底的封装**必做**：既能查 EOS 引起的开/短路，也是**成像内部裂纹**（die crack）的有效手段 |
| ③ | **电学验证（不可跳）** | 曲线追踪仪取 I-V | **测试座接触不良与间歇性极常见**，即便失效单只是"简单开路/短路"，也必须在实验台复核失效特征；**I-V 曲线必取**——它比"开/短路"这个标签信息量大得多（阻性短路 vs 纯短路 vs 漏电） |
| ④ | **故障隔离** | 按失效签名选型（见 A2 表） | **纪律**：除非已经拿到了"能解释该电学特征的缺陷图像"，否则**都应先做故障隔离**再解剖 |
| ⑤ | **破坏性分析** | SEM + 成分分析 + 逐层去加工 | 缺陷已被成像或位置已高置信确定后，才逐步检视与去层。光学检视优先（简单、可看亚表层） |

> **这张表与总纲三条铁律同源**：①②③ 都是非破坏，④ 是定位收窄，⑤ 才破坏。手册的价值在于它把每一步的**反面理由**也写清楚了（不做会误判什么）。

## A2 · 故障隔离手段选型与定量分辨率（本模块核心增量）

按**失效签名**选手段，而不是按"手上有什么设备"选：

| 失效签名 | 首选手段 | 原理要点 | **定量分辨能力** | 适用边界 |
|---|---|---|---|---|
| **短路（含阻性短路）** | **IR Lock-in Thermography（LIT）** | 在短路两脚间加偏置激发，缺陷点发热 → 热传导至封装表面 → 红外相机探测；用 lock-in 信号同步"激励失效"与"采集热像"以提信噪比 | **可探测几 µK 级的温度调制** | 需能施加偏置激发；热源定位后常与 X-ray 图像叠加确认在封装内部的确切层位 |
| **开路** | **TDR（时域反射）** | 带宽 18–20 GHz 以上的采样示波器 + 内部阶跃发生器，向失效脚注入快上升沿，比较反射与入射波形 | 30–40 ps 上升沿 + FR4（εr=4）条件下**空间分辨率约 1 mm** | **仅适用于线缆与 PCB 级**；对多数封装应用太粗 |
| **开路（封装/基板级）** | **EOTPR（电光太赫兹脉冲反射）** | 电脉冲注入失效器件，反射波形由**高速光电导开关**时域采集（TDR 的革新版） | **空间分辨率 < 10 µm** | 需要专用设备；是封装级开路的主力手段 |
| **开路（互补）** | **TDT（时域透射）** | 透射模式，与 TDR 反射模式互补 | 依设备 | 反射路径不清晰时的备选 |
| **软缺陷 / 临界失效（marginal）** | **LADA（激光辅助器件改变）/ SDL（软缺陷定位）** | 激光扫描与测试同步，监测选定测试引脚信号；激光局部改变器件特性从而使临界失效暴露 | 依光斑与扫描步长 | 需在探针卡上**取出测试引脚信号**（从 plated through-hole / pogo pin 路径引出，可经探针卡 PCB 走线到正面）——这是实操中的关键工程细节 |
| **硅基漏电/结击穿/寄生晶体管** | **Photon Emission（光子发射显微）** | 发射机制分三类：**带间复合**、**带内弛豫/单极机制（场助发射 F-PE）**、**基本 pn 结发射**；FET 工作模式下另有特征谱 | 依物镜与波长 | **F-PE 与结发射的区分**是判读关键（不同机制对应不同失效类型） |
| **电流路径/金属互连缺陷** | **MFI（磁场成像）** | 测电流产生的磁场反演电流路径 | 依探头 | 对埋层、无法通过光学/热学到达的路径有效 |
| 需 3D 定位时 | **3D Hot-Spot Localization by Lock-In Thermography** | Lock-in 热像的深度分辨/层析 | 依锁相频率 | 多层堆叠、需确定热源深度时 |
| 需波形级内部节点观测 | **LVP（激光电压探针）** | 激光探测内部节点电压波形 | 依设备 | 与 CAD 导航配合使用 |

**选型纪律（三条）**：
1. **先按签名分组**（开路 / 短路 / 软缺陷 / 漏电 / 参数漂移），再在组内选手段——不要"先拿设备再找问题"。
2. **分辨率是选型的硬约束**：TDR 1 mm 与 EOTPR 10 µm 是**两个量级**的差别，选错手段会得到"定位到了但没用"的结果。
3. **叠加确认**：手册示例中把 **X-ray 图像与 IR-LIT 热像叠加**来确认热源在封装内部的具体位置——单一手段给的是投影，叠加才给三维位置。

---

## E · 执行步骤（接到"要定位/要找点"类请求时）

1. **先确认失效签名**：是开路、短路（纯/阻性）、软缺陷、漏电还是参数漂移？——这决定 A2 表的哪一格。
2. **按 A1 补非破坏三件套**：SAM（分层/裂纹，制样前必留证据）→ IR（背面裂纹与 EOS 征象）→ **I-V 曲线复核**（必做，不做不得进入定位）。
3. **按 A2 选隔离手段**，并核对其分辨率/灵敏度是否与目标尺度匹配（封装级开路直接上 EOTPR，不要拿 TDR 凑）。
4. **多手段叠加确认位置**（X-ray + LIT 叠加是最常用组合），得到高置信位置后才进入破坏性制样（模块 4）。
5. **制样后再回到电学**：用模块 2 验证"看到的缺陷"能否解释"测到的电学特征"——不能解释则回到第 3 步。

---

## B · 边界

1. **L1 一手源，但为案头手册而非标准**：本模块给的是**行业权威实践**，不是 JEDEC/IEC/AEC 的合规判据；认证与判定门限仍回标准原文（模块 13/17）。
2. **图集不可见**：Desk Reference 的核心价值之一是形貌图鉴，本次蒸馏取到的是**文本层**，图、谱、波形均未纳入。**凡涉及"看图判读"的结论，必须回原书图谱核对**，不得据本文描述定论。
3. **Section 9 的《Differentiating between EOS and ESD Failures for ICs》（Leo G. Henry, p.652）本轮文本层未命中**（PDF 该章文本提取缺失或为图片页），**本模块不提供其判据内容**，属明确待补项——需要用该判据时，请回原书 p.652–665，不得由本技能的 ESD 专节（模块 7，源自邓永孝 1989）替代。
4. **设备参数会迭代**：TDR 18–20 GHz、EOTPR <10 µm、LIT 几 µK 等为 2019 年版手册给出量级，具体设备以现行手册/厂商规格为准。
5. **本模块仅蒸馏了手册的部分章节**（Section 1 的封装 FA 章、Section 3 的定位技术群、Section 9 目录结构）。Section 4（器件与电路表征）、5（FIB）、6（物理分析）、7（存储器 FA）、8（特殊应用）**尚未取正文**，相关细节回原书。
