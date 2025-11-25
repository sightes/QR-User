# Generador de Códigos QR para Trabajadores

Aplicación web en **FastAPI** que permite:

- Ingresar datos de un trabajador **1 a 1**.
- Cargar un **Excel masivo** con trabajadores.
- Generar un **Código QR** para cada registro.
- Mostrar el contenido del QR en **formato JSON**, fácil de interpretar por otras herramientas (por ejemplo, apps móviles).

El QR contiene un JSON con la siguiente estructura:

```json
{
  "nombre": "...",
  "rut": "...",
  "area": "...",
  "epp": "...",
  "vigilancia": "...",
  "riesgo": "..."
}
```

---

## 1. Requisitos

- Python 3.9+ (idealmente 3.10+)
- `pip`

Instalar dependencias:

```bash
pip install fastapi uvicorn "qrcode[pil]" python-multipart jinja2 pandas openpyxl
```

> Nota: En `zsh` los corchetes requieren comillas (`"qrcode[pil]"`).

---

## 2. Estructura del proyecto

Ejemplo de estructura de carpetas:

```bash
QR-User/
├─ main.py
├─ templates/
│  └─ index.html
└─ static/
   └─ app.js
```

- `main.py`: aplicación FastAPI, lógica de negocio, lectura de Excel, validación de RUT, generación de QR.
- `templates/index.html`: interfaz web (formulario 1 a 1, pestañas, tabla desde Excel).
- `static/app.js`: JavaScript para validación de RUT en frontend y manejo de pestañas.

---

## 3. Cómo ejecutar la aplicación

Desde la carpeta raíz del proyecto (donde está `main.py`):

```bash
uvicorn main:app --reload
```

Luego abrir en el navegador:

```text
http://127.0.0.1:8000/
```

o

```text
http://localhost:8000/
```

---

## 4. Uso de la aplicación

### 4.1. Interfaz principal

Al entrar a la aplicación se muestran dos paneles:

- **Panel izquierdo**: datos y opciones de ingreso
  - Pestañas:
    - **Ingreso 1 a 1**
    - **Procesar Excel**
- **Panel derecho**: resultado del **Código QR generado**
  - Imagen del QR.
  - Texto JSON que contiene la información codificada.
  - Botón **“Volver al listado”** para regresar a la página anterior (por ejemplo, al listado del Excel).

---

### 4.2. Pestaña “Ingreso 1 a 1”

Esta pestaña permite ingresar manualmente la información de un trabajador.

Campos:

- `Nombre`
- `RUT`
- `Área donde trabaja`
- `EPP`
- `Vigilancia`
- `Riesgo`

Pasos:

1. Completar todos los campos requeridos (Nombre, RUT, Área).  
2. Opcionalmente completar EPP, Vigilancia y Riesgo.
3. Presionar **“Generar QR”**.

Validaciones:

- El **RUT** se valida en:
  - **Frontend (JavaScript)**: evita enviar el formulario si el RUT es inválido.
  - **Backend (Python)**: valida nuevamente el RUT (cálculo de dígito verificador).

Si el RUT es inválido:

- Se muestra un mensaje de error en rojo junto al campo RUT.
- No se genera QR.
- Los campos quedan rellenados para poder corregir.

Si el RUT es válido:

- En el panel derecho se muestra:
  - Imagen del **QR**.
  - Texto en JSON con todos los campos.
  - Botón **“Volver al listado”** (vuelve a la pantalla anterior con los datos).

---

### 4.3. Pestaña “Procesar Excel”

Esta pestaña permite cargar un archivo Excel con múltiples trabajadores.

#### 4.3.1. Formato del Excel

El archivo debe ser `.xls` o `.xlsx` y **debe contener estas columnas exactamente**:

- `RUT`
- `NOMBRE Y APELLIDOS`
- `ÁREA`
- `EPP`
- `VIGILANCIA`
- `RIESGO`

> Importante: Los nombres deben coincidir (mayúsculas, acentos incluidos).

Ejemplo de cabecera:

| RUT          | NOMBRE Y APELLIDOS | ÁREA        | EPP            | VIGILANCIA | RIESGO |
|--------------|--------------------|-------------|----------------|------------|--------|
| 11.111.111-1 | Juan Pérez Soto    | Mantención  | Casco, Guantes | Directa    | Medio  |

#### 4.3.2. Carga del Excel

Pasos:

1. Ir a la pestaña **“Procesar Excel”**.
2. Seleccionar el archivo Excel en el campo **“Importar desde Excel”**.
3. Presionar **“Cargar Excel”**.

Si el archivo:

- No es Excel (`.xls` / `.xlsx`) → se muestra mensaje de error.
- No tiene las columnas requeridas → se muestra mensaje indicando qué columnas se esperan.
- No se puede leer → se muestra el error capturado.

Si todo es correcto:

- Se mostrará una tabla con las columnas:
  - Nombre
  - RUT
  - Área
  - EPP
  - Vigilancia
  - Riesgo
  - Acción

En la columna **Acción** aparece un botón **“Ver QR”** por cada fila.

#### 4.3.3. Generar QR para una fila del Excel

1. En la tabla de la pestaña Excel, elegir un trabajador.
2. Presionar **“Ver QR”** en esa fila.

El sistema:

- Envía esa fila al endpoint `/qr`.
- Valida el RUT.
- Si es válido, genera el QR y lo muestra en el panel derecho.
- Si es inválido, muestra el mensaje de error.

En el panel derecho se muestra también el botón:

```text
Volver al listado
```

que utiliza `window.history.back()` para regresar a la página anterior, donde estaba el listado del Excel.

---

## 5. Contenido del QR (formato JSON)

El valor interno del QR es un JSON como este:

```json
{
  "nombre": "Juan Pérez",
  "rut": "11.111.111-1",
  "area": "Mantención",
  "epp": "Casco, Guantes",
  "vigilancia": "Directa",
  "riesgo": "Medio"
}
```

Este contenido:

- Es visible como texto si lees el QR con la Cámara de iOS/Android.
- Puede ser fácilmente interpretado por una futura app móvil o sistema que:
  1. Escanee el QR.
  2. Parse el JSON.
  3. Use los campos para mostrar la ficha del trabajador o validar acceso, EPP, etc.

---

## 6. Validación de RUT

La función `validar_rut(rut: str) -> bool`:

- Acepta RUT con o sin puntos, con guion.
  - Ej.: `12.345.678-5` o `12345678-5`.
- Limpia formato (quita puntos y guion y pasa a mayúsculas).
- Separa `cuerpo` y dígito verificador.
- Calcula el DV con el algoritmo estándar (factores 2–7).
- Soporta DV `0–9` y `K`.

Se usa en:

- El endpoint `/qr`: si el RUT es inválido, se devuelve el formulario con error.
- El frontend (JS): evita enviar formularios con RUT inválido.

---

## 7. Ideas de extensiones

Algunas ideas para futuras mejoras:

- **Guardar en base de datos**  
  Al momento de generar el QR (en `/qr`), insertar el `payload` JSON en una tabla (PostgreSQL, MySQL, etc.).

- **Convertir JSON → URL**  
  En lugar de JSON, hacer que el QR contenga una URL con un identificador (`id_trabajador`) y que la ficha se cargue desde un sistema interno.

- **Agregar más campos**  
  Solo hay que:
  - Añadir el campo al contexto en `read_form`.
  - Agregarlo al formulario en `index.html`.
  - Incluirlo en el `payload` del QR.
  - Añadirlo a la lectura del Excel (si aplica).

---

## 8. Soporte / troubleshooting

- **QR no se genera**  
  Revisar la consola donde corre `uvicorn` para ver errores de Python.

- **Pestaña “Procesar Excel” no cambia**  
  Revisar la consola del navegador (F12 → Console) por errores de JavaScript (`app.js`).

- **El Excel no se acepta**  
  Confirmar nombres de columnas, incluyendo mayúsculas y acentos.

---

Hecho con FastAPI + cariño para uso interno 👷‍♂️📱
