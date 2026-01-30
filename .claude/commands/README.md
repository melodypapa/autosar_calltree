# Custom Slash Commands

This directory contains custom slash commands (skills) for Claude Code to automate common workflows in the autosar-pdf2txt project.

## Available Commands

### `/gh-workflow` - GitHub Workflow Automation
Automates the complete GitHub workflow:
1. Create GitHub issue based on changes
2. Create feature branch
3. Stage and commit changes
4. Push to GitHub only (not gitee)
5. Create pull request

**Usage:**
```
/gh-workflow
/gh-workflow Implement new parser for AUTOSAR models
/gh-workflow feature: Add support for base class extraction
```

### `/merge-pr` - Merge Pull Request
Check pull request status, merge it, and return to master branch.

**Usage:**
```
/merge-pr                # Merge current branch's PR
/merge-pr 36             # Merge PR #36
/merge-pr --no-cleanup   # Merge but keep feature branch
/merge-pr --force        # Merge even if CI is not passing
```

### `/test` - Test Runner
Run the project test suite with comprehensive reporting.

**Usage:**
```
/test                    # Run all tests
/test --unit            # Run only unit tests
/test --integration     # Run only integration tests
/test tests/models/test_autosar_models.py  # Run specific test file
```

### `/quality` - Quality Check
Run all quality checks (linting, type checking, testing) to ensure code meets project standards.

**Usage:**
```
/quality        # Run all quality checks
/quality --fix  # Auto-fix linting issues
/quality --test-only  # Run only tests
```

**Quality Gates:**
- ✅ Ruff linting: No errors
- ✅ Mypy type checking: No issues
- ✅ Pytest: All tests pass
- ✅ Coverage: ≥95%

### `/parse` - PDF Parser
Parse AUTOSAR PDF files and extract model hierarchies.

**Usage:**
```
/parse                           # Parse PDFs in current directory
/parse input.pdf                 # Parse single PDF
/parse input.pdf -o output.md    # Parse and save to file
/parse /path/to/pdfs/            # Parse all PDFs in directory
/parse --write-class-files       # Write individual class files
/parse -v                        # Verbose mode for debugging
```

### `/req` - Requirement Management
Manage AUTOSAR project requirements with traceability.

**Usage:**
```
/req add SWR_WRITER_00007 "Add support for custom markdown templates"
/req update SWR_WRITER_00006 maturity accept
/req check traceability
/req list draft
/req search parser
```

### `/sync-docs` - Synchronize Documentation
Synchronize requirements, test cases, and source code to ensure consistency across the codebase.

**What It Does:**
- Analyzes source code to extract implementation details
- Compares implementation with requirements and test case documentation
- Updates documentation to match actual implementation
- Ensures traceability and accuracy across the codebase

**Common Synchronization Tasks:**
- Attribute changes (added/removed/moved)
- Inheritance hierarchy updates
- Type changes and signature updates
- Unit test case alignment with implementation
- Integration test workflow updates

**Files Modified:**
- `docs/requirements/requirements.md` - Requirements specifications
- `docs/test_cases/unit_tests.md` - Unit test case documentation
- `docs/test_cases/integration_tests.md` - Integration test case documentation

**Usage:**
```
/sync-docs    # Analyze and sync all documentation
```

**Verification After Sync:**
```bash
pytest tests/ --cache-clear
ruff check src/ tests/
mypy src/autosar_pdf2txt/
```

**Related Commands:**
- `/req` - Manage individual requirements
- `/test` - Run tests and coverage
- `/quality` - Run quality checks

## Creating New Commands

To create a new slash command:

1. Create a new markdown file in `.claude/commands/`
2. The filename becomes the command name (e.g., `debug.md` → `/debug`)
3. Write the workflow instructions in markdown format
4. Use `$ARGUMENTS` to accept dynamic user input

### Example Command Structure

```markdown
# Command Title

Brief description of what the command does.

## Actions

Step-by-step instructions for Claude to follow.

## Usage Examples

```
/command
/command arg1 arg2
```

## Notes

Additional context or constraints.
```

## Best Practices

- **One command per file**: Each file defines one slash command
- **Descriptive names**: Use clear, descriptive command names
- **Project context**: Commands automatically have access to `CLAUDE.md` for project context
- **Use $ARGUMENTS**: Accept dynamic input from users
- **Track progress**: Use TodoWrite tool for multi-step workflows
- **Error handling**: Handle errors gracefully and ask for guidance
- **Show progress**: Report progress updates at each step

## Command Development

When creating or modifying commands:

1. Test the command thoroughly before committing
2. Ensure it follows project coding standards
3. Update this README with new commands
4. Document any special requirements or dependencies
5. Run quality checks: `/quality`

## References

- Project documentation: `CLAUDE.md`
- Requirements: `docs/requirement/requirements.md`
- Coding standards: `docs/development/coding_rules.md`
