// src/pages/Home.tsx
import { useEffect, useState } from "react";
import PerformanceChart from "../components/PerformanceChart";
import OrdersTable from "../components/OrdersTable";
import PositionsTable from "../components/PositionsTable";
import { fetchAuthStatus, type AuthStatus } from "../lib/api";

export default function Home() {
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const res = await fetchAuthStatus();
        if (alive) setAuth(res);
      } catch {
        if (alive) setAuth(null);
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  const name: string | null = auth?.fullName ?? auth?.name ?? null;

  const gridStyle: React.CSSProperties = {
    display: "grid",
    gridTemplateColumns: "1.5fr 1fr",      // venstre lidt bredere end højre
    gridTemplateRows: "auto 1fr",          // øverste række efter indhold, nederste fylder resten
    gridTemplateAreas: `
      "chart status"
      "orders positions"
    `,
    columnGap: 16,
    rowGap: 8,
    alignItems: "stretch",                 // VIGTIGT: få boksene til at fylde hele rækken
    minWidth: 0,
    minHeight: "60vh",                     // lidt højde så man kan se effekten (tilpas evt.)
  };

  return (
    <div style={{ display: "grid", gap: 8 }}>
      <header style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between" }}>
        <h2 style={{ margin: 0 }}>{name ? `Hej ${name}` : "Hej Trader"}</h2>
        {!loading && (
          <small style={{ opacity: 0.8 }}>
            {auth?.connected ? "Forbundet" : "Ikke forbundet"}
          </small>
        )}
      </header>

      <div style={gridStyle}>
        {/* Performance */}
        <section
          style={{
            gridArea: "chart",
            border: "1px solid #e5e7eb",
            borderRadius: 12,
            padding: 12,
            height: "100%",                  // fyld hele grid-arealet
            display: "flex",
            flexDirection: "column",
            minHeight: 0,
          }}
        >
          <h4 style={{ margin: 0 }}>Performance</h4>
          <div style={{ flex: 1, minHeight: 0 }}>
            {/* Hvis PerformanceChart er ResponsiveContainer-baseret, vil den nu fylde */}
            <PerformanceChart name={name ?? "Trader"} />
          </div>
        </section>

        {/* Status */}
        <aside
          style={{
            gridArea: "status",
            border: "1px solid #e5e7eb",
            borderRadius: 12,
            padding: 12,
            height: "100%",
            display: "flex",
            flexDirection: "column",
            minHeight: 0,
          }}
        >
          <h4 style={{ margin: 0 }}>Status</h4>
          <div style={{ flex: 1, minHeight: 0 }}>
            {loading ? (
              <p style={{ margin: 0 }}>Henter...</p>
            ) : auth?.connected ? (
              <ul style={{ margin: "8px 0 0 16px" }}>
                <li>Forbindelse: aktiv</li>
                <li>Brugernavn: {name ?? "ukendt"}</li>
              </ul>
            ) : (
              <p style={{ margin: 0 }}>Ikke forbundet</p>
            )}
          </div>
        </aside>

        {/* Aktive ordrer */}
        <section
          style={{
            gridArea: "orders",
            border: "1px solid #e5e7eb",
            borderRadius: 12,
            padding: 12,
            height: "100%",
            display: "flex",
            flexDirection: "column",
            minHeight: 0,
          }}
        >
          <h4 style={{ margin: 0, fontSize: 18 }}>Aktive ordrer</h4>
          <div style={{ flex: 1, minHeight: 0, overflow: "auto" }}>
            <OrdersTable />
          </div>
        </section>

        {/* Positioner */}
        <section
          style={{
            gridArea: "positions",
            border: "1px solid #e5e7eb",
            borderRadius: 12,
            padding: 12,
            height: "100%",
            display: "flex",
            flexDirection: "column",
            minHeight: 0,
          }}
        >
          <h4 style={{ margin: 0, fontSize: 18 }}>Positioner</h4>
          <div style={{ flex: 1, minHeight: 0, overflow: "auto" }}>
            <PositionsTable />
          </div>
        </section>
      </div>
    </div>
  );
}
