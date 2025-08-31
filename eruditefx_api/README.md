# EruditeFX API (FastAPI)

API para gerar análise completa de Forex no formato EruditeFX, incluindo:
- Contexto de mercado
- Zonas de liquidação e institucionais
- 3 setups (entrada, SL, TP, RR, % de sucesso) com **checklist** em sistema de **cores (VERDE/AMARELO/VERMELHO)**
- Notícias relevantes com hora de Lisboa, direção prevista (↑/↓/Volátil) e **Sinal (par)** BUY/SELL
- Imagem com **retângulos de contorno** (sem preenchimento) e linhas de liquidez
- Exportação para **PDF** no template aprovado

## Arranque rápido

```bash
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
# Abrir: http://localhost:8000/docs
```

## Exemplo de request

```bash
curl -X POST "http://localhost:8000/api/v1/eruditefx/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "instrumento": "EUR/USD",
    "timeframe": "5M",
    "tipo_setup": "Scalp",
    "gerar_imagem": true,
    "gerar_pdf": true,
    "chart_image_b64": null
  }'
```

A resposta inclui `image_url` e `pdf_url` servidos em `/outputs`.


## Integração com Provider de Notícias Real

Pode usar a API da TradingEconomics para notícias macroeconómicas.

1. Criar conta em [https://developer.tradingeconomics.com/](https://developer.tradingeconomics.com/)
2. Obter `API_KEY` e `API_SECRET`
3. Criar arquivo `.env` no diretório raiz:
   ```bash
   cp .env.example .env
   nano .env
   ```
4. Preencher os valores:
   ```
   NEWS_PROVIDER=tradingeconomics
   TE_API_KEY=seu_key
   TE_API_SECRET=seu_secret
   ```

Ao iniciar o backend, ele usará automaticamente o provider da TradingEconomics.


## Exemplo de consumo SSE em React
```jsx
import { useEffect } from "react";

function useEruditeFXStream(requestBody) {
  useEffect(() => {
    const evtSource = new EventSource("/api/v1/eruditefx/analyze-stream?provider=auto", {
      withCredentials: false
    });
    evtSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("Progresso:", data.step, data);
    };
    evtSource.onerror = (err) => {
      console.error("Erro SSE:", err);
      evtSource.close();
    };
    return () => evtSource.close();
  }, [requestBody]);
}
```


## Provider de notícias (default = TradingEconomics)
Por omissão, o backend tenta usar o **TradingEconomicsNewsProvider** (`provider=te`). Podes trocar para o estático via query.

### POST (JSON) com provider por query
```
POST /api/v1/eruditefx/analyze?provider=static
```

### SSE GET (compatível com EventSource)
```
GET /api/v1/eruditefx/analyze-stream?instrumento=EUR/USD&timeframe=5M&tipo_setup=Scalp&gerar_imagem=true&gerar_pdf=true&provider=te
```
