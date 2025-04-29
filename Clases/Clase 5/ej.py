from multiprocessing import Process, Queue

def worker(q):
    q.put("Mensaje del proceso hijo")

if __name__ == "__main__":
    cola = Queue()
    p = Process(target=worker, args=(cola,))
    p.start()
    print(cola.get())  # Imprime: "Mensaje del proceso hijo"
    p.join()