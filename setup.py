from setuptools import setup, find_packages

# This function will be used to create the setup file for the HyperProcess package.
# It specifies the necessary metadata and dependencies for the package.

setup(
    # The name of the package. This should be unique if you are publishing it to PyPI.
    name='hyperprocess',
    version='0.1.0',  # The initial release version of the package.
    # A short description of the package.
    description='A Python package for parallel processing and optimization.',
    # This will load the content of the README.md as the long description.
    long_description=open('README.md').read(),
    # Specifies the format of the long description.
    long_description_content_type='text/markdown',
    author='Amir Hossein Partovi',  # The author of the package.
    # The author's email address. This will be used for contacting in case of issues.
    author_email='amir@example.com',
    # The URL to the project on GitHub (or other repository).
    url='https://github.com/yourusername/HyperProcess',
    # Automatically discover and include all packages and sub-packages in the project.
    packages=find_packages(),
    classifiers=[  # Classifiers help users find your package on PyPI.
        # Specifies Python 3 compatibility.
        'Programming Language :: Python :: 3',
        # Compatibility with Python 3.7.
        'Programming Language :: Python :: 3.7',
        # Compatibility with Python 3.8.
        'Programming Language :: Python :: 3.8',
        # Compatibility with Python 3.9.
        'Programming Language :: Python :: 3.9',
        # Compatibility with Python 3.10.
        'Programming Language :: Python :: 3.10',
        # License used for the package.
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',  # The package is OS-independent.
    ],
    python_requires='>=3.7',  # The minimum Python version required.
    install_requires=[  # List of dependencies that need to be installed alongside the package.
        'numpy>=1.20.0',  # Specifies that NumPy is a required dependency.
        'pandas>=1.2.0',  # Specifies that pandas is a required dependency.
        # Specifies that scikit-learn is a required dependency.
        'scikit-learn>=0.24.0',
    ],
    extras_require={  # Optional extra dependencies that can be installed for additional features.
        'dev': [
            'pytest>=6.2.0',  # For running tests during development.
            'sphinx>=4.0.0',  # For generating documentation.
        ],
        'docs': [
            'sphinx>=4.0.0',  # For generating documentation.
        ],
    },
    test_suite='tests',  # The directory containing the tests for the package.
    tests_require=[  # List of test dependencies.
        'pytest>=6.2.0',  # For running the unit tests.
    ],
    # This ensures that any non-Python files in your package are included.
    include_package_data=True,
    # Indicates whether the package can be reliably used if zipped (False means it's not guaranteed).
    zip_safe=False,
)
