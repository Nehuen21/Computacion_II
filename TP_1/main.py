import multiprocessing as mp
from multiprocessing import Pipe, Queue
import random
import time
from datetime import datetime
import json
import hashlib

# ---------------- Funciones ---------------- #

def calcular_media_desv(valores):
    if not valores:
        return 0, 0
    n = len(valores)
    media = sum(valores) / n
    varianza = sum((x - media) ** 2 for x in valores) / n
    desv = varianza ** 0.5
    return media, desv

def analizador(nombre, conn, queue, ventana):
    ventana_valores = []
    while True:
        paquete = conn.recv()
        if paquete is None:  # señal de finalización
            break
        if nombre == "frecuencia":
            valor = paquete["frecuencia"]
        elif nombre == "oxigeno":
            valor = paquete["oxigeno"]
        else:  # presion
            valor = paquete["presion"][0]  # sistólica
        ventana_valores.append(valor)
        if len(ventana_valores) > ventana:
            ventana_valores.pop(0)
        media, desv = calcular_media_desv(ventana_valores)
        resultado = {
            "tipo": nombre,
            "timestamp": paquete["timestamp"],
            "media": media,
            "desv": desv
        }
        queue.put(resultado)

def generador_pipe(parent_pipes, total):
    for _ in range(total):
        paquete = {
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "frecuencia": random.randint(60, 180),
            "presion": [random.randint(110, 180), random.randint(70, 110)],
            "oxigeno": random.randint(90, 100)
        }
        for parent in parent_pipes:
            parent.send(paquete)
        time.sleep(1)
    # señal de finalización
    for parent in parent_pipes:
        parent.send(None)

def crear_bloque(prev_hash, bloque_datos, timestamp):
    # Crear hash SHA256
    contenido = str(prev_hash) + str(bloque_datos) + timestamp
    hash_bloque = hashlib.sha256(contenido.encode()).hexdigest()
    bloque = {
        "timestamp": timestamp,
        "datos": bloque_datos,
        "alerta": any_alerta(bloque_datos),
        "prev_hash": prev_hash,
        "hash": hash_bloque
    }
    return bloque

def any_alerta(bloque_datos):
    freq = bloque_datos["frecuencia"]["media"]
    oxi = bloque_datos["oxigeno"]["media"]
    pres = bloque_datos["presion"]["media"]
    if freq >= 200 or oxi < 90 or oxi > 100 or pres >= 200:
        return True
    return False

def verificador(queues, total):
    blockchain = []
    prev_hash = "0"  # primer bloque
    for _ in range(total):
        bloque_datos = {}
        for tipo, q in queues.items():
            res = q.get()
            bloque_datos[tipo] = res
        bloque = crear_bloque(prev_hash, bloque_datos, bloque_datos["frecuencia"]["timestamp"])
        prev_hash = bloque["hash"]
        blockchain.append(bloque)
        # mostrar por pantalla
        idx = len(blockchain) - 1
        print(f"Bloque {idx} | Hash: {bloque['hash']} | Alerta: {bloque['alerta']}")
        print("--- Resultados finales ---")
        for res in bloque_datos.values():
            print(res)
    # guardar blockchain en archivo
    with open("blockchain.json", "w") as f:
        json.dump(blockchain, f, indent=4)
    print("\nBlockchain guardada en blockchain.json")

# ---------------- Función Principal ---------------- #

def main():
    ventana = 30
    total = 60

    # Pipes para cada analizador
    parent_a, child_a = Pipe()
    parent_b, child_b = Pipe()
    parent_c, child_c = Pipe()

    # Queues para resultados al verificador
    q_a = Queue()
    q_b = Queue()
    q_c = Queue()

    # Procesos Analizadores
    proc_a = mp.Process(target=analizador, args=("frecuencia", child_a, q_a, ventana))
    proc_b = mp.Process(target=analizador, args=("presion", child_b, q_b, ventana))
    proc_c = mp.Process(target=analizador, args=("oxigeno", child_c, q_c, ventana))

    proc_a.start()
    proc_b.start()
    proc_c.start()

    # Generador
    generador_pipe([parent_a, parent_b, parent_c], total)

    # Verificador / Construcción de blockchain
    verificador({"frecuencia": q_a, "presion": q_b, "oxigeno": q_c}, total)

    # Esperar que finalicen los analizadores
    proc_a.join()
    proc_b.join()
    proc_c.join()

if __name__ == "__main__":
    main()
