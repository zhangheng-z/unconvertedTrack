# 未转化用户价值项目 MVP 后端

这是基于 `未转化用户价值项目执行说明书.pdf` 落地的 FastAPI 后端 MVP，覆盖家长端首次分层、内容池、领取/下载/分享、我的资料，以及后台看板、内容管理、用户偏好统计和简单 AI 选题推荐。

## 本地运行

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[test]"
uvicorn app.main:app --reload
```

默认使用 MySQL，连接信息在 `.env` 中拆分配置：

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=unconvertedTrack
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_CHARSET=utf8mb4
TEST_MYSQL_DATABASE=unconvertedTrack_test
```

本地 MySQL 初始化示例：

```sql
CREATE DATABASE unconvertedTrack CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE unconvertedTrack_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
FLUSH PRIVILEGES;
```

也可以直接启动仓库内置 MySQL：

```bash
docker compose up -d mysql
copy .env.example .env
python -m app.seed
uvicorn app.main:app --reload
```

测试默认读取同一组 `MYSQL_USER` / `MYSQL_PASSWORD`，数据库名使用 `TEST_MYSQL_DATABASE`，例如：

```bash
set TEST_MYSQL_DATABASE=unconvertedTrack_test
pytest
```

## 常用命令

```bash
pytest
python -m app.seed
```

## 小程序前端

家长端小程序源码在 `miniprogram/`。用微信开发者工具导入该目录即可预览。

本地联调：

```bash
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

小程序当前默认请求 `http://127.0.0.1:8000`，配置在 `miniprogram/app.js` 的 `apiBaseUrl`。开发阶段 `project.config.json` 已关闭域名校验；正式发布前需要把后端部署到 HTTPS，并在微信公众平台配置 request 合法域名。

小程序登录：

- 已接入 `wx.login` 和后端 `/api/v1/auth/wechat-login`
- `.env` 配置 `WECHAT_APP_ID` / `WECHAT_APP_SECRET` 后会调用微信 `code2session`
- 未配置时走本地开发 open_id，方便本地预览
- 登录接口返回 `access_token`，小程序会保存并自动通过 `Authorization: Bearer ...` 携带
- 正式环境必须把 `.env` 里的 `JWT_SECRET_KEY` 换成随机长字符串

资料文件：

- 后台上传接口：`POST /admin/files`
- 本地文件目录：`storage/files`
- 静态访问地址：`http://127.0.0.1:8000/files/...`

后台 H5：

- 本地地址：`http://127.0.0.1:8000/admin-ui/`
- 支持查看看板、查看内容列表、新增资料、上传文件、创建后自动发布

已实现页面：

- 首页内容池：搜索、学科/类型/排序筛选、资料卡片
- 资料：已领取资料列表
- 测评：语文能力测评报告、分数进度条、行动入口
- 训练营：7 天基础提升训练入口
- 我的：家长信息、孩子档案、资料/测评/训练营/邀请奖励
- 首次分层：年龄、年级、关注问题，最多选择 3 个问题
- 资料详情：大封面、标签、领取/分享数据、领取方式、下一步测评、相关推荐

## 主要接口

- `POST /api/v1/onboarding/profile`
- `GET /api/v1/contents`
- `GET /api/v1/contents/{id}`
- `POST /api/v1/contents/{id}/claim`
- `POST /api/v1/contents/{id}/download`
- `POST /api/v1/contents/{id}/share`
- `GET /api/v1/me/assets`
- `GET /admin/dashboard/overview`
- `GET /admin/preferences`
- `POST /admin/contents`
- `PATCH /admin/contents/{id}`
- `PATCH /admin/contents/{id}/publish`
- `GET /admin/ai/topic-suggestions`
