#!/usr/bin/env python
"""Regenerate Mermaid diagram for Mcu_Init."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from autosar_calltree.database.function_database import FunctionDatabase
from autosar_calltree.analyzers.call_tree_builder import CallTreeBuilder
from autosar_calltree.generators.mermaid_generator import MermaidGenerator
from autosar_calltree.config.module_config import ModuleConfig

# Paths - using raw strings to avoid backslash issues
SOURCE_DIR = Path(r"E:\project\CHY_E0X_25\ZCU\zcud\app\tools_cfg\call_tree_analysis_cfg\sources\T22FL_zcud")
CONFIG_FILE = Path(r"E:\project\CHY_E0X_25\ZCU\zcud\app\tools_cfg\call_tree_analysis_cfg\cfg\T22FL_zcud_module_config.yaml")
OUTPUT_FILE = Path(r"E:\project\CHY_E0X_25\ZCU\zcud\build\T22FL_zcud.Debug\app\tools\calltree\report.md")

def main():
    print("Building function database...")
    config = ModuleConfig(CONFIG_FILE)
    db = FunctionDatabase(source_dir=SOURCE_DIR, module_config=config)
    db.build_database(use_cache=False, verbose=False)

    print("Building call tree...")
    builder = CallTreeBuilder(db)
    result = builder.build_tree("Mcu_Init", max_depth=3, include_rte=True)

    print(f"Total functions: {result.statistics.total_functions}")
    print(f"Max depth: {result.statistics.max_depth}")

    print("Generating Mermaid diagram...")
    generator = MermaidGenerator(use_module_names=True)
    generator.generate(result, output_path=OUTPUT_FILE)

    print(f"\nMermaid diagram generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
