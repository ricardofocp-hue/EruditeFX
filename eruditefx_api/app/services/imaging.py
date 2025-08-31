import os

import io
import base64
from PIL import Image, ImageDraw
from typing import List
from ..schemas import ZonaLiquidacao, ZonaInstitucional

_DEF_W, _DEF_H = 1280, 720

def _decode_b64_img(data_b64: str) -> Image.Image:
    raw = base64.b64decode(data_b64.split(",")[-1])
    return Image.open(io.BytesIO(raw)).convert("RGBA")

def draw_zonas(
    zonas_liq: List[ZonaLiquidacao],
    zonas_inst: List[ZonaInstitucional],
    base_img_b64: str | None = None,
) -> Image.Image:
    if base_img_b64:
        img = _decode_b64_img(base_img_b64).copy().convert("RGBA")
    else:
        bg = Image.new("RGB", (_DEF_W, _DEF_H), (245, 247, 250))
        img = bg.convert("RGBA")

    draw = ImageDraw.Draw(img)

    prices = [z.preco for z in zonas_liq] + [z.limite_inferior for z in zonas_inst] + [z.limite_superior for z in zonas_inst]
    pmin, pmax = min(prices), max(prices)
    def y(p: float) -> int:
        if pmax == pmin:
            return _DEF_H // 2
        return int((1 - (p - pmin) / (pmax - pmin)) * (_DEF_H - 80)) + 40

    # Zonas institucionais: contorno (sem preenchimento)
    for z in zonas_inst:
        y1, y2 = y(z.limite_superior), y(z.limite_inferior)
        x1, x2 = 100, _DEF_W - 100
        draw.rectangle([(x1, y1), (x2, y2)], outline=(15, 76, 129, 255), width=3)
        draw.text((x1 + 6, min(y1, y2) - 18), z.tipo, fill=(15, 76, 129, 255))

    # Linhas de liquidez
    for z in zonas_liq:
        yy = y(z.preco)
        draw.line([(80, yy), (_DEF_W - 80, yy)], fill=(200, 100, 0, 255), width=2)
        draw.text((85, yy - 16), f"Liquidez {z.tipo} {z.preco}", fill=(200, 100, 0, 255))

    return img

def save_image(img: Image.Image, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    out_path = f"{out_dir}/imagem_zonas.png"
    img.save(out_path, "PNG")
    return out_path
