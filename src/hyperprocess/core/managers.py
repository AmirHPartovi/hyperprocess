from __future__ import annotations
import queue
import threading
import multiprocessing
from multiprocessing.managers import SyncManager
from typing import Any, Optional, Tuple

__all__ = ['HyperSyncManager', 'get_manager']



class HyperSyncManager(SyncManager):
    """
    A SyncManager subclass for Hyperprocess providing shared
    Queue, Lock, Event, Semaphore, Value, Array, and Namespace.
    """
    pass


    # pylint: disable=no-member

# FIFO queue :contentReference[oaicite:5]{index=5}
HyperSyncManager.register('Queue', queue.Queue)
# Mutex lock
HyperSyncManager.register('Lock', threading.Lock)
# Reentrant lock
HyperSyncManager.register('RLock', threading.RLock)
# Counting semaphore
HyperSyncManager.register('Semaphore', threading.Semaphore)
HyperSyncManager.register(
    'BoundedSemaphore', threading.BoundedSemaphore)   # Bounded semaphore
# Event flag
HyperSyncManager.register('Event', threading.Event)
# Condition variable
HyperSyncManager.register('Condition', threading.Condition)
# Simple namespace :contentReference[oaicite:6]{index=6}
HyperSyncManager.register('Namespace', dict)
# Shared ctypes Value :contentReference[oaicite:7]{index=7}
HyperSyncManager.register('Value', multiprocessing.Value)
# Shared ctypes Array
HyperSyncManager.register('Array', multiprocessing.Array)




def get_manager(
    address: Optional[Tuple[str, int]] = None,
    authkey: Optional[bytes] = None,
    **start_kwargs: Any
) -> HyperSyncManager:
    """
    Create and start a HyperSyncManager, returning the manager instance.
    
    :param address: (host, port) for manager server; if None, picks arbitrary free port
    :param authkey: bytes key for HMAC authentication
    :param start_kwargs: passed to manager.start(), e.g. daemon=True
    :returns: a started HyperSyncManager
    """
    mgr = HyperSyncManager(address=address, authkey=authkey)
    # spawn the server process :contentReference[oaicite:8]{index=8}
    mgr.start(**start_kwargs)
    return mgr
