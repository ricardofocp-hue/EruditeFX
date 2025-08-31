from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

SetupType = Literal["Scalp", "Intradia", "Swing"]

class ChecklistItem(BaseModel):
    criterio: str
    estado: Literal["VERDE", "AMARELO", "VERMELHO"]

class Setup(BaseModel):
    nome: str
    direcao: Literal["BUY", "SELL"]
    entrada: float
    stop_loss: float
    take_profit: float
    rr: float
    prob_sucesso: int
    checklist: List[ChecklistItem]
    explicacao: str

class ZonaLiquidacao(BaseModel):
    tipo: Literal["High", "Low"]
    preco: float

class ZonaInstitucional(BaseModel):
    tipo: Literal["OB de Compra", "OB de Venda"]
    limite_inferior: float
    limite_superior: float

class Noticia(BaseModel):
    data_hora_lisboa: str  # "YYYY-MM-DD HH:MM"
    evento: str
    moeda: str  # ex.: "USD", "EUR"
    impacto: Literal["Baixo", "Médio", "Alto"]
    direcao_prevista: Literal["↑", "↓", "Volátil"]
    sinal_par: Literal["BUY", "SELL", "BUY/SELL (volatilidade)"]

class Analise(BaseModel):
    instrumento: str
    timeframe: str
    tipo_setup: SetupType
    data_execucao_lisboa: str
    contexto_mercado: str
    zonas_liquidacao: List[ZonaLiquidacao]
    zonas_institucionais: List[ZonaInstitucional]
    setups: List[Setup]
    noticias_relevantes: List[Noticia]
    quadro_resumo: List[dict]

class AnalysisRequest(BaseModel):
    instrumento: str = Field(..., example="EUR/USD")
    timeframe: str = Field(..., example="5M")
    tipo_setup: SetupType
    gerar_imagem: bool = True
    gerar_pdf: bool = True
    chart_image_b64: Optional[str] = None  # opcional (PNG/JPG em base64)

class AnalysisResponse(BaseModel):
    analise: Analise
    image_url: Optional[str] = None
    pdf_url: Optional[str] = None
