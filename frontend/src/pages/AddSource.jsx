import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { createSource, previewSelector } from "../api/client";
import SelectorForm from "../components/SelectorForm";

const defaultSelectors = {
  article_list: "",
  title: "",
  author: "",
  content: "",
  published_at: "",
  image: "",
  date_format: ""
};

function extractErrorMessage(error, fallback) {
  return error?.response?.data?.detail || error?.message || fallback;
}

export default function AddSource() {
  const [form, setForm] = useState({
    name: "",
    base_url: "",
    crawl_type: "http",
    selector_type: "css",
    selectors: defaultSelectors
  });
  const [previewUrl, setPreviewUrl] = useState("");
  const [previewResult, setPreviewResult] = useState(null);

  const createMutation = useMutation({
    mutationFn: createSource,
    onSuccess: () => {
      setPreviewResult(null);
    }
  });

  const previewMutation = useMutation({
    mutationFn: previewSelector,
    onSuccess: (data) => setPreviewResult(data)
  });

  const updateField = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const updateSelector = (key, value) => {
    setForm((prev) => ({
      ...prev,
      selectors: { ...prev.selectors, [key]: value }
    }));
  };

  const handlePreview = () => {
    if (!previewUrl) return;
    previewMutation.mutate({
      url: previewUrl,
      selector_type: form.selector_type,
      selectors: {
        title: form.selectors.title,
        author: form.selectors.author,
        content: form.selectors.content,
        published_at: form.selectors.published_at,
        image: form.selectors.image
      }
    });
  };

  const handleSave = () => {
    createMutation.mutate(form);
  };

  return (
    <section>
      <header className="page-header">
        <span className="page-header__eyebrow">Cấu hình</span>
        <h1>Thêm nguồn mới</h1>
        <p>Khai báo URL, loại thu thập (HTTP hoặc trình duyệt) và tùy chọn selector.</p>
      </header>

      {createMutation.isSuccess ? (
        <p className="alert alert--success" role="status">
          Đã lưu nguồn thành công.
        </p>
      ) : null}
      {createMutation.isError ? (
        <p className="alert alert--error" role="alert">
          {extractErrorMessage(createMutation.error, "Không thể lưu nguồn.")}
        </p>
      ) : null}
      {previewMutation.isError ? (
        <p className="alert alert--error" role="alert">
          {extractErrorMessage(previewMutation.error, "Kiểm tra selector thất bại.")}
        </p>
      ) : null}

      <div className="form-section">
        <h2>Thông tin cơ bản</h2>
        <div className="form-row">
          <div className="field">
            <span className="field__label">Tên nguồn</span>
            <input
              type="text"
              placeholder="Ví dụ: Tên báo / chuyên mục"
              value={form.name}
              onChange={(e) => updateField("name", e.target.value)}
            />
          </div>
          <div className="field">
            <span className="field__label">URL trang chủ / danh sách</span>
            <input
              type="url"
              placeholder="https://…"
              value={form.base_url}
              onChange={(e) => updateField("base_url", e.target.value)}
            />
          </div>
        </div>
        <div className="form-row" style={{ marginBottom: 0 }}>
          <div className="field">
            <span className="field__label">Công cụ thu thập</span>
            <select
              value={form.crawl_type}
              onChange={(e) => updateField("crawl_type", e.target.value)}
            >
              <option value="http">HTTP (nhanh, phù hợp trang tĩnh)</option>
              <option value="playwright">Playwright (JS, trang cần trình duyệt)</option>
            </select>
          </div>
          <div className="field">
            <span className="field__label">Loại trỏ dữ liệu</span>
            <select
              value={form.selector_type}
              onChange={(e) => updateField("selector_type", e.target.value)}
            >
              <option value="css">CSS Selector</option>
              <option value="xpath">XPath</option>
            </select>
          </div>
        </div>
      </div>

      <SelectorForm selectors={form.selectors} onSelectorChange={updateSelector} />

      <div className="form-section" style={{ marginTop: 16 }}>
        <h2>Kiểm thử trước khi lưu</h2>
        <div
          className="row"
          style={{ width: "100%", alignItems: "flex-end", gap: 10, marginBottom: 0 }}
        >
          <div className="field" style={{ flex: 1, minWidth: 200, margin: 0 }}>
            <span className="field__label">URL bài để preview (tùy chọn)</span>
            <input
              type="url"
              placeholder="Dán link một bài cụ thể…"
              value={previewUrl}
              onChange={(e) => setPreviewUrl(e.target.value)}
            />
          </div>
          <button
            type="button"
            className="btn btn--secondary"
            onClick={handlePreview}
            disabled={previewMutation.isPending || !previewUrl.trim()}
          >
            {previewMutation.isPending ? "Đang kiểm…" : "Xem thử selector"}
          </button>
          <button
            type="button"
            className="btn btn--primary"
            onClick={handleSave}
            disabled={createMutation.isPending}
          >
            {createMutation.isPending ? "Đang lưu…" : "Lưu nguồn"}
          </button>
        </div>
      </div>

      {previewResult ? (
        <pre
          className="preview-json"
          style={{ marginTop: 16 }}
        >
          {JSON.stringify(previewResult, null, 2)}
        </pre>
      ) : null}
    </section>
  );
}
