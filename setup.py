"""Setup configuration for chezmoi-manager."""

from setuptools import setup, find_packages

setup(
    name="chezmoi-manager",
    version="0.1.0",
    description="A TUI for managing chezmoi dotfiles",
    author="Scott Williams",
    packages=find_packages(),
    install_requires=[
        "textual>=0.40.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "chezmoi-manager=main:main",
        ],
    },
    python_requires=">=3.10",
)
