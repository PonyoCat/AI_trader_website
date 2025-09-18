import { useEffect, useState } from "react";
import { fetchPositions } from "../lib/api";

type Position = {
  symbol: string;
  quantity: number;
  avgPrice?: number;
  marketValue?: number;
  currency?: string;
};

export default function PositionsTable() {
  const [rows, setRows] = useState<Position[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    setErr(null);
    try {
      const data = await fetchPositions();
      setRows(data);
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (loading) return <p>Henter positioner…</p>;
  if (err) return <p style={{ color: "crimson" }}>Fejl: {err}</p>;
  if (!rows.length) return <p>Ingen positioner.</p>;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
        <h3></h3>
        <button onClick={load} className="px-2 py-1 rounded border">Opdater</button>
      </div>
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="border p-2 text-left">Symbol</th>
            <th className="border p-2 text-right">Antal</th>
            <th className="border p-2 text-right">Gns. pris</th>
            <th className="border p-2 text-right">Markedsværdi</th>
            <th className="border p-2 text-left">Valuta</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              <td className="border p-2">{r.symbol}</td>
              <td className="border p-2 text-right">{r.quantity}</td>
              <td className="border p-2 text-right">{r.avgPrice?.toFixed(2) ?? "-"}</td>
              <td className="border p-2 text-right">{r.marketValue?.toFixed(2) ?? "-"}</td>
              <td className="border p-2">{r.currency ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
