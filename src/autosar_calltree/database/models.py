"""
Core data models for the AUTOSAR Call Tree Analyzer.

This module defines the data structures used throughout the package.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Set, Dict
from datetime import datetime


class FunctionType(Enum):
    """Classification of function types."""

    AUTOSAR_FUNC = "autosar_func"  # FUNC(rettype, memclass) name()
    AUTOSAR_FUNC_P2VAR = "autosar_func_p2var"  # FUNC_P2VAR(type, ...)
    AUTOSAR_FUNC_P2CONST = "autosar_func_p2const"  # FUNC_P2CONST(type, ...)
    TRADITIONAL_C = "traditional_c"  # Standard C: rettype name()
    RTE_CALL = "rte_call"  # Rte_Read_*, Rte_Write_*, etc.
    UNKNOWN = "unknown"


@dataclass
class Parameter:
    """Function parameter information."""

    name: str
    param_type: str  # Actual type (uint32, uint8*, etc.)
    is_pointer: bool = False
    is_const: bool = False
    memory_class: Optional[str] = None  # AUTOSAR memory class (AUTOMATIC, etc.)

    def __str__(self) -> str:
        """String representation of parameter."""
        const_str = "const " if self.is_const else ""
        ptr_str = "*" if self.is_pointer else ""
        if self.memory_class:
            return f"{const_str}{self.param_type}{ptr_str} {self.name} [{self.memory_class}]"
        return f"{const_str}{self.param_type}{ptr_str} {self.name}"


@dataclass
class FunctionInfo:
    """Complete function information."""

    name: str
    return_type: str
    file_path: Path
    line_number: int
    is_static: bool
    function_type: FunctionType
    memory_class: Optional[str] = None  # AUTOSAR memory class (RTE_CODE, etc.)
    parameters: List[Parameter] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)  # Functions called within
    called_by: Set[str] = field(default_factory=set)  # Functions that call this

    # AUTOSAR specific
    macro_type: Optional[str] = None  # "FUNC", "FUNC_P2VAR", etc.

    # For disambiguation of static functions
    qualified_name: Optional[str] = None  # file::function for static functions

    # SW module assignment (from configuration)
    sw_module: Optional[str] = None  # SW module name from config

    def __hash__(self) -> int:
        """Hash function for use in sets/dicts."""
        return hash((self.name, str(self.file_path), self.line_number))

    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, FunctionInfo):
            return False
        return (
            self.name == other.name
            and self.file_path == other.file_path
            and self.line_number == other.line_number
        )

    def get_signature(self) -> str:
        """Get function signature string."""
        params_str = ", ".join(str(p) for p in self.parameters)
        return f"{self.return_type} {self.name}({params_str})"

    def is_rte_function(self) -> bool:
        """Check if this is an RTE function."""
        return (
            self.name.startswith("Rte_") or self.function_type == FunctionType.RTE_CALL
        )


@dataclass
class CallTreeNode:
    """Node in the function call tree."""

    function_info: FunctionInfo
    depth: int
    children: List["CallTreeNode"] = field(default_factory=list)
    parent: Optional["CallTreeNode"] = None
    is_recursive: bool = False  # True if function already in call stack
    is_truncated: bool = False  # True if depth limit reached
    call_count: int = 1  # Number of times this function is called

    def add_child(self, child: "CallTreeNode") -> None:
        """Add a child node."""
        child.parent = self
        self.children.append(child)

    def get_all_functions(self) -> Set[FunctionInfo]:
        """Get all unique functions in this subtree."""
        functions = {self.function_info}
        for child in self.children:
            functions.update(child.get_all_functions())
        return functions

    def get_max_depth(self) -> int:
        """Get maximum depth of this subtree."""
        if not self.children:
            return self.depth
        return max(child.get_max_depth() for child in self.children)


@dataclass
class CircularDependency:
    """Represents a circular call chain."""

    cycle: List[str]
    depth: int

    def __str__(self) -> str:
        """String representation of cycle."""
        return " -> ".join(self.cycle)


@dataclass
class AnalysisStatistics:
    """Statistics from call tree analysis."""

    total_functions: int = 0
    unique_functions: int = 0
    max_depth_reached: int = 0
    total_function_calls: int = 0
    static_functions: int = 0
    rte_functions: int = 0
    autosar_functions: int = 0
    circular_dependencies_found: int = 0

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {
            "total_functions": self.total_functions,
            "unique_functions": self.unique_functions,
            "max_depth_reached": self.max_depth_reached,
            "total_function_calls": self.total_function_calls,
            "static_functions": self.static_functions,
            "rte_functions": self.rte_functions,
            "autosar_functions": self.autosar_functions,
            "circular_dependencies_found": self.circular_dependencies_found,
        }


@dataclass
class AnalysisResult:
    """Complete analysis result."""

    root_function: str
    call_tree: Optional[CallTreeNode]
    statistics: AnalysisStatistics
    circular_dependencies: List[CircularDependency] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    source_directory: Optional[Path] = None
    max_depth_limit: int = 3

    def get_all_functions(self) -> Set[FunctionInfo]:
        """Get all unique functions in the call tree."""
        return self.call_tree.get_all_functions()

    def has_circular_dependencies(self) -> bool:
        """Check if circular dependencies were found."""
        return len(self.circular_dependencies) > 0


# Type aliases for convenience
FunctionDict = Dict[str, List[FunctionInfo]]  # Maps name to list of FunctionInfo
