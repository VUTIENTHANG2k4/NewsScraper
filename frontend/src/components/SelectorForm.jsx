export default function SelectorForm({ selectors, onSelectorChange }) {
  const fields = [
    { key: "article_list", label: "Danh sách bài (link)" },
    { key: "title", label: "Tiêu đề" },
    { key: "author", label: "Tác giả" },
    { key: "content", label: "Nội dung" },
    { key: "published_at", label: "Thời gian đăng" },
    { key: "image", label: "Ảnh đại diện" },
    { key: "date_format", label: "Định dạng ngày (tùy chọn)" }
  ];

  return (
    <div className="form-section" style={{ marginTop: 12 }}>
      <h2>CSS / XPath</h2>
      <p style={{ fontSize: "0.9rem", color: "var(--color-text-muted)", marginTop: -6, marginBottom: 12 }}>
        Để trống để dùng chế độ dự đoán mặc định; điền nếu bạn muốn trỏ chính xác theo trang.
      </p>
      <div className="selector-grid">
        {fields.map((field) => (
          <div key={field.key} className="field" style={{ marginBottom: 10 }}>
            <span className="field__label">{field.label}</span>
            <input
              type="text"
              value={selectors[field.key] || ""}
              onChange={(e) => onSelectorChange(field.key, e.target.value)}
              autoComplete="off"
              spellCheck="false"
            />
          </div>
        ))}
      </div>
    </div>
  );
}
