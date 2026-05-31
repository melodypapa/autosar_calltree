"""
AST visitor for extracting function definitions from clang AST.

This module provides the ClangFunctionVisitor class that walks clang
AST nodes to extract function definitions and calls.
"""

from dataclasses import dataclass
from typing import List, Optional, Set
from pathlib import Path

import clang.cindex
from clang.cindex import CursorKind, Cursor, TranslationUnit

from ..database.models import FunctionInfo, FunctionCall, Parameter, FunctionType


@dataclass
class ControlFlowContext:
    """Tracks current control flow nesting."""
    context_type: str  # 'if', 'else', 'for', 'while', 'do', 'switch', 'case'
    condition: Optional[str] = None
    depth: int = 0


class ClangFunctionVisitor:
    """
    Visit clang AST to extract functions and all their calls.
    """
    
    C_KEYWORDS: Set[str] = {
        'if', 'else', 'while', 'for', 'do', 'switch', 'case', 'default',
        'return', 'break', 'continue', 'goto', 'sizeof', 'typeof',
        '__typeof__', '__builtin_offsetof'
    }
    
    def __init__(self, file_path: Path, translation_unit: TranslationUnit):
        """
        Initialize the visitor.
        
        Args:
            file_path: Path to the source file
            translation_unit: Clang translation unit
        """
        self.file_path = file_path
        self.tu = translation_unit
        self.functions: List[FunctionInfo] = []
        self.current_function: Optional[FunctionInfo] = None
        self.control_flow_stack: List[ControlFlowContext] = []
    
    def extract_functions(self) -> List[FunctionInfo]:
        """Extract all functions from the translation unit."""
        self._visit_cursor(self.tu.cursor)
        return self.functions
    
    def _visit_cursor(self, cursor: Cursor):
        """Recursively visit AST nodes."""
        if cursor.kind == CursorKind.FUNCTION_DECL:
            self._handle_function_decl(cursor)
        
        for child in cursor.get_children():
            self._visit_cursor(child)
    
    def _handle_function_decl(self, cursor: Cursor):
        """Handle function declaration/definition."""
        if not cursor.is_definition():
            return  # Skip declarations, only process definitions
        
        # Extract parameters
        parameters = self._extract_parameters(cursor)
        
        # Extract function info
        func_info = FunctionInfo(
            name=cursor.spelling,
            return_type=cursor.result_type.spelling,
            file_path=self.file_path,
            line_number=cursor.location.line,
            is_static=cursor.storage_class == clang.cindex.StorageClass.STATIC,
            function_type=FunctionType.TRADITIONAL_C,
            parameters=parameters,
            calls=[]
        )
        
        self.functions.append(func_info)
    
    def _extract_parameters(self, cursor: Cursor) -> List[Parameter]:
        """Extract function parameters."""
        params = []
        for arg in cursor.get_arguments():
            param_type = arg.type.spelling
            param = Parameter(
                name=arg.spelling,
                param_type=param_type,
                is_pointer='*' in param_type,
                is_const='const' in param_type
            )
            params.append(param)
        return params
