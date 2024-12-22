import functools
import queue
import threading

def timeout(time_args):
    def _timeout(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            q = queue.Queue(maxsize=1)
            def run():
                try:
                    result = func(*args, **kwargs)
                    q.put((result,None))
                except Exception as e:
                    exception = e
                    q.put((None,exception))
            thread = threading.Thread(target=run)
            thread.start()
            thread.join(time_args)
            if thread.is_alive():
                raise Exception("Function call timed out.")
            result, exception = q.get()
            if exception:
                raise exception
            return result
        return wrapper
    return _timeout