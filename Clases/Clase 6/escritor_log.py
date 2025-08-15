import os
import time

fifo_path = "/tmp/log_fifo"

# Verificar si el FIFO existe antes de crearlo
if not os.path.exists(fifo_path):
    os.mkfifo(fifo_path, 0o600)
    print("FIFO creado correctamente.")
else:
    print("El FIFO ya existe. Reutilizando...")

with open(fifo_path, "w") as fifo:
    for i in range(3):
        mensaje = f"Log {i}: Hora {time.ctime()}\n"
        fifo.write(mensaje)
        print(f"Mensaje {i} enviado.")
        time.sleep(1)