"""
HyperProcess - High-performance parallel processing toolkit for Python.

This package provides a unified interface for thread-based and process-based parallelism,
alongside accelerated modules for NumPy, pandas, and scikit-learn operations.

Author: Amir Hossein Partovi
License: Custom License - Free for open-source, commercial license required for enterprise use.
"""

__version__ = "0.1.0"
__author__ = "Amir Hossein Partovi"
__license__ = "Custom - Open Source Friendly"

# Core modules
from .core.cpu import compute
from .core.io import streams
from .core.shared import queues

# Parallel pools
from .pool.threadpool import ThreadPoolExecutorPlus
from .pool.processpool import ProcessPoolExecutorPlus

# Accelerated integrations
from .test_integration.numpy_accel import NumpyAccelerator
from .test_integration.pandas_accel import PandasAccelerator
from .test_integration.sklearn_accel import SklearnAccelerator

# Expose key utilities for direct access
from .decorators import parallelize, profile_execution

__all__ = [
    "compute",
    "streams",
    "queues",
    "ThreadPoolExecutorPlus",
    "ProcessPoolExecutorPlus",
    "NumpyAccelerator",
    "PandasAccelerator",
    "SklearnAccelerator",
    "parallelize",
    "profile_execution",
]
