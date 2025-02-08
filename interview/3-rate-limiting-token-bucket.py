import time
from threading import Lock, current_thread, Thread, Condition
from datetime import datetime


# Approach 1: Don't use a thread to add tokens to bucket, just keep track of last request and calculate how many
# tokens are currently available!
class TokenBucketFilter:
    def __init__(self, max_tokens):
        self.max_tokens = max_tokens
        self.last_request_time = time.time()
        self.current_tokens = 0
        self.lock = Lock()

    def get_token(self):
        with self.lock:
            tokens_added_since_last_request = int(time.time() - self.last_request_time)

            self.current_tokens = min(
                self.current_tokens + tokens_added_since_last_request, self.max_tokens
            )

            if self.current_tokens > 0:
                self.current_tokens -= 1
            else:  # i.e. no tokens available, wait 1s so there will be a token and continue
                time.sleep(1)

            self.last_request_time = time.time()
            print(f"Granting {current_thread().name} token at {str(datetime.now())}")


# Approach 2: Use a daemon(background) thread to add tokens to bucket at fixed rate
class TokenBucketFactory:
    @staticmethod
    def make_token_bucket(capacity):
        tbf = MultithreadedTokenBucketFilter(capacity)
        tbf.initialize()
        return tbf


class MultithreadedTokenBucketFilter(TokenBucketFilter):
    def __init__(self, max_tokens):
        self.max_tokens = max_tokens
        self.current_tokens = 0
        self.cond = Condition()

    def initialize(self):
        dt = Thread(target=self.daemon_thread)
        dt.daemon = True
        dt.start()

    def daemon_thread(self):
        while True:
            self.cond.acquire()
            if self.current_tokens < self.max_tokens:
                self.current_tokens += 1
            # We just want to notify one dude waiting! Not all! This works because we only have user threads waiting
            # on tokens, so no chance of deadlock
            self.cond.notify()
            self.cond.release()

            time.sleep(1)

    def get_token(self):
        self.cond.acquire()
        while self.current_tokens == 0:
            self.cond.wait()
        self.current_tokens -= 1
        self.cond.release()

        print(f"Granting {current_thread().name} token at {str(datetime.now())}")


if __name__ == "__main__":

    # token_bucket_filter = TokenBucketFilter(1)
    token_bucket_filter = TokenBucketFactory.make_token_bucket(1)

    threads = []
    for _ in range(10):
        threads.append(Thread(target=token_bucket_filter.get_token))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
