import axios from "axios";

// Timeout 30s — đủ cho mọi endpoint thông thường, kể cả /crawl/preview phải fetch HTML.
// Endpoint /crawl/trigger có thể lâu hơn, nên override riêng phía dưới.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
  timeout: 30_000
});

// Gắn X-API-Key vào mọi request nếu VITE_API_KEY được cấu hình.
// Backend bỏ qua header này nếu API_KEY chưa đặt (dev mode).
const _apiKey = import.meta.env.VITE_API_KEY || "";
if (_apiKey) {
  api.defaults.headers.common["X-API-Key"] = _apiKey;
}

// Interceptor toàn cục: log lỗi network/server để dễ debug, không nuốt exception.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === "ECONNABORTED") {
      console.warn("[api] Request timeout:", error.config?.url);
    } else if (!error.response) {
      console.warn("[api] Network error:", error.message);
    } else if (error.response.status >= 500) {
      console.error(
        "[api] Server error",
        error.response.status,
        error.config?.url,
        error.response.data
      );
    }
    return Promise.reject(error);
  }
);

export const getNews = (params) => api.get("/news", { params }).then((res) => res.data);
export const getSources = () => api.get("/sources").then((res) => res.data);
export const createSource = (payload) => api.post("/sources", payload).then((res) => res.data);
export const updateSource = (id, payload) =>
  api.patch(`/sources/${id}`, payload).then((res) => res.data);
export const deleteSource = (id) => api.delete(`/sources/${id}`);

// Crawl trigger có thể chạy lâu (nhiều nguồn × nhiều bài) — cần timeout dài hơn.
export const triggerAllCrawl = () =>
  api.post("/crawl/trigger", null, { timeout: 5 * 60_000 }).then((res) => res.data);
export const triggerOneCrawl = (id) =>
  api
    .post(`/crawl/trigger/${id}`, null, { timeout: 2 * 60_000 })
    .then((res) => res.data);

export const previewSelector = (payload) =>
  api.post("/crawl/preview", payload).then((res) => res.data);
export const getStats = () => api.get("/stats").then((res) => res.data);
