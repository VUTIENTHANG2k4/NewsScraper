const VIETNAM_TIMEZONE = "Asia/Ho_Chi_Minh";

export function formatDateTimeGmt7(value, options = {}) {
  if (!value) return "—";
  const date = new Date(value);
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

  return `${formatted} GMT+7`;
}

