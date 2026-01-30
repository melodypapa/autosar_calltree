# GitHub Workflow Automation

Automate the complete GitHub workflow for creating issues, feature branches, commits, and pull requests.

## Workflow Steps

When the user runs `/gh-workflow`, perform the following steps in order:

### 1. Quality Checks (Must Pass Before Proceeding)
- Run linting: `ruff check src/ tests/`
- Run type checking: `mypy src/`
- Run unit tests: `pytest tests/ --cov=autosar_calltree`
- **All checks must pass** before proceeding to next step
- If any checks fail, report errors and ask user if they want to:
  - Abort the workflow
  - Fix issues and retry
  - Continue anyway (not recommended)
- Display quality gate summary table:
  ```
  Check        Status    Details
  ───────────────────────────────────
  Ruff         ✅ Pass    No errors
  Mypy         ✅ Pass    No issues
  Pytest       ✅ Pass    278/278 tests, 94% coverage
  ```

### 2. Analyze Current Changes
- Run `git status` to see modified files
- Run `git diff` to review unstaged changes
- Ask the user for a brief summary of the changes if not clear from the diff
- Determine the commit type based on the changes (feat, fix, docs, etc.)

### 3. Ask About Version Bump (Manual)
- Ask the user if a version bump is needed for this change
- If user confirms version bump is needed:
  - Ask which version part to bump (MAJOR, MINOR, or PATCH)
  - Wait for user to manually update version files
  - Verify version files are updated correctly
- If user declines, continue without version bump
- Display current version: `[INFO] Current version: 0.3.0`

**NOTE**: Version bumps must be done manually by the user before running this workflow, or in response to this prompt.

### 4. Create GitHub Issue
- Create a GitHub issue using `gh issue create`
- Title format: `"<type>: <brief description>"` (type can be: feat, fix, docs, refactor, test, chore)
- Include sections: Summary, Changes, Files Modified, Test Coverage, Requirements (if applicable), Version Change
- Capture the issue number (e.g., #20)

### 5. Create Feature Branch
- Create and checkout a new feature branch
- Branch naming convention: `feature/<requirement-id>-short-description` or `feature/<type>-short-description`
- Example: `feature/swr-writer-00006-class-file-structure` or `feature/add-new-parser`

### 6. Stage and Commit Changes
- Stage all relevant modified files including:
  - Updated version files (if user manually bumped version)
  - Source code changes
  - Test changes
- Create a commit with:
  - Conventional commit format: `<type>: <description>`
  - Detailed commit body describing changes
  - Version change information if applicable
  - List of modified files
  - Reference to the issue (e.g., `Closes #20`)

### 7. Push to GitHub Only
- Push the branch to GitHub remote (origin)
- **Important**: Do NOT push to gitee remote
- Use explicit GitHub URL if needed: `git push git@github.com:melodypapa/autosar-pdf.git`

### 8. Create Pull Request
- Create a pull request using `gh pr create`
- Include comprehensive PR description with:
  - Summary section
  - Changes section
  - Files Modified list
  - Test Coverage information
  - Requirements traceability (if applicable)
  - **Version Change** section (if version was bumped)
  - Reference to the issue being closed
- Use `--head` flag if branch tracking is not properly set up

## Commit Types and Version Bumping

This workflow follows **Semantic Versioning** (https://semver.org/):

**Version Format**: `MAJOR.MINOR.PATCH` (e.g., 0.1.0)

**Commit Types:**
- `feat`: New feature → **Increment MINOR** (0.1.0 → 0.2.0)
- `fix`: Bug fix → **Increment PATCH** (0.1.0 → 0.1.1)
- `breaking`: Breaking change → **Increment MAJOR** (0.1.0 → 1.0.0)
- `docs`: Documentation changes → No version bump
- `style`: Code style changes (formatting, etc.) → No version bump
- `refactor`: Code refactoring → No version bump
- `test`: Adding or updating tests → No version bump
- `chore`: Maintenance tasks → No version bump

**Version Bump Rules:**
- MAJOR version: Incompatible API changes
- MINOR version: Backwards-compatible functionality additions
- PATCH version: Backwards-compatible bug fixes

## Arguments

Use `$ARGUMENTS` to accept optional context:
- Issue title/description
- Branch name (if different from auto-generated)
- Specific files to include/exclude
- Commit type override

## Example Usage

```
/gh-workflow
/gh-workflow Implement new parser for AUTOSAR models
/gh-workflow feat: Add support for base class extraction
```

## Example Workflow

```
User: /gh-workflow feat: Add support for primitive types

System: [Step 1] Running quality checks...
        Check        Status    Details
        ───────────────────────────────────
        Ruff         ✅ Pass    No errors
        Mypy         ✅ Pass    No issues
        Pytest       ✅ Pass    278/278 tests, 94% coverage

        [Step 2] Analyzing current changes...
        Modified files:
          - src/autosar_calltree/models/autosar_models.py
          - src/autosar_calltree/parser/pdf_parser.py
          - tests/parser/test_pdf_parser.py

        Commit type: feat (new feature)

        [Step 3] Checking version bump...
        Does this change require a version bump? (y/n): y
        Which version part to bump? (MAJOR/MINOR/PATCH): MINOR
        [INFO] Please manually update version files now.
        [INFO] Update pyproject.toml and src/autosar_calltree/version.py
        Press Enter when ready...

        [Step 4] Creating GitHub issue...
        Issue #53 created: feat: Add support for primitive types

        [Step 5] Creating feature branch...
        Branch: feature/add-primitive-type-support

        [Step 6] Staging and committing changes...
        Committed: feat: Add support for primitive types
        - Added AutosarPrimitive model
        - Updated parser to recognize 'Primitive <name>' pattern
        - Version: 0.3.0 -> 0.4.0 (manually bumped)
        - Files modified:
          * pyproject.toml
          * src/autosar_calltree/version.py
          * src/autosar_calltree/models/autosar_models.py
          * src/autosar_calltree/parser/pdf_parser.py
          * tests/parser/test_pdf_parser.py
        Closes #53

        [Step 7] Pushing to GitHub...
        Branch pushed to origin

        [Step 8] Creating pull request...
        PR #54 created: https://github.com/melodypapa/autosar_calltree/pull/54

        ✅ Workflow complete!
```

## Version Bump Examples

| Commit Type | Old Version | New Version | Reason |
|-------------|-------------|-------------|---------|
| feat | 0.1.0 | 0.2.0 | New feature added |
| fix | 0.1.0 | 0.1.1 | Bug fix |
| breaking | 0.1.0 | 1.0.0 | Breaking API change |
| docs | 0.1.0 | 0.1.0 | Documentation only (no bump) |
| test | 0.1.0 | 0.1.0 | Tests only (no bump) |


## Notes

- **Version management is manual**: Users must manually update version files if needed
- Version files to update when bumping:
  - `pyproject.toml` (project version)
  - `src/autosar_calltree/version.py` (runtime version)
- Always confirm with the user before executing destructive operations
- Show progress updates at each step
- Report any errors and ask for guidance
- Provide links to the created issue and pull request
- Update the todo list to track progress
