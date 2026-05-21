const FIELD_LABELS = {
  title: "Tiêu đề",
  author: "Tác giả",
  content: "Nội dung",
  published_at: "Ngày đăng",
  image_url: "Ảnh"
};

function FieldBadge({ label, value }) {
  const hasValue = value && String(value).trim().length > 0;
  return (
    <span className={`preview-field-badge ${hasValue ? "preview-field-badge--ok" : "preview-field-badge--empty"}`}>
      <span className="preview-field-badge__dot" />
      {label}: {hasValue ? "Lấy được" : "Không có"}
    </span>
  );
}

export default function PreviewCard({ result }) {
  if (!result) return null;

  const { title, author, content, published_at, image_url } = result;

  const formattedDate = published_at
    ? (() => {
        try {
          return new Date(published_at).toLocaleString("vi-VN");
        } catch {
          return published_at;
        }
      })()
    : null;

  const contentSnippet = content ? content.slice(0, 220) + (content.length > 220 ? "…" : "") : null;

  return (
    <div className="preview-card">
      <div className="preview-card__header">
        <span className="preview-card__label">Kết quả xem thử</span>
      </div>

      {image_url && (
        <div className="preview-card__image-wrap">
          <img
            src={image_url}
            alt="Ảnh bài viết"
            className="preview-card__image"
            onError={(e) => { e.currentTarget.style.display = "none"; }}
          />
        </div>
      )}

      <div className="preview-card__body">
        {title ? (
          <h3 className="preview-card__title">{title}</h3>
        ) : (
          <p className="preview-card__missing">Không lấy được tiêu đề</p>
        )}

        <div className="preview-card__meta">
          {author && <span className="preview-card__author">{author}</span>}
          {author && formattedDate && <span className="preview-card__sep">·</span>}
          {formattedDate && <span className="preview-card__date">{formattedDate}</span>}
        </div>

        {contentSnippet && (
          <p className="preview-card__content">{contentSnippet}</p>
        )}

        <div className="preview-card__status-row">
          {Object.entries(FIELD_LABELS).map(([key, label]) => (
            <FieldBadge key={key} label={label} value={result[key]} />
          ))}
        </div>
      </div>
    </div>
  );
}
