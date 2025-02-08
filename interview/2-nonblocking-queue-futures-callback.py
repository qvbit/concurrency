import time
import random
from threading import RLock, Thread, current_thread
from concurrent.futures import Future


# Approach 2: Use a future to keep track of requests when queue is full or empty
class NonBlockingQueue:
    def __init__(self, max_size):
        self.max_size = max_size
        self.q = []
        self.q_waiting_puts = []
        self.q_waiting_gets = []
        self.lock = (
            RLock()
        )  # CRITICAL TO USE RLOCK TO PREVENT DEADLOCK HERE. See educative for why

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
                future = Future()
                self.q_waiting_gets.append(future)

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
                    self.q_waiting_gets.pop(0).set_result(self.q.pop(0))
            else:  # Queue is full, so create a future for a put request
                future = Future()
                self.q_waiting_puts.append(future)

        return future


def consumer_thread(q):
    while True:
        item, future = q.dequeue()

        if item is None:
            future.add_done_callback(retry_dequeue)
        else:
            print(f"{current_thread().name} consumed item {item}")

        # slow down consumer thread
        time.sleep(random.randint(1, 3))


def producer_thread(q):
    item = 1
    while True:
        future = q.enqueue(item)
        if future is not None:
            future.item = item
            future.q = q
            future.add_done_callback(retry_enqueue)
        item += 1
        # slow down the producer
        time.sleep(random.randint(1, 3))


def retry_enqueue(future):
    item = future.item
    q = future.q
    new_future = q.enqueue(item)

    # Just do it again lol.. but can't this continue infinitely.. bad code
    if new_future is not None:
        future.item = item
        future.q = q
        future.add_done_callback(retry_enqueue)
    else:
        print("\n{0} successfully added on a retry".format(item))


def retry_dequeue(future):
    item = future.result()
    print(
        f"retry_dequeue executed by thread {current_thread().name} and {item} consumed on a retry"
    )


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
