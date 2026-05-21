# NewsScraper

Ứng dụng tổng hợp tin tức tự động từ các nguồn báo Việt Nam. Crawl định kỳ, lưu vào MongoDB và hiển thị qua giao diện React.

## Tính năng

- Tự động crawl tin tức từ 20+ nguồn báo Việt Nam theo lịch định kỳ
- Hỗ trợ cả trang tĩnh (HTTP) và trang render JavaScript (Playwright)
- Thêm nguồn mới qua giao diện wizard — không cần chỉnh code
- Cấu hình CSS selector để trỏ chính xác dữ liệu từng trang
- Xem thử selector trước khi lưu nguồn
- Tìm kiếm, lọc theo từ khóa, ngày, nguồn
- Dashboard quản lý nguồn: bật/tắt, crawl thủ công, xem thống kê

## Stack

| Tầng | Công nghệ |
|------|-----------|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Database | MongoDB 7 (local) hoặc MongoDB Atlas |
| Crawling | httpx + Playwright (Chromium), BeautifulSoup4 |
| Scheduling | APScheduler |
| Frontend | React 18, Vite 5, TanStack Query v5 |

## Yêu cầu

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- File `.env` (xem hướng dẫn bên dưới)

## Cài đặt và chạy

### 1. Clone repo

```bash
git clone <repo-url>
cd NewsScraper
```

### 2. Tạo file `.env`

```bash
cp .env.example .env
```

Mở `.env` và điền thông tin phù hợp (xem chi tiết trong `.env.example`).

### Chế độ A — Dùng MongoDB local (dev offline)

```bash
docker compose up -d
```

### Chế độ B — Dùng MongoDB Atlas (cloud)

Cập nhật `MONGODB_URI` trong `.env` thành connection string Atlas:

```env
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

Sau đó chạy:

```bash
docker compose -f docker-compose.atlas.yml up -d
```

### 3. Truy cập

| Dịch vụ | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

## Cấu trúc dự án

```
NewsScraper/
├── backend/
│   ├── api/              # FastAPI routes (news, sources, crawl)
│   ├── db/               # MongoDB connection, indexes, seed data
│   ├── models/           # Pydantic schemas
│   ├── scraper/          # Crawl engine, fetcher, extractor, scheduler
│   ├── scripts/          # Sprint proof scripts
│   ├── tests/            # Unit tests
│   ├── config.py         # Settings từ env
│   ├── main.py           # FastAPI app entry
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── api/          # Axios client
│       ├── components/   # UI components
│       └── pages/        # NewsFeed, Dashboard, AddSource
├── reports/              # Crawl proof reports
├── docker-compose.yml          # Dev: MongoDB local + backend + frontend
├── docker-compose.atlas.yml    # Dev/Prod: MongoDB Atlas + backend + frontend
├── .env.example                # Template biến môi trường
└── README.md
```

## Biến môi trường

| Biến | Mặc định | Mô tả |
|------|----------|-------|
| `MONGODB_URI` | `mongodb://mongodb:27017` | URI kết nối MongoDB |
| `MONGODB_DB` | `newsdb` | Tên database |
| `BACKEND_PORT` | `8000` | Port backend |
| `CRAWL_INTERVAL_MINUTES` | `30` | Chu kỳ crawl tự động (phút) |
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | URL API cho frontend |

## API

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/health` | Kiểm tra trạng thái app + MongoDB |
| GET | `/api/v1/news` | Danh sách tin (có filter, pagination) |
| GET | `/api/v1/stats` | Thống kê tổng quan |
| GET/POST/PATCH/DELETE | `/api/v1/sources` | Quản lý nguồn crawl |
| POST | `/api/v1/crawl/trigger` | Crawl tất cả nguồn ngay |
| POST | `/api/v1/crawl/trigger/{id}` | Crawl một nguồn |
| POST | `/api/v1/crawl/preview` | Xem thử selector trên URL bài |

## Chạy tests

```bash
docker compose exec backend pytest tests/ -v
```

## Ghi chú

- File `.env` chứa credentials — **không commit lên git**
- Backend sử dụng Playwright Chromium (~300MB RAM) — VPS nên có tối thiểu 2GB RAM
- Lần đầu khởi động sẽ tự seed 20 nguồn mặc định nếu collection `sources` trống
