import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getNews, getSources } from "../api/client";
import ArticleCard from "../components/ArticleCard";
import FilterBar from "../components/FilterBar";
import Pagination from "../components/Pagination";

const defaultFilters = {
  q: "",
  from: "",
  to: "",
  source_id: ""
};

export default function NewsFeed() {
  const [filters, setFilters] = useState(defaultFilters);
  const [appliedFilters, setAppliedFilters] = useState(defaultFilters);
  const [page, setPage] = useState(1);
  const limit = 20;

  const params = useMemo(() => {
    const payload = { page, limit };
    if (appliedFilters.q) payload.q = appliedFilters.q;
    if (appliedFilters.from) payload.from = new Date(appliedFilters.from).toISOString();
    if (appliedFilters.to) payload.to = new Date(appliedFilters.to).toISOString();
    if (appliedFilters.source_id) payload.source_id = appliedFilters.source_id;
    return payload;
  }, [appliedFilters, page]);

  const newsQuery = useQuery({
    queryKey: ["news", params],
    queryFn: () => getNews(params)
  });

  const sourcesQuery = useQuery({
    queryKey: ["sources-options"],
    queryFn: getSources
  });

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleApply = () => {
    setAppliedFilters(filters);
    setPage(1);
  };

  const handleReset = () => {
    setFilters(defaultFilters);
    setAppliedFilters(defaultFilters);
    setPage(1);
  };

  const list = newsQuery.data?.data || [];
  const empty = !newsQuery.isLoading && !newsQuery.isError && list.length === 0;

  return (
    <section>
      <header className="page-header">
        <span className="page-header__eyebrow">Tổng hợp tự động</span>
        <h1>Tin tức mới nhất</h1>
        <p>Đọc bài từ các nguồn đang bật, lọc theo từ khóa hoặc nguồn báo.</p>
      </header>

      <FilterBar
        filters={filters}
        sources={sourcesQuery.data || []}
        onChange={handleFilterChange}
        onApply={handleApply}
        onReset={handleReset}
      />

      {newsQuery.isError ? (
        <p className="alert alert--error" role="alert">
          Không thể tải danh sách bài viết. Kiểm tra API backend và thử lại.
        </p>
      ) : null}
      {sourcesQuery.isError ? (
        <p className="alert alert--error" role="alert">
          Không tải được danh sách nguồn cho bộ lọc.
        </p>
      ) : null}

      {newsQuery.isLoading ? (
        <div className="loading-block" aria-busy>
          <p className="skeleton" style={{ maxWidth: 200, height: 14, marginBottom: 16 }} />
          <div
            className="grid-articles"
            style={{ pointerEvents: "none", opacity: 0.7 }}
            aria-hidden
          >
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div
                key={i}
                className="card"
                style={{ minHeight: 220, display: "flex", flexDirection: "column", gap: 8 }}
              >
                <div className="skeleton" style={{ height: 120, width: "100%" }} />
                <div className="skeleton" style={{ height: 16, width: "60%" }} />
                <div className="skeleton" style={{ height: 12, width: "90%" }} />
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {empty ? (
        <div className="empty-state" role="status">
          <strong style={{ color: "var(--color-text)", display: "block", marginBottom: 6 }}>
            Chưa có bài nào phù hợp
          </strong>
          Có thể cần crawl từ trang <strong>Quản lý nguồn</strong> hoặc bộ lọc đang quá hẹp.
        </div>
      ) : null}

      {list.length > 0 ? (
        <div className="grid-articles">
          {list.map((article) => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      ) : null}

      {!newsQuery.isLoading && (newsQuery.data?.total || 0) > 0 ? (
        <Pagination
          page={page}
          total={newsQuery.data?.total || 0}
          limit={limit}
          onPageChange={setPage}
        />
      ) : null}
    </section>
  );
}
