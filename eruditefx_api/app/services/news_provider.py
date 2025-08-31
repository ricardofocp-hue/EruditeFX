from __future__ import annotations
from typing import List, Dict
from datetime import datetime
from zoneinfo import ZoneInfo
import os

try:
    import httpx  # optional dependency for real providers
except Exception:
    httpx = None

class NewsProvider:
    def get_events(self, instrumento: str) -> List[Dict]:
        raise NotImplementedError

class StaticDemoNewsProvider(NewsProvider):
    """
    Provider de demonstração (sem chaves). Produz 3 eventos comuns.
    Os horários já vêm em Europe/Lisbon.
    """
    def get_events(self, instrumento: str) -> List[Dict]:
        today = datetime.now(ZoneInfo("Europe/Lisbon")).strftime("%Y-%m-%d")
        return [
            {
                "data_hora_lisboa": f"{today} 13:30",
                "evento": "US Core PCE Price Index (m/m)",
                "moeda": "USD",
                "impacto": "Alto",
                "direcao_prevista": "↑",
            },
            {
                "data_hora_lisboa": f"{today} 07:00",
                "evento": "DE CPI (m/m)",
                "moeda": "EUR",
                "impacto": "Médio",
                "direcao_prevista": "↑",
            },
            {
                "data_hora_lisboa": f"{today} 15:00",
                "evento": "US ISM Manufacturing PMI",
                "moeda": "USD",
                "impacto": "Médio",
                "direcao_prevista": "Volátil",
            },
        ]

class TradingEconomicsNewsProvider(NewsProvider):
    """
    Exemplo de provider real usando TradingEconomics Economic Calendar.
    Configure a variável de ambiente TRADINGECONOMICS_API_KEY="user:pass" (ou key única).
    Documentação: https://developer.tradingeconomics.com/
    NOTA: Esta implementação é simplificada e poderá requerer ajustes de endpoints/params conforme o plano.
    """
    BASE = "https://api.tradingeconomics.com/calendar"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("TRADINGECONOMICS_API_KEY")

    def get_events(self, instrumento: str) -> List[Dict]:
        if httpx is None or not self.api_key:
            return []
        # Derivar moedas do par
        pair = instrumento.replace("-", "/").upper()
        try:
            base, quote = [x.strip() for x in pair.split("/")]
        except Exception:
            base, quote = "EUR", "USD"
        currencies = [base, quote]

        today = datetime.now(ZoneInfo("Europe/Lisbon")).strftime("%Y-%m-%d")
        params = {"country": ",".join(currencies), "d1": today, "d2": today, "c": self.api_key, "format": "json"}
        try:
            with httpx.Client(timeout=10) as client:
                r = client.get(self.BASE, params=params)
                r.raise_for_status()
                data = r.json()
        except Exception:
            return []

        out: List[Dict] = []
        for ev in data if isinstance(data, list) else []:
            # Campos comuns (podem variar conforme API)
            dt_utc = ev.get("Date") or ev.get("DateUtc") or ev.get("DateISO") or ""
            # Converter para Lisboa se possível
            try:
                dt = datetime.fromisoformat(dt_utc.replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/Lisbon"))
                lis = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                lis = f"{today} 00:00"
            event = ev.get("Event") or ev.get("Category") or "Evento"
            currency = ev.get("Currency") or ev.get("Country") or ""
            importance = ev.get("Importance") or ev.get("Impact") or ""
            impact_map = {"Low": "Baixo", "Medium": "Médio", "High": "Alto"}
            impacto = impact_map.get(importance, "Médio")
            # Direção prevista muito simplificada (placeholder)
            forecast = ev.get("Forecast")
            previous = ev.get("Previous")
            direcao_prevista = "Volátil"
            if isinstance(forecast, (int, float)) and isinstance(previous, (int, float)):
                direcao_prevista = "↑" if forecast > previous else "↓"
            out.append({
                "data_hora_lisboa": lis,
                "evento": str(event),
                "moeda": str(currency)[:3] if currency else "",
                "impacto": impacto,
                "direcao_prevista": direcao_prevista,
            })
        return out
