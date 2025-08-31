import os
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import json
import asyncio

from .schemas import AnalysisRequest, AnalysisResponse
from .services.analysis import run_analysis
from .services.imaging import draw_zonas, save_image
from .services.pdf import build_pdf
from .services.news_provider import StaticDemoNewsProvider, TradingEconomicsNewsProvider

APP_VERSION = "1.1.1"
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="EruditeFX API", version=APP_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")


def _pick_news_provider(provider_key: str | None):
    key = (provider_key or "te").lower()
    if key in ("te", "tradingeconomics", "real"):
        return TradingEconomicsNewsProvider()
    return StaticDemoNewsProvider()


@app.get("/health")
def health():
    return {"status": "ok", "version": APP_VERSION}


@app.post("/api/v1/eruditefx/analyze", response_model=AnalysisResponse)
def analyze(req: AnalysisRequest, provider: str | None = None):
    if "/" not in req.instrumento:
        raise HTTPException(status_code=400, detail="Instrumento deve estar no formato 'BASE/QUOTE', ex.: 'EUR/USD'")

    news_provider = _pick_news_provider(provider)
    analise = run_analysis(req.instrumento.upper(), req.timeframe.upper(), req.tipo_setup, news_provider=news_provider)

    image_url = None
    image_path = None
    if req.gerar_imagem:
        img = draw_zonas(analise.zonas_liquidacao, analise.zonas_institucionais, req.chart_image_b64)
        run_id = str(uuid.uuid4())
        run_dir = OUTPUT_DIR / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        image_path = save_image(img, str(run_dir))
        image_url = f"/outputs/{run_id}/" + os.path.basename(image_path)

    pdf_url = None
    if req.gerar_pdf:
        if image_path is None:
            img = draw_zonas(analise.zonas_liquidacao, analise.zonas_institucionais, req.chart_image_b64)
            run_id = str(uuid.uuid4())
            run_dir = OUTPUT_DIR / run_id
            run_dir.mkdir(parents=True, exist_ok=True)
            image_path = save_image(img, str(run_dir))
            image_url = f"/outputs/{run_id}/" + os.path.basename(image_path)
        pdf_path = str(Path(image_path).with_suffix(".pdf"))
        build_pdf(analise, image_path, pdf_path)
        pdf_url = "/outputs/" + Path(pdf_path).relative_to(OUTPUT_DIR).as_posix()

    return AnalysisResponse(analise=analise, image_url=image_url, pdf_url=pdf_url)


@app.get("/api/v1/eruditefx/analyze-stream")
async def analyze_stream(
    instrumento: str,
    timeframe: str,
    tipo_setup: str,
    gerar_imagem: bool = True,
    gerar_pdf: bool = True,
    provider: str | None = None,
):
    async def event_gen():
        # start
        yield "data: " + json.dumps({"step": "start"}) + "\n\n"
        await asyncio.sleep(0)

        # analysis
        news_provider = _pick_news_provider(provider)
        analise = run_analysis(instrumento.upper(), timeframe.upper(), tipo_setup, news_provider=news_provider)
        yield "data: " + json.dumps({"step": "analysis", "analise": analise.model_dump()}) + "\n\n"
        await asyncio.sleep(0)

        # image
        image_url = None
        image_path = None
        if gerar_imagem:
            img = draw_zonas(analise.zonas_liquidacao, analise.zonas_institucionais, None)
            run_id = str(uuid.uuid4())
            run_dir = OUTPUT_DIR / run_id
            run_dir.mkdir(parents=True, exist_ok=True)
            image_path = save_image(img, str(run_dir))
            image_url = f"/outputs/{run_id}/" + os.path.basename(image_path)
        yield "data: " + json.dumps({"step": "image", "image_url": image_url}) + "\n\n"
        await asyncio.sleep(0)

        # pdf
        pdf_url = None
        if gerar_pdf:
            if image_path is None:
                img = draw_zonas(analise.zonas_liquidacao, analise.zonas_institucionais, None)
                run_id = str(uuid.uuid4())
                run_dir = OUTPUT_DIR / run_id
                run_dir.mkdir(parents=True, exist_ok=True)
                image_path = save_image(img, str(run_dir))
                image_url = f"/outputs/{run_id}/" + os.path.basename(image_path)
            pdf_path = str(Path(image_path).with_suffix(".pdf"))
            build_pdf(analise, image_path, pdf_path)
            pdf_url = "/outputs/" + Path(pdf_path).relative_to(OUTPUT_DIR).as_posix()
        yield "data: " + json.dumps({"step": "pdf", "pdf_url": pdf_url}) + "\n\n"

        # done
        yield "data: " + json.dumps({"step": "done"}) + "\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")
