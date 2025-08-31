import hashlib
import random
from typing import List, Tuple
from .news_provider import NewsProvider, StaticDemoNewsProvider
from ..schemas import (
    Analise, Setup, ChecklistItem, ZonaLiquidacao, ZonaInstitucional,
    Noticia, SetupType
)
from ..utils.time import now_lisbon_iso

CURRENCY_CODES = {"EUR", "USD", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"}

def parse_pair(pair: str) -> Tuple[str, str]:
    p = pair.replace("-", "/").upper()
    base, quote = [x.strip() for x in p.split("/")]
    return base, quote

def seed_from(*parts: str) -> int:
    h = hashlib.sha256("|".join(parts).encode()).hexdigest()
    return int(h[:16], 16)

def rnd_between(seed: int, a: float, b: float, nd: int = 5) -> float:
    random.seed(seed)
    return round(random.uniform(a, b), nd)

def make_checklist(seed: int) -> List[ChecklistItem]:
    random.seed(seed)
    estados = ["VERDE", "AMARELO", "VERMELHO"]
    criterios = [
        "Confluência com zona institucional",
        "Liquidez tomada antes da entrada",
        "Estrutura de mercado alinhada",
        "Direção do timeframe superior",
        "RR ≥ 1.5",
    ]
    items = []
    for i, c in enumerate(criterios):
        e = random.choices(estados, weights=[0.6, 0.3, 0.1])[0]
        items.append(ChecklistItem(criterio=c, estado=e))
    return items

def make_setups(pair: str, setup_type: SetupType, seed: int) -> List[Setup]:
    base_seed = seed + 999
    direction = random.choice(["BUY", "SELL"]) if setup_type == "Scalp" else "BUY"
    base_price = rnd_between(base_seed, 0.8, 1.25, nd=5)
    setups: List[Setup] = []
    for i in range(3):
        s = base_seed + i * 111
        rr = rnd_between(s, 1.4, 2.8, nd=2)
        prob = int(rnd_between(s + 1, 58, 78, nd=0))
        if direction == "BUY":
            entrada = base_price
            sl = round(entrada - rnd_between(s + 2, 0.0008, 0.0022), 5)
            tp = round(entrada + rr * (entrada - sl), 5)
        else:
            entrada = base_price
            sl = round(entrada + rnd_between(s + 2, 0.0008, 0.0022), 5)
            tp = round(entrada - rr * (sl - entrada), 5)
        setups.append(
            Setup(
                nome=f"Setup {i+1} – {direction}",
                direcao=direction,
                entrada=entrada,
                stop_loss=sl,
                take_profit=tp,
                rr=rr,
                prob_sucesso=prob,
                checklist=make_checklist(s + 3),
                explicacao=(
                    "Entrada baseada em reteste à zona institucional e tomada prévia de liquidez. "
                    "Confirmação por estrutura e confluência multi‑timeframe."
                ),
            )
        )
        if setup_type == "Scalp":
            direction = "SELL" if direction == "BUY" else "BUY"
    return setups

def make_zonas(seed: int):
    base = rnd_between(seed, 1.05, 1.12)
    liquidez = [
        ZonaLiquidacao(tipo="Low", preco=round(base - 0.0045, 5)),
        ZonaLiquidacao(tipo="High", preco=round(base + 0.0047, 5)),
    ]
    zonas = [
        ZonaInstitucional("OB de Compra", round(base - 0.0018, 5), round(base - 0.0010, 5)),
        ZonaInstitucional("OB de Venda", round(base + 0.0010, 5), round(base + 0.0018, 5)),
    ]
    return liquidez, zonas

def signal_from_event(pair: str, currency: str, direction_arrow: str) -> str:
    base, quote = parse_pair(pair)
    if direction_arrow == "↑":
        if currency == base:
            return "BUY"
        if currency == quote:
            return "SELL"
    elif direction_arrow == "↓":
        if currency == base:
            return "SELL"
        if currency == quote:
            return "BUY"
    return "BUY/SELL (volatilidade)"

def build_context(pair: str, timeframe: str, setup_type: SetupType) -> str:
    base, quote = parse_pair(pair)
    return (
        f"{pair} apresenta tomada de liquidez recente e consolidação no {timeframe}. "
        f"Para {setup_type}, procuramos retestes a zonas institucionais com RR competitivo, "
        f"idealmente após varrimento do extremo anterior."
    )

def run_analysis(
    instrumento: str,
    timeframe: str,
    tipo_setup: SetupType,
    news_provider: NewsProvider | None = None,
) -> Analise:
    seed = seed_from(instrumento, timeframe, tipo_setup)
    liquidez, zonas = make_zonas(seed)
    setups = make_setups(instrumento, tipo_setup, seed)

    if news_provider is None:
        news_provider = StaticDemoNewsProvider()
    raw_news = news_provider.get_events(instrumento)

    noticias: List[Noticia] = []
    for ev in raw_news:
        sinal = signal_from_event(instrumento, ev["moeda"], ev["direcao_prevista"])  # type: ignore
        noticias.append(
            Noticia(
                data_hora_lisboa=ev["data_hora_lisboa"],
                evento=ev["evento"],
                moeda=ev["moeda"],
                impacto=ev["impacto"],
                direcao_prevista=ev["direcao_prevista"],
                sinal_par=sinal,
            )
        )

    quadro = [
        {
            "setup": s.nome,
            "direcao": s.direcao,
            "entrada": s.entrada,
            "SL": s.stop_loss,
            "TP": s.take_profit,
            "RR": s.rr,
            "%sucesso": s.prob_sucesso,
        }
        for s in setups
    ]

    analise = Analise(
        instrumento=instrumento,
        timeframe=timeframe,
        tipo_setup=tipo_setup,
        data_execucao_lisboa=now_lisbon_iso(),
        contexto_mercado=build_context(instrumento, timeframe, tipo_setup),
        zonas_liquidacao=liquidez,
        zonas_institucionais=zonas,
        setups=setups,
        noticias_relevantes=noticias,
        quadro_resumo=quadro,
    )
    return analise
