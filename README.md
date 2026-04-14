# 🧮 MathKids - 儿童数学启蒙教学平台

面向 6-10 岁儿童的互动数学启蒙 Web 平台，支持可视化教程动画、趣味练习游戏、多种解题方法展示，以及 AI 辅助课程内容生成。

## 项目架构

```
mathkids/
├── backend/                  # Python FastAPI 后端
│   ├── main.py               # API 路由 & 应用入口
│   ├── models.py             # SQLite 数据模型 & 种子数据
│   ├── validators.py         # 数学校验器
│   ├── services/
│   │   ├── course.py         # 课程/课时 CRUD
│   │   ├── exercise.py       # 题目管理 & 答案判定
│   │   ├── progress.py       # 学习进度追踪
│   │   └── ai.py             # 多 LLM 服务商接入
│   └── mathkids.db           # SQLite 数据库（自动创建）
├── student-app/              # React 学生端
│   └── src/App.jsx           # 课程地图 + 动画教程 + 练习游戏
├── admin-app/                # React 管理端
│   └── src/App.jsx           # 课程编辑 + 题库管理 + AI配置 + 学情分析
├── shared/types.ts           # 共享类型定义
├── start.sh                  # 一键启动脚本
└── .env.example              # 环境变量模板
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
python main.py
# 或: uvicorn main:app --reload --port 8000
```

后端启动后会自动创建 SQLite 数据库并插入种子数据（包含完整的 "20以内加减法" 课程、8个课时、配套习题）。

- API 地址: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 2. 启动学生端

```bash
cd student-app
npm install
npm run dev
# 访问 http://localhost:3000
```

### 3. 启动管理端

```bash
cd admin-app
npm install
npm run dev
# 访问 http://localhost:3001
```

### 一键启动

```bash
chmod +x start.sh
./start.sh
```

## 核心功能

### 📖 学生端

| 功能 | 描述 |
|------|------|
| **课程地图** | 蜿蜒路径展示学习进度，逐步解锁关卡 |
| **可视化教程** | 动画演示数学概念，支持逐步播放、自动播放 |
| **一题多解** | 凑十法、数轴法、数数法等多种方法切换展示 |
| **趣味练习** | 限时闯关游戏，填空题+选择题混合 |
| **即时反馈** | 答对鼓励、答错给提示引导，不直接揭晓答案 |
| **星级评定** | 1-3 星评级，跟踪学习成就 |

### 🔧 管理端

| 功能 | 描述 |
|------|------|
| **课程管理** | 创建/编辑/发布课程和课时 |
| **动画编辑器** | JSON 可视化编辑教学动画步骤 |
| **题库管理** | 查看、删除题目，按课时筛选 |
| **AI 配置** | 多服务商切换，在线生成教程和题目 |
| **学情分析** | 学习人数、正确率、星级等统计 |

### 🤖 AI 服务

支持以下 LLM 服务商（均通过管理端界面配置，无需改代码）：

| 服务商 | Base URL | 推荐模型 |
|--------|----------|----------|
| **OpenAI** | `https://api.openai.com/v1` | gpt-4o-mini |
| **Claude** | `https://api.anthropic.com` | claude-sonnet-4-20250514 |
| **Grok (xAI)** | `https://api.x.ai/v1` | grok-3-mini |
| **Kimi (月之暗面)** | `https://api.moonshot.cn/v1` | moonshot-v1-8k |
| **DeepSeek** | `https://api.deepseek.com/v1` | deepseek-chat |
| **自定义** | 任意 OpenAI 兼容 API | 自定义 |

AI 生成的内容会经过**数学校验层**验证（答案正确性、数值范围、步骤逻辑），确保不会出错。

## 动画系统设计

采用**数据驱动 + 预制组件**模式：

1. **前端动画组件库**（开发者预制）:
   - `MakeTenAnimation` — 凑十法动画（苹果拆分合并）
   - `NumberLineAnimation` — 数轴跳跃动画
   - `CountingAnimation` — 实物计数动画
   - `BreakTenAnimation` — 破十法动画
   - `StepByStepAnimation` — 分步计算动画

2. **JSON 数据**（管理员/AI 生成）:
   ```json
   {
     "type": "make_ten",
     "steps": [
       { "action": "show_objects", "left": 8, "right": 5, "shape": "apple" },
       { "action": "split", "target": "right", "parts": [2, 3] },
       { "action": "move_to_left", "count": 2 },
       { "action": "combine", "values": [10, 3], "result": 13 }
     ]
   }
   ```

3. **同一组件 + 不同数据 = 不同教程**，无需重复开发。

## API 接口一览

### 课程

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/courses` | 课程列表 |
| POST | `/api/courses` | 创建课程 |
| PUT | `/api/courses/:id` | 更新课程 |
| DELETE | `/api/courses/:id` | 删除课程 |

### 课时

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/courses/:id/lessons` | 课时列表 |
| GET | `/api/lessons/:id` | 课时详情（含习题） |
| POST | `/api/lessons` | 创建课时 |
| PUT | `/api/lessons/:id` | 更新课时 |

### 题目

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/lessons/:id/exercises` | 获取课时题目 |
| POST | `/api/exercises` | 创建题目 |
| POST | `/api/exercises/:id/check` | 判定答案 |

### AI

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/ai/config` | 获取 AI 配置 |
| PUT | `/api/ai/config` | 更新 AI 配置 |
| GET | `/api/ai/providers` | 获取可用服务商 |
| POST | `/api/ai/generate-lesson` | AI 生成教程内容 |
| POST | `/api/ai/generate-exercises` | AI 生成练习题 |

### 进度

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/progress/:userId` | 获取学习进度 |
| POST | `/api/progress/:userId` | 更新进度 |
| GET | `/api/analytics` | 学情统计 |

## 课程扩展指南

### 添加新课程

1. 在管理端 → 课程管理 → 新建课程
2. 添加课时，配置教学方法
3. 使用 AI 生成或手动编辑动画数据
4. 添加练习题（AI 批量生成或手动创建）
5. 发布课程

### 添加新动画类型

1. 在 `student-app/src/components/animations/` 创建新组件
2. 在 `AnimationPlayer` 路由器中注册
3. 在 AI Prompt 模板中添加新的 action 类型

## 预设课程内容

首期已预置完整的 **20以内加减法** 课程，包含 8 个课时：

1. 认识加法（数数法）
2. 10以内加法（数数法 + 数轴法）
3. 10以内减法（拿走法 + 数轴法）
4. 20以内不进位加法（分步法 + 数轴法）
5. **20以内进位加法（凑十法 + 数轴法 + 数数法）** ← 重点课时
6. 20以内退位减法（破十法 + 数轴法）
7. 加减混合练习
8. 三个数连算（草稿状态）

## 开发说明

- 后端使用 FastAPI + aiosqlite（异步SQLite），零外部依赖
- 前端使用 Vite + React 18 + Framer Motion
- 管理端和学生端共享同一后端 API
- SQLite 数据库文件 `mathkids.db` 位于 backend 目录下
- 首次启动自动建表 + 插入种子数据

## License

MIT
