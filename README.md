# 幕墙单元件快速生成验证系统

基于《基于参数化设计的幕墙单元件快速生成验证系统》专利核心流程实现的前端控制台，使用 Bootstrap 5 构建交互界面，整合参数输入处理、单元件生成、结构验证、误差修正与数据关联等五大模块。系统通过 `uv` 管理依赖并生成静态数据集，可直接部署到任意静态网站托管平台。

## 项目结构

```
curtain_wall/
├── data/
│   └── system_dataset.json          # 由脚本生成的基线数据集（原始备份）
├── public/
│   ├── index.html                   # 登录入口
│   ├── app.html                     # 主控制台
│   ├── data/
│   │   └── system_dataset.json      # 静态站点直接读取的数据集
│   └── assets/
│       ├── css/custom.css           # 视觉风格定义
│       └── js/
│           ├── app.js               # 核心逻辑与图表渲染
│           └── login.js             # 登录校验与会话控制
├── scripts/
│   └── generate_initial_data.py     # 使用专利算法生成示例数据
├── pyproject.toml                   # uv 管理的依赖定义
├── uv.lock                          # 依赖锁定文件（首次 `uv add` 后自动生成）
└── README.md
```

## 环境准备

- Python 3.12（`uv` 会自动安装解释器）
- [uv](https://docs.astral.sh/uv/) 0.7+ 已预装（若本地未安装，请参考官方文档）
- 浏览器访问即可，无需后端运行时

## 快速开始

```bash
cd /Users/fuwei/curtain_wall

# 1. 同步依赖（生成 .venv）
UV_CACHE_DIR=.uv-cache uv sync

# 2. 生成基线数据集（同步至 data/ 与 public/data/）
UV_CACHE_DIR=.uv-cache uv run python scripts/generate_initial_data.py

# 3. 本地预览（静态服务），默认监听 http://localhost:8000
UV_CACHE_DIR=.uv-cache uv run python -m http.server --directory public 8000
```

**提示**：
`UV_CACHE_DIR` 指向项目内缓存目录，方便在受限环境下运行且易于清理。数据脚本会同步写入 `data/` 与 `public/data/`，确保静态页面开箱即用。

# Testing
同步依赖并生成数据：
UV_CACHE_DIR=.uv-cache uv sync
UV_CACHE_DIR=.uv-cache uv run python scripts/generate_initial_data.py
本地静态预览：
UV_CACHE_DIR=.uv-cache uv run python -m http.server --directory public 8000
然后访问 http://localhost:8000/index.html 使用默认账号 facade.engineer@atlaslabs.com / StrataMesh!905 登录。

# Notes
部署到静态平台前，请确认 `public/data/system_dataset.json` 已更新，确保前端直接读取。
若需替换账号体系，只需更新 AUTH_RECORD 与配套文档，前端守卫逻辑已封装完毕。

## 部署到静态托管平台

1. 确保执行完“快速开始”中的步骤 1-2，保证 `public/data/system_dataset.json` 与前端资产已更新。
2. 将整个 `public/` 目录上传至目标平台（如 GitHub Pages、Vercel、Netlify 等）。
3. 如需发布额外文档，可同时上传 `docs/` 目录。
4. 发布后即可通过平台分配的公网地址访问。

### GitHub Pages 快速方案

在 Pages 设置中选择 `public` 目录作为发布源即可。


## 系统操作指南

详见 `docs/system-guide.md`。以下为摘要：

1. **登录访问**：
   - 访问部署地址后进入登录页，系统默认启用工程账号 `facade.engineer@atlaslabs.com`，访问密钥 `StrataMesh!905`（在生产环境请替换为实际凭证）。
   - 登录成功后，凭证摘要写入浏览器 `localStorage`，可随时点击“安全退出”清除会话。

2. **参数输入处理模块**：
   - 在“基础参数与约束配置”面板填入单元尺寸、曲率、倾角、风速、热梯度等信息。
   - 提交后系统按专利描述执行完整性校核、规则匹配与参数权重分析，结果以雷达图与进度条反馈。

3. **单元件生成模块**：
   - 基于参数映射生成几何构成要素，展示投影面积、包络体积、框架重量等指标。
   - 通过环形图呈现生成路径分布比例，动态系数标签反映曲率影响、倾角响应、竖梃耦合等特征值。

4. **结构验证模块**：
   - 计算风压、恒载及各节点应力分布，折线图对比原始生成与优化后的应力曲线。
   - 稳定性指数以专利方法衡量验证指标均衡性，表格列出关键节点数据。

5. **误差修正模块**：
   - 根据实时偏差率与形态偏移量生成迭代收敛曲线，柱线组合图直观呈现尺寸与形态收敛趋势。
   - 表格记录每轮迭代的偏差值和路径权重，显示残余偏差与装配适配性评分。

6. **数据关联模块**：
   - 分阶段展示设计参数与施工数据的关联浓度，提供设计-现场指标对照表及同步滞后天数。
   - 支持多方案切换，自动刷新关联曲线和对照表。

7. **操作日志**：
   - 每次参数提交均记录时间戳、当前方案、结构稳定性与适配性指标，便于追溯。

## 数据再生成与扩展

- 修改 `scripts/generate_initial_data.py` 可融入项目自有数据源或算法。
- 运行脚本生成新数据后，刷新浏览器即可加载最新指标。
- 若需接入真实后端，可将前端 `fetch` 指向 API，并保留本系统的前端交互与展示逻辑。

## 常见问题

- **登录后跳回首页**：浏览器可能阻止了 `localStorage`，请检查隐私设置或清空站点数据。
- **图表未显示**：确保网络允许访问 `cdn.jsdelivr.net`，或将 Bootstrap / Chart.js 打包成本地文件发布。
- **数据未更新**：确认重新运行数据生成脚本，或在浏览器控制台执行 `localStorage.removeItem('facade-session')` 后刷新以强制重新加载基础数据。

如需二次开发或接入企业 SSO，可在现有登录模块基础上替换凭证校验逻辑，并保留 `SESSION_KEY` 以维持控制台守卫。



