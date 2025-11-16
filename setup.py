from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="api2pydantic",
    version="0.1.0",
    author="Sornalingam",
    author_email="devcode1992@gmail.com",
    description="Automatically generate Pydantic models from API responses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/codedev1992/api2pydantic",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "requests>=2.28.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "api2pydantic=api2pydantic.cli:main",
        ],
    },
    keywords="pydantic api json schema generator code-generation",
    project_urls={
        "Bug Reports": "https://github.com/codedev1992/api2pydantic/issues",
        "Source": "https://github.com/codedev1992/api2pydantic",
    },
)
