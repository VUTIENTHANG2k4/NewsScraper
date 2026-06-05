const VIETNAM_TIMEZONE = "Asia/Ho_Chi_Minh";

// Nếu giá trị là chuỗi ISO không có tz (ví dụ "2026-06-02T03:00:00" hoặc
// "2026-06-02T03:00:00.123"), coi như giờ UTC để parse — tránh việc JS hiểu
// nhầm là local time và lệch múi giờ khi chuyển sang giờ Việt Nam.
function parseAsUtcAware(value) {
  if (value instanceof Date) return value;
  if (typeof value !== "string") return new Date(value);

  const hasTz = /(Z|[+-]\d{2}:?\d{2})$/.test(value.trim());
  const looksLikeIsoNaive = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?$/.test(value.trim());
  if (!hasTz && looksLikeIsoNaive) {
    return new Date(`${value}Z`);
  }
  return new Date(value);
}

/**
 * Chuyển giá trị từ <input type="date"> (dạng "YYYY-MM-DD") thành ISO string UTC,
 * giả định người dùng chọn theo giờ Việt Nam.
 *
 * Vấn đề nếu dùng `new Date("2026-06-04")` trực tiếp:
 *   JS parse date-only string theo UTC → 2026-06-03T17:00:00Z (lệch -7h)
 *   → query backend trả bài của ngày hôm trước.
 *
 * @param {"start"|"end"} boundary - "start" lấy 00:00:00 VN, "end" lấy 23:59:59 VN
 */
export function dateInputToIso(dateStr, boundary = "start") {
  if (!dateStr) return undefined;
  const time = boundary === "end" ? "T23:59:59" : "T00:00:00";
  // +07:00 = Asia/Ho_Chi_Minh offset cố định (VN không đổi giờ mùa hè)
  return new Date(`${dateStr}${time}+07:00`).toISOString();
}

export function formatDateTimeGmt7(value, options = {}) {
  if (!value) return "—";
  const date = parseAsUtcAware(value);
  if (Number.isNaN(date.getTime())) return String(value);

  const formatted = new Intl.DateTimeFormat("vi-VN", {
    timeZone: VIETNAM_TIMEZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    ...options
  }).format(date);

  return `${formatted} (giờ VN)`;
}

