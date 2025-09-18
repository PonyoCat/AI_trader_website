// src/components/LoginButton.tsx
import { API_BASE } from "../lib/api";

export default function LoginButton() {
  async function handleLogin() {
    try {
      const next = window.location.origin; // frontend vender tilbage hertil
      window.location.href = `${API_BASE}/auth/login?next=${encodeURIComponent(next)}`;
    } catch (e) {
      console.error(e);
      alert("Kunne ikke starte login.");
    }
  }

  return (
    <button onClick={handleLogin} className="px-3 py-2 rounded border">
      Connect Saxo
    </button>
  );
}
