import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid } from "recharts";
import { fetchPerformance, type PerformancePoint } from "../lib/api";

export default function PerformanceChart({}: { name: string }) {
  const [data, setData] = useState<PerformancePoint[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Henter performance data. Viser fallback hvis endpoint ikke findes
  useEffect(() => {
    let mounted = true;
    fetchPerformance()
      .then(d => {
        if (!mounted) return;
        setData(d);
        setLoading(false);
      })
      .catch(() => {
        if (!mounted) return;
        // Fallback eksempeldata hvis backend ikke er klar
        const demo: PerformancePoint[] = [
          { date: "2025-09-01", ai: 0, sp500: 0 },
          { date: "2025-09-02", ai: 0.4, sp500: 0.2 },
          { date: "2025-09-03", ai: 0.7, sp500: 0.5 },
          { date: "2025-09-04", ai: -0.2, sp500: 0.1 },
          { date: "2025-09-05", ai: 1.1, sp500: 0.8 },
        ];
        setData(demo);
        setLoading(false);
        setErr(null);
      });
    return () => { mounted = false; };
  }, []);

  if (loading) return <p>Henter performance…</p>;
  if (err) return <p style={{ color: "crimson" }}>Fejl: {err}</p>;

  // Formatter akser som pct
  const pct = (v: number) => `${v.toFixed(2)}%`;

  return (
    <div style={{ display: "grid", gap: 8 }}>
      {/* Hilsen over grafen */}
      <h3 style={{ margin: 0 }}></h3>
      <div style={{ width: "100%", height: 300 }}>
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 8, right: 12, bottom: 44, left: 8 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tickMargin={8} />
            <YAxis tickFormatter={(v) => pct(Number(v))} tickMargin={8} />
            <Tooltip formatter={(v) => pct(Number(v))} labelFormatter={(l) => `Date: ${l}`} />
            <Legend verticalAlign="bottom" height={28} />
            <Line type="monotone" dataKey="ai" name="AI Trader" dot={false} />
            <Line type="monotone" dataKey="sp500" name="S&P 500" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
