import queue
import threading
from contextlib import contextmanager


def just_call(worker_queue: queue.Queue, all_put_event: threading.Event):
    while True:
        try:
            fn, args = worker_queue.get(timeout=1)
            fn(*args)
        except queue.Empty:
            if all_put_event.set():
                break


@contextmanager
def threaded(thread_num=16, target=just_call):
    worker_queue = queue.Queue()

    threads = []
    all_put_event = threading.Event()
    for _ in range(thread_num):
        thread = threading.Thread(
            target=target,
            args=(worker_queue, all_put_event)
        )
        threads.append(thread)

    for thread in threads:
        thread.start()

    yield worker_queue
    all_put_event.set()

    for thread in threads:
        thread.join()
