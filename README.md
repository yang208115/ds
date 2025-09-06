# DreamShell API

人设市场管理系统后端API

## 架构

这是一个采用分层架构的 FastAPI 后端应用程序。

- **`app/main.py`**: 应用程序的入口点，用于初始化和配置 FastAPI 应用。
- **`app/api/`**: 包含 API 端点。端点在 `app/api/endpoints/` 中定义，并被主应用包含。
- **`app/crud/`**: 处理数据库操作（创建、读取、更新、删除）。
- **`app/schemas/`**: 定义用于数据验证和序列化的 Pydantic 模型。
- **`app/db/`**: 包含数据库会话管理和 SQLAlchemy 的基础模型。
- **`app/core/`**: 核心应用设置和配置。
- **`tests/`**: 包含使用 `pytest` 编写的应用程序测试。
- **`alembic/`**: 包含由 Alembic 管理的数据库迁移脚本。

## API Endpoints

### Authentication (`/api/v1/auth`)

- `POST /register`: 注册新用户
- `POST /login`: 用户登录
- `GET /github/login`: 重定向到 GitHub OAuth 登录
- `GET /github/callback`: GitHub OAuth 回调
- `GET /me`: 获取当前用户信息
- `PUT /profile`: 更新当前用户信息

### Personas (`/api/personas`)

- `POST /`: 创建新的人设
- `GET /`: 获取人设列表 (分页)
- `GET /{person-id}`: 获取单个人设详情
- `PUT /{person-id}`: 更新人设
- `DELETE /{person-id}`: 删除人设
- `POST /search`: 搜索人设
- `GET /author/{author_uuid}`: 根据作者UUID获取人设列表
- `POST /{person-id}/view`: 增加人设浏览量
- `GET /tags/{tags}`: 根据标签获取人设列表

### Tags (`/api/tags`)

- `GET /`: 获取所有标签
- `GET /stats`: 获取标签统计信息

### Authors (`/api/authors`)

- `GET /`: 获取所有作者
- `GET /stats`: 获取作者统计信息
- `GET /avatar/{user_uuid}`: 获取用户头像
- `GET /top`: 获取创作数量最多的作者列表
- `GET /user/{user_uuid}`: 根据UUID获取用户信息

## 安装

1.  克隆仓库:

    ```bash
    git clone https://github.com/your-username/your-repository.git
    cd your-repository
    ```

2.  创建并激活虚拟环境:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  安装依赖:

    ```bash
    pip install -r requirements.txt
    ```

4.  创建 `.env` 文件并设置环境变量。可以参考 `.env.example` (如果提供).

## 使用

运行开发服务器:

```bash
uvicorn app.main:app --reload
```

## API 文档

服务启动后, API 文档可在以下地址访问:

-   **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
-   **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 运行测试

```bash
pytest
```

## Linting

-   格式化代码:

    ```bash
    black .
    isort .
    ```

-   类型检查:

    ```bash
    mypy .
    ```

## 数据库迁移

-   创建新的迁移:

    ```bash
    alembic revision --autogenerate -m "Your migration message"
    ```

-   应用迁移:

    ```bash
    alembic upgrade head
    ```

## 许可证

[MIT](LICENSE)
