import { useEffect, useState, type ReactNode } from "react";
import { fetchPositions } from "../lib/api";
import LoginButton from "./LoginButton";

export default function AuthGate({ children }: { children: ReactNode }) {
  const [state, setState] = useState<"checking"|"authed"|"anon">("checking");

  useEffect(() => {
    fetchPositions()
      .then(() => setState("authed"))
      .catch((e) => setState(e.message === "UNAUTHENTICATED" ? "anon" : "anon"));
  }, []);

  if (state === "checking") return <p>Checker session…</p>;
  if (state === "anon") {
    return (
      <div style={{ display: "grid", gap: 12, placeItems: "start" }}>
        <p>Ikke logget ind.</p>
        <LoginButton />
      </div>
    );
  }
  return <>{children}</>;
}
