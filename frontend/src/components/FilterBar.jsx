export default function FilterBar({ filters, sources, onChange, onApply, onReset }) {
  return (
    <div className="card" style={{ marginBottom: 24 }}>
      <div className="filter-bar__grid">
        <div className="field">
          <span className="field__label">Từ khóa</span>
          <input
            type="search"
            placeholder="Tìm theo từ khóa…"
            value={filters.q}
            onChange={(e) => onChange("q", e.target.value)}
            autoComplete="off"
          />
        </div>
        <div className="field">
          <span className="field__label">Từ ngày</span>
          <input
            type="datetime-local"
            value={filters.from}
            onChange={(e) => onChange("from", e.target.value)}
          />
        </div>
        <div className="field">
          <span className="field__label">Đến ngày</span>
          <input
            type="datetime-local"
            value={filters.to}
            onChange={(e) => onChange("to", e.target.value)}
          />
        </div>
        <div className="field">
          <span className="field__label">Nguồn</span>
          <select
            value={filters.source_id}
            onChange={(e) => onChange("source_id", e.target.value)}
          >
            <option value="">Tất cả nguồn</option>
            {sources.map((source) => (
              <option key={source.id} value={source.id}>
                {source.name}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="filter-bar__actions">
        <button type="button" className="btn btn--primary" onClick={onApply}>
          Áp dụng bộ lọc
        </button>
        <button type="button" className="btn btn--ghost" onClick={onReset}>
          Xóa bộ lọc
        </button>
      </div>
    </div>
  );
}
