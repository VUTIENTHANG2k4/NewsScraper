import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import NewsFeed from "./pages/NewsFeed";
import Dashboard from "./pages/Dashboard";
import AddSource from "./pages/AddSource";

export default function App() {
  return (
    <div className="app-shell">
      <Navbar />

      <main className="container">
        <Routes>
          <Route path="/" element={<NewsFeed />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/them-nguon" element={<AddSource />} />
        </Routes>
      </main>
    </div>
  );
}
