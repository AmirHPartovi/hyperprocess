"""
Thread Pool implementation for HyperProcess.

Provides a high-level, context-managed API for threading
using ThreadPoolExecutor under the hood.
"""
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Any, Callable, Iterable, Iterator, Optional, TypeVar, List
from contextlib import AbstractContextManager
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Callable, Iterable, Iterator, Optional, TypeVar
from multiprocessing import get_context, cpu_count

_T = TypeVar("_T")
T = TypeVar("T")
R = TypeVar("R")


class ThreadPool(ThreadPoolExecutor):
    """
    A context-managed thread pool supporting sync and async map/apply.
    """

    def __init__(self,
                 max_workers: int | None = None,
                 initializer: Callable[[], None] | None = None,
                 initargs: tuple = ()):
        super().__init__(max_workers=max_workers,
                         initializer=initializer,
                         initargs=initargs)
        self._maxtasks = maxtasksperchild

    def __enter__(self) -> "ThreadPool":
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_val: Any,
        exc_tb: Any
    ) -> None:
        # Ensure clean shutdown
        self.shutdown(wait=True)


    def map(
        self,
        fn: Callable[..., _T],
        *iterables: Iterable[Any],
        timeout: float | None = None,
        chunksize: int = 1
    ) -> Iterator[_T]:
        """Match Executor.map signature exactly."""
        return super().map(fn, *iterables,
                           timeout=timeout,
                           chunksize=chunksize)

    def map_async(
        self,
        func: Callable[[T], R],
        iterable: Iterable[T],
        callback: Optional[Callable[[List[R]], None]] = None,
        timeout: Optional[float] = None
    ) -> Future:
        """
        Asynchronous map: returns a Future whose result() is the list.
        Optionally execute a callback once done.
        """
        future = super().submit(lambda seq: list(
            seq), super().map(func, iterable, timeout=timeout))
        if callback:
            future.add_done_callback(lambda fut: callback(fut.result()))
        return future

    def apply(
        self,
        func: Callable[..., R],
        *args: Any,
        timeout: Optional[float] = None,
        **kwargs: Any
    ) -> R:
        """
        Synchronous apply: runs func(*args, **kwargs) in a worker thread.
        """
        return self.apply_async(func, *args, timeout=timeout, **kwargs).result(timeout)

    def apply_async(
        self,
        func: Callable[..., R],
        *args: Any,
        callback: Optional[Callable[[R], None]] = None,
        timeout: Optional[float] = None,
        **kwargs: Any
    ) -> Future:
        """
        Asynchronous apply: returns a Future.
        Optionally execute a callback once done.
        """
        future = super().submit(func, *args, **kwargs)
        if callback:
            future.add_done_callback(lambda fut: callback(fut.result()))
        return future

    def imap_unordered(
        self,
        func: Callable[[T], R],
        iterable: Iterable[T]
    ) -> Iterator[R]:
        """
        Iterator yielding results as soon as they are ready (unordered).
        """
        futures = [self.submit(func, item) for item in iterable]
        for fut in concurrent.futures.as_completed(futures):
            yield fut.result()
