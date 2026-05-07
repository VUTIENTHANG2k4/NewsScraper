# SPRINT 1 — TÀI LIỆU THIẾT KẾ HỆ THỐNG (TÀI LIỆU GỐC)

> **Đây là tài liệu thiết kế duy nhất và có thẩm quyền cho Giai đoạn 1.**
> Mọi quyết định code, cấu trúc thư mục, API, schema đều phải tuân thủ tài liệu này.
> Khi có thay đổi, cập nhật tài liệu này trước, sau đó mới code.

---

## 1. MỤC TIÊU & PHẠM VI

### Mục tiêu
Xây dựng một **MVP khép kín** để tự động thu thập, lưu trữ và hiển thị tin tức từ **≥20 nguồn báo**, với khả năng thêm nguồn mới hoàn toàn qua giao diện mà không cần chạm vào code.

### Ưu tiên
1. **Ổn định** — Crawler không crash khi HTML thay đổi nhẹ
2. **Đúng dữ liệu** — Trích xuất đủ 6 trường, thời gian đồng nhất UTC
3. **Mở rộng được** — Thêm nguồn mới qua UI, không sửa code

### Ngoài phạm vi Giai đoạn 1
- Authentication / phân quyền người dùng
- Phân tích nội dung, AI tagging
- Push notification, RSS export
- Deploy production (chỉ local + Docker)

---

## 2. QUYẾT ĐỊNH CÔNG NGHỆ (ĐÃ CHỐT)

| Hạng mục | Lựa chọn | Lý do |
|---|---|---|
| **Backend framework** | FastAPI (Python 3.11+) | Async native, auto OpenAPI docs |
| **Database** | **MongoDB only** | Đủ cho cả news lẫn source config ở giai đoạn 1 |
| **HTTP Crawler** | `httpx` + `asyncio` | Async, hiệu suất cao |
| **JS-rendered sites** | `Playwright` (async) | Các nguồn dùng React/Vue render |
| **HTML Parser** | `BeautifulSoup4` + `lxml` | CSS Selector + XPath |
| **Date Parsing** | `python-dateutil` | Linh hoạt với nhiều định dạng |
| **Scheduler** | `APScheduler` (AsyncIOScheduler) | Tích hợp thẳng vào FastAPI |
| **Frontend** | React 18 + Vite | Lightweight SPA |
| **Styling** | Vanilla CSS | Không dùng Tailwind |
| **HTTP Client (FE)** | Axios + React Query | Cache, loading state |
| **Router (FE)** | React Router v6 | SPA routing |
| **Dev environment** | Docker Compose | MongoDB + Backend + Frontend |
| **Ngôn ngữ UI** | **Tiếng Việt** | Toàn bộ label, placeholder, thông báo |
| **Authentication** | **Không có** | Để public hoàn toàn ở giai đoạn 1 |

---

## 3. KIẾN TRÚC HỆ THỐNG

```
┌──────────────────────────────────────────────────────────────┐
│                      FRONTEND (React + Vite)                  │
│                                                               │
│   /           /dashboard        /them-nguon                   │
│  [News Feed] [Quản lý nguồn]  [Thêm nguồn mới]               │
│                                                               │
└────────────────────────┬─────────────────────────────────────┘
                         │ REST API (JSON)
                         │ http://localhost:8000
┌────────────────────────▼─────────────────────────────────────┐
│                      BACKEND (FastAPI)                        │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │  API Router │  │  Scheduler   │  │   Scraper Engine    │  │
│  │             │  │ (30 phút)    │  │                     │  │
│  │ /news       │  │              │  │  fetcher.py         │  │
│  │ /sources    │  │  trigger →   │──▶  extractor.py       │  │
│  │ /crawl      │  │  engine      │  │  normalizer.py      │  │
│  └─────────────┘  └──────────────┘  └──────────┬──────────┘  │
│                                                 │             │
└─────────────────────────────────────────────────┼────────────┘
                                                  │
┌─────────────────────────────────────────────────▼────────────┐
│                  MongoDB (single database: newsdb)             │
│                                                               │
│  Collection: news          Collection: sources                │
│  (bài báo thu thập)        (cấu hình nguồn + selectors)       │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 4. CẤU TRÚC THƯ MỤC DỰ ÁN

```
NewsScraper/
│
├── SPRINT_1_DESIGN.md          ← TÀI LIỆU NÀY (nguồn sự thật)
│
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── backend/
│   ├── main.py                 # FastAPI app, lifespan, CORS
│   ├── config.py               # Settings từ .env (MongoDB URI, ports)
│   ├── requirements.txt
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes_news.py      # GET /news
│   │   ├── routes_sources.py   # GET/POST/PATCH /sources
│   │   └── routes_crawl.py     # POST /crawl/trigger, POST /crawl/preview
│   │
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── engine.py           # Orchestrator: load active sources → dispatch
│   │   ├── fetcher.py          # httpx async fetch + Playwright fallback
│   │   ├── extractor.py        # CSS Selector / XPath → 6 fields
│   │   ├── normalizer.py       # Date → UTC, clean text, dedup hash
│   │   └── scheduler.py        # APScheduler setup
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   └── mongo.py            # Motor client, collection refs, indexes
│   │
│   └── models/
│       ├── __init__.py
│       ├── news.py             # Pydantic model cho bài báo
│       └── source.py           # Pydantic model cho nguồn/selector
│
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── package.json
    │
    └── src/
        ├── main.jsx
        ├── App.jsx             # Route setup
        ├── index.css           # Design tokens, global styles
        │
        ├── pages/
        │   ├── NewsFeed.jsx    # Trang chính — danh sách bài báo
        │   ├── Dashboard.jsx   # Quản lý nguồn
        │   └── AddSource.jsx   # Form thêm nguồn mới + selector
        │
        ├── components/
        │   ├── Navbar.jsx
        │   ├── ArticleCard.jsx     # Card bài báo
        │   ├── FilterBar.jsx       # Ô tìm kiếm + DateRange
        │   ├── Pagination.jsx
        │   ├── SourceRow.jsx       # Hàng trong bảng dashboard
        │   └── SelectorForm.jsx    # Input fields cho từng selector
        │
        └── api/
            └── client.js       # Axios instance + tất cả API calls
```

---

## 5. MONGODB SCHEMA

### Database: `newsdb`

---

### Collection: `sources` (Cấu hình nguồn báo)

```json
{
  "_id": "ObjectId",
  "name": "VnExpress",
  "base_url": "https://vnexpress.net",
  "crawl_type": "http",
  "is_active": true,
  "last_crawled": "2026-04-17T03:00:00Z",
  "selectors": {
    "article_list":  "CSS hoặc XPath — trỏ đến danh sách link bài",
    "title":         "CSS hoặc XPath — tiêu đề bài báo",
    "author":        "CSS hoặc XPath — tên tác giả",
    "content":       "CSS hoặc XPath — nội dung chính (text)",
    "published_at":  "CSS hoặc XPath — chuỗi ngày giờ",
    "image":         "CSS hoặc XPath — ảnh đại diện (src hoặc og:image)",
    "date_format":   "%d/%m/%Y %H:%M (tuỳ chọn, dùng nếu dateutil không parse được)"
  },
  "selector_type": "css",
  "created_at": "2026-04-17T02:00:00Z"
}
```

**Index:**
- `base_url`: unique

**Ghi chú `crawl_type`:**
- `"http"` — Dùng `httpx` (nhanh, hầu hết các báo tĩnh)
- `"playwright"` — Dùng Playwright (báo dùng JS render)

---

### Collection: `news` (Bài báo thu thập được)

```json
{
  "_id": "ObjectId",
  "source_id": "ObjectId liên kết sources._id",
  "source_name": "VnExpress",
  "source_url": "https://vnexpress.net/bai-bao-abc.html",
  "title": "Tiêu đề bài báo",
  "author": "Nguyễn Văn A",
  "content": "Nội dung toàn văn bài báo...",
  "image_url": "https://i1-vnexpress.vnecdn.net/...",
  "published_at": "2026-04-17T02:00:00Z",
  "created_at": "2026-04-17T03:05:00Z"
}
```

**Index:**
- `source_url`: unique — **dùng để dedup, không insert nếu đã tồn tại**
- `published_at`: descending — dùng cho filter theo thời gian
- `title`: text index — dùng cho full-text search

---

### Collection: `crawl_logs` (Lịch sử crawl)

```json
{
  "_id": "ObjectId",
  "source_id": "ObjectId",
  "source_name": "VnExpress",
  "crawled_at": "2026-04-17T03:00:00Z",
  "articles_found": 30,
  "articles_new": 5,
  "status": "success",
  "error_msg": null
}
```

**Giá trị `status`:** `"success"` | `"partial"` | `"error"`

---

## 6. API ENDPOINTS

**Base URL:** `http://localhost:8000/api/v1`

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/news` | Lấy danh sách bài báo (có filter + phân trang) |
| `GET` | `/sources` | Lấy danh sách nguồn báo |
| `POST` | `/sources` | Thêm nguồn mới |
| `PATCH` | `/sources/{id}` | Cập nhật nguồn (bật/tắt, sửa selector) |
| `DELETE` | `/sources/{id}` | Xóa nguồn |
| `POST` | `/crawl/trigger` | Kích hoạt crawl thủ công toàn bộ |
| `POST` | `/crawl/trigger/{id}` | Crawl thủ công 1 nguồn cụ thể |
| `POST` | `/crawl/preview` | Preview dữ liệu khi test selector |
| `GET` | `/stats` | Tổng số bài, nguồn đang active, lần crawl cuối |

---

### Chi Tiết API

#### `GET /api/v1/news`

**Query params:**

| Param | Kiểu | Mặc định | Mô tả |
|---|---|---|---|
| `q` | string | — | Tìm kiếm trong tiêu đề + nội dung |
| `from` | ISO date | — | Lọc từ ngày (UTC) |
| `to` | ISO date | — | Lọc đến ngày (UTC) |
| `source_id` | string | — | Lọc theo nguồn cụ thể |
| `page` | int | 1 | Trang hiện tại |
| `limit` | int | 20 | Số bài/trang (max 100) |

**Response:**
```json
{
  "total": 1500,
  "page": 1,
  "limit": 20,
  "data": [ { ...ArticleObject } ]
}
```

---

#### `POST /api/v1/sources`

**Request body:**
```json
{
  "name": "Tên báo",
  "base_url": "https://example.com",
  "crawl_type": "http",
  "selector_type": "css",
  "selectors": {
    "article_list": ".article-list a",
    "title": "h1.title",
    "author": ".author-name",
    "content": ".article-content",
    "published_at": ".publish-date",
    "image": "meta[property='og:image']"
  }
}
```

**Response:** `201 Created` + nguồn vừa tạo

---

#### `POST /api/v1/crawl/preview`

Dùng để test selector trước khi lưu nguồn. Backend fetch URL → áp dụng selectors → trả về kết quả preview.

**Request body:**
```json
{
  "url": "https://example.com/some-article",
  "selector_type": "css",
  "selectors": {
    "title": "h1.title",
    "author": ".author",
    "content": ".content",
    "published_at": ".date",
    "image": "meta[property='og:image']"
  }
}
```

**Response:**
```json
{
  "title": "Tiêu đề lấy được",
  "author": "Tên tác giả",
  "content": "200 ký tự đầu của nội dung...",
  "published_at": "2026-04-17T02:00:00Z",
  "image_url": "https://..."
}
```

---

## 7. LOGIC SCRAPER ENGINE

### Luồng Crawl (engine.py)

```
1. Đọc tất cả sources có is_active = true từ MongoDB
2. Tạo async tasks cho từng source (asyncio.gather)
3. Mỗi task:
   a. fetcher.py → lấy HTML (httpx hoặc Playwright tuỳ crawl_type)
   b. extractor.py → parse article links từ selector "article_list"
   c. Với mỗi article link:
      - fetch HTML bài báo
      - extractor.py → trích xuất 6 fields
      - normalizer.py → chuẩn hoá date → UTC, clean text
      - Kiểm tra source_url đã tồn tại trong MongoDB chưa
      - Nếu chưa → insert vào collection news
   d. Ghi crawl_log kết quả
4. Cập nhật last_crawled của source
```

### Quy Tắc Xử Lý Lỗi

- **Time out**: httpx timeout = 30s, Playwright timeout = 60s
- **Connection error**: log lỗi, đánh dấu status = "error", **không crash toàn bộ scheduler**
- **Selector không match**: trả về field = `null`, vẫn lưu bài (partial data)
- **HTML thay đổi**: Log cảnh báo, không crash

### Chuẩn Hoá Dữ Liệu (normalizer.py)

```python
# Date → UTC
- Dùng python-dateutil.parser.parse() (tự phát hiện định dạng)
- Nếu fail → dùng date_format từ selectors config
- Nếu vẫn fail → dùng datetime.utcnow() (fallback)
- Luôn convert về UTC (replace tzinfo hoặc assume +07:00 nếu không có tz)

# Text cleaning
- Strip HTML tags khỏi content
- Strip whitespace thừa
- Giới hạn content tối đa 50,000 ký tự

# Dedup
- Kiểm tra: db.news.find_one({"source_url": url})
- Nếu tồn tại → skip
```

---

## 8. FRONTEND — MÔ TẢ TRANG

### `/` — Trang Tin Tức (NewsFeed)

**Chức năng:**
- Hiển thị bài báo dạng grid (3 cột desktop, 2 tablet, 1 mobile)
- Mỗi card: ảnh đại diện, tiêu đề, tên báo, tác giả, thời gian đăng (định dạng "X giờ trước" hoặc ngày cụ thể)
- **Bộ lọc** (FilterBar):
  - Ô tìm kiếm: "Tìm kiếm bài báo..."
  - Chọn ngày bắt đầu: "Từ ngày"
  - Chọn ngày kết thúc: "Đến ngày"
  - Dropdown lọc theo nguồn
  - Nút "Tìm kiếm" + nút "Xoá bộ lọc"
- Phân trang: 20 bài/trang, hiển thị số trang

---

### `/dashboard` — Trang Quản Lý Nguồn (Dashboard)

**Chức năng:**
- Bảng danh sách nguồn báo, mỗi hàng gồm:
  - Tên báo
  - URL
  - Loại crawl (`http` / `playwright`)
  - Trạng thái: Toggle **Bật / Tắt**
  - Lần crawl cuối
  - Số bài đã thu thập
  - Nút **"Crawl ngay"** (kích hoạt crawl 1 nguồn)
  - Nút **"Chỉnh sửa"** (mở modal sửa selector)
  - Nút **"Xoá"**
- Nút **"+ Thêm nguồn mới"** → chuyển đến `/them-nguon`
- Nút **"Crawl tất cả ngay"** (kích hoạt crawl toàn bộ)
- Hiển thị stats tổng: Tổng bài / Nguồn đang bật / Lần crawl gần nhất

---

### `/them-nguon` — Trang Thêm Nguồn (AddSource)

**Chức năng:**
- Form nhập:
  - Tên nguồn (text)
  - URL trang chủ / trang danh mục (text)
  - Loại crawl: radio `HTTP` / `Playwright`
  - Loại selector: radio `CSS Selector` / `XPath`
- **SelectorForm** — mỗi field có label + input + tooltip:
  - Danh sách bài (article_list)
  - Tiêu đề (title)
  - Tác giả (author)
  - Nội dung (content)
  - Thời gian đăng (published_at)
  - Ảnh đại diện (image)
  - Định dạng ngày (tùy chọn)
- Nút **"Kiểm tra Selector"**: gọi `POST /crawl/preview`, hiển thị kết quả preview ngay bên dưới
- Nút **"Lưu nguồn"**: gọi `POST /sources`

---

## 9. DOCKER COMPOSE

```yaml
version: "3.9"
services:
  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: newsdb

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - mongodb
    env_file:
      - .env
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  mongo_data:
```

---

## 10. BIẾN MÔI TRƯỜNG (.env)

```env
# MongoDB
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DB=newsdb

# Backend
BACKEND_PORT=8000
CRAWL_INTERVAL_MINUTES=30

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 11. DANH SÁCH 20 NGUỒN BÁO KHỞI ĐẦU

Các nguồn sau sẽ được seed vào MongoDB khi khởi tạo (file `backend/db/seed.py`):

| # | Tên | URL | Crawl Type |
|---|---|---|---|
| 1 | VnExpress | https://vnexpress.net | http |
| 2 | Tuổi Trẻ | https://tuoitre.vn | http |
| 3 | Thanh Niên | https://thanhnien.vn | http |
| 4 | Dân Trí | https://dantri.com.vn | http |
| 5 | Zing News | https://zingnews.vn | http |
| 6 | VietnamNet | https://vietnamnet.vn | http |
| 7 | Nhân Dân | https://nhandan.vn | http |
| 8 | Lao Động | https://laodong.vn | http |
| 9 | Tiền Phong | https://tienphong.vn | http |
| 10 | Người Lao Động | https://nld.com.vn | http |
| 11 | Pháp Luật TP.HCM | https://plo.vn | http |
| 12 | An Ninh Thủ Đô | https://anninhthudo.vn | http |
| 13 | Sức Khỏe & Đời Sống | https://suckhoedoisong.vn | http |
| 14 | CafeF | https://cafef.vn | http |
| 15 | VnEconomy | https://vneconomy.vn | http |
| 16 | ICTNews | https://ictnews.vn | http |
| 17 | Báo Mới | https://baomoi.com | playwright |
| 18 | Kenh14 | https://kenh14.vn | playwright |
| 19 | GameK | https://gamek.vn | http |
| 20 | BBC Tiếng Việt | https://www.bbc.com/vietnamese | http |

> **Lưu ý:** Selectors cho từng nguồn sẽ được điền trong quá trình Sprint 1 - Tuần 1 sau khi kiểm tra HTML thực tế.

---

## 12. LỘ TRÌNH TRIỂN KHAI

### Sprint 1 — Tuần 1: "Nền Móng"
- [ ] Tạo repo, cấu trúc thư mục theo mục 4
- [ ] Setup Docker Compose, MongoDB
- [ ] Viết `config.py`, `db/mongo.py`, tạo indexes
- [ ] Viết `fetcher.py` (httpx async)
- [ ] Viết `extractor.py` (CSS Selector)
- [ ] Seed 20 nguồn + crawl thử nghiệm 5 nguồn báo http
- [ ] Ghi crawl_logs sau mỗi lần crawl

### Sprint 2 — Tuần 2: "Scraper Hoàn Chỉnh"
- [ ] Viết `normalizer.py` (date → UTC, dedup, clean text)
- [ ] Tích hợp `scheduler.py` (APScheduler 30 phút)
- [ ] Thêm Playwright cho 2 nguồn playwright
- [ ] Crawl đủ 20 nguồn, kiểm tra `crawl_logs`
- [ ] Xử lý error không crash toàn bộ

### Sprint 3 — Tuần 3: "API + Frontend Cơ Bản"
- [ ] Xây dựng toàn bộ API endpoints (FastAPI)
- [ ] Frontend: Trang Tin Tức (card, filter, pagination)
- [ ] Frontend: Trang Dashboard (bảng nguồn, toggle, crawl ngay)
- [ ] Kết nối Frontend ↔ Backend hoàn chỉnh

### Sprint 4 — Tuần 4: "Thêm Nguồn Động + Hoàn Thiện"
- [ ] Frontend: Trang Thêm Nguồn + SelectorForm
- [ ] Backend: `POST /crawl/preview` (test selector live)
- [ ] End-to-end test: thêm nguồn mới → 30 phút sau bài xuất hiện
- [ ] Xử lý loading states, error states trên UI
- [ ] Viết unit test cho normalizer + extractor

---

## 13. CHỈ SỐ KỸ THUẬT CẦN ĐẠT

| Chỉ số | Mục tiêu |
|---|---|
| Số nguồn crawl ổn định | ≥ 20 nguồn |
| Thời gian crawl 20 nguồn | < 5 phút (async song song) |
| Dedup rate | 0 bài trùng URL trong DB |
| Date format | 100% bài có `published_at` dạng UTC |
| API response time `/news` | < 500ms |
| UI không bị block khi crawl | ✅ (crawler chạy background) |
| Thêm nguồn mới → bài xuất hiện | < 35 phút (1 chu kỳ scheduler) |

---

*Tài liệu này được tạo ngày 17/04/2026. Phiên bản 1.0.*
