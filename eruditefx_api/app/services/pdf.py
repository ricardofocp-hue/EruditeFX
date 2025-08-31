from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from ..schemas import Analise, ChecklistItem

TITLE = ParagraphStyle(name="Title", fontSize=16, leading=20, spaceAfter=12)
H2 = ParagraphStyle(name="H2", fontSize=13, leading=16, spaceAfter=8)
BODY = ParagraphStyle(name="Body", fontSize=10.5, leading=14)

COLOR_MAP = {
    "VERDE": colors.green,
    "AMARELO": colors.orange,
    "VERMELHO": colors.red,
}

def _checklist_flow(items: list[ChecklistItem]):
    flows = []
    for it in items:
        flows.append(Paragraph(f"<font color='{COLOR_MAP[it.estado].hexval()}'>• {it.criterio}: {it.estado}</font>", BODY))
    return flows

def build_pdf(analise: Analise, image_path: str | None, out_path: str) -> str:
    doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    story = []

    story.append(Paragraph("EruditeFX – Relatório de Análise", TITLE))
    story.append(Paragraph(f"Instrumento: <b>{analise.instrumento}</b> | Timeframe: <b>{analise.timeframe}</b> | Tipo de Setup: <b>{analise.tipo_setup}</b>", BODY))
    story.append(Paragraph(f"Data (Lisboa): {analise.data_execucao_lisboa}", BODY))
    story.append(Spacer(1, 8))

    story.append(Paragraph("1. Contexto de mercado", H2))
    story.append(Paragraph(analise.contexto_mercado, BODY))
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. Zonas de liquidação", H2))
    tbl_liq = [["Tipo", "Preço"]] + [[z.tipo, f"{z.preco:.5f}"] for z in analise.zonas_liquidacao]
    t = Table(tbl_liq, hAlign='LEFT')
    t.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))

    story.append(Paragraph("3. Zonas institucionais", H2))
    tbl_inst = [["Tipo", "Limite Inferior", "Limite Superior"]] + [
        [z.tipo, f"{z.limite_inferior:.5f}", f"{z.limite_superior:.5f}"] for z in analise.zonas_institucionais
    ]
    ti = Table(tbl_inst, hAlign='LEFT')
    ti.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))
    story.append(ti)
    story.append(Spacer(1, 10))

    story.append(Paragraph("4. Setups detalhados", H2))
    for i, s in enumerate(analise.setups, start=1):
        story.append(Paragraph(f"<b>{s.nome}</b>", BODY))
        story.append(Paragraph(
            f"Entrada: {s.entrada:.5f} | SL: {s.stop_loss:.5f} | TP: {s.take_profit:.5f} | RR: {s.rr:.2f} | % Sucesso: {s.prob_sucesso}%", BODY))
        story.extend(_checklist_flow(s.checklist))
        story.append(Paragraph(s.explicacao, BODY))
        story.append(Spacer(1, 6))

    story.append(Paragraph("5. Notícias relevantes", H2))
    tbl_news = [["Data/Hora (Lisboa)", "Evento", "Moeda", "Impacto", "Prev.", "Sinal (par)"]]
    for n in analise.noticias_relevantes:
        tbl_news.append([n.data_hora_lisboa, n.evento, n.moeda, n.impacto, n.direcao_prevista, n.sinal_par])
    tn = Table(tbl_news, hAlign='LEFT')
    tn.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))
    story.append(tn)
    story.append(Spacer(1, 8))

    story.append(Paragraph("6. Quadro resumo", H2))
    tbl_sum = [["Setup", "Direção", "Entrada", "SL", "TP", "RR", "% Sucesso"]]
    for r in analise.quadro_resumo:
        tbl_sum.append([r["setup"], r["direcao"], f"{r['entrada']:.5f}", f"{r['SL']:.5f}", f"{r['TP']:.5f}", f"{r['RR']:.2f}", f"{r['%sucesso']}%"])
    ts = Table(tbl_sum, hAlign='LEFT')
    ts.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))
    story.append(ts)

    if image_path:
        story.append(Spacer(1, 10))
        story.append(Paragraph("Imagem com zonas (contorno, sem preenchimento)", H2))
        story.append(RLImage(image_path, width=16*cm, height=9*cm))

    doc.build(story)
    return out_path
