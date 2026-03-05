import dotenv from "dotenv";
import { fileURLToPath } from "url";
import { dirname, resolve } from "path";
import express from "express";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
// Resolve .env relative to server directory (one level up from src)
const envPath = resolve(__dirname, "..", ".env");
const result = dotenv.config({ path: envPath });
if (result.error) {
  console.warn(`Warning: Could not load .env from ${envPath}:`, result.error.message);
} else {
  console.log(`Loaded env from: ${envPath}`);
}
import cors from "cors";
import { port } from "./config.js";
import chatRoutes from "./routes/chat.js";

const app = express();
app.use(cors());
app.use(express.json({ limit: "20mb" }));

app.use("/api/chat", chatRoutes);

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
