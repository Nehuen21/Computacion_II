import multiprocessing as mp
from multiprocessing import Pipe, Queue, Event
import random
import time
from datetime import datetime

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
        if paquete is None:
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

def verificador(queues, total):
    resultados = { "frecuencia": [], "presion": [], "oxigeno": [] }
    for _ in range(total):
        bloque = {}
        for tipo, q in queues.items():
            res = q.get()
            bloque[tipo] = res
        print("--- Resultados finales ---")
        for res in bloque.values():
            print(res)

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

    verificador({"frecuencia": q_a, "presion": q_b, "oxigeno": q_c}, total)

    proc_a.join()
    proc_b.join()
    proc_c.join()

if __name__ == "__main__":
    main()
