# PersonaHub 后端API

基于FastAPI的AI人设管理后端服务

## 功能特性

- 人设管理：创建、读取、更新、删除人设
- 标签系统：为人设添加和管理标签
- 作者管理：管理人设创作者信息
- 搜索功能：根据名称、标签、作者搜索人设
- 数据库迁移：使用Alembic进行数据库版本管理

## 项目结构

```
nap/
├── app/                    # 主应用目录
│   ├── api/               # API路由
│   │   ├── endpoints/      # 端点实现
│   │   └── deps.py        # 依赖注入
│   ├── core/              # 核心配置
│   │   └── config.py      # 应用配置
│   ├── crud/              # 数据库操作
│   ├── db/                # 数据库相关
│   │   ├── models/        # 数据模型
│   │   └── session.py     # 数据库会话
│   ├── schemas/           # Pydantic模式
│   └── main.py            # 应用入口
├── alembic/               # 数据库迁移
├── tests/                 # 测试文件
├── requirements.txt       # 依赖列表
├── .env.example          # 环境变量示例
└── test_api.py           # API测试脚本
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制`.env.example`为`.env`并修改配置：

```bash
cp .env.example .env
```

编辑`.env`文件，设置数据库连接等参数。

### 3. 数据库迁移

```bash
# 应用数据库迁移
alembic upgrade head
```

### 4. 启动服务

```bash
# 开发模式启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问API文档

启动后访问：
- Swagger UI: https://api.dshell.top//docs
- ReDoc: https://api.dshell.top//redoc

## API端点

### 人设管理
- `GET /api/personas/` - 获取人设列表（分页）
- `POST /api/personas/` - 创建新人设
- `GET /api/personas/{id}` - 获取特定人设
- `PUT /api/personas/{id}` - 更新人设
- `DELETE /api/personas/{id}` - 删除人设
- `GET /api/personas/search/` - 搜索人设
- `GET /api/personas/by-author/{author}` - 按作者获取人设
- `GET /api/personas/by-tag/{tag}` - 按标签获取人设

### 标签管理
- `GET /api/tags/` - 获取所有标签
- `GET /api/tags/stats/` - 获取标签统计

### 作者管理
- `GET /api/authors/` - 获取所有作者
- `GET /api/authors/stats/` - 获取作者统计
- `GET /api/authors/top/` - 获取热门作者

## 测试

使用提供的测试脚本测试API：

```bash
# 确保服务已启动
python test_api.py
```

## 开发

### 添加新模型

1. 在`app/db/models/`创建模型文件
2. 在`app/schemas/`创建对应的Pydantic模式
3. 在`app/crud/`创建CRUD操作类
4. 在`app/api/endpoints/`创建API端点
5. 运行数据库迁移：
   ```bash
   alembic revision --autogenerate -m "描述"
   alembic upgrade head
   ```

### 数据库迁移

```bash
# 创建新的迁移
alembic revision --autogenerate -m "迁移描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接URL | mysql+pymysql://username:password@localhost:3306/persona_hub |
| SECRET_KEY | JWT密钥 | 随机生成 |
| DEBUG | 调试模式 | True |
| CORS_ORIGINS | CORS源 | ["http://localhost:3000"] |
| HOST | 服务主机 | 0.0.0.0 |
| PORT | 服务端口号 | 8000 |
| LOG_LEVEL | 日志级别 | INFO |

## MySQL配置

### 1. 安装MySQL
确保系统已安装MySQL服务器，并创建数据库：

```sql
CREATE DATABASE persona_hub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 创建用户并授权
```sql
CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON persona_hub.* TO 'username'@'localhost';
FLUSH PRIVILEGES;
```

### 3. 配置连接
在`.env`文件中设置正确的数据库连接：
```
DATABASE_URL=mysql+pymysql://your_username:your_password@localhost:3306/persona_hub
```

## 技术栈

- **FastAPI**: 现代、快速的Python Web框架
- **SQLAlchemy**: Python SQL工具包和ORM
- **Alembic**: 轻量级数据库迁移工具
- **Pydantic**: 数据验证和设置管理
- **SQLite**: 轻量级数据库（默认）
- **Uvicorn**: ASGI服务器

## 注意事项

- 生产环境请使用PostgreSQL或MySQL
- 确保SECRET_KEY安全且唯一
- 定期备份数据库
- 使用HTTPS部署生产环境