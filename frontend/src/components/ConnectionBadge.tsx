import { useEffect, useState } from "react";
import { fetchPositions } from "../lib/api";

export default function ConnectionBadge() {
  const [connected, setConnected] = useState<null | boolean>(null);

  useEffect(() => {
    // Simpel check: hvis /positions virker, er der en gyldig session
    fetchPositions()
      .then(() => setConnected(true))
      .catch(() => setConnected(false));
  }, []);

  if (connected === null) return <span>Checker forbindelse…</span>;
  return connected ? (
    <span style={{ color: "green" }}>Forbundet</span>
  ) : (
    <span style={{ color: "crimson" }}>Ikke forbundet</span>
  );
}
