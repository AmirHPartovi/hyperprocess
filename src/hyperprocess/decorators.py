"""
HyperProcess Custom Decorators

These decorators are tightly coupled with HyperProcess's internal architecture,
utilizing its enhanced pools and shared modules for high-performance and
traceable parallel execution.

Author: Amir Hossein Partovi
"""

import functools
import time
import logging
from hyperprocess.pool.threadpool import ThreadPoolExecutorPlus
from hyperprocess.pool.processpool import ProcessPoolExecutorPlus
from hyperprocess.core.shared.queues import SafeQueue  # Custom queue if needed
from hyperprocess.core.io.streams import log_event  # Optional centralized logging

logger = logging.getLogger("hyperprocess")
logging.basicConfig(level=logging.INFO)


def profile_execution(log_to_stream=False):
    """
    Measure execution time and optionally log to HyperProcess's I/O stream module.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            message = f"[PROFILE] {func.__name__} ran in {duration:.4f}s"
            logger.info(message)
            if log_to_stream:
                log_event(message)  # Custom logging stream
            return result
        return wrapper
    return decorator


def parallelize_plus(mode="thread", max_workers=None, return_results=True):
    """
    Use HyperProcess-enhanced executors for parallel execution over iterable data.
    
    Args:
        mode (str): 'thread' or 'process'
        max_workers (int): Number of workers.
        return_results (bool): If True, results will be collected and returned.
    
    Usage:
        @parallelize_plus(mode="process")
        def work(x): ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(data_list, *args, **kwargs):
            Executor = ThreadPoolExecutorPlus if mode == "thread" else ProcessPoolExecutorPlus
            results = []
            with Executor(max_workers=max_workers) as executor:
                futures = [executor.submit(
                    func, item, *args, **kwargs) for item in data_list]
                if return_results:
                    for f in futures:
                        results.append(f.result())
            return results if return_results else None
        return wrapper
    return decorator


def log_calls(level=logging.INFO, stream=False):
    """
    Log function calls and arguments. Optionally logs to HyperProcess I/O streams.
    
    Args:
        level (int): Logging level
        stream (bool): Log to HyperProcess stream module
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"[CALL] {func.__name__} called with args={args}, kwargs={kwargs}"
            logger.log(level, msg)
            if stream:
                log_event(msg)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def use_queue(queue: SafeQueue):
    """
    Automatically enqueue the function's result to a shared HyperProcess queue.
    
    Args:
        queue (SafeQueue): Shared queue instance from core.shared.queues
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            queue.put(result)
            return result
        return wrapper
    return decorator
