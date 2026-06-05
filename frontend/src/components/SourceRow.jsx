import { formatDateTimeGmt7 } from "../utils/datetime";

export default function SourceRow({ source, onToggle, onDelete, onCrawlNow }) {
  return (
    <tr>
      <td>
        <strong>{source.name}</strong>
      </td>
      <td>
        <a
          className="data-table__url"
          href={source.base_url}
          target="_blank"
          rel="noreferrer"
          title={source.base_url}
        >
          {source.base_url}
        </a>
      </td>
      <td>
        <span
          className="pill"
          style={
            source.crawl_type === "playwright" ? { background: "#f3e8ff", color: "#6b21a8" } : undefined
          }
        >
          {source.crawl_type}
        </span>
      </td>
      <td>
        {source.is_active ? (
          <span className="pill">Hoạt động</span>
        ) : (
          <span className="pill pill--off">Tắt</span>
        )}{" "}
        <button
          type="button"
          className="btn btn--ghost btn--sm"
          onClick={() => onToggle(source)}
        >
          {source.is_active ? "Tắt" : "Bật"}
        </button>
      </td>
      <td>
        {source.last_crawled
          ? formatDateTimeGmt7(source.last_crawled)
          : "—"}
      </td>
      <td>
        <button type="button" className="btn btn--secondary btn--sm" onClick={() => onCrawlNow(source.id)}>
          Crawl ngay
        </button>
      </td>
      <td>
        <button
          type="button"
          className="btn btn--danger btn--sm"
          onClick={() => {
            if (window.confirm(`Xóa nguồn "${source.name}"?\nThao tác này không thể hoàn tác.`)) {
              onDelete(source.id);
            }
          }}
        >
          Xóa
        </button>
      </td>
    </tr>
  );
}
