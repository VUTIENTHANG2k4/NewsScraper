import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import ErrorBoundary from "./components/ErrorBoundary";
import NewsFeed from "./pages/NewsFeed";
import Dashboard from "./pages/Dashboard";
import AddSource from "./pages/AddSource";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <div className="app-shell">
      <Navbar />

      <main className="container">
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<NewsFeed />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/them-nguon" element={<AddSource />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </ErrorBoundary>
      </main>
    </div>
  );
}
