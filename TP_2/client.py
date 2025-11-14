#!/usr/bin/env python3
import requests
import sys
import json

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 client.py <url_a_scrapear>")
        print("Ejemplo: python3 client.py http://example.com")
        sys.exit(1)

    target_url = sys.argv[1]
    
    # Asumimos que el Servidor A corre en localhost:8080
    server_a_url = f"http://localhost:8080/scrape"
    
    print(f"Solicitando al Servidor A ({server_a_url}) que scrapee: {target_url}\n")
    
    try:
        response = requests.get(server_a_url, params={'url': target_url}, timeout=60)
        
        response.raise_for_status() # Lanza error si es 4xx o 5xx
        
        try:
            data = response.json()
            print("Respuesta JSON recibida:")
            # Imprimir bonito
            print(json.dumps(data, indent=2, ensure_ascii=False))

            # Pequeño resumen
            if data.get('status') == 'success':
                print("\n--- Resumen ---")
                print(f"Título: {data['scraping_data']['title']}")
                print(f"Links encontrados: {len(data['scraping_data']['links'])}")
                print(f"Imágenes encontradas: {data['scraping_data']['images_count']}")
                print(f"Tiempo de carga (ms): {data['processing_data']['performance']['load_time_ms']}")
                print(f"Thumbnails generados: {len(data['processing_data']['thumbnails'])}")
            
        except requests.exceptions.JSONDecodeError:
            print("Error: La respuesta del servidor no fue un JSON válido.")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print(f"Error: No se pudo conectar al Servidor A en {server_a_url}")
        print("¿Está server_scraping.py corriendo?")
    except requests.exceptions.Timeout:
        print("Error: Timeout esperando la respuesta del Servidor A")
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP del Servidor A: {e.response.status_code}")
        print(e.response.text)
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")


if __name__ == "__main__":
    main()