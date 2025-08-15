# Sistema Concurrente de Análisis Biométrico con Cadena de Bloques Local

## Descripción
Sistema distribuido que simula la captura y análisis de datos biométricos en tiempo real y los almacena en una **cadena de bloques local** (`blockchain.json`).  

- **Tarea 1:** Genera 60 muestras simuladas (frecuencia, presión sistólica/diastólica y oxígeno), procesadas por analizadores concurrentes mediante Pipes, calculando media y desviación en una ventana de 30 segundos.  
- **Tarea 2:** Un verificador recibe los resultados mediante Queues, construye bloques con alertas si hay valores fuera de rango y los encadena con hash SHA-256.  
- **Tarea 3:** El script `verificar_cadena.py` valida la integridad de la cadena y genera `reporte.txt` con promedios y alertas.

## Estructura de Archivos

TP_1/
├── main.py # Tareas 1 y 2: generación, análisis y blockchain
├── verificar_cadena.py # Tarea 3: verificación de integridad y reporte
├── blockchain.json # Generado por main.py
├── reporte.txt # Generado por verificar_cadena.py
└── README.md # Este archivo


## Requisitos

- Python ≥ 3.9

## Uso

1. Ejecutar `main.py` para generar la cadena de bloques:

```bash
python3 main.py

Ejecutar verificar_cadena.py para validar la cadena y generar el reporte:
python3 verificar_cadena.py

Notas

Cada bloque incluye media, desviación y flag de alerta si los valores están fuera de rango.

La cadena se valida mediante SHA-256 para garantizar integridad.

Se usan Pipes y Queues para comunicación concurrente entre procesos, y todos se cierran correctamente.