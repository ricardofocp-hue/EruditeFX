import React, { useEffect, useState } from "react";

/**
 * Props:
 * - baseUrl (ex.: "http://localhost:8000")
 * - instrumento (ex.: "EUR/USD")
 * - timeframe (ex.: "5M")
 * - tipoSetup (ex.: "Scalp" | "Intradia" | "Swing")
 * - gerarImagem (boolean)
 * - gerarPdf (boolean)
 * - provider ("te" | "static")
 */
export default function SSEViewer({
  baseUrl,
  instrumento,
  timeframe,
  tipoSetup,
  gerarImagem = true,
  gerarPdf = true,
  provider = "te",
}) {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const params = new URLSearchParams({
      instrumento,
      timeframe,
      tipo_setup: tipoSetup,
      gerar_imagem: String(gerarImagem),
      gerar_pdf: String(gerarPdf),
      provider,
    });
    const url = `${baseUrl}/api/v1/eruditefx/analyze-stream?${params.toString()}`;

    const es = new EventSource(url);
    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        setEvents((prev) => [...prev, data]);
      } catch (err) {
        console.error("SSE parse error:", err);
      }
    };
    es.onerror = (e) => {
      console.error("SSE error:", e);
      es.close();
    };
    return () => es.close();
  }, [baseUrl, instrumento, timeframe, tipoSetup, gerarImagem, gerarPdf, provider]);

  return (
    <div style={{fontFamily: "Inter, system-ui", lineHeight: 1.4}}>
      <h3>EruditeFX – Stream</h3>
      <ol>
        {events.map((ev, i) => (
          <li key={i}>
            <pre style={{whiteSpace: "pre-wrap"}}>{JSON.stringify(ev, null, 2)}</pre>
          </li>
        ))}
      </ol>
    </div>
  );
}
