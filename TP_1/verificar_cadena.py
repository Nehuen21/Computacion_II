import json
import hashlib

def recalcular_hash(prev_hash, bloque_datos, timestamp):
    contenido = str(prev_hash) + str(bloque_datos) + timestamp
    return hashlib.sha256(contenido.encode()).hexdigest()

def main():
    try:
        with open("blockchain.json", "r") as f:
            blockchain = json.load(f)
    except FileNotFoundError:
        print("Error: blockchain.json no existe. Ejecuta primero main.py")
        return

    bloques_corruptos = []
    total_bloques = len(blockchain)
    suma_frecuencia = 0
    suma_presion = 0
    suma_oxigeno = 0
    count_alertas = 0

    for i, bloque in enumerate(blockchain):
        # Verificar hash
        prev_hash = "0" if i == 0 else blockchain[i-1]["hash"]
        recalculado = recalcular_hash(prev_hash, bloque["datos"], bloque["timestamp"])
        if recalculado != bloque["hash"] or bloque["prev_hash"] != prev_hash:
            bloques_corruptos.append(i)

        # Acumular para promedios
        suma_frecuencia += bloque["datos"]["frecuencia"]["media"]
        suma_presion += bloque["datos"]["presion"]["media"]
        suma_oxigeno += bloque["datos"]["oxigeno"]["media"]
        if bloque["alerta"]:
            count_alertas += 1

    # Calcular promedios
    promedio_frecuencia = suma_frecuencia / total_bloques if total_bloques else 0
    promedio_presion = suma_presion / total_bloques if total_bloques else 0
    promedio_oxigeno = suma_oxigeno / total_bloques if total_bloques else 0

    # Guardar reporte
    with open("reporte.txt", "w") as f:
        f.write(f"Cantidad total de bloques: {total_bloques}\n")
        f.write(f"Número de bloques con alertas: {count_alertas}\n")
        f.write(f"Promedio general de frecuencia: {promedio_frecuencia:.2f}\n")
        f.write(f"Promedio general de presión: {promedio_presion:.2f}\n")
        f.write(f"Promedio general de oxígeno: {promedio_oxigeno:.2f}\n")
        f.write(f"Bloques corruptos: {bloques_corruptos if bloques_corruptos else 'Ninguno'}\n")

    print("Verificación completada. Reporte guardado en reporte.txt")
    if bloques_corruptos:
        print(f"Bloques corruptos: {bloques_corruptos}")
    else:
        print("La cadena de bloques es íntegra.")

if __name__ == "__main__":
    main()
