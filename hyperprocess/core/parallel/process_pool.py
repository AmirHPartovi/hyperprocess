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
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Callable, Iterable, Iterator, Optional, TypeVar
from multiprocessing import get_context, cpu_count
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context, cpu_count
from typing import Optional, Callable, Iterable, Iterator, Any

_T = TypeVar("_T")
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
        self._processes  = processes or cpu_count()
        ctx = get_context(start_method)
        
        super().__init__(
            max_workers=self._processes,
            mp_context=ctx,
            initializer=initializer,
            initargs=initargs
        )
        self._maxtasks = maxtasksperchild
\

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
        fn: Callable[..., _T],
        *iterables: Iterable[Any],
        timeout: float | None = None,
        chunksize: int = 1
    ) -> Iterator[_T]:
        """
            Exactly the same signature as Executor.map,
            but delegates to super().map() using our context.
            """
        return super().map(fn, *iterables,
                           timeout=timeout,
                           chunksize=chunksize)

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
        future = super().submit(lambda seq: list(seq), super().map(
            func, iterable, timeout=timeout, chunksize=chunksize))
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
        Synchronous apply: runs func(*args, **kwargs) in a worker.
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
