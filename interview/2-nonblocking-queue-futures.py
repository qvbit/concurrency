import time
import random
from threading import Lock, Thread, current_thread
from concurrent.futures import Future


# Approach 2: Use a future to keep track of requests when queue is full or empty
class NonBlockingQueue:
    def __init__(self, max_size):
        self.max_size = max_size
        self.q = []
        self.q_waiting_puts = []
        self.q_waiting_gets = []
        self.lock = Lock()

    def dequeue(self):
        result = None
        future = None

        with self.lock:
            curr_size = len(self.q)

            if curr_size != 0:
                result = self.q.pop(0)
                # Resolve pending future for put request if one exists
                if len(self.q_waiting_puts) != 0:
                    self.q_waiting_puts.pop(0).set_result(True)
            else:
                # Queue is empty so we create a future for a get request
                self.q_waiting_gets.append(Future())

        # Note how we just return the future and let client handle. All we do is make sure to set it to True
        # once the result is available
        return result, future

    def enqueue(self, item):
        future = None

        with self.lock:
            curr_size = len(self.q)
            if curr_size < self.max_size:
                self.q.append(item)
                # Resolve pending future for get request if one exists
                if len(self.q_waiting_gets) != 0:
                    self.q_waiting_gets.pop(0).set_result(True)
            else:  # Queue is full, so create a future for a put request
                self.q_waiting_puts.append(Future())

        return future


def consumer_thread(q):
    while 1:
        item, future = q.dequeue()

        if item is None:
            print("Consumer received a future but we are ignoring it")
        else:
            print(
                "\n{0} consumed item {1}".format(current_thread().name, item),
                flush=True,
            )

        # slow down consumer thread
        time.sleep(random.randint(1, 3))


def producer_thread(q):
    item = 1
    while 1:
        future = q.enqueue(item)
        if future is not None:
            while not future.done():  # Polling/busy waiting
                print("waiting for future to resolve")
                time.sleep(0.1)
            # Future is done, attempt reequeue now or whatever other logic
        else:
            item += 1


if __name__ == "__main__":
    no_block_q = NonBlockingQueue(5)

    consumerThread1 = Thread(
        target=consumer_thread, name="consumer", args=(no_block_q,), daemon=True
    )
    producerThread1 = Thread(
        target=producer_thread, name="producer", args=(no_block_q,), daemon=True
    )

    consumerThread1.start()
    producerThread1.start()

    time.sleep(15)
    print("Main thread exiting")
