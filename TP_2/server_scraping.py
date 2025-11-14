#!/usr/bin/env python3
import argparse
import asyncio
from aiohttp import web
import json
from datetime import datetime

# --- Importaciones de nuestros módulos ---
from scraper.core import perform_local_scraping
from common.protocol import request_processing_from_b

# --- Configuración ---
app_config = {}

# --- Handler HTTP de AIOHTTP ---
async def handle_scrape(request: web.Request) -> web.Response:
    """
    Manejador principal que recibe las peticiones HTTP de los clientes.
    """
    url = request.query.get('url')
    if not url:
        return web.json_response(
            {"error": "Se requiere el parámetro 'url'"}, 
            status=400
        )

    print(f"\n[Servidor A] Petición recibida para: {url}")

    try:
        # 1. Scraping (de scraper/core.py)
        scraping_results = await perform_local_scraping(url)
        
        image_urls_to_process = scraping_results.get('image_urls', [])

        # 2. Procesamiento (de common/protocol.py)
        processing_results = await request_processing_from_b(
            url, 
            image_urls_to_process,
            app_config['b_host'],
            app_config['b_port']
        )

        # 3. Consolidar y responder (Parte C)
        final_response = {
            "url": url,
            "timestamp": datetime.now().isoformat() + "Z", 
            "scraping_data": scraping_results,
            "processing_data": processing_results,
            "status": "success"
        }
        return web.json_response(final_response)

    except Exception as e:
        print(f"[Servidor A] Error procesando {url}: {e}")
        return web.json_response({"error": str(e), "status": "failed"}, status=500)


# --- Configuración y Arranque ---
def main():
    global app_config
    
    parser = argparse.ArgumentParser(description="Servidor de Scraping Web Asíncrono (Servidor A)")
    parser.add_argument("-i", "--ip", required=True, help="Dirección de escucha (e.g., '0.0.0.0' o '::')")
    parser.add_argument("-p", "--port", required=True, type=int, help="Puerto de escucha")
    parser.add_argument("-w", "--workers", type=int, default=4, help="Número de workers (default: 4, informativo)")
    
    parser.add_argument("--b-host", default="::1", help="Host del Servidor B (default: ::1, localhost IPv6)")
    parser.add_argument("--b-port", type=int, default=9999, help="Puerto del Servidor B (default: 9999)")
    
    args = parser.parse_args()

    app_config['b_host'] = args.b_host
    app_config['b_port'] = args.b_port

    print(f"Iniciando Servidor A (Asyncio) en http://{args.ip}:{args.port}")
    print(f"Conectándose al Servidor B en: {args.b_host}:{args.b_port}")
    
    app = web.Application()
    app.router.add_get("/scrape", handle_scrape)
    
    web.run_app(app, host=args.ip, port=args.port)

if __name__ == "__main__":
    main()