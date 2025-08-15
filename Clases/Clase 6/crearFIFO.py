import os
# Crear fifo
fifo_path = "/tmp/mi_fifo"

 # Permisos

# Editar fifo (proceso escritor)

with open(fifo_path,"w") as fifo :
    fifo.write("Hola desde el escritor!/n")

# Leer del FIFO (proceso lector)

with open(fifo_path,"r") as fifo:
    data = fifo.read()
    print("Lector recibido", data)