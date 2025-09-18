// src/pages/OAuthCallback.tsx
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function OAuthCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    // Læs gemt retur-sted og naviger tilbage
    const after = window.localStorage.getItem("afterLogin") || "/";
    window.localStorage.removeItem("afterLogin");
    navigate(after, { replace: true });
  }, [navigate]);

  return <p>Logger ind...</p>;
}
