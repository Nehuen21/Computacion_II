import asyncio
import json

async def request_processing_from_b(url: str, image_urls: list, b_host: str, b_port: int) -> dict:
    """
    Se comunica con el Servidor B por sockets (Parte A, Tarea 2).
    Esta es la implementación del *cliente* del protocolo.
   
    """
    print(f"[Servidor A] Conectando a Servidor B en {b_host}:{b_port} para: {url}")
    
    try:
        # 1. Conectar (asyncio maneja el socket)
        #
        reader, writer = await asyncio.open_connection(b_host, b_port)
        
        # 2. Preparar y enviar la petición a B
        request_data = json.dumps({
            "url": url,
            "image_urls": image_urls
        })
        
        writer.write(request_data.encode('utf-8'))
        await writer.drain() 
        
        # 3. Señalizar fin de envío (EOF)
        writer.write_eof() 
        
        # 4. Leer la respuesta completa de B
        response_bytes = await reader.read() # Lee hasta EOF
        
        # 5. Cerrar
        writer.close()
        await writer.wait_closed()
        
        # 6. Decodificar y devolver
        response_json = json.loads(response_bytes.decode('utf-8'))
        
        if response_json.get('status') == 'success':
            pid = response_json.get('data', {}).get('processed_by_pid', 'PID_DESCONOCIDO')
            print(f"[Servidor A] Servidor B (PID: {pid}) terminó de procesar: {url}")
            return response_json['data']
        else:
            raise Exception(f"Error del Servidor B: {response_json.get('message', 'Error desconocido')}")
            
    except ConnectionRefusedError:
        print(f"[Servidor A] ERROR: No se pudo conectar al Servidor B en {b_host}:{b_port}")
        raise Exception("Servidor de procesamiento (B) no está disponible")
    except Exception as e:
        print(f"[Servidor A] ERROR en comunicación con B: {e}")
        raise