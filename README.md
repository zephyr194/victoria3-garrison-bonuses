# Victoria 3 · 驻军收益与成本

[GitHub](https://github.com/zephyr194/victoria3-garrison-bonuses)

固定的 **卫戍营区** 为本州提供治安与长期治理效果，消耗基础设施、人员、军需和建设投入。

**状态：v0.2 实验实现，尚未在游戏中运行验证。不是已经确认兼容的正式版本。**

## 首版实现
- 新增可扩建的政府建筑“卫戍营区”；每级设 950 名士兵、50 名军官岗位，不生成可调往前线的营。
- 常备卫戍 / 封存营区两种生产方式；空建筑、封存或军需短缺不提供治理收益。
- 按本州已就业卫戍人员 / 人口需求计算覆盖，递减收益，动乱惩罚减免上限 40%。
- 每级额外减少 2 点可用基础设施；即使封存也保留设施占用，军需随实际人员消耗。
- 月度结算：连续运转 3 个月后缓慢减少激进派；6 个月后，在已整合、动乱较低、生活条件达标的州缓慢增加忠诚派。
- 政治态度变化有边界条件；撤掉营区会撤销秩序修正，不会把已经改变的态度瞬间反转。

这是**固定卫戍模式**。引擎文档提供军队当前 HQ，并不能直接证明军队驻在某州。此版本不把一支野战军重复计入多个州，也不以兵营等级冒充实际驻军。

## 开发与检查
Python 3.11+，不需要第三方库。

```bash
python3 tools/generate.py
python3 tools/validate.py
python3 -m unittest discover -s tests -v
python3 scripts/package.py --target 1.13 --experimental
```

生成的 ZIP 是用于本地游戏验证的实验包。只在测试 playset 和另存的测试存档上核验；验证前不要宣称可正常游玩。完整步骤见 [安装和游戏内验证](docs/INSTALL_TEST.md)。

## 文档
- [设计与取舍](docs/DESIGN.zh-CN.md)
- [驻军可行性研究](docs/RESEARCH.zh-CN.md)
- [技术实现与限制](docs/IMPLEMENTATION.md)
- [来源及接口证据](docs/SOURCES.md)
- [验收矩阵](docs/VALIDATION.md)
- [开发路线](docs/ROADMAP.md)

1.13.11 与 1.14.5-openbeta 的关键脚本接口已对照；两版游戏运行、正式版 1.14、AI 建造策略和多人同步均未验证。没有分发游戏原始资产；只引用原版图标路径。项目尚未选择开源许可证。
