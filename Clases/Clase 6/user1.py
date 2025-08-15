import os

fifo_write = "/tmp/chat1to2"
fifo_read = "/tmp/chat2to1"

if not os.path.exists(fifo_write):
    os.mkfifo(fifo_write)

if not os.path.exists(fifo_read):
    os.mkfifo(fifo_read)


# Enviar mensaje
with open(fifo_write, 'w') as fw:
    msg = input("Vos: ")
    fw.write(msg + '\n')
    fw.flush()

# Leer respuesta
with open(fifo_read, 'r') as fr:
    respuesta = fr.readline().strip()
    print(f"Otro: {respuesta}")