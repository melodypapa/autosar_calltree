.. AUTOSAR Call Tree Analyzer documentation master file

Welcome to AUTOSAR Call Tree Analyzer's Documentation
======================================================

.. toctree::
   :maxdepth: 2
   :caption: Getting Started
   
   getting_started/installation
   getting_started/quickstart
   getting_started/configuration

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   
   user_guide/basic_usage
   user_guide/output_formats
   user_guide/advanced_features
   user_guide/integration

.. toctree::
   :maxdepth: 2
   :caption: Tutorials
   
   tutorials/analyzing_autosar
   tutorials/generating_diagrams
   tutorials/rhapsody_integration

.. toctree::
   :maxdepth: 2
   :caption: API Reference
   
   api/modules
   api/parsers
   api/analyzers
   api/generators
   api/database

.. toctree::
   :maxdepth: 2
   :caption: Architecture
   
   architecture/overview
   architecture/components
   architecture/data_flow

.. toctree::
   :maxdepth: 2
   :caption: Development
   
   development/contributing
   development/testing
   development/documentation

.. toctree::
   :maxdepth: 1
   :caption: Reference
   
   reference/cli
   reference/changelog
   reference/license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

About
=====

**AUTOSAR Call Tree Analyzer** is a Python tool that analyzes C/AUTOSAR codebases 
and generates function call trees with Mermaid sequence diagrams or IBM Rhapsody XMI output.

Key Features
------------

* **Clang-based Parser**: Production-grade C parsing using libclang for maximum accuracy
* **AUTOSAR Support**: Built-in understanding of AUTOSAR patterns and macros
* **Multiple Output Formats**: Generate Mermaid diagrams, Rhapsody XMI, or text-based call trees
* **Interactive Analysis**: Visualize function call relationships with sequence diagrams
* **Cache Support**: Fast incremental analysis with intelligent caching
* **Module Mapping**: Organize functions by software modules

Quick Example
-------------

.. code-block:: bash

   # Install the tool
   pip install autosar-calltree

   # Analyze your codebase
   calltree -i /path/to/source -s main_function -o call_tree.md

   # List all functions
   calltree -l -i /path/to/source

.. note::

   This documentation covers version |version|. For other versions, use the version 
   switcher in the bottom-left corner.

Getting Help
------------

* **Documentation**: You're reading it!
* **GitHub Issues**: https://github.com/melodypapa/autosar_calltree/issues
* **Source Code**: https://github.com/melodypapa/autosar_calltree

License
-------

This project is licensed under the MIT License - see the :doc:`reference/license` for details.
