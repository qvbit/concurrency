from threading import Condition, current_thread, Thread
import time
import random


class BlockingQueue:
    def __init__(self, max_size):
        self.max_size = max_size
        self.curr_size = 0
        self.cond = Condition()
        self.q = []

    def enqueue(self, item):
        self.cond.acquire()  # Make sure to acquire lock before checking curr_size
        while self.curr_size == self.max_size:
            self.cond.wait()
        self.q.append(item)
        self.curr_size += 1
        self.cond.notify_all()  # Notifies any waiting consumers blocked on empty queue
        self.cond.release()

    def dequeue(self):
        self.cond.acquire()
        while self.curr_size == 0:
            self.cond.wait()

        item = self.q.pop(0)
        self.curr_size -= 1

        self.cond.notify_all()  # Notifies any waiting producers blocked on full queue
        self.cond.release()

        return item


def consumer_thread(q: BlockingQueue):
    while True:
        item = q.dequeue()
        print(f"Thread {current_thread().name} consumed item {item}")
        time.sleep(random.randint(1, 3))


def producer_thread(q: BlockingQueue, item):
    while True:
        q.enqueue(item)
        item += 1
        time.sleep(0.1)


if __name__ == "__main__":
    bq = BlockingQueue(5)

    consumer_thread_1 = Thread(
        target=consumer_thread, name="consumer-1", args=(bq,), daemon=True
    )
    consumer_thread_2 = Thread(
        target=consumer_thread, name="consumer-2", args=(bq,), daemon=True
    )
    producer_thread_1 = Thread(
        target=producer_thread, name="producer-1", args=(bq, 1), daemon=True
    )
    producer_thread_2 = Thread(
        target=producer_thread, name="producer-2", args=(bq, 1000), daemon=True
    )

    consumer_thread_1.start()
    consumer_thread_2.start()
    producer_thread_1.start()
    producer_thread_2.start()

    time.sleep(15)
    print("Main thread exiting!")
