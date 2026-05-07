export default function Pagination({ page, total, limit, onPageChange }) {
  const totalPages = Math.max(1, Math.ceil(total / limit));
  return (
    <div className="pagination" role="navigation" aria-label="Phân trang">
      <button
        type="button"
        className="btn btn--secondary btn--sm"
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
      >
        ← Trước
      </button>
      <span className="pagination__text">
        Trang <strong style={{ color: "var(--color-text)" }}>{page}</strong> / {totalPages}
        <span style={{ color: "var(--color-text-faint)" }}> · {total} bài</span>
      </span>
      <button
        type="button"
        className="btn btn--secondary btn--sm"
        disabled={page >= totalPages}
        onClick={() => onPageChange(page + 1)}
      >
        Sau →
      </button>
    </div>
  );
}
