import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import {
  deleteSource,
  getSources,
  getStats,
  triggerAllCrawl,
  triggerOneCrawl,
  updateSource
} from "../api/client";
import SourceRow from "../components/SourceRow";

function extractErrorMessage(error, fallback) {
  return error?.response?.data?.detail || error?.message || fallback;
}

export default function Dashboard() {
  const [feedback, setFeedback] = useState("");
  const [errorFeedback, setErrorFeedback] = useState("");

  const queryClient = useQueryClient();
  const sourcesQuery = useQuery({ queryKey: ["sources"], queryFn: getSources });
  const statsQuery = useQuery({ queryKey: ["stats"], queryFn: getStats });

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ["sources"] });
    queryClient.invalidateQueries({ queryKey: ["stats"] });
  };

  const toggleMutation = useMutation({
    mutationFn: (source) => updateSource(source.id, { is_active: !source.is_active }),
    onSuccess: () => {
      setErrorFeedback("");
      setFeedback("Đã cập nhật trạng thái nguồn.");
      refresh();
    },
    onError: (error) => {
      setFeedback("");
      setErrorFeedback(extractErrorMessage(error, "Không thể cập nhật nguồn."));
    }
  });

  const deleteMutation = useMutation({
    mutationFn: deleteSource,
    onSuccess: () => {
      setErrorFeedback("");
      setFeedback("Đã xóa nguồn.");
      refresh();
    },
    onError: (error) => {
      setFeedback("");
      setErrorFeedback(extractErrorMessage(error, "Không thể xóa nguồn."));
    }
  });

  const crawlOneMutation = useMutation({
    mutationFn: triggerOneCrawl,
    onSuccess: () => {
      setErrorFeedback("");
      setFeedback("Đã kích hoạt crawl cho một nguồn.");
      refresh();
    },
    onError: (error) => {
      setFeedback("");
      setErrorFeedback(extractErrorMessage(error, "Không thể crawl nguồn này."));
    }
  });

  const crawlAllMutation = useMutation({
    mutationFn: triggerAllCrawl,
    onSuccess: () => {
      setErrorFeedback("");
      setFeedback("Đang crawl tất cả nguồn. Dữ liệu sẽ cập nhật sau vài phút.");
      refresh();
    },
    onError: (error) => {
      setFeedback("");
      setErrorFeedback(extractErrorMessage(error, "Không thể chạy crawl tất cả nguồn."));
    }
  });

  return (
    <section>
      <header className="page-header">
        <span className="page-header__eyebrow">Bảng điều khiển</span>
        <h1>Quản lý nguồn</h1>
        <p>Bật tắt nguồn, gọi crawl thủ công và theo dõi thống kê tổng thể.</p>
      </header>

      {feedback ? (
        <p className="alert alert--success" role="status">
          {feedback}
        </p>
      ) : null}
      {errorFeedback ? (
        <p className="alert alert--error" role="alert">
          {errorFeedback}
        </p>
      ) : null}

      <div className="stat-grid" style={{ marginBottom: 24 }}>
        <div className="stat-card">
          <span className="stat-card__label">Tổng bài đã thu thập</span>
          <span className="stat-card__value">
            {statsQuery.isLoading ? "—" : statsQuery.data?.total_news ?? 0}
          </span>
        </div>
        <div className="stat-card">
          <span className="stat-card__label">Nguồn đang bật</span>
          <span className="stat-card__value" style={{ color: "var(--color-success)" }}>
            {statsQuery.isLoading ? "—" : statsQuery.data?.active_sources ?? 0}
          </span>
        </div>
        <div className="stat-card">
          <span className="stat-card__label">Lần crawl gần nhất</span>
          <span
            className="stat-card__value"
            style={{ fontSize: "1.05rem", lineHeight: 1.3, fontWeight: 600 }}
          >
            {statsQuery.data?.last_crawl_at
              ? new Date(statsQuery.data.last_crawl_at).toLocaleString("vi-VN")
              : "—"}
          </span>
        </div>
      </div>

      <div
        className="card"
        style={{ marginBottom: 20, display: "flex", flexWrap: "wrap", alignItems: "center", gap: 12 }}
      >
        <button
          type="button"
          className="btn btn--primary"
          onClick={() => crawlAllMutation.mutate()}
          disabled={crawlAllMutation.isPending}
        >
          {crawlAllMutation.isPending ? "Đang khởi chạy…" : "Crawl tất cả ngay"}
        </button>
        {crawlAllMutation.isPending ? (
          <span className="alert alert--info" style={{ margin: 0, border: "none" }}>
            Đang yêu cầu server crawl toàn bộ nguồn đang bật.
          </span>
        ) : null}
        {statsQuery.isLoading ? (
          <span style={{ color: "var(--color-text-muted)" }}>Đang tải thống kê…</span>
        ) : null}
        {statsQuery.isError ? (
          <span style={{ color: "var(--color-danger)" }}>Không tải được thống kê.</span>
        ) : null}
      </div>

      {sourcesQuery.isLoading ? <p className="alert alert--info">Đang tải danh sách nguồn…</p> : null}
      {sourcesQuery.isError ? <p className="alert alert--error">Không tải được danh sách nguồn.</p> : null}

      <div className="table-wrap">
        <table className="data-table" role="grid" aria-label="Nguồn tin">
          <thead>
            <tr>
              <th>Tên</th>
              <th>URL</th>
              <th>Loại</th>
              <th>Trạng thái</th>
              <th>Lần crawl cuối</th>
              <th style={{ minWidth: 100 }}>Crawl</th>
              <th style={{ minWidth: 80 }}>Xóa</th>
            </tr>
          </thead>
          <tbody>
            {(sourcesQuery.data || []).map((source) => (
              <SourceRow
                key={source.id}
                source={source}
                onToggle={(item) => toggleMutation.mutate(item)}
                onDelete={(id) => deleteMutation.mutate(id)}
                onCrawlNow={(id) => crawlOneMutation.mutate(id)}
              />
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
