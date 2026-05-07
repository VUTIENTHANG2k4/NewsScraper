# CHECKLIST TONG HOP TIEN DO (THEO SPRINT_1_DESIGN.md)

Cap nhat lan cuoi: 2026-04-17

Trang thai:
- [x] Da hoan thanh
- [~] Da lam mot phan / dat ve ky thuat nhung chua dat ve van hanh
- [ ] Chua lam
- [!] Bi chan boi moi truong / ket noi ngoai

---

## Sprint 1 — Tuan 1: Nen Mong

- [x] Tao repo, cau truc thu muc theo muc 4
- [x] Setup Docker Compose, MongoDB
- [x] Viet `config.py`, `db/mongo.py`, tao indexes
- [x] Viet `fetcher.py` (httpx async)
- [x] Viet `extractor.py` (CSS Selector)
- [x] Seed 20 nguon + crawl thu nghiem 5 nguon bao http
- [x] Ghi `crawl_logs` sau moi lan crawl

Bang chung:
- `reports/sprint1_crawl5_report.md`
- `reports/sprint1_crawl5_report.json`

---

## Sprint 2 — Tuan 2: Scraper Hoan Chinh

- [x] Viet `normalizer.py` (date -> UTC, dedup, clean text)
- [x] Tich hop `scheduler.py` (APScheduler 30 phut)
- [x] Them Playwright cho 2 nguon playwright
- [x] Crawl du 20 nguon, kiem tra `crawl_logs`
- [~] Xu ly error khong crash toan bo

Ghi chu:
- Engine da chay song song va khong crash toan bo khi loi tung nguon.
- Van con loi ket noi doi voi mot so nguon theo tung thoi diem mang/website (vi du BBC/ICTNews/SKDS).

Bang chung:
- `reports/sprint2_crawl20_report.md`
- `reports/sprint2_crawl20_report.json`
- Kiem tra DB: latest batch co 20 logs, 20 unique sources.

---

## Sprint 3 — Tuan 3: API + Frontend Co Ban

- [x] Xay dung toan bo API endpoints (FastAPI)
- [x] Frontend: Trang Tin Tuc (card, filter, pagination)
- [x] Frontend: Trang Dashboard (bang nguon, toggle, crawl ngay)
- [x] Ket noi Frontend <-> Backend hoan chinh (muc MVP)

Ghi chu:
- Da ket noi API client va cac trang chinh.
- Da bo sung loading/error states co ban cho cac man hinh chinh.

---

## Sprint 4 — Tuan 4: Them Nguon Dong + Hoan Thien

- [x] Frontend: Trang Them Nguon + SelectorForm
- [x] Backend: `POST /crawl/preview` (test selector live)
- [x] End-to-end test: them nguon moi -> sau 1 chu ky crawler co bai xuat hien
- [x] Xu ly loading states, error states tren UI
- [x] Viet unit test cho normalizer + extractor

Bang chung:
- E2E: `reports/e2e_add_source_cycle_report.md`, `reports/e2e_add_source_cycle_report.json`
- Unit test: `backend/tests/test_normalizer.py`, `backend/tests/test_extractor.py`
- Ket qua test: `13 passed`

Luu y:
- E2E trong bo script xac nhan theo "1 chu ky crawl" (kich hoat cycle ngay) thay vi cho dung 30 phut thoi gian thuc.
- Chu ky 30 phut production van duoc scheduler quan ly.

---

## Tong ket nhanh

- Hoan thanh phan lon checklist ky thuat cua 4 sprint.
- Con rui ro van hanh chu yeu o tinh on dinh ket noi mot so nguon ben ngoai (theo thoi diem).
- Co day du report file de doi chieu tien do va nghiem thu.
