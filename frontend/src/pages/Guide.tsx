
const PRICES: Array<[model: string, input: string, cached: string, output: string]> = [
  ["Gemini 2.5-Flash", "Gratis", "Gratis", "Gratis"],
  ["GPT-5", "1.25", "0.13", "10.00"],
  ["GPT-5 mini", "0.25", "0.03", "2.00"],
  ["GPT-5 nano", "0.05", "0.01", "0.40"],
];

export default function Guide() {
  return (
    <div className="panel" style={{ padding: 12, border: "1px solid #e5e7eb", borderRadius: 12 }}>
        <h3 style={{ margin: 0 }}>Overordnet</h3>
        <p style={{ marginTop: 8 }}>Dette program gør brug af AI til at researche og skabe et lille portfolie inden for Micro Cap Aktier.
        <br />Det er ment som et ekspiriment for at se hvordan den vil klare sig, og intet er finansiel rådgivning. Se disclaimeren.
        </p>
        <h3 style={{ margin: 0 }}>Manuel version</h3>
        <p style={{ marginTop: 8 }}>
        Den manuelle version er designet som et gratis alternativ for API versionen, og har kun support for ChatGPT.
        <br />
        Placeholder:
        <img
          src="/AI_Cat.png"                // fil i public/
          alt="Eksempel/illustration"
          style={{ display: "block", marginTop: 8, maxWidth: "100%", borderRadius: 8 }}
        />
        <br />
        {/* Trinliste med indlejrede a/b punkter */}
        <ol style={{ paddingLeft: 24, marginTop: 12, lineHeight: 1.6 }}>
          <li>Vælg en model (jeg foreslår GPT-5).</li>
          <li>
            Vælg hvad AI'en skal gøre:
            <ol type="a" style={{ paddingLeft: 18, marginTop: 2, marginBottom: 2 }}>
              <li><strong>Administrér positioner:</strong> Kigger på ny data og nyheder for eksisterende positioner.</li>
              <li><strong>Deep Research:</strong> Finder nye potentielle micro cap aktier at investere i.</li>
            </ol>
          </li>
          <li>Klik på "Prompt i ChatGPT" knappen eller kopier prompten og indsæt i ChatGPT.</li>
          <li>Kopier ChatGPT's svar på teksten med knappen "Importér JSON fra clipboard"</li>
          <li>Klik på knappen placer ordrer ud fra svar eller gør det manuelt</li>
          <li>Gem svar i systemet så ChatGPT kan itere på det til næste gang</li>
          <li>Når din chat bliver for lang (En lang chat kan gøre den begyndere at hallucinere mere)<br /> så kan du placere din chat i et projekt, og få den til at opsumere chatten</li>
        </ol>
        </p>
        <h3 style={{ margin: 0 }}>Automatisk version (ved brug af API)</h3>
        <p style={{ marginTop: 8 }}>
        Den automatiske version gør brug af en AI API til automatiske at prompte og researche. Jeg ville foreslå GPT-5. 
        <br />
        Placeholder:
        <img
          src="/AI_Cat.png"                // fil i public/
          alt="Eksempel/illustration"
          style={{ display: "block", marginTop: 8, maxWidth: "100%", borderRadius: 8 }}
        />
        <br />
        1. Vælg en model (Gemini 2.5 Flash er gratis, se modeller*)        <br />
        2. Klik på "Promp" knappen      <br />
        3. Indtast manuelt positioner
        </p>
        <h3 style={{ margin: 0, marginTop: 24 }}>Modeller*</h3>

        <p style={{ marginTop: -8 }}>
          (Priser er i dollars$ og pr 1 million tokens ca. 750000 ord, updateret: 11/09/2025)
        </p>


    <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 8 }}>
      <thead>
        <tr>
          <th style={{ textAlign: "left", padding: "6px 10px" }}>Model</th>
          <th style={{ textAlign: "right", padding: "6px 10px", borderLeft: "1px solid #e5e7eb" }}>Input</th>
          <th style={{ textAlign: "right", padding: "6px 10px", borderLeft: "1px solid #e5e7eb" }}>Cached input</th>
          <th style={{ textAlign: "right", padding: "6px 10px", borderLeft: "1px solid #e5e7eb" }}>Output</th>
        </tr>
      </thead>
      <tbody>
        {PRICES.map(([model, input, cached, output]) => (
          <tr key={model}>
            <td style={{ padding: "6px 10px", borderTop: "1px solid #e5e7eb" }}>{model}</td>
            <td style={{ padding: "6px 10px", textAlign: "right", borderTop: "1px solid #e5e7eb", borderLeft: "1px solid #e5e7eb" }}>{input}</td>
            <td style={{ padding: "6px 10px", textAlign: "right", borderTop: "1px solid #e5e7eb", borderLeft: "1px solid #e5e7eb" }}>{cached}</td>
            <td style={{ padding: "6px 10px", textAlign: "right", borderTop: "1px solid #e5e7eb", borderLeft: "1px solid #e5e7eb" }}>{output}</td>
          </tr>
        ))}
      </tbody>
    </table>
    </div>
  );
}