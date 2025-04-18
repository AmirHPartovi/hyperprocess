"""
HyperProcess Custom Decorators

These decorators are tightly coupled with HyperProcess's internal architecture,
utilizing its enhanced pools and shared modules for high-performance and
traceable parallel execution.

Author: Amir Hossein Partovi
"""
import pytest
from hyperprocess.decorators import (
    profile_execution,
    parallelize_plus,
    log_calls,
    use_queue
)
from hyperprocess.core.shared.queues import SafeQueue


def test_profile_execution():
    @profile_execution()
    def slow_func(x):
        return x * 2

    assert slow_func(5) == 10


def test_parallelize_plus_thread():
    @parallelize_plus(mode="thread", max_workers=2)
    def square(x):
        return x * x

    data = [1, 2, 3, 4]
    assert square(data) == [1, 4, 9, 16]


def test_parallelize_plus_process():
    @parallelize_plus(mode="process", max_workers=2)
    def cube(x):
        return x ** 3

    data = [1, 2, 3]
    assert cube(data) == [1, 8, 27]


def test_log_calls(caplog):
    @log_calls()
    def echo(x):
        return x

    with caplog.at_level("INFO"):
        result = echo("hi")
        assert result == "hi"
        assert "called with args" in caplog.text


def test_use_queue():
    queue = SafeQueue()

    @use_queue(queue)
    def produce(x):
        return x + 1

    result = produce(9)
    assert result == 10
    assert queue.get(timeout=1) == 10
