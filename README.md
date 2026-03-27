# Scrap Master 3000

CLI en Python para extraer contenido de sitios web (scraping etico) y exportar resultados a `.xlsx` mientras se define la base de datos.

## Caracteristicas
- Arquitectura extensible con registro de scrapers por tipo de pagina.
- Soporta Blogger (`blogger`), Guatemala.com (`guatemala.com`) y MysteryInternet (`misteryinternet.com`).
- Soporta Blogger via API (`blogger_api`) usando `BLOGGER_API_KEY`.
- Descubre URLs desde una raiz y procesa cada pagina.
- Limpia HTML removiendo anuncios (Adsense) y elementos no relacionados.
- Extrae texto e imagenes relevantes.
- Exporta registros a Excel y opcionalmente a JSON.

## Instalacion rapida
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
```

Configura variables para Blogger:
```bash
export BLOGGER_API_KEY=tu_api_key  # opcional, para lectura API de Blogger

# opcion 1: token directo
export BLOGGER_ACCESS_TOKEN=tu_access_token_oauth

# opcion 2 (recomendada): refresh automatico de token
export GOOGLE_CLIENT_ID=tu_client_id
export GOOGLE_CLIENT_SECRET=tu_client_secret
export BLOGGER_REFRESH_TOKEN=tu_refresh_token
```

## Uso
Lista tipos soportados:
```bash
python -m scrap.cli sites
```

Ejecuta un scraping completo (con descubrimiento de URLs):
```bash
python -m scrap.cli run \
  --site blogger \
  --root-url https://ejemplo.blogspot.com/ \
  --limit 50 \
  --output resultados.xlsx \
  --json-output resultados.json

Para misteryinternet.com (un post individual, sin descubrimiento):
```bash
python -m scrap.cli run \
  --site misteryinternet.com \
  --root-url https://misteryinternet.com/creepypasta-nueva-era/ \
  --single \
  --format txt \
  --output mistery.txt
```

Para Blogger API (requiere `BLOGGER_API_KEY` en entorno):
```bash
export BLOGGER_API_KEY=tu_clave
python -m scrap.cli run \
  --site blogger_api \
  --root-url https://tublog.blogspot.com/ \
  --limit 20 \
  --format txt \
  --output blogger_api.txt
```

## API ligera + Frontend
- Arranque conjunto (recomendado):
```bash
./dev.sh
```

- Servidor (Flask):
```bash
PYTHONPATH=src flask --app api_server run --port 8000
```

- Frontend: abre `http://localhost:5173` (si usas `./dev.sh`) o `frontend/index.html` directamente en el navegador. Ingresa URL y selecciona sitio; descarga un `.txt` (bloc de notas) con el contenido limpio.

Regla de publicacion en API:
- `guatemala.com` publica en el blog `7446224671990318703`.
- `misteryinternet.com` publica en el blog `6453803480920778505`.
- Los demas sitios mantienen la salida en `.txt`.

Normalizacion de imagenes para `misteryinternet.com`:
- Si una imagen trae `data-src` y `src` vacio o en placeholder base64 (`data:image/...`), el scraper reemplaza `src` por `data-src` antes de publicar en Blogger.

Prioridad de credenciales para publicar:
1. Usa `BLOGGER_ACCESS_TOKEN` si existe.
2. Si no existe, intenta generar un access token usando `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` y `BLOGGER_REFRESH_TOKEN`.
3. Si faltan ambas opciones, responde error de credenciales.

## Salida de datos
Cada fila del `.xlsx` contiene:
- `url`
- `page_type`
- `cleaned_html`
- `text_content`
- `image_urls` (lista separada por comas)
- `fetched_at` (UTC ISO8601)

## Extender con nuevos sitios
1. Crear una clase que herede de `Scraper` en `src/scrap/sites/`.
2. Implementar `discover_urls` y `scrape` reutilizando utilidades de `src/scrap/utils.py`.
3. Registrar la clase en `src/scrap/cli.py` dentro del `ScraperRegistry`.

## Notas
- Usa `requests` + `BeautifulSoup` (lxml) y `openpyxl` para la exportacion.
- La limpieza elimina scripts, estilos, iframes y firmas comunes de anuncios.
- Para Blogger, la publicacion usa HTML limpio del scraper y conserva `img src` normalizado cuando el origen usa lazy loading.
