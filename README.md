# HyperProcess

[![License: MIT](https://img.shields.io/badgeLicense-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)![coverage](https://codecov.io/gh/AmirHPartovi/hyperprocess/branch/main/graph/badge.svg)
[![Build Status](https://github.com/YOUR_USERNAME/hyperprocess/actions/workflows/build.yml/badge.svg)](https://github.com/YOUR_USERNAME/hyperprocess/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/hyperprocess/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/hyperprocess)
[![PyPI version](https://badge.fury.io/py/hyperprocess.svg)](https://badge.fury.io/py/hyperprocess)
[![License](https://img.shields.io/github/license/AmirHPartovi/hyperprocess.svg)](https://github.com/AmirHPartovi/hyperprocess/blob/main/LICENSE)

A high-performance Python package for parallel processing and optimization, designed to accelerate CPU-bound and I/O-bound tasks. HyperProcess provides seamless integration with NumPy, pandas, and scikit-learn while offering both thread-based and process-based parallelism.

## 🚀 Features

- **CPU-bound parallelism**: Efficient management of CPU-intensive tasks using ProcessPool
- **I/O-bound parallelism**: Streamlined I/O operations using ThreadPool
- **Task queues**: Advanced task management and synchronization
- **Library acceleration**: Optimized support for NumPy, pandas, and scikit-learn
- **Flexible integration**: Extensible architecture for various libraries

## 📦 Installation

```bash
pip install hyperprocess
```

or install from source:

```bash
git clone https://github.com/yourusername/HyperProcess.git
cd HyperProcess
pip install .
```

## 🔧 Usage

### Basic Example

```python
# CPU-bound tasks
from hyperprocess.core.cpu.compute import compute_task
result = compute_task(data)

# I/O-bound tasks
from hyperprocess.core.io.streams import io_task
result = io_task(data)
```

### Thread and Process Pools

```python
# ThreadPool Example
from hyperprocess.pool.threadpool import ThreadPool

with ThreadPool() as pool:
    results = pool.map(lambda x: x * 2, [1, 2, 3, 4, 5])

# ProcessPool Example
from hyperprocess.pool.processpool import ProcessPool

with ProcessPool() as pool:
    results = pool.map(lambda x: x * 2, [1, 2, 3, 4, 5])
```

### Library Integration

```python
from hyperprocess.integration.numpy_accel import accelerated_function
import numpy as np

data = np.array([1, 2, 3])
result = accelerated_function(data)
```

## 📁 Project Structure

```
hyperprocess/
├── core/                      # Core functionality
├── pool/                      # Pool implementations
├── integration/              # Library integrations
├── tests/                    # Unit tests
└── docs/                     # Documentation
```
## :chart: Flowchart
---
config:
  layout: fixed
---
flowchart LR
    API["api.py"] --> DEC["decorators.py"] & PAR_P["core/parallel/process_pool.py"] & PAR_T["core/parallel/thread_pool.py"] & Q["core/queue.py"] & CONN["core/connection.py"] & MEM["core/shared_memory.py"] & SYNC["core/sync.py"]
    DEC --> CPU["core/cpu/compute.*"] & IO["core/io/io_utils.py"] & PAR_P & PAR_T
    PAR_P --> CPU & IO & MEM & SYNC
    PAR_T --> IO
    Q --> CONN
    MAN["core/managers.py"] --> CONN & RED["core/reduction.py"]
    PR["core/process.py"] --> FORK["core/forking.py"] & RED & MAN
    RED --> CONN & MEM
    SYNC --> MEM
    NP["integration/numpy_integration.py"] --> CPU
    PD["integration/pandas_integration.py"] --> PAR_P & IO
    SK["integration/sklearn_integration.py"] --> CPU & PAR_P
     API:::api
     DEC:::api
     CPU:::core
     IO:::core
     PAR_P:::core
     PAR_T:::core
     Q:::core
     CONN:::core
     PR:::core
     FORK:::core
     RED:::core
     MEM:::core
     SYNC:::core
     MAN:::core
     NP:::intg
     PD:::intg
     SK:::intg
    classDef api fill:#f9f,stroke:#333,stroke-width:1px
    classDef core fill:#9ff,stroke:#333,stroke-width:1px
    classDef intg fill:#ff9,stroke:#333,stroke-width:1px


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📫 Contact

For inquiries, please reach out at: a.partovi99@gmail.com

---

Made with ❤️ by Amir Hossein Partovi
