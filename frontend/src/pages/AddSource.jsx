import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createSource, previewSelector, triggerOneCrawl } from "../api/client";
import SelectorForm from "../components/SelectorForm";
import PreviewCard from "../components/PreviewCard";

const DEFAULT_SELECTORS = {
  article_list: "",
  title: "",
  author: "",
  content: "",
  published_at: "",
  image: "",
  date_format: ""
};

const STEPS = [
  { number: 1, label: "Thông tin cơ bản" },
  { number: 2, label: "Cấu hình selector" },
  { number: 3, label: "Xem thử & Xác nhận" }
];

function isValidUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}

function extractErrorMessage(error, fallback) {
  return error?.response?.data?.detail || error?.message || fallback;
}

function WizardSteps({ current }) {
  return (
    <div className="wizard-steps">
      {STEPS.map((step, idx) => {
        const state =
          step.number < current ? "done" : step.number === current ? "active" : "pending";
        return (
          <div key={step.number} className="wizard-steps__item">
            <div className={`wizard-step-circle wizard-step-circle--${state}`}>
              {state === "done" ? "✓" : step.number}
            </div>
            <span className={`wizard-step-label wizard-step-label--${state}`}>{step.label}</span>
            {idx < STEPS.length - 1 && <div className={`wizard-step-line ${state === "done" ? "wizard-step-line--done" : ""}`} />}
          </div>
        );
      })}
    </div>
  );
}

export default function AddSource() {
  const queryClient = useQueryClient();
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    name: "",
    base_url: "",
    crawl_type: "http",
    selector_type: "css",
    selectors: DEFAULT_SELECTORS
  });
  const [errors, setErrors] = useState({});
  const [previewUrl, setPreviewUrl] = useState("");
  const [previewResult, setPreviewResult] = useState(null);
  const [savedSource, setSavedSource] = useState(null);
  const [crawlDone, setCrawlDone] = useState(false);

  const createMutation = useMutation({
    mutationFn: createSource,
    onSuccess: (data) => {
      setSavedSource(data);
      queryClient.invalidateQueries({ queryKey: ["sources"] });
    }
  });

  const previewMutation = useMutation({
    mutationFn: previewSelector,
    onSuccess: (data) => setPreviewResult(data)
  });

  const crawlMutation = useMutation({
    mutationFn: triggerOneCrawl,
    onSuccess: () => setCrawlDone(true)
  });

  const updateField = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    if (errors[key]) setErrors((prev) => ({ ...prev, [key]: null }));
  };

  const updateSelector = (key, value) => {
    setForm((prev) => ({
      ...prev,
      selectors: { ...prev.selectors, [key]: value }
    }));
  };

  const validateStep1 = () => {
    const newErrors = {};
    if (!form.name.trim()) newErrors.name = "Vui lòng nhập tên nguồn.";
    if (!form.base_url.trim()) {
      newErrors.base_url = "Vui lòng nhập URL.";
    } else if (!isValidUrl(form.base_url.trim())) {
      newErrors.base_url = "URL không hợp lệ. Ví dụ: https://vnexpress.net";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const goNext = () => {
    if (step === 1 && !validateStep1()) return;
    setStep((s) => s + 1);
  };

  const goBack = () => {
    setStep((s) => s - 1);
    setPreviewResult(null);
  };

  const handlePreview = () => {
    if (!previewUrl.trim()) return;
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

  const handleReset = () => {
    setStep(1);
    setForm({
      name: "",
      base_url: "",
      crawl_type: "http",
      selector_type: "css",
      selectors: DEFAULT_SELECTORS
    });
    setErrors({});
    setPreviewUrl("");
    setPreviewResult(null);
    setSavedSource(null);
    setCrawlDone(false);
    createMutation.reset();
  };

  if (savedSource) {
    return (
      <section>
        <header className="page-header">
          <span className="page-header__eyebrow">Cấu hình</span>
          <h1>Thêm nguồn mới</h1>
        </header>

        <div className="save-success-banner">
          <div className="save-success-banner__icon">✓</div>
          <div className="save-success-banner__body">
            <strong>Đã lưu nguồn "{savedSource.name}" thành công!</strong>
            <p>Hệ thống sẽ tự động crawl nguồn này theo lịch. Bạn cũng có thể crawl ngay bây giờ.</p>
          </div>

          {crawlDone ? (
            <div className="alert alert--success" style={{ margin: 0 }}>
              Đã khởi động crawl. Dữ liệu sẽ cập nhật sau vài phút.
            </div>
          ) : (
            <div className="save-success-banner__actions">
              <button
                type="button"
                className="btn btn--primary"
                onClick={() => crawlMutation.mutate(savedSource.id)}
                disabled={crawlMutation.isPending}
              >
                {crawlMutation.isPending ? "Đang crawl…" : "Crawl ngay"}
              </button>
              <button
                type="button"
                className="btn btn--secondary"
                onClick={handleReset}
              >
                Thêm nguồn khác
              </button>
            </div>
          )}

          {crawlDone && (
            <button
              type="button"
              className="btn btn--secondary"
              onClick={handleReset}
              style={{ marginTop: 8 }}
            >
              Thêm nguồn khác
            </button>
          )}
        </div>
      </section>
    );
  }

  return (
    <section>
      <header className="page-header">
        <span className="page-header__eyebrow">Cấu hình</span>
        <h1>Thêm nguồn mới</h1>
        <p>Khai báo địa chỉ trang báo và hướng dẫn hệ thống lấy bài viết.</p>
      </header>

      <WizardSteps current={step} />

      {createMutation.isError && (
        <p className="alert alert--error" role="alert">
          {extractErrorMessage(createMutation.error, "Không thể lưu nguồn.")}
        </p>
      )}

      {step === 1 && (
        <div className="form-section">
          <h2>Thông tin cơ bản</h2>

          <div className="form-row">
            <div className="field">
              <span className="field__label">Tên nguồn <span className="field__required">*</span></span>
              <input
                type="text"
                placeholder="Ví dụ: VnExpress, Tuổi Trẻ…"
                value={form.name}
                onChange={(e) => updateField("name", e.target.value)}
                className={errors.name ? "input--error" : ""}
              />
              {errors.name && <span className="field__error">{errors.name}</span>}
              <span className="field__helper">Tên hiển thị trong danh sách nguồn.</span>
            </div>
            <div className="field">
              <span className="field__label">URL trang chủ <span className="field__required">*</span></span>
              <input
                type="url"
                placeholder="https://vnexpress.net"
                value={form.base_url}
                onChange={(e) => updateField("base_url", e.target.value)}
                onBlur={() => {
                  if (form.base_url.trim() && !isValidUrl(form.base_url.trim())) {
                    setErrors((prev) => ({ ...prev, base_url: "URL không hợp lệ. Ví dụ: https://vnexpress.net" }));
                  }
                }}
                className={errors.base_url ? "input--error" : ""}
              />
              {errors.base_url && <span className="field__error">{errors.base_url}</span>}
              <span className="field__helper">Địa chỉ trang chủ hoặc trang danh sách bài của báo.</span>
            </div>
          </div>

          <details className="details-toggle">
            <summary>Cài đặt nâng cao</summary>
            <div className="details-toggle__body">
              <div className="form-row" style={{ marginBottom: 0 }}>
                <div className="field">
                  <span className="field__label">Công cụ thu thập</span>
                  <select
                    value={form.crawl_type}
                    onChange={(e) => updateField("crawl_type", e.target.value)}
                  >
                    <option value="http">HTTP — Nhanh, dùng cho hầu hết các báo</option>
                    <option value="playwright">Trình duyệt — Cho trang dùng JavaScript</option>
                  </select>
                  <span className="field__helper">Chọn "Trình duyệt" nếu trang báo tải nội dung bằng JavaScript (SPA, lazy load…).</span>
                </div>
                <div className="field">
                  <span className="field__label">Loại selector</span>
                  <select
                    value={form.selector_type}
                    onChange={(e) => updateField("selector_type", e.target.value)}
                  >
                    <option value="css">CSS Selector (khuyến nghị)</option>
                    <option value="xpath">XPath</option>
                  </select>
                  <span className="field__helper">Mặc định CSS là đủ cho phần lớn trường hợp.</span>
                </div>
              </div>
            </div>
          </details>

          <div className="wizard-nav">
            <button
              type="button"
              className="btn btn--primary"
              onClick={goNext}
            >
              Tiếp theo →
            </button>
          </div>
        </div>
      )}

      {step === 2 && (
        <>
          <SelectorForm selectors={form.selectors} onSelectorChange={updateSelector} />

          <div className="wizard-nav">
            <button type="button" className="btn btn--secondary" onClick={goBack}>
              ← Quay lại
            </button>
            <button type="button" className="btn btn--ghost" onClick={() => setStep(3)}>
              Bỏ qua → dùng chế độ tự động
            </button>
            <button type="button" className="btn btn--primary" onClick={goNext}>
              Tiếp theo →
            </button>
          </div>
        </>
      )}

      {step === 3 && (
        <>
          <div className="form-section">
            <h2>Xem thử kết quả trước khi lưu</h2>
            <p style={{ fontSize: "0.9rem", color: "var(--color-text-muted)", marginTop: -6, marginBottom: 14 }}>
              Dán link một bài báo cụ thể để kiểm tra selector đã cấu hình. Bước này tuỳ chọn.
            </p>
            <div className="preview-input-row">
              <div className="field" style={{ flex: 1, margin: 0 }}>
                <span className="field__label">URL một bài báo cụ thể</span>
                <input
                  type="url"
                  placeholder="https://vnexpress.net/bai-bao-cu-the.html"
                  value={previewUrl}
                  onChange={(e) => {
                    setPreviewUrl(e.target.value);
                    setPreviewResult(null);
                  }}
                />
              </div>
              <button
                type="button"
                className="btn btn--secondary"
                onClick={handlePreview}
                disabled={previewMutation.isPending || !previewUrl.trim()}
              >
                {previewMutation.isPending ? "Đang kiểm…" : "Xem thử"}
              </button>
            </div>

            {previewMutation.isError && (
              <p className="alert alert--error" style={{ marginTop: 12, marginBottom: 0 }}>
                {extractErrorMessage(previewMutation.error, "Kiểm tra selector thất bại.")}
              </p>
            )}
          </div>

          {previewResult && <PreviewCard result={previewResult} />}

          <div className="form-section" style={{ marginTop: 8 }}>
            <h2>Xác nhận lưu nguồn</h2>
            <div className="confirm-summary">
              <div className="confirm-summary__row">
                <span className="confirm-summary__key">Tên nguồn</span>
                <span className="confirm-summary__val">{form.name}</span>
              </div>
              <div className="confirm-summary__row">
                <span className="confirm-summary__key">URL</span>
                <a href={form.base_url} target="_blank" rel="noreferrer" className="confirm-summary__val">
                  {form.base_url}
                </a>
              </div>
              <div className="confirm-summary__row">
                <span className="confirm-summary__key">Công cụ</span>
                <span className="confirm-summary__val">
                  {form.crawl_type === "playwright" ? "Trình duyệt (Playwright)" : "HTTP"}
                </span>
              </div>
              <div className="confirm-summary__row">
                <span className="confirm-summary__key">Selector</span>
                <span className="confirm-summary__val">
                  {Object.values(form.selectors).some((v) => v.trim())
                    ? "Đã cấu hình"
                    : "Chế độ tự động"}
                </span>
              </div>
            </div>
          </div>

          <div className="wizard-nav">
            <button type="button" className="btn btn--secondary" onClick={goBack}>
              ← Quay lại
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
        </>
      )}
    </section>
  );
}
