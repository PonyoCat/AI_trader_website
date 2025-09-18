import { NavLink } from "react-router-dom";

function linkStyle({ isActive }: { isActive: boolean }): React.CSSProperties {
  return {
    display: "flex",        // gør ankeret til en flex-container
    alignItems: "center",
    justifyContent: "center",      // centrer indholdet vandret
    textAlign: "center",           // hvis teksten wrap’er
    whiteSpace: "nowrap",          // fjern hvis linjeskift ønskes
    fontSize: 20,                  // ← ændrer tekststørrelsen
    fontFamily: "'Inconsolata', monospace", // brug monospace font

    padding: "12px 20px",
    minWidth: 215,                 // gør knappen længere og ensartet
    borderRadius: 12,
    textDecoration: "none",
    fontWeight: 500,
    border: "1px solid #e5e7eb",
    background: isActive ? "#f3f4f6" : "transparent",
    
  };
}


export default function NavBar() {
  return (
    <nav className="nav" style={{ display: "flex", gap: 20, transform: "translateX(+16px)"}}>
      <NavLink to="/" style={linkStyle} end>Hjem</NavLink>
      <NavLink to="/guide" style={linkStyle}>Guide</NavLink>
      <NavLink to="/manuel" style={linkStyle}>Manuel</NavLink>
      <NavLink to="/auto" style={linkStyle}>Auto</NavLink>
      <NavLink to="/profil" style={linkStyle}>Profil</NavLink>
    </nav>
  );
}
