"""
Process Pool implementation for HyperProcess.

Provides a high-level, context-managed API for multiprocessing
using ProcessPoolExecutor under the hood.
"""
from concurrent.futures import ProcessPoolExecutor, Future
import concurrent.futures
from multiprocessing import get_context, cpu_count
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Optional,
    TypeVar,
    List,
    Tuple
)
from collections.abc import Sized
from contextlib import AbstractContextManager

# Define type variables
T = TypeVar('T')
R = TypeVar('R')
_T = TypeVar('_T')


class Pool(ProcessPoolExecutor, AbstractContextManager):
    """
    A context-managed process pool supporting sync and async map/apply.
    """

    def __init__(
        self,
        processes: Optional[int] = None,
        initializer: Optional[Callable[..., Any]] = None,
        initargs: Tuple[Any, ...] = (),
        max_tasks_per_child: Optional[int] = None,
        start_method: str = 'spawn'
    ):
        """
        Custom ProcessPoolExecutor with support for initializer and initargs.

        :param processes: Number of worker processes to use. Defaults to the number of CPU cores.
        :param initializer: A callable invoked by each worker process when it starts.
        :param initargs: A tuple of arguments passed to the initializer.
        :param max_tasks_per_child: Maximum number of tasks a worker process can execute before it will exit and be replaced.
        :param start_method: Method used to start the worker processes. Common values are 'fork', 'spawn', or 'forkserver'.
        """
        max_workers = processes or cpu_count()
        ctx = get_context(start_method)
        super().__init__(
            max_workers=max_workers,
            mp_context=ctx,
            initializer=initializer,
            initargs=initargs,
            max_tasks_per_child=max_tasks_per_child
        )

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
        timeout: Optional[float] = None,
        chunksize: int = 1
    ) -> Iterator[_T]:
        """
        Apply a function to every item of the given iterables, yielding the results.

        :param fn: The function to apply to the items.
        :param iterables: One or more iterable arguments that supply the data to process.
        :param timeout: The maximum number of seconds to wait. If None, then there is no limit.
        :param chunksize: The size of the chunks the iterable will be split into and submitted to the process pool.
        :return: An iterator equivalent to map(fn, *iterables) but the calls may be evaluated out-of-order.
        """
        return super().map(fn, *iterables, timeout=timeout, chunksize=chunksize)

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
