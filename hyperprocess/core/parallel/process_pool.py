"""
Process Pool implementation for HyperProcess.

Provides a high-level, context-managed API for multiprocessing
using ProcessPoolExecutor under the hood.
"""
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, Future
from multiprocessing import get_context, cpu_count
from typing import Any, Callable, Iterable, Iterator, Optional, TypeVar, List
from collections.abc import Sized
from contextlib import AbstractContextManager

T = TypeVar("T")
R = TypeVar("R")


class Pool(ProcessPoolExecutor, AbstractContextManager):
    """
    A context-managed process pool supporting sync and async map/apply.
    """

    def __init__(
        self,
        processes: Optional[int] = None,
        initializer: Optional[Callable] = None,
        initargs: tuple = (),
        maxtasksperchild: Optional[int] = None,
        start_method: str = 'spawn'
    ):
        # Determine number of workers
        self._max_workers = processes or cpu_count()
        # Obtain a multiprocessing context
        ctx = get_context(start_method)
        super().__init__(
            max_workers=self._max_workers,
            mp_context=ctx,
            initializer=initializer,
            initargs=initargs
        )
        self._maxtasks = maxtasksperchild

    def __enter__(self) -> "Pool":
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
        func: Callable[..., R],
        iterable: Iterable[T],
        timeout: Optional[float] = None,
        chunksize: Optional[int] = 1
    ) -> List[R]:
        """
        Synchronous map with optional timeout and chunk sizing.
        """
        if chunksize is None:
            chunksize = _calculate_chunksize(iterable, self._max_workers)
        return list(super().map(func, iterable, timeout=timeout, chunksize=chunksize))

    def map_async(
        self,
        func: Callable[[T], R],
        iterable: Iterable[T],
        callback: Optional[Callable[[List[R]], None]] = None,
        timeout: Optional[float] = None,
        chunksize: Optional[int] = None
    ) -> Future:
        """
        Asynchronous map: returns a Future whose result() is the list.
        Optionally execute a callback once done.
        """
        if chunksize is None:
            chunksize = _calculate_chunksize(iterable, self._max_workers)
        future = super().submit(lambda data: list(data),
                                super().map(func, iterable, timeout=timeout))
        if callback:
            def _on_complete(fut: Future):
                callback(fut.result())
            future.add_done_callback(_on_complete)
        return future

    def apply(
        self,
        func: Callable[..., R],
        *args: Any,
        timeout: Optional[float] = None,
        **kwargs: Any
    ) -> R:
        """
        Synchronous apply: runs func(*args, **kwargs) in a worker.
        """
        return self.apply_async(func, *args, **kwargs).result(timeout)

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
        iterable: Iterable[T],
        chunksize: Optional[int] = None
    ) -> Iterator[R]:
        """
        Iterator yielding results as soon as they are ready (unordered).
        """
        # Use underlying ProcessPoolExecutor's map to drive order,
        # but unwrap futures to yield in completion order.
        futures = [self.submit(func, item) for item in iterable]
        for fut in concurrent.futures.as_completed(futures):
            yield fut.result()


def _calculate_chunksize(
    iterable: Iterable,
    workers: int
) -> int:
    """
    Determine a sensible chunksize for map operations.
    """
    if isinstance(iterable, Sized):
        length = len(iterable)
        chunksize, extra = divmod(length, workers * 4)
        return chunksize + 1 if extra else max(1, chunksize)
    return 1
