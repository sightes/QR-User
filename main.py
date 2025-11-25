from fastapi import FastAPI, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import qrcode
from io import BytesIO
import base64
import json
import pandas as pd

app = FastAPI()

# Montar archivos estáticos (para JS, CSS, imágenes, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar templates (Jinja2)
templates = Jinja2Templates(directory="templates")


def validar_rut(rut: str) -> bool:
    """
    Valida un RUT chileno en formato con o sin puntos y con guion,
    por ejemplo: 12.345.678-5 o 12345678-5.
    """
    rut = rut.replace(".", "").replace("-", "").upper()

    if len(rut) < 2:
        return False

    cuerpo, dv = rut[:-1], rut[-1]

    if not cuerpo.isdigit():
        return False

    reversed_digits = list(map(int, reversed(cuerpo)))
    factores = [2, 3, 4, 5, 6, 7]
    suma = 0
    factor_index = 0

    for d in reversed_digits:
        suma += d * factores[factor_index]
        factor_index = (factor_index + 1) % len(factores)

    resto = 11 - (suma % 11)
    if resto == 11:
        dv_esperado = "0"
    elif resto == 10:
        dv_esperado = "K"
    else:
        dv_esperado = str(resto)

    return dv == dv_esperado


@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    # Valores por defecto la primera vez
    context = {
        "request": request,
        "nombre": "",
        "rut": "",
        "area": "",
        "epp": "",
        "vigilancia": "",
        "riesgo": "",
        "qr_img": None,
        "qr_text": None,
        "error": None,
        "rows": None,
    }
    return templates.TemplateResponse("index.html", context)


@app.post("/qr", response_class=HTMLResponse)
async def generate_qr(
    request: Request,
    nombre: str = Form(...),
    rut: str = Form(...),
    area: str = Form(...),
    epp: str = Form(""),
    vigilancia: str = Form(""),
    riesgo: str = Form("")
):
    """
    Genera un código QR con la información recibida del formulario
    y devuelve una página HTML en formato empresarial, con el formulario
    a la izquierda y el QR generado a la derecha. Debajo del QR se muestra
    el texto que se codificó, para poder almacenarlo en una base de datos
    a futuro.
    """

    # Validar RUT
    if not validar_rut(rut):
        context = {
            "request": request,
            "nombre": nombre,
            "rut": rut,
            "area": area,
            "epp": epp,
            "vigilancia": vigilancia,
            "riesgo": riesgo,
            "qr_img": None,
            "qr_text": None,
            "error": "RUT inválido. Verifique el número y el dígito verificador.",
            "rows": None,
        }
        return templates.TemplateResponse("index.html", context, status_code=400)

    # Texto que irá dentro del QR (formato JSON para ser fácil de interpretar)
    payload = {
        "nombre": nombre,
        "rut": rut,
        "area": area,
        "epp": epp,
        "vigilancia": vigilancia,
        "riesgo": riesgo,
    }
    data = json.dumps(payload, ensure_ascii=False)

    # Crear imagen QR
    img = qrcode.make(data)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    context = {
        "request": request,
        "nombre": nombre,
        "rut": rut,
        "area": area,
        "epp": epp,
        "vigilancia": vigilancia,
        "riesgo": riesgo,
        "qr_img": img_b64,
        "qr_text": data,
        "error": None,
        "rows": None,
    }

    return templates.TemplateResponse("index.html", context)


@app.post("/upload_excel", response_class=HTMLResponse)
async def upload_excel(
    request: Request,
    file: UploadFile = File(...)
):
    # Validar extensión
    if not file.filename.lower().endswith((".xls", ".xlsx")):
        context = {
            "request": request,
            "nombre": "",
            "rut": "",
            "area": "",
            "epp": "",
            "vigilancia": "",
            "riesgo": "",
            "qr_img": None,
            "qr_text": None,
            "error": "El archivo debe ser Excel (.xls o .xlsx)",
            "rows": None,
        }
        return templates.TemplateResponse("index.html", context, status_code=400)

    # Leer todo el archivo en memoria
    contents = await file.read()

    try:
        df = pd.read_excel(BytesIO(contents))
    except Exception as e:
        context = {
            "request": request,
            "nombre": "",
            "rut": "",
            "area": "",
            "epp": "",
            "vigilancia": "",
            "riesgo": "",
            "qr_img": None,
            "qr_text": None,
            "error": f"No se pudo leer el Excel: {e}",
            "rows": None,
        }
        return templates.TemplateResponse("index.html", context, status_code=400)

    # Asegurar que existen las columnas esperadas (según tu Excel)
    columnas_requeridas = ["RUT", "NOMBRE Y APELLIDOS", "ÁREA", "EPP", "VIGILANCIA", "RIESGO"]
    if not all(col in df.columns for col in columnas_requeridas):
        context = {
            "request": request,
            "nombre": "",
            "rut": "",
            "area": "",
            "epp": "",
            "vigilancia": "",
            "riesgo": "",
            "qr_img": None,
            "qr_text": None,
            "error": "El Excel debe contener las columnas: RUT, NOMBRE Y APELLIDOS, ÁREA, EPP, VIGILANCIA, RIESGO",
            "rows": None,
        }
        return templates.TemplateResponse("index.html", context, status_code=400)

    # Nos quedamos solo con esas columnas
    df = df[columnas_requeridas]

    # Convertimos a lista de diccionarios para pasarlo al template
    rows = [
        {
            "nombre": row["NOMBRE Y APELLIDOS"],
            "rut": row["RUT"],
            "area": row["ÁREA"],
            "epp": row["EPP"],
            "vigilancia": row["VIGILANCIA"],
            "riesgo": row["RIESGO"],
        }
        for _, row in df.iterrows()
    ]

    context = {
        "request": request,
        "nombre": "",
        "rut": "",
        "area": "",
        "epp": "",
        "vigilancia": "",
        "riesgo": "",
        "qr_img": None,
        "qr_text": None,
        "error": None,
        "rows": rows,
    }
    return templates.TemplateResponse("index.html", context)