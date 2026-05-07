import { useState } from "react";

export default function ArticleCard({ article }) {
  const [imgError, setImgError] = useState(false);

  const dateLabel = article.published_at
    ? new Date(article.published_at).toLocaleString("vi-VN", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      })
    : null;

  const showImage = article.image_url && !imgError;

  return (
    <article className="article-card">
      <div className="article-card__media">
        {showImage ? (
          <img
            src={article.image_url}
            alt=""
            loading="lazy"
            decoding="async"
            onError={() => setImgError(true)}
          />
        ) : null}
        {!showImage ? (
          <div className="article-card__placeholder" aria-hidden>
            Không có ảnh
          </div>
        ) : null}
      </div>
      <div className="article-card__body">
        {article.source_name || dateLabel ? (
          <div className="article-card__meta">
            {article.source_name ? (
              <span className="badge badge--source" title={article.source_name}>
                {article.source_name}
              </span>
            ) : null}
            {dateLabel ? <time dateTime={article.published_at}>{dateLabel}</time> : null}
          </div>
        ) : null}
        <h2 className="article-card__title">
          {article.title || "Không có tiêu đề"}
        </h2>
        {article.author ? (
          <p
            className="article-card__meta"
            style={{ margin: 0, color: "var(--color-text-muted)" }}
          >
            Tác giả: {article.author}
          </p>
        ) : null}
        <div className="article-card__footer">
          <a
            className="btn-link"
            href={article.source_url}
            target="_blank"
            rel="noreferrer"
          >
            Xem bài gốc
          </a>
        </div>
      </div>
    </article>
  );
}
