import signal
import time
import os
def handler(signum, frame):
    print(f"Señal {signum} recibida!")

# Registrar handler para SIGUSR1 (10 en sistemas UNIX)
signal.signal(signal.SIGUSR1, handler)

print(f"PID: {os.getpid()} - Esperando señales...")
time.sleep(30)  # Da tiempo para enviar SIGUSR1 desde otra terminal