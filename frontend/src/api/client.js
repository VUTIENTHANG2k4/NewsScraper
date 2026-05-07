import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1"
});

export const getNews = (params) => api.get("/news", { params }).then((res) => res.data);
export const getSources = () => api.get("/sources").then((res) => res.data);
export const createSource = (payload) => api.post("/sources", payload).then((res) => res.data);
export const updateSource = (id, payload) =>
  api.patch(`/sources/${id}`, payload).then((res) => res.data);
export const deleteSource = (id) => api.delete(`/sources/${id}`);
export const triggerAllCrawl = () => api.post("/crawl/trigger").then((res) => res.data);
export const triggerOneCrawl = (id) =>
  api.post(`/crawl/trigger/${id}`).then((res) => res.data);
export const previewSelector = (payload) =>
  api.post("/crawl/preview", payload).then((res) => res.data);
export const getStats = () => api.get("/stats").then((res) => res.data);
