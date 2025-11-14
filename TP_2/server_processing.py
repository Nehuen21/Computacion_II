#!/usr/bin/env python3
import argparse
import socketserver
from concurrent.futures import ProcessPoolExecutor
import os
import json
import socket

# --- Importaciones de nuestros módulos ---
from processor.tasks import run_heavy_processing

# Pool de procesos global
process_pool = None

# --- Handler del SocketServer ---
class ProcessingHandler(socketserver.BaseRequestHandler):
    """
    Manejador para cada conexión TCP recibida en el Servidor B.
   
    """
    def handle(self):
        print(f"\n[Servidor B] Conexión recibida de {self.client_address}")
        
        try:
            # 1. Recibir datos de Servidor A (en bucle hasta EOF)
            data_chunks = []
            while True:
                chunk = self.request.recv(1024)
                if not chunk:
                    break 
                data_chunks.append(chunk)
            
            data = b"".join(data_chunks)
            if not data:
                print("[Servidor B] Conexión vacía, cerrando.")
                return

            request = json.loads(data.decode('utf-8'))
            url = request.get('url')
            image_urls = request.get('image_urls', []) 
            
            print(f"[Servidor B] Petición recibida para procesar: {url}")

            # 2. Enviar tarea al ProcessPoolExecutor
            #
            future = process_pool.submit(run_heavy_processing, url, image_urls)
            
            results = future.result() 

            # 3. Devolver resultados a Servidor A
            response_data = {
                "status": "success",
                "url": url,
                "data": results
            }
            response_bytes = json.dumps(response_data).encode('utf-8')
            
            self.request.sendall(response_bytes)
            
        except Exception as e:
            print(f"[Servidor B] Error en handler: {e}")
            error_response = json.dumps({"status": "error", "message": str(e)})
            self.request.sendall(error_response.encode('utf-8'))


# --- Clase de Servidor ---
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Servidor TCP que usa hilos para manejar conexiones.
   
    """
    daemon_threads = True
    allow_reuse_address = True
    address_family = socket.AF_INET6 

    def server_bind(self):
        """
        Sobreescribimos server_bind para configurar el socket ANTES de bind().
        """
        if self.address_family == socket.AF_INET6 and self.server_address[0] == '::':
            try:
                print("[Servidor B] Configurando socket para dual-stack (IPv4/IPv6)...")
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            except (OSError, AttributeError) as e:
                print(f"[Servidor B] Advertencia: No se pudo configurar dual-stack: {e}")
        
        super().server_bind()

# --- Configuración y Arranque ---
def main():
    global process_pool
    
    parser = argparse.ArgumentParser(description="Servidor de Procesamiento Distribuido (Servidor B)")
    parser.add_argument("-i", "--ip", required=True, help="Dirección de escucha (e.g., '0.0.0.0' o '::')")
    parser.add_argument("-p", "--port", required=True, type=int, help="Puerto de escucha")
    parser.add_argument("-n", "--processes", type=int, default=os.cpu_count(), 
                        help="Número de procesos en el pool (default: CPU count)")
    args = parser.parse_args()

    with ProcessPoolExecutor(max_workers=args.processes) as pool:
        process_pool = pool
        print(f"Iniciando Pool de Procesos con {args.processes} workers.")
        
        try:
            server_ip = args.ip
            server_port = args.port

            if ':' not in server_ip:
                print("[Servidor B] Detectada IP IPv4, cambiando familia de socket a AF_INET.")
                ThreadedTCPServer.address_family = socket.AF_INET
            
            server = ThreadedTCPServer((server_ip, server_port), ProcessingHandler)
            print(f"Iniciando Servidor B (SocketServer) en {server_ip}:{server_port}")
            server.serve_forever()

        except KeyboardInterrupt:
            print("\nCerrando servidor B...")
        finally:
            server.server_close()
            print("Servidor B cerrado.")

if __name__ == "__main__":
    #
    main()