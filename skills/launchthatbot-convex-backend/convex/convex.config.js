import { defineApp } from "convex/server";
import openclawBackendComponent from "./components/openclawBackend/convex.config";

const app = defineApp();

app.use(openclawBackendComponent, { name: "LTBopenclawBackend" });

export default app;
