import time
from threading import Thread, Semaphore, Lock

SIZE = 5
BUFFER = ["" for i in range(SIZE)]  # Shared buffer
producer_idx = 0
mutex = Lock()
empty = Semaphore(SIZE)
filled = Semaphore(0)


class Producer(Thread):
    def __init__(self, name, max_items=5):
        super().__init__()
        self.counter = 0
        self.name = name
        self.max_items = max_items

    @staticmethod
    def next_index(index):
        return (index + 1) % SIZE

    def run(self):
        global producer_idx
        while self.counter < self.max_items:
            empty.acquire()  # I.e. there is at least one empty slot in buffer
            mutex.acquire()  # Guard buffer from concurrent access
            self.counter += 1
            BUFFER[producer_idx] = f"{self.name} - {self.counter}"
            print(
                f"{self.name} produced: "
                f"'{BUFFER[producer_idx]}' into slot {producer_idx}"
            )
            producer_idx = self.next_index(producer_idx)
            mutex.release()
            filled.release()  # A new item has been added to the buffer so there is one more filled slot
            time.sleep(1)


class Consumer(Thread):
    def __init__(self, name, max_items=10):
        super().__init__()
        self.name = name
        self.idx = 0
        self.counter = 0
        self.max_items = max_items

    def next_index(self):
        return (self.idx + 1) % SIZE

    def run(self):
        while self.counter < self.max_items:
            filled.acquire()  # Must be at least one filled slot to continue
            mutex.acquire()
            item = BUFFER[self.idx]
            print(f"{self.name} consumed item: " f"'{item}' from slot {self.idx}")
            self.idx = self.next_index()
            self.counter += 1
            mutex.release()
            empty.release()  # A new empty slot is available, release to increment by one
            time.sleep(2)


if __name__ == "__main__":
    threads = [Producer("SpongeBob"), Producer("Patrick"), Consumer("Squidward")]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
