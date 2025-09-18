import { useEffect, useRef, useState } from "react";
import { buy, sell } from "../lib/api";

type Action = "manage" | "research";
type ModelOpt = "gemini-2.5-flash" | "gpt-5" | "gpt-5-mini" | "gpt-5-nano";

export default function APITrader() {
  // STATE
  const [model, setModel] = useState<ModelOpt>("gpt-5");                // ✅ flyttet ind i komponenten
  const [autoPlaceOrder, setAutoPlaceOrder] = useState(
    localStorage.getItem("autoPlace") === "1"
  );
  const [busy, setBusy] = useState<"" | Action>("");
  const [log, setLog] = useState<string[]>([]);
  const boxRef = useRef<HTMLDivElement>(null);

  const add = (m: string) =>
    setLog((x) => [...x, `[${new Date().toLocaleTimeString()}] ${m}`]);
  // inde i APITrader-komponenten:

  const MAX_JSON = 1500; // beskær lange svar for at holde UI snappy
  const addJSON = (label: string, obj: unknown) => {
    try {
      const s = JSON.stringify(obj as any, null, 2);
      const body = s.length > MAX_JSON ? s.slice(0, MAX_JSON) + "\n... (truncated)" : s;
      add(`${label}:\n${body}`);
    } catch {
      add(`${label}: [kunne ikke serialisere JSON]`);
    }
  };


async function run(kind: Action) {
  if (busy) return;
  setBusy(kind);
  add(`Starter ${kind === "manage" ? "Manage positioner" : "Deep Research"}...`);
  try {
    const res = await callBackend(kind);
    add("AI svar modtaget.");
    addJSON("AI svar", res);                // ⬅️ log AI-svaret
    const orders = Array.isArray(res?.orders) ? res.orders : [];
    if (orders.length) add(`Fandt ${orders.length} ordre(r).`);

    add(`${kind === "manage" ? "Manage positioner" : "Deep Research"} færdig.`);
    autoPlaceOrder ? await place(orders) : add("Auto ordreplacering er slukket.");
  } catch (e: any) {
    add(`Fejl: ${e.message || e}`);
  } finally {
    setBusy("");
  }
}


  async function callBackend(kind: Action) {
    const url =
      (import.meta.env.VITE_API_BASE || "") +
      (kind === "manage" ? "/auto/manage" : "/auto/research");
    try {
      const r = await fetch(url, { method: "POST", credentials: "include" });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return await r.json().catch(() => ({}));
    } catch {
      // simpel fallback / demo
      return kind === "research"
        ? { orders: [{ symbol: "AAPL", side: "Buy", quantity: 1 }] }
        : { orders: [{ symbol: "AAPL", side: "Sell", quantity: 1 }] };
    }
  }

  async function place(orders: any[]) {
    if (!orders.length) return add("Ingen ordrer fundet.");
    add(`Placerer ${orders.length} ordre(r)...`);
    for (const o of orders) {
      const sym = String(o.symbol || o.ticker || "").toUpperCase();
      const qty = Math.max(1, Math.trunc(o.quantity || 1));
      try {
        const resp =
          String(o.side).toLowerCase().startsWith("s")
            ? await sell(sym, qty)
            : await buy(sym, qty);
        const id = (resp as any)?.order_id || (resp as any)?.id || "?";
        const st = (resp as any)?.status || "";
        add(`${o.side || "Buy"} ${sym} x${qty} placeret. ID: ${id}${st ? ` · ${st}` : ""}`);
      } catch (e: any) {
        add(`Ordrefejl ${sym}: ${e.message || e}`);
      }
    }
    add("Ordreplacering færdig.");
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12, minHeight: "70vh" }}>
      <div className="panel" style={{ flex: 1, minHeight: 0, display: "grid", gridTemplateRows: "auto auto 1fr", gap: 12 }}>
        <h3 style={{ margin: 0 }}>Auto trade</h3>

        {/* Actions-række */}
        <div className="actions flush-x" style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
          {/* Model dropdown */}
          <label style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
            Model:
            <select
              value={model}
              onChange={(e) => setModel(e.target.value as ModelOpt)}
              style={{ padding: "6px 10px", borderRadius: 8, border: "1px solid #e5e7eb" }}
            >
              <option value="gemini-2.5-flash">Gemini 2.5-Flash</option>
              <option value="gpt-5">GPT-5</option>
              <option value="gpt-5-mini">GPT-5 mini</option>
              <option value="gpt-5-nano">GPT-5 nano</option>
            </select>
          </label>

          <button onClick={() => run("manage")} disabled={!!busy}>
            {busy === "manage" ? "Kører..." : "Manage positioner"}
          </button>
          <button onClick={() => run("research")} disabled={!!busy}>
            {busy === "research" ? "Kører..." : "Deep Research"}
          </button>

          <label style={{ display: "inline-flex", alignItems: "center", gap: 8, marginLeft: 8 }}>
            <input
              type="checkbox"
              checked={autoPlaceOrder}
              onChange={(e) => {
                const v = e.target.checked;
                setAutoPlaceOrder(v);                           // ✅ brug korrekt setter
                localStorage.setItem("autoPlace", v ? "1" : "0");
              }}
            />
            Placer ordrer automatisk
          </label>

          <button style={{ marginLeft: "auto" }} onClick={() => setLog([])}>Ryd konsol</button>
        </div>

        {/* Konsol (uændret) */}
        <div
          ref={boxRef}
          style={{
            border: "1px solid #e5e7eb",
            borderRadius: 12,
            padding: 12,
            minHeight: 0,
            overflow: "auto",
            fontFamily: "ui-monospace, Menlo, Consolas, monospace",
            fontSize: 13,
            background: "#0b0d10",
            color: "#d1d5db",
            whiteSpace: "pre-wrap",
          }}
        >
          {log.length ? log.map((l, i) => <div key={i}>{l}</div>) : <div style={{ opacity: 0.8 }}>Klar.</div>}
        </div>
      </div>
    </div>
  );
}
