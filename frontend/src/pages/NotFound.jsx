import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <section className="not-found">
      <header className="page-header">
        <span className="page-header__eyebrow">404</span>
        <h1>Không tìm thấy trang</h1>
        <p>Đường dẫn bạn truy cập không tồn tại hoặc đã bị xoá.</p>
      </header>
      <Link to="/" className="btn btn--primary">
        Về trang Tin tức
      </Link>
    </section>
  );
}
