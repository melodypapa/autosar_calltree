# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# Add the source directory to the path for autodoc
sys.path.insert(0, os.path.abspath('../src'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'AUTOSAR Call Tree Analyzer'
copyright = '2026, melodypapa'
author = 'melodypapa'

# Get version from the package
try:
    from autosar_calltree import __version__
    release = __version__
except ImportError:
    release = '0.12.0'

version = release

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Markdown support
    'myst_parser',
    
    # API documentation
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    
    # Code highlighting
    'sphinx.ext.viewcode',
    'sphinx.ext.doctest',
    
    # Links and references
    'sphinx.ext.intersphinx',
    'sphinx.ext.githubpages',
    
    # Diagrams
    'sphinxcontrib.mermaid',
    
    # PDF export
    'rst2pdf.pdfbuilder',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix(es) of source filenames.
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# -- Markdown configuration (MyST-Parser) ------------------------------------

# Enable MyST extensions
myst_enable_extensions = [
    'colon_fence',
    'deflist',
    'dollarmath',
    'fieldlist',
    'html_admonition',
    'html_image',
    'linkify',
    'replacements',
    'smartquotes',
    'strikethrough',
    'substitution',
    'tasklist',
]

# GitHub-flavored Markdown
myst_gfm_only = False

# Enable heading anchors
myst_heading_anchors = 3

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'style_nav_header_background': '#2980B9',
    
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
    
    # GitHub integration
    'logo_only': False,
    'display_github': True,
    'github_user': 'melodypapa',
    'github_repo': 'autosar_calltree',
    'github_version': 'main',
    'conf_py_path': '/docs/',
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom CSS
html_css_files = [
    'custom.css',
]

# -- Options for LaTeX/PDF output --------------------------------------------

latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual])
latex_documents = [
    ('index', 'autosar_calltree.tex', 'AUTOSAR Call Tree Analyzer Documentation',
     'melodypapa', 'manual'),
]

# -- PDF output configuration ------------------------------------------------

pdf_documents = [
    ('index', 'autosar_calltree', 'AUTOSAR Call Tree Analyzer Documentation',
     'melodypapa'),
]

pdf_stylesheets = ['sphinx', 'kerning', 'a4']

pdf_break_level = 1

pdf_breakside = 'any'

# -- Autodoc configuration ---------------------------------------------------

# Automatically extract typehints when specified and place them in
# descriptions of the relevant function/method.
autodoc_typehints = 'description'

# Don't show type hints for parameters in the signature
autodoc_typehints_format = 'short'

# -- Napoleon configuration --------------------------------------------------

# Enable Google style docstrings
napoleon_google_docstring = True

# Enable NumPy style docstrings
napoleon_numpy_docstring = True

# Include private members
napoleon_include_private_with_doc = False

# Include special members
napoleon_include_special_with_doc = True

# Use adjectives instead of verbs for attribute docstrings
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Intersphinx configuration -----------------------------------------------

# Link to external documentation
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}

# -- Mermaid configuration ---------------------------------------------------

mermaid_version = 'latest'
mermaid_init_js = "mermaid.initialize({startOnLoad:true,theme:'neutral'});"

# -- Copy button configuration -----------------------------------------------

# Add copy button to code blocks
html_js_files = [
    'https://cdnjs.cloudflare.com/ajax/libs/clipboard.js/2.0.6/clipboard.min.js',
    'copybutton.js',
]
