# AUTOSAR Call Tree Analyzer Documentation

This directory contains the Sphinx documentation for AUTOSAR Call Tree Analyzer.

## Documentation Structure

```
docs/
├── _static/              # Static files (CSS, JS, images)
│   ├── custom.css        # Custom styling
│   └── copybutton.js     # Copy button functionality
├── _templates/           # Custom Sphinx templates
├── getting_started/      # Getting started guides
│   ├── installation.md   # Installation instructions
│   ├── quickstart.md     # Quick start guide
│   └── configuration.md  # Configuration options
├── user_guide/          # User guide
├── tutorials/           # Tutorials and examples
├── api/                 # API reference
│   └── modules.rst      # Auto-generated API docs
├── architecture/        # Architecture documentation
├── development/         # Development guides
├── reference/           # Reference documentation
├── conf.py             # Sphinx configuration
├── index.rst           # Documentation index
└── requirements.txt    # Python dependencies for docs
```

## Building the Documentation

### Prerequisites

Install the documentation dependencies:

```bash
pip install -r requirements.txt
```

### Build HTML Documentation

```bash
# Build HTML documentation
make html

# Or using sphinx-build directly
sphinx-build -b html . _build/html
```

The built documentation will be in `_build/html/`.

### Build PDF Documentation

```bash
# Build PDF
make pdf

# Or using sphinx-build
sphinx-build -b pdf . _build/pdf
```

### Live Preview

For live preview during development:

```bash
# Install sphinx-autobuild
pip install sphinx-autobuild

# Start live preview server
sphinx-autobuild . _build/html
```

Then open http://localhost:8000 in your browser.

## Writing Documentation

### Markdown Support

This documentation uses **MyST-Parser** to support Markdown files. You can write documentation in either:

- **Markdown** (`.md` files) - Recommended for most content
- **reStructuredText** (`.rst` files) - For advanced Sphinx features

### Markdown Examples

```markdown
# Heading 1

## Heading 2

### Heading 3

**Bold text** and *italic text*.

- Bullet list item 1
- Bullet list item 2

1. Numbered list item 1
2. Numbered list item 2

[Link text](https://example.com)

`inline code`

```python
def example():
    """Code block example"""
    pass
```

### Cross-References

Link to other documentation pages:

```markdown
See {doc}`/getting_started/installation` for installation instructions.
```

Reference API documentation:

```markdown
The {class}`autosar_calltree.database.FunctionDatabase` class manages...
```

### Admonitions

Use admonitions for notes, warnings, tips:

```markdown
.. note::
   This is a note.

.. warning::
   This is a warning.

.. tip::
   This is a tip.
```

## ReadTheDocs Configuration

The documentation is configured to build on ReadTheDocs automatically. The configuration is in `readthedocs.yaml` at the project root.

### ReadTheDocs Settings

- **Python version**: 3.13
- **OS**: Ubuntu 24.04
- **Format**: HTML and PDF
- **Theme**: sphinx-rtd-theme

## Contributing to Documentation

### Guidelines

1. **Keep it simple** - Write for your target audience
2. **Use examples** - Show, don't just tell
3. **Update index** - Add new pages to the appropriate `toctree`
4. **Check links** - Ensure cross-references work
5. **Test locally** - Build and review before pushing

### File Naming

- Use lowercase with underscores: `my_page.md`
- Be descriptive: `installation.md`, not `install.md`
- Group related files in subdirectories

### Committing Changes

1. Build documentation locally to verify
2. Check for warnings: `make html 2>&1 | grep warning`
3. Commit both source and built HTML (if needed)
4. Update `CHANGELOG.md` for significant changes

## Useful Sphinx Directives

### Code Blocks

```markdown
.. code-block:: python
   :linenos:
   :emphasize-lines: 2,3

   def example():
       line1()
       line2()  # highlighted
       line3()  # highlighted
```

### Tables

```markdown
.. list-table:: Table Title
   :header-rows: 1

   * - Header 1
     - Header 2
   * - Cell 1
     - Cell 2
```

### Images

```markdown
.. image:: images/diagram.png
   :width: 600px
   :align: center
   :alt: Diagram description
```

## Troubleshooting

### Build Errors

**Missing dependencies:**
```bash
pip install -r requirements.txt
```

**Import errors:**
```bash
# Ensure the package is installed
pip install -e ..
```

**Theme not found:**
```bash
pip install sphinx-rtd-theme
```

### Warnings

**Duplicate labels:**
- Each label must be unique
- Use explicit labels: `.. _my-label:`

**Missing references:**
- Check spelling of references
- Ensure referenced files exist

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [MyST-Parser Documentation](https://myst-parser.readthedocs.io/)
- [ReadTheDocs Documentation](https://docs.readthedocs.io/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
