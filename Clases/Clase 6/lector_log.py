import os
fifo_path = "/tmp/log_fifo"
if not os.path.exists(fifo_path) :
    os.mkfifo(fifo_path,0o600)




fifo_path = "/tmp/log_fifo"

with open(fifo_path, "r") as fifo :
    while True :
        linea = fifo.readline()
        if not linea:
            break
        print("Log recibido", linea.strip())