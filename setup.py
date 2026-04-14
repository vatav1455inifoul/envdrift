"""Package setup for envdrift."""

from setuptools import setup, find_packages

setup(
    name="envdrift",
    version="0.1.0",
    description="Detect and report configuration drift between .env files across environments.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="envdrift contributors",
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests*"]),
    entry_points={
        "console_scripts": [
            "envdrift=envdrift.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    extras_require={
        "dev": [
            "pytest>=.0",
            "pytest-cov",
        ]
    },
)
