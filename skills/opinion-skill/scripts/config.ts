// ========================
// 共享配置模块 (纯 API, 无 SDK 依赖)
// ========================
//
// 数据查询脚本只需 import 此文件
// 交易脚本额外 import ./sdk-config

const OPINION_API_HOST = "http://newopinion.predictscanapi.xyz:10001";

// 轻量 fetch wrapper, 不依赖 axios
async function apiFetch<T = any>(path: string, params?: Record<string, any>): Promise<T> {
  const url = new URL(path, OPINION_API_HOST);
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
    }
  }
  const resp = await fetch(url.toString(), { signal: AbortSignal.timeout(30000) });
  if (!resp.ok) throw new Error(`API ${resp.status}: ${resp.statusText}`);
  return resp.json() as Promise<T>;
}

export { apiFetch, OPINION_API_HOST };
