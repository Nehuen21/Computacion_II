import multiprocessing as mp
from collections import deque
from datetime import datetime
import random
import time
import statistics


# =====================
# Funciones de análisis
# =====================
def analizador_frecuencia(conn, ventana, cola_salida):
    """Analiza frecuencia cardíaca."""
    buffer = deque(maxlen=ventana)
    while True:
        paquete = conn.recv()
        if paquete is None:
            break
        buffer.append(paquete["frecuencia"])
        media = statistics.mean(buffer)
        desv = statistics.pstdev(buffer) if len(buffer) > 1 else 0.0
        cola_salida.put({
            "tipo": "frecuencia",
            "timestamp": paquete["timestamp"],
            "media": media,
            "desv": desv
        })


def analizador_presion(conn, ventana, cola_salida):
    """Analiza presión arterial (solo sistólica para ejemplo)."""
    buffer = deque(maxlen=ventana)
    while True:
        paquete = conn.recv()
        if paquete is None:
            break
        sistolica = paquete["presion"][0]
        buffer.append(sistolica)
        media = statistics.mean(buffer)
        desv = statistics.pstdev(buffer) if len(buffer) > 1 else 0.0
        cola_salida.put({
            "tipo": "presion",
            "timestamp": paquete["timestamp"],
            "media": media,
            "desv": desv
        })


def analizador_oxigeno(conn, ventana, cola_salida):
    """Analiza saturación de oxígeno."""
    buffer = deque(maxlen=ventana)
    while True:
        paquete = conn.recv()
        if paquete is None:
            break
        buffer.append(paquete["oxigeno"])
        media = statistics.mean(buffer)
        desv = statistics.pstdev(buffer) if len(buffer) > 1 else 0.0
        cola_salida.put({
            "tipo": "oxigeno",
            "timestamp": paquete["timestamp"],
            "media": media,
            "desv": desv
        })


# =====================
# Proceso principal
# =====================
def main(samples=60, ventana=30):
    # Creación de colas de salida
    cola_frec = mp.Queue()
    cola_pres = mp.Queue()
    cola_oxi = mp.Queue()

    # Creación de Pipes unidireccionales (padre -> hijo)
    child_a, parent_a = mp.Pipe(duplex=False)  # hijo lee, padre escribe
    child_b, parent_b = mp.Pipe(duplex=False)
    child_c, parent_c = mp.Pipe(duplex=False)

    # Lanzar procesos de análisis
    p_a = mp.Process(target=analizador_frecuencia, args=(child_a, ventana, cola_frec), name="Proc-A-Frecuencia")
    p_b = mp.Process(target=analizador_presion, args=(child_b, ventana, cola_pres), name="Proc-B-Presion")
    p_c = mp.Process(target=analizador_oxigeno, args=(child_c, ventana, cola_oxi), name="Proc-C-Oxigeno")

    p_a.start()
    p_b.start()
    p_c.start()

    # Generar datos simulados
    for _ in range(samples):
        paquete = {
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "frecuencia": random.randint(60, 180),
            "presion": [random.randint(110, 180), random.randint(70, 110)],
            "oxigeno": random.randint(90, 100)
        }

        parent_a.send(paquete)
        parent_b.send(paquete)
        parent_c.send(paquete)

        time.sleep(1)

    # Enviar señal de terminación a los hijos
    parent_a.send(None)
    parent_b.send(None)
    parent_c.send(None)

    # Esperar que terminen
    p_a.join()
    p_b.join()
    p_c.join()

    # Mostrar resultados acumulados de las colas
    print("\n--- Resultados finales ---")
    while not cola_frec.empty():
        print(cola_frec.get())
    while not cola_pres.empty():
        print(cola_pres.get())
    while not cola_oxi.empty():
        print(cola_oxi.get())


if __name__ == "__main__":
    main()
