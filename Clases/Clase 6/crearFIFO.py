import os
# Crear fifo
fifo_path = "/tmp/mi_fifo"

os.mkfifo(fifo_path, 0o600) # Permisos

# Editar fifo (proceso escritor)

with open(fifo_path,"w") as fifo :
    fifo.write("Hola desde el escritor!/n")

# Leer del FIFO (proceso lector)

with open(fifo_path,"r") as fifo:
    data = fifo.read()
    print("Lector recibido", data)