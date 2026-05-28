# Workspace File Browser

一个独立的 FastAPI + Vue 3 WebUI，用于浏览默认目录 `/workspace`，并维护右侧已选择路径列表。

## 开发模式启动

后端：

```bash
cd /workspace/projects/training/web
python -m pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

前端：

```bash
cd /workspace/projects/training/web/frontend
npm install
npm run dev
```

然后访问 Vite 输出的地址，通常是 `http://localhost:5173`。

## 生产构建

```bash
cd /workspace/projects/training/web/frontend
npm install
npm run build
```

构建完成后，FastAPI 会自动托管 `frontend/dist`：

```bash
cd /workspace/projects/training/web
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000` 即可打开页面。
