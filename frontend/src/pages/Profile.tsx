import { useEffect, useState } from "react";
import { fetchAuthStatus, type AuthStatus } from "../lib/api";

export default function Profile() {
  const [data, setData] = useState<AuthStatus | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetchAuthStatus()
      .then(setData)
      .catch((e: any) => setErr(e.message ?? "Ukendt fejl"));
  }, []);

  if (err) return <p style={{ color: "crimson" }}>Fejl: {err}</p>;
  if (!data) return <p>Henter profil…</p>;

  return (
    <div style={{ display: "grid", gap: 12 }}>
      <h3 style={{ marginTop: 0 }}>Profil</h3>
      <div>
        <div><strong>Status:</strong> {data.connected ? "Forbundet" : "Ikke forbundet"}</div>
        <div><strong>Broker:</strong> {data.broker ? `${data.broker.name} (${data.broker.id})` : "-"}</div>
        <div><strong>AccountKey:</strong> {data.account_key ?? "-"}</div>
      </div>
      {/* Knapper til logout eller udskift broker kan tilføjes her senere */}
    </div>
  );
}
