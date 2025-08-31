# Frontend Example (React + SSE)

Pequeno exemplo de componente React a consumir o endpoint SSE `GET /api/v1/eruditefx/analyze-stream` via **EventSource**.

## Uso rápido

Cola `SSEViewer.jsx` no teu projeto React e usa assim:

```jsx
<SSEViewer
  baseUrl={process.env.REACT_APP_API || "http://localhost:8000"}
  instrumento="EUR/USD"
  timeframe="5M"
  tipoSetup="Scalp"
  gerarImagem={true}
  gerarPdf={true}
  provider="te"
/>
```
