# Workbench

A web app to create and edit canvas images by conversing with an AI agent. Upload materials (e.g. images), chat to generate or modify a declarative canvas (RenderData), preview and edit JSON, and download the result.

## Setup

1. Install dependencies from the workbench root:

   ```bash
   cd workbench
   pnpm install
   cd server && pnpm install && cd ..
   cd client && pnpm install && cd ..
   ```

2. Create `server/.env` with your API configuration:

   ```bash
   # Edit server/.env and set:
   # OPENAI_API_KEY=your-key
   # OPENAI_BASE_URL=https://api.hunyuan.cloud.tencent.com/v1  # Optional, for custom endpoints
   # OPENAI_MODEL=hunyuan-lite  # Optional, defaults to gpt-4o
   # PICUI_TOKEN=your-token     # Optional, for image uploads. Get from https://picui.cn personal center
   ```

## Run

From the workbench directory:

```bash
pnpm dev
```

- **Server** runs at http://localhost:3001 (API: `/api/chat`).
- **Client** renders canvas in the browser (no server-side rendering).
- **Client** runs at http://localhost:5173 with Vite proxy so `/api` requests go to the server.

## Usage

1. Use the **left panel** to chat: type messages and optionally attach images (materials). Images are sent as base64 in the message; the server uploads them to [PICUI](https://picui.cn) and passes URLs to the agent. Set `PICUI_TOKEN` in `server/.env` to enable uploads. The agent returns updated canvas JSON (RenderData) when it produces or changes a design.
2. Use the **right panel** tabs:
   - **Preview**: view the current rendered image and click **Download** to save it.
   - **JSON**: edit the RenderData and click **Apply** to re-render and update the preview.
3. Continue the conversation to refine the result; the agent can update the canvas based on your feedback.
