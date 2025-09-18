// src/layouts/AppLayout.tsx
import { type ReactNode } from "react";
import { APP_NAME } from "../config";
import NavBar from "../components/NavigationBar";
import ConnectionBadge from "../components/ConnectionBadge";
import LoginButton from "../components/LoginButton";
import Footer from "../components/Footer";

export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-container" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 100 }}>
          <h2 style={{ margin: 0 }}>{APP_NAME}</h2>
          <NavBar />
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <ConnectionBadge />
            <LoginButton />
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="app-container">
          {children}
        </div>
      </main>

      {/* Footer fast i bunden via flex layout */}
      <Footer />
    </div>
  );
}

