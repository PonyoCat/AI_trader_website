export const API_BASE =
  import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
    // Funktion der kalder backend API
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    // Returnerer 401 når ikke logget ind er forventet i flere views
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status} ${res.statusText} ${text}`.trim());
  }
  // Nogle endpoints kan returnere tomt body
  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) return {} as T;
  return (await res.json()) as T;
}

// Typer kan tilpasses backendens svar
export type Position = {
  symbol: string;
  quantity: number;
  avgPrice?: number;
  marketValue?: number;
};

export type PlaceOrderResponse = { order_id: string; status: string };

/*-----------------------------------------------------------------
//                                                               //
//  Connection og authentication funktioner                      //
//                                                               //
-----------------------------------------------------------------*/

export type AuthStatus = { // Data type for at se om man er connected og hvem man er connected med
  connected: boolean;
  broker?: { id: string; name: string };
  account_key?: string;
  name?: string;
  fullName?: string;
};

export async function fetchAuthStatus(): Promise<AuthStatus> { // Checker connection med backend
  return api<AuthStatus>("/auth/status");
}

export async function getLoginUrl(next?: string): Promise<string> {
    // Henter login URL fra backend
    // Forventet backend-svar: { "login_url": "https://..." }
  const qp = next ? `?next=${encodeURIComponent(next)}` : "";
  const data = await api<{ login_url: string }>(`/auth/login${qp}`);
  return data.login_url;
}

/*-----------------------------------------------------------------
//                                                               //
//  Henter data fra broker                                       //
//                                                               //
-----------------------------------------------------------------*/

// Performance data fra backend
export type PerformancePoint = {
  date: string;   // ISO dato fx "2025-09-01"
  ai: number;     // kumulativ pct afkast i hele tal eller decimal
  sp500: number;  // kumulativ pct afkast
};

export async function fetchPerformance(): Promise<PerformancePoint[]> {
  // Forventet backend rute: GET /analytics/performance
  // Eksempel svar: [{ "date":"2025-09-01","ai":1.2,"sp500":0.8 }, ...]
  return api<PerformancePoint[]>("/analytics/performance");
}


export async function fetchPositions(): Promise<Position[]> {
    // Henter åbne positioner for konto fra backend
    // Forventet backend-svar, normaliseret eksempel:
    // [ { "symbol": "AAPL", "quantity": 5, "avgPrice": 185.2, "marketValue": 926.0 } ]
  return await api<Position[]>("/positions");
}

export async function fetchOpenOrders(): Promise<Order[]> {
    // Henter åbne ordrer fra backend
    // Forventet backend-svar:
    // [ { "id":"abc", "symbol":"AAPL","side":"Buy","quantity":5,"status":"Placed"} ]
  return await api<Order[]>("/orders/open");
}

/*-----------------------------------------------------------------
//                                                               //
//  Kører vores backend funktioner på broker                     //
//                                                               //
-----------------------------------------------------------------*/

export type Order = { // Alt den data vi skal bruge for at sende en order igennem API
  id: string;
  symbol: string;
  side: "Buy" | "Sell";
  quantity: number;
  status: string;
  createdAt?: string;
};


export async function buy(symbol: string, quantity: number): Promise<PlaceOrderResponse> {
  return await api<PlaceOrderResponse>(`/trade/buy?symbol=${encodeURIComponent(symbol)}&quantity=${quantity}`, {
    method: "POST",
  });
}

export async function sell(symbol: string, quantity: number): Promise<PlaceOrderResponse> {
  return await api<PlaceOrderResponse>(`/trade/sell?symbol=${encodeURIComponent(symbol)}&quantity=${quantity}`, {
    method: "POST",
  });
}

