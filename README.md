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
cp .env.example .env  # coloca tu BLOGGER_API_KEY si usaras blogger_api
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
- Servidor (Flask):
```bash
PYTHONPATH=src flask --app api_server run --port 8000
```

- Frontend: abre `frontend/index.html` en el navegador. Ingresa URL y selecciona sitio; descarga un `.txt` (bloc de notas) con el contenido limpio.
```

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
