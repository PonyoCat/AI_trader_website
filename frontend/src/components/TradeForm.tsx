import { useState } from "react";
import { buy, sell } from "../lib/api";

export default function TradeForm() {
  const [symbol, setSymbol] = useState("AAPL");
  const [qty, setQty] = useState(1);
  const [loading, setLoading] = useState<null | "Buy" | "Sell">(null);

  async function doBuy() {
    setLoading("Buy");
    try {
      const res: any = await buy(symbol.trim(), qty);
      const oid = res?.orderId ?? res?.order_id ?? "(ukendt id)";
      alert(`Købsordre sendt. ID: ${oid}`);
    } catch (e: any) {
      alert(`Fejl ved køb: ${e.message}`);
    } finally {
      setLoading(null);
    }
  }

  async function doSell() {
    setLoading("Sell");
    try {
      const res: any = await sell(symbol.trim(), qty);
      const oid = res?.orderId ?? res?.order_id ?? "(ukendt id)";
      alert(`Salgsordre sendt. ID: ${oid}`);
    } catch (e: any) {
      alert(`Fejl ved salg: ${e.message}`);
    } finally {
      setLoading(null);
    }
  }

  return (
    <div style={{ display: "grid", gap: 8, maxWidth: 420 }}>
      <label>
        Symbol
        <input
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          placeholder="AAPL"
          className="border rounded px-2 py-1 w-full"
        />
      </label>
      <label>
        Antal
        <input
          type="number"
          min={1}
          value={qty}
          onChange={(e) => setQty(Math.max(1, Number(e.target.value)))}
          className="border rounded px-2 py-1 w-full"
        />
      </label>
      <div style={{ display: "flex", gap: 8 }}>
        <button disabled={loading !== null} onClick={doBuy} className="px-3 py-2 rounded border">
          {loading === "Buy" ? "Køber…" : "Køb"}
        </button>
        <button disabled={loading !== null} onClick={doSell} className="px-3 py-2 rounded border">
          {loading === "Sell" ? "Sælger…" : "Sælg"}
        </button>
      </div>
    </div>
  );
}
