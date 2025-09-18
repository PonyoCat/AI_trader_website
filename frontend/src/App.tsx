// src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import AppLayout from "./layouts/AppLayout";
import AuthGate from "./components/AuthGate";

// Sider
import Home from "./pages/Home";
import ManualTrade from "./pages/ManualTrader";
import AutoTrade from "./pages/APITrader";
import Profile from "./pages/Profile";
import Disclaimer from "./pages/Disclaimer";
import Guide from "./pages/Guide"; 

export default function App() {
  return (
    <BrowserRouter>
      <AppLayout>
        <Routes>
          <Route
            path="/"
            element={
              <AuthGate>
                <Home />
              </AuthGate>
            }
          />
          <Route
            path="/manuel"
            element={
              <AuthGate>
                <ManualTrade />
              </AuthGate>
            }
          />
          <Route
            path="/auto"
            element={
              <AuthGate>
                <AutoTrade />
              </AuthGate>
            }
          />
          <Route
            path="/profil"
            element={
              <AuthGate>
                <Profile />
              </AuthGate>
            }
          />
          <Route 
          path="/guide" 
          element={
              <AuthGate>
                <Guide />
              </AuthGate>} 
          />
          {/* Offentlig side */}
          <Route path="/disclaimer" element={<Disclaimer />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>

      </AppLayout>
    </BrowserRouter>
  );
}
