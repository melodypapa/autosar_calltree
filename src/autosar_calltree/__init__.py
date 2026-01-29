"""
AUTOSAR Call Tree Analyzer

A Python package to analyze C/AUTOSAR codebases and generate function call trees
with multiple output formats (Mermaid, XMI/UML).
"""

from .version import __version__, __author__, __email__
from .database.function_database import FunctionDatabase
from .analyzers.call_tree_builder import CallTreeBuilder
from .generators.mermaid_generator import MermaidGenerator
from .parsers.autosar_parser import AutosarParser
from .parsers.c_parser import CParser

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "FunctionDatabase",
    "CallTreeBuilder",
    "MermaidGenerator",
    "AutosarParser",
    "CParser",
]
