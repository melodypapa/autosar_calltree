"""
C function parser using clang (libclang).

This module uses clang for accurate parsing of C code with built-in
preprocessing and comprehensive AST analysis.
"""

import clang.cindex
from clang.cindex import Index, TranslationUnit
from pathlib import Path
from typing import List, Optional

from .clang_function_visitor import ClangFunctionVisitor
from ..database.models import FunctionInfo


class ClangParser:
    """C parser using libclang for maximum accuracy."""
    
    def __init__(
        self,
        include_dirs: Optional[List[str]] = None,
        compiler_flags: Optional[List[str]] = None
    ):
        """
        Initialize the clang parser.
        
        Args:
            include_dirs: List of include directories for header resolution
            compiler_flags: Additional compiler flags (e.g., -std=c99)
        """
        self.index = Index.create()
        self.include_dirs = include_dirs or []
        self.compiler_flags = compiler_flags or []
    
    def parse_file(self, file_path: Path) -> List[FunctionInfo]:
        """
        Parse a C source file and extract all function definitions.
        
        Args:
            file_path: Path to the C source file
            
        Returns:
            List of FunctionInfo objects
        """
        args = self._get_clang_args()
        
        tu = self.index.parse(
            str(file_path),
            args=args,
            options=TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
        )
        
        visitor = ClangFunctionVisitor(file_path, tu)
        return visitor.extract_functions()
    
    def _get_clang_args(self) -> List[str]:
        """Build clang compiler arguments."""
        args = ['-fsyntax-only']
        
        for inc_dir in self.include_dirs:
            args.extend(['-I', inc_dir])
        
        args.extend(self.compiler_flags)
        
        # Add common system include directories
        # These are typical locations for system headers on Unix-like systems
        system_includes = [
            '/usr/include',
            '/usr/local/include',
            '/opt/homebrew/include',  # macOS with Homebrew
        ]
        
        for sys_inc in system_includes:
            import os
            if os.path.exists(sys_inc):
                args.extend(['-I', sys_inc])
        
        return args
