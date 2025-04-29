### ¿Qué son las señales y por qué son importantes?

- Explicación teórica
Las señales son interrupciones software enviadas a un proceso por el kernel o por otros procesos. Su función principal es notificar eventos importantes, como:

- Errores críticos (ej. `SIGSEGV` por acceso inválido a memoria)

- Solicitudes de terminación (ej. `SIGINT` por Ctrl+C)

- Eventos de tiempo (ej. `SIGALRM`)

- Comunicación entre procesos (IPC básico)

---

- Tipos de señales:

- Síncronas: Generadas por acciones del propio proceso (ej. `SIGFPE` por división por cero).

- Asíncronas: Provienen de eventos externos (ej. `SIGTERM` enviado con kill).

- Tiempo Real (`SIGRTMIN` a `SIGRTMAX`): Permiten colas de señales y priorización.

No todas las señales son capturables (ej. `SIGKILL`).
---

1) ¿Por qué SIGKILL y SIGSTOP no pueden ser ignorados?

El sistema operativo garantiza control absoluto sobre procesos. Por ejemplo:

`SIGKILL` (9) termina un proceso de inmediato (útil para detener procesos bloqueados).

`SIGSTOP` (19) pausa un proceso para depuración o gestión de recursos.


2) ¿Qué sucede si una señal asíncrona llega mientras se ejecuta el handler?

Por defecto, el handler no es reentrante, y la señal se marca como pendiente pero no se procesa hasta que termine el handler actual.

---


# kill (en C/Python):
Función para enviar una señal a un proceso (no necesariamente para "matarlo").

En Python: os.kill(pid, signal)

Ejemplo: os.kill(pid, signal.SIGUSR1) envía SIGUSR1 al proceso con ID pid.

# sigqueue (solo en C):
Envía una señal junto con datos adicionales (un entero o puntero). Útil para señales en tiempo real (SIGRT).

No existe en Python estándar, pero se puede emular con otros métodos de IPC (ej. shared memory).

# sigaction (en C):
Reemplaza a signal() para manejo más robusto de señales. Permite:

Definir handlers con contexto (siginfo_t).

Bloquear señales durante la ejecución del handler.

Especificar flags como SA_RESTART (reiniciar syscalls interrumpidos).

# Señales no bloqueables
- Casos especiales
        1_ SIGKILL (9): Terminación inmediata del proceso.

        2_ SIGSTOP (19): Pausa la ejecución del proceso.

¿Por qué no pueden ignorarse?
Diseño del sistema operativo: Mantener control sobre procesos "rebeldes".

Seguridad: Evitar que procesos maliciosos eviten su terminación.