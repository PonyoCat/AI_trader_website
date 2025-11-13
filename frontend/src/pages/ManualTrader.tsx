// src/pages/ManualTrader.tsx
import { useEffect, useMemo, useState} from "react";
import { useSearchParams } from "react-router-dom";
import { buy, sell, type PlaceOrderResponse } from "../lib/api";
import { CONTEXT_PROMPT, MANAGE_PROMPT, RESEARCH_PROMPT } from "src/lib/prompts";

const AI_CONTEXT = CONTEXT_PROMPT;
const MANAGE_POSITIONS_PROMPT = MANAGE_PROMPT;
const DEEPRESEARCH_STOCKS_PROMPT = RESEARCH_PROMPT;

type ModelOpt = "gpt-5" | "gpt-4o" | "gpt-4o-mini" | "gpt-3.5";
type Mode = "manage" | "research";
type OrderSideOpt = "Auto" | "Buy" | "Sell";


export default function ManualTrader() {
  const [searchParams] = useSearchParams();
  const [mode, setMode] = useState<Mode>("manage");

  // separate states → ingen navnekonflikt
  const [managePrompt, setManagePrompt] = useState<string>(MANAGE_POSITIONS_PROMPT);
  const [researchPrompt, setResearchPrompt] = useState<string>(DEEPRESEARCH_STOCKS_PROMPT);

  const [model, setModel] = useState<ModelOpt>("gpt-5");
  const [copied, setCopied] = useState(false);
  const [jsonPreview, setJsonPreview] = useState<any>(null);
  const [jsonError, setJsonError] = useState<string | null>(null);
  const [orderSide, setOrderSide] = useState<OrderSideOpt>("Auto");
  const [quantity, setQuantity] = useState<number>(1);
  const [placing, setPlacing] = useState(false);
  
  
  const effectiveSide = useMemo<"Buy" | "Sell">(() => {
  if (orderSide !== "Auto") return orderSide;
  const entry = Number((jsonPreview ?? {}).entry);
  const target = Number((jsonPreview ?? {}).target);
  if (Number.isFinite(entry) && Number.isFinite(target)) {
    return target >= entry ? "Buy" : "Sell";
  }
  return "Buy"; // fallback
}, [orderSide, jsonPreview]);
  
  // Læs ?mode=manage|research ved første render
  useEffect(() => {
    const m = searchParams.get("mode");
    if (m === "research" || m === "manage") setMode(m);
  }, [searchParams]);

  // Afhængig af valgt mode bruger vi det rigtige prompt + setter
  const currentPrompt = useMemo(
    () => (mode === "manage" ? managePrompt : researchPrompt),
    [mode, managePrompt, researchPrompt]
  );
  const setCurrentPrompt = mode === "manage" ? setManagePrompt : setResearchPrompt;

  async function copyToClipboard() {
    try {
      await navigator.clipboard.writeText(currentPrompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {
      alert("Kunne ikke kopiere. Marker og kopier manuelt.");
    }
  }

function openInChatGPT() {
  const url =
    "https://chatgpt.com/?" +
    new URLSearchParams({
      model,
      prompt: currentPrompt || "",
    }).toString();

  window.open(url, "_blank");
}

  // Strikt import (kan erstattes af tolerant version vi lavede tidligere)
  async function importFromClipboardJSON() {
    try {
      const clip = await navigator.clipboard.readText();
      try {
        const obj = JSON.parse(clip);
        setJsonPreview(obj);
        setJsonError(null);
      } catch {
        setJsonPreview(null);
        setJsonError("Teksten på clipboard er ikke gyldig JSON.");
      }
    } catch {
      alert("Kunne ikke læse fra clipboard. Indsæt manuelt.");
    }
  }

async function placeOrderFromJSON() {
  if (!jsonPreview) { alert("Importér gyldig JSON først."); return; }
  const tickerRaw = String(jsonPreview.ticker || "").trim();
  if (!tickerRaw) { alert("JSON mangler feltet 'ticker'."); return; }
  if (!Number.isFinite(quantity) || quantity <= 0) { alert("Ugyldigt antal."); return; }

  const symbol = tickerRaw.toUpperCase();
  setPlacing(true);
  try {
    const side = effectiveSide; // "Buy" | "Sell"
    const resp: PlaceOrderResponse =
      side === "Buy"
        ? await buy(symbol, Math.trunc(quantity))
        : await sell(symbol, Math.trunc(quantity));

    // Robust udtræk af id hvis backend skulle navngive anderledes
    const orderId =
      (resp as any)?.order_id ??
      (resp as any)?.OrderId ??
      (resp as any)?.id ??
      "(ukendt id)";
    const status = (resp as any)?.status ?? "Ukendt";

    alert(`Ordre placeret: ${side} ${symbol} x${Math.trunc(quantity)}\nID: ${orderId}\nStatus: ${status}`);
  } catch (err: any) {
    const msg = String(err?.message || err || "Ukendt fejl");
    if (msg.includes("401")) alert("Ikke logget ind. Forbind til broker under Profil.");
    else alert("Kunne ikke placere ordre: " + msg);
  } finally {
    setPlacing(false);
  }
}


  function validateCurrentJSON() {
    try {
      const obj = typeof jsonPreview === "string" ? JSON.parse(jsonPreview) : jsonPreview;
      const required = ["ticker", "setup", "entry", "stop", "target", "timeframe", "rationale", "confidence"];
      const missing = required.filter((k) => !(k in (obj || {})));
      if (missing.length) {
        setJsonError("Mangler nøgler: " + missing.join(", "));
        return;
      }
      if (typeof obj.confidence !== "number" || obj.confidence < 0 || obj.confidence > 1) {
        setJsonError("Feltet confidence skal være et tal i [0,1].");
        return;
      }
      setJsonError(null);
      alert("JSON ser gyldig ud.");
    } catch {
      setJsonError("JSON kunne ikke valideres.");
    }
  }

  function saveLaterStub() {
    console.log("Gem-mer senere:", jsonPreview);
    alert("Gem-funktion implementeres senere.");
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12, minHeight: "70vh" }}>
      <div className="panel" style={{ flex: 1, minHeight: 0, display: "grid", gridTemplateRows: "auto 1fr auto" }}>
        <h3 style={{ margin: 0 }}>ChatGPT prompt (JSON-only)</h3>

        {/* MIDTEN: kontroller + editor + preview */}
        <div style={{ display: "flex", flexDirection: "column", gap: 12, flex: 1, minHeight: 0 }}>
          {/* Mode tabs + model + prompt i ChatGPT */}
          <div className="flush-x" style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap", justifyContent: "space-between" }}>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <button
                onClick={() => setMode("manage")}
                style={{
                  padding: "6px 10px",
                  borderRadius: 8,
                  border: "1px solid var(--tab-border)",
                  background: mode === "manage" ? "var(--tab-active-bg)" : "transparent",
                }}
              >
                Administrér positioner
              </button>

              <button
                onClick={() => setMode("research")}
                style={{
                  padding: "6px 10px",
                  borderRadius: 8,
                  border: "1px solid var(--tab-border)",
                  background: mode === "research" ? "var(--tab-active-bg)" : "transparent",
                }}
              >
                Deep Research (aktier)
              </button>
            </div>


            <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
                Model:
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value as ModelOpt)}
                  style={{ padding: "6px 10px", borderRadius: 8, border: "1px solid #e5e7eb" }}
                >
                  <option value="gpt-5">GPT-5</option>
                  <option value="o4">GPT-4o</option>
                  <option value="o4-mini">o4-mini</option>
                </select>
              </label>
              <button onClick={openInChatGPT}>Prompt i ChatGPT</button>
            </div>
          </div>

          {/* Editor */}
          <div className="textbox" style={{ position: "relative", flex: 2, minHeight: 0 }}>
            <textarea
              value={currentPrompt}
              onChange={(e) => setCurrentPrompt(e.target.value)}
              style={{
                width: "100%",
                height: "100%",
                padding: "12px",
                paddingRight: 56,
                borderRadius: 12,
                border: "1px solid #e5e7eb",
                fontFamily: "inherit",
                fontSize: 14,
                lineHeight: 1.5,
                resize: "none",
              }}
              placeholder="Skriv eller indsæt prompt her..."
            />
            <button
              className="copy-btn"
              aria-label="Kopier tekst"
              title="Kopier"
              onClick={copyToClipboard}
              style={{
                position: "absolute",
                top: 8,
                right: 8,
                transform: "none",
                width: 40,
                height: 40,
                fontSize: 18,
                background: "transparent",
                border: "1px solid #e5e7eb",
                borderRadius: 10,
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
              }}
            >
              {copied ? "✓" : "📋"}
            </button>
          </div>

          {/* Import-knap over preview */}
          <div style={{ display: "flex", gap: 12, justifyContent: "flex-start", alignItems: "center" }}>
            <button onClick={importFromClipboardJSON}>Importér JSON fra clipboard</button>
          </div>

          {/* Preview */}
          <div style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 12, flex: 1, minHeight: 0, overflow: "auto" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <strong>Forhåndsvisning af JSON</strong>
              {jsonError && <span style={{ color: "crimson", fontSize: 13 }}>{jsonError}</span>}
            </div>
            <pre style={{ margin: 0, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
              {jsonPreview ? JSON.stringify(jsonPreview, null, 2) : "Ingen JSON importeret endnu."}
            </pre>
          </div>
        </div>

      {/* Actions nederst */}
      <div className="actions flush-x" style={{ justifyContent: "flex-start", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <button onClick={validateCurrentJSON} disabled={!jsonPreview}>Validér JSON</button>
        <button onClick={saveLaterStub} disabled={!jsonPreview}>Gem note (stub)</button>

        {/* Ordre-kontrol */}
        <div style={{ display: "inline-flex", alignItems: "center", gap: 10, marginLeft: 8 }}>
          <label style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
            Side:
            <select
              value={orderSide}
              onChange={(e) => setOrderSide(e.target.value as OrderSideOpt)}
              style={{ padding: "6px 10px", borderRadius: 8, border: "1px solid #e5e7eb" }}
            >
              <option value="Auto">Auto</option>
              <option value="Buy">Buy</option>
              <option value="Sell">Sell</option>
            </select>
          </label>

          <label style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
            Antal:
            <input
              type="number"
              min={1}
              step={1}
              value={quantity}
              onChange={(e) => setQuantity(parseInt(e.target.value, 10) || 1)}
              style={{ width: 90, padding: "6px 10px", borderRadius: 8, border: "1px solid #e5e7eb" }}
            />
          </label>

          <button onClick={placeOrderFromJSON} disabled={!jsonPreview || placing}>
            {placing ? "Sender..." : `Placer ordre (${effectiveSide})`}
          </button>
        </div>
      </div>
    </div>
  </div>
  );
}
