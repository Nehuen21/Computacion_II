import signal

class SignalLogger:
    def __init__(self):
        self.received = False
    
    def handler(self, signum, frame):
        self.received = True

logger = SignalLogger()
signal.signal(signal.SIGUSR2, logger.handler)

# En otro proceso o terminal:
# os.kill(<PID>, signal.SIGUSR2)