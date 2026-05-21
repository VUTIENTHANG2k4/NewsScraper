const REQUIRED_FIELDS = [
  {
    key: "article_list",
    label: "Danh sách bài (CSS selector)",
    placeholder: "Ví dụ: .article-list a, .news-item h3 a",
    helper: "Trỏ đến các thẻ <a> liệt kê bài báo trên trang chủ. Dùng F12 → chuột phải phần tử → Copy selector."
  },
  {
    key: "title",
    label: "Tiêu đề bài báo",
    placeholder: "Ví dụ: h1.article-title, .detail-title h1",
    helper: "Thẻ chứa tiêu đề chính của bài viết."
  },
  {
    key: "content",
    label: "Nội dung bài viết",
    placeholder: "Ví dụ: .article-body, div.content-detail",
    helper: "Vùng chứa toàn bộ nội dung văn bản bài báo."
  }
];

const OPTIONAL_FIELDS = [
  {
    key: "author",
    label: "Tác giả",
    placeholder: "Ví dụ: .author-name, span.byline",
    helper: "Tên người viết bài. Để trống nếu không cần."
  },
  {
    key: "published_at",
    label: "Ngày đăng",
    placeholder: "Ví dụ: time.article-date, .post-time",
    helper: "Thẻ chứa thời gian đăng bài."
  },
  {
    key: "image",
    label: "Ảnh đại diện",
    placeholder: "Ví dụ: meta[property='og:image'], .article-thumb img",
    helper: "Thẻ <img> hoặc meta og:image của bài viết."
  },
  {
    key: "date_format",
    label: "Định dạng ngày (nâng cao)",
    placeholder: "Ví dụ: %d/%m/%Y %H:%M",
    helper: "Chỉ cần điền nếu ngày bị lỗi format. Để trống để hệ thống tự nhận diện."
  }
];

function SelectorField({ field, value, onChange }) {
  return (
    <div className="field" style={{ marginBottom: 14 }}>
      <span className="field__label">{field.label}</span>
      <input
        type="text"
        value={value || ""}
        placeholder={field.placeholder}
        onChange={(e) => onChange(field.key, e.target.value)}
        autoComplete="off"
        spellCheck="false"
      />
      <span className="field__helper">{field.helper}</span>
    </div>
  );
}

export default function SelectorForm({ selectors, onSelectorChange }) {
  return (
    <div className="form-section" style={{ marginTop: 12 }}>
      <h2>Cấu hình CSS Selector</h2>

      <details className="details-toggle" style={{ marginBottom: 16 }}>
        <summary>Selector là gì? Cách tìm ở đâu?</summary>
        <div className="details-toggle__body">
          <p>
            CSS Selector giúp hệ thống biết <strong>lấy dữ liệu ở đâu</strong> trong HTML của trang báo.
            Ví dụ: <code>.article-title</code> sẽ lấy text trong phần tử có class <em>article-title</em>.
          </p>
          <p>
            Cách tìm nhanh: Mở trang báo → nhấn <kbd>F12</kbd> → chọn tab <strong>Elements</strong> →
            chuột phải vào tiêu đề bài → chọn <strong>Copy → Copy selector</strong>.
          </p>
          <p style={{ marginBottom: 0 }}>
            Bạn có thể để trống tất cả — hệ thống sẽ tự cố gắng nhận diện nội dung theo chế độ tự động.
          </p>
        </div>
      </details>

      <p className="form-section__sub">Trường bắt buộc</p>
      {REQUIRED_FIELDS.map((field) => (
        <SelectorField
          key={field.key}
          field={field}
          value={selectors[field.key]}
          onChange={onSelectorChange}
        />
      ))}

      <details className="details-toggle" style={{ marginTop: 4 }}>
        <summary>Trường tuỳ chọn (tác giả, ngày đăng, ảnh…)</summary>
        <div className="details-toggle__body">
          {OPTIONAL_FIELDS.map((field) => (
            <SelectorField
              key={field.key}
              field={field}
              value={selectors[field.key]}
              onChange={onSelectorChange}
            />
          ))}
        </div>
      </details>
    </div>
  );
}
