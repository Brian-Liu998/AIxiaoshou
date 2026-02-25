# AI小说创作助手

一个基于 DeepSeek API 的 AI 小说生成网页应用。

## 项目结构

```
ai-novel-app/
├── index.html      # 前端页面
├── app.py          # Flask 后端 API
├── requirements.txt
├── render.yaml     # Render 配置
├── vercel.json     # Vercel 配置
└── README.md
```

## 本地开发

### 1. 安装依赖

```bash
cd ai-novel-app
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
DEEPSEEK_API_KEY=your-deepseek-api-key
```

获取 DeepSeek API Key：
1. 访问 https://platform.deepseek.com/
2. 注册/登录账号
3. 在控制台获取 API Key

### 3. 运行后端

```bash
python app.py
```

后端将在 http://localhost:5000 运行。

### 4. 修改前端 API 地址

在 `index.html` 中找到配置区域：

```javascript
const API_URL = 'http://localhost:5000/api/generate';
```

### 5. 打开页面

直接在浏览器中打开 `index.html`，或使用 Live Server。

---

## 部署教程

### 第一步：部署后端到 Render

1. **注册 Render 账号**
   - 访问 https://render.com/
   - 使用 GitHub 登录

2. **创建 Web Service**
   - 点击 "New +" → "Web Service"
   - 连接你的 GitHub 仓库（需要将项目推送到 GitHub）
   - 或者直接上传 `app.py` 和 `requirements.txt`

3. **配置**
   - Name: `ai-novel-api`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

4. **设置环境变量**
   - 添加 `DEEPSEEK_API_KEY`，填入你的 API Key

5. **部署**
   - 点击 "Create Web Service"
   - 等待部署完成，获取后端 URL（如：`https://ai-novel-api.onrender.com`）

### 第二步：部署前端到 Vercel

1. **注册 Vercel 账号**
   - 访问 https://vercel.com/
   - 使用 GitHub 登录

2. **修改前端配置**
   - 打开 `index.html`
   - 找到 `const API_URL = 'https://your-backend-url.onrender.com/api/generate';`
   - 将 `your-backend-url` 替换为你的 Render 后端 URL

3. **部署**
   - 在 Vercel 导入你的 GitHub 仓库
   - 或者使用 Vercel CLI：
     ```bash
     vercel
     ```
   - 按照提示完成部署

### 第三步：访问你的应用

部署完成后，你将获得：
- 前端地址：如 `https://ai-novel-app.vercel.app`
- 后端地址：如 `https://ai-novel-api.onrender.com`

打开前端地址即可使用！

---

## 功能说明

- **故事大纲输入**：输入你想要的故事情节、人物、背景等
- **小说类型**：科幻、修仙、末世、都市、悬疑、奇幻、武侠、浪漫、历史
- **字数限制**：1千、3千、5千、1万、2字
- **AI创作**：基于 DeepSeek 大模型生成小说内容

---

## 费用说明

- **DeepSeek API**：按token计费，具体价格见 https://platform.deepseek.com/pricing
- **Render**：免费版每月 750 小时
- **Vercel**：免费版每月 100GB 流量

---

## 常见问题

### 1. API 调用失败
- 检查 DeepSeek API Key 是否正确
- 检查后端是否正常运行

### 2. 响应太慢
- DeepSeek API 需要几秒钟生成内容
- 免费服务器首次调用需要冷启动

### 3. 内容不符合预期
- 可以在故事大纲中更详细地描述
- 调整 `app.py` 中的 `temperature` 参数（0-2，越高越有创意）
