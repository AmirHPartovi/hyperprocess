from __future__ import annotations
import os
import sys
import signal
import warnings
import multiprocessing as mp
from pickle import Pickler
import copyreg
from typing import Any, Callable, Dict, Tuple, Type, Optional
from functools import partial


class ForkingPickler(Pickler):
    """
    A Pickler subclass with its own dispatch_table, used by hyperprocess
    to support pickling of methods, partials, and other callables.
    """
    # type: ignore[attr-defined
    dispatch_table: Dict[
        Type[Any],
        Callable[[Any], Tuple[Callable, Tuple[Any, ...]]]
    ] = copyreg.dispatch_table.copy() 

    dispatch = Pickler.dispatch.copy()

    @classmethod
    def register(
        cls,
        typ: Type[Any],
        reduce_func: Callable[[Any], Tuple[Callable, Tuple[Any, ...]]]
    ) -> None:
        """
        Register a reduction function for `typ` in this pickler's dispatch_table.
        """
        cls.dispatch_table[typ] = reduce_func

        def dispatcher(self: ForkingPickler, obj: Any) -> None:
            rv = reduce_func(obj)
            self.save_reduce(obj=obj, *rv)
        cls.dispatch[typ] = dispatcher


# Get multiprocessing context
ctx = mp.get_context()
Popen = ctx.Process._Popen

if sys.platform == 'darwin' and ctx.get_start_method() == 'fork':
    warnings.warn(
        "Using 'fork' start method on macOS is unsafe; "
        "consider using 'spawn' or 'forkserver'",
        UserWarning
    )

__all__ = ['Popen', 'assert_spawning', 'exit',
           'duplicate', 'close', 'ForkingPickler']

# System functions
exit = os._exit
duplicate = os.dup
close = os.close


def assert_spawning(self: Any) -> None:
    """Raise RuntimeError if not currently spawning a new process."""
    if not Popen.thread_is_spawning():
        raise RuntimeError(
            f"{type(self).__name__} objects should only be shared "
            "between processes through inheritance"
        )


def _reduce_method(m: Any) -> tuple[Any, tuple[Any, ...]]:
    """Reduce method objects for pickling."""
    return getattr, (m.__self__ or m.__objclass__, m.__name__)


def _rebuild_partial(
    func: Callable,
    args: tuple[Any, ...],
    keywords: Optional[dict[str, Any]]
) -> partial:
    """Rebuild partial objects from pickled state."""
    return partial(func, *args, **(keywords or {}))


def _reduce_partial(p: partial) -> tuple[Any, tuple[Any, ...]]:
    """Reduce partial objects for pickling."""
    return _rebuild_partial, (p.func, p.args, p.keywords)


# Register reduction functions
ForkingPickler.register(type(ForkingPickler.save), _reduce_method)
ForkingPickler.register(type(list.append), _reduce_method)
ForkingPickler.register(type(int.__add__), _reduce_method)
ForkingPickler.register(partial, _reduce_partial)
