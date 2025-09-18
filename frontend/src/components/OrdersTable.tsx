import { useEffect, useState } from "react";
import { fetchOpenOrders } from "../lib/api";

type Order = {
  id: string;
  symbol: string;
  side: "Buy" | "Sell";
  quantity: number;
  status: string;
  orderType?: string;
  createdAt?: string;
};

export default function OrdersTable() {
  const [rows, setRows] = useState<Order[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    setErr(null);
    try {
      const data = await fetchOpenOrders();
      // Sikrer id feltet selv hvis backend returnerer orderId
      const normalized = data.map((o: any) => ({
        id: o.id ?? o.orderId ?? o.order_id ?? "",
        symbol: o.symbol,
        side: o.side,
        quantity: o.quantity,
        status: o.status,
        orderType: o.orderType ?? o.order_type,
        createdAt: o.createdAt ?? o.created_at,
      })) as Order[];
      setRows(normalized);
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (loading) return <p>Henter åbne ordrer…</p>;
  if (err) return <p style={{ color: "crimson" }}>Fejl: {err}</p>;
  if (!rows.length) return <p>Ingen åbne ordrer.</p>;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
        <h3></h3>
        <button onClick={load} className="px-2 py-1 rounded border">Opdater</button>
      </div>
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="border p-2 text-left">ID</th>
            <th className="border p-2 text-left">Symbol</th>
            <th className="border p-2 text-left">Side</th>
            <th className="border p-2 text-right">Antal</th>
            <th className="border p-2 text-left">Status</th>
            <th className="border p-2 text-left">Type</th>
            <th className="border p-2 text-left">Oprettet</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td className="border p-2">{r.id}</td>
              <td className="border p-2">{r.symbol}</td>
              <td className="border p-2">{r.side}</td>
              <td className="border p-2 text-right">{r.quantity}</td>
              <td className="border p-2">{r.status}</td>
              <td className="border p-2">{r.orderType ?? "-"}</td>
              <td className="border p-2">{r.createdAt ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
