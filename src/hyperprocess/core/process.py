from __future__ import annotations
import logging
from multiprocessing import Process as _BaseProcess, current_process, freeze_support
from multiprocessing.context import SpawnProcess
from multiprocessing import AuthenticationError
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger(__name__)
__all__ = ['Process', 'current_process']


class Process(_BaseProcess):
    """
    A drop-in replacement for multiprocessing.Process with modern enhancements:
    - Type hints & docstrings
    - Logging for lifecycle events
    - Simplified initialization via super()
    """

    def __init__(
        self,
        target: Optional[Callable[..., Any]] = None,
        args: Tuple[Any, ...] = (),
        kwargs: Optional[Dict[str, Any]] = None,
        *,
        name: Optional[str] = None,
        daemon: Optional[bool] = None
    ) -> None:
        kwargs = kwargs or {}
        super().__init__(target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        logger.debug("Initialized Process(name=%s, daemon=%s)",
                     self.name, self.daemon)

    def run(self) -> None:
        """
        Method invoked in the child process.
        Override this if subclassing directly.
        """
        logger.info("Process %s starting run()", self.name)
        try:
            super().run()
        except Exception as e:
            logger.exception("Exception in process %s: %s", self.name, e)
            raise

    def start(self) -> None:
        """
        Start the process.
        """
        logger.info("Process %s starting", self.name)
        super().start()

    def join(self, timeout: Optional[float] = None) -> None:
        """
        Block until the process finishes or timeout elapses.
        """
        logger.info("Waiting for process %s to finish", self.name)
        super().join(timeout)
        if self.is_alive():
            logger.warning(
                "Process %s is still alive after join(timeout=%s)", self.name, timeout)
        else:
            logger.info("Process %s terminated with exitcode=%s",
                        self.name, self.exitcode)

    def terminate(self) -> None:
        """
        Terminate the process.
        """
        logger.info("Terminating process %s", self.name)
        super().terminate()

    def is_alive(self) -> bool:
        """
        Return whether process is alive.
        """
        alive = super().is_alive()
        logger.debug("Process %s is_alive -> %s", self.name, alive)
        return alive


# Example usage for Windows compatibility
if __name__ == "__main__":
    freeze_support()

    def worker(x):
        print(f"Worker got {x}")

    p = Process(target=worker, args=(42,), name="MyWorker")
    p.start()
    p.join()
