
import os

fifo_write = "/tmp/chat2to1"
fifo_read = "/tmp/chat1to2"

if not os.path.exists(fifo_write):
    os.mkfifo(fifo_write)

if not os.path.exists(fifo_read):
    os.mkfifo(fifo_read)


# Leer primero
with open(fifo_read, 'r') as fr:
    mensaje = fr.readline().strip()
    print(f"Otro: {mensaje}")

# Escribir respuesta
with open(fifo_write, 'w') as fw:
    msg = input("Vos: ")
    fw.write(msg + '\n')
    fw.flush()