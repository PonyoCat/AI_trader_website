// src/components/Footer.tsx
import { Link } from "react-router-dom";
import { COPYRIGHT_OWNER } from "../config";

export default function Footer() {
  return (
    <footer style={{ borderTop: "1px solid #e5e7eb", padding: "12px 16px", marginTop: 24 }}>
      <div
        style={{
          maxWidth: 1100,
          margin: "0 auto",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: 12,
        }}
      >
        <small>© {new Date().getFullYear()} {COPYRIGHT_OWNER}</small>

        <div style={{ textAlign: "right" }}>
          {/* Kort risikotekst i footer */}
          <div style={{ fontSize: 12, opacity: 0.9, marginBottom: 6 }}>
            Trading involves risk. This site is not investment advice. Read our Disclaimer.
          </div>

          {/* Link til side med fuld disclaimer */}
          <Link to="/disclaimer" style={{ textDecoration: "underline" }}>
            Read full Disclaimer
          </Link>
        </div>
      </div>
    </footer>
  );
}
