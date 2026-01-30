# Testing and CI/CD Implementation Design

**Date:** 2025-01-30
**Author:** Claude (with user validation)
**Status:** Approved

## Executive Summary

This design establishes a comprehensive testing and CI/CD infrastructure for the AUTOSAR Call Tree Analyzer project. The approach follows an **iterative module-by-module workflow** that provides early CI feedback while building thorough test coverage and requirements documentation incrementally.

**Key Goals:**
- Achieve ≥95% test coverage with pytest
- Implement GitHub Actions CI/CD pipeline for all pull requests
- Document all 87 missing requirements with traceability
- Adapt custom slash commands to match project structure
- Follow TDD principles: failing test → minimal implementation → refactor

**Timeline:** ~3.5 days for complete coverage across 6 core modules

## Architecture Overview

### Phase 1: Foundation Setup (One-time)

Create the infrastructure that supports iterative development:

1. **GitHub Actions workflow skeleton** - Basic CI pipeline that can run pytest
2. **Test directory structure** - Organized fixtures/, unit/, integration/ hierarchy
3. **Supporting scripts** - Test runners, quality checks, traceability validation
4. **Documentation templates** - Standardized format for requirements and test cases

### Phase 2: Iterative Module Development (Repeat per module)

For each of the 6 core modules, execute this workflow:

```
Analyze Code → Document Requirements → Write Tests (TDD) → Verify in CI → Update Traceability
```

**Modules in priority order:**
1. models (188 lines) - Foundation dataclasses
2. autosar_parser (311 lines) - AUTOSAR macro parsing
3. c_parser (412 lines) - Traditional C parsing
4. function_database (499 lines) - Critical complexity
5. call_tree_builder (370 lines) - Graph algorithms
6. module_config (180 lines) - YAML configuration
7. mermaid_generator (483 lines) - Output generation
8. CLI (332 lines) - Command interface
9. End-to-end integration

### Phase 3: Integration & Polish

- CLI and end-to-end tests
- Coverage reporting validation (target: ≥95%)
- Slash command adaptation
- Documentation synchronization

## GitHub Actions CI/CD Pipeline

### Workflow Structure

```
.github/workflows/
├── ci.yml              # Main CI pipeline (push/PR)
├── quality.yml         # Daily quality checks (optional)
└── release.yml         # Automated releases (future)
```

### Main CI Pipeline (`ci.yml`)

**Triggers:** Push to any branch, pull requests

**Test Matrix:** Python 3.8, 3.9, 3.10, 3.11, 3.12

**Jobs:**

```yaml
1. quality-check:
   - Black (formatting check)
   - isort (import sorting check)
   - flake8 (linting)
   - mypy (type checking with strict mode)

2. test:
   - Needs: quality-check
   - Install: pip install -e ".[dev]"
   - Run: pytest --cov --cov-report=xml --cov-report=term
   - Upload coverage to Codecov (optional)

3. requirements-check:
   - Parse test files for SWUT_XXX references
   - Validate all SWUT_XXX trace to SWR_XXX requirements
   - Fail if orphaned tests found
```

**Design Decisions:**

1. **Quality gate first** - Catch formatting/linting before expensive tests
2. **Matrix testing** - Ensure Python 3.8-3.12 compatibility
3. **Coverage reporting** - XML for CI, terminal for developers
4. **Requirements validation** - Automated traceability enforcement

**Status Checks:** All jobs must pass before PR can merge

## Test Structure & Documentation

### Directory Layout

```
tests/
├── fixtures/
│   ├── autosar_code/          # AUTOSAR C source samples
│   │   ├── basic_functions.c
│   │   ├── with_parameters.c
│   │   └── complex_macros.c
│   ├── traditional_c/         # Traditional C samples
│   │   └── standard_functions.c
│   └── configs/               # Module config YAMLs
│       └── module_mapping.yaml
├── unit/
│   ├── test_models.py                  # SWUT_MODEL_*
│   ├── test_autosar_parser.py          # SWUT_PARSER_AUTOSAR_*
│   ├── test_c_parser.py                # SWUT_PARSER_C_*
│   ├── test_function_database.py       # SWUT_DB_*
│   ├── test_call_tree_builder.py       # SWUT_ANALYZER_*
│   ├── test_mermaid_generator.py       # SWUT_GENERATOR_*
│   └── test_module_config.py           # SWUT_CONFIG_*
└── integration/
    ├── test_cli.py                     # SWUT_CLI_*
    └── test_end_to_end.py              # SWUT_E2E_*
```

### Documentation Structure

```
docs/
├── requirements/
│   ├── models.md                       # SWR_MODEL_00001-00027
│   ├── parsers.md                      # SWR_PARSER_00001-00032
│   ├── database.md                     # SWR_DB_00001-*
│   ├── analyzers.md                    # SWR_ANALYZER_00001-*
│   ├── generators.md                   # SWR_GENERATOR_00001-*
│   └── cli.md                          # SWR_CLI_00001-00014
├── tests/
│   ├── models.md                       # Test cases for models
│   ├── parsers.md                      # Test cases for parsers
│   └── ... (one per module)
└── TRACEABILITY.md                     # SWR_XXX → SWUT_XXX mapping
```

### Naming Conventions

- **Requirements:** `SWR_<MODULE>_<NUMBER>` (e.g., `SWR_MODEL_00001`)
- **Test cases:** `SWUT_<MODULE>_<NUMBER>` (e.g., `SWUT_MODEL_00001`)
- **Test functions:** `test_SWUT_<MODULE>_<NUMBER>_<description>`

### Traceability Example

```markdown
| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_MODEL_00001 | SWUT_MODEL_00001 | test_SWUT_MODEL_00001_function_info_creation | ✅ Pass |
```

## Custom Slash Commands & Scripts

### Commands to Adapt

| Command | Issue | Action |
|---------|-------|--------|
| `/test` | References non-existent `scripts/run_tests.py` | Update to use pytest directly |
| `/quality` | Wrong project path (`autosar_pdf2txt/`) | Fix to `autosar_calltree/` |
| `/gh-workflow` | Missing supporting scripts | Create workflow generation |
| `/parse` | Different project (PDF parsing) | Remove or mark optional |
| `/sync-docs` | Different project | Remove or adapt |
| `/merge-pr` | Should work | Verify |
| `/req` | Should work | Verify |

### New Scripts to Create

```bash
scripts/
├── run_tests.sh           # pytest wrapper with coverage
├── run_quality.sh         # All quality checks (black, isort, flake8, mypy)
├── check_traceability.py  # Validate SWUT_XXX → SWR_XXX links
└── generate_workflow.py   # Generate GitHub workflow files
```

### Updated Command Implementations

**`/test` Command:**
```bash
# Old: python scripts/run_tests.py --unit
# New: pytest tests/ -v --cov=autosar_calltree --cov-report=html --cov-report=term
```

**`/quality` Command:**
```bash
black --check src/ tests/
isort --check-only src/ tests/
flake8 src/ tests/
mypy src/autosar_calltree/
```

**Traceability Checker:**
- Parse test files for `# SWUT_XXX:` comments
- Parse requirement docs for `SWR_XXX:` definitions
- Validate every SWUT references an existing SWR
- Report orphaned tests and untested SWRs

## Implementation Roadmap

### Module Priority Order

**Wave 1: Core Data & Parsing** (Foundation)
1. models - Dataclasses, foundational
2. autosar_parser - AUTOSAR-specific, high risk
3. c_parser - Complex patterns, high risk

**Wave 2: Database & Analysis** (Core Logic)
4. function_database - Critical complexity, caching, smart lookup
5. call_tree_builder - Graph algorithms, cycle detection

**Wave 3: Output & Configuration** (Interface)
6. module_config - YAML parsing, validation
7. mermaid_generator - Output formatting

**Wave 4: Integration** (End-to-End)
8. CLI - Command orchestration
9. End-to-end - Full workflow validation

### Per-Module Workflow

For each module:
1. **Analyze code** → Extract requirements (30-60 min)
2. **Document requirements** → Write to docs/requirements/ (20-30 min)
3. **Create test fixtures** (if needed) (15-30 min)
4. **Write tests** (TDD) → tests/unit/test_<module>.py (1-3 hours)
5. **Document test cases** → docs/tests/<module>.md (20-30 min)
6. **Update traceability** → docs/TRACEABILITY.md (10 min)
7. **Push & verify CI** → GitHub Actions validates (5 min)

### Estimated Timeline

- Wave 1: ~1 day (models + parsers)
- Wave 2: ~1 day (database + analyzer)
- Wave 3: ~1 day (config + generator)
- Wave 4: ~0.5 day (CLI + E2E)
- **Total: ~3.5 days for complete coverage**

## TDD Workflow

### Red-Green-Refactor Cycle

**RED:**
1. Write one failing test showing expected behavior
2. Run pytest: verify test fails correctly
3. Confirm failure message is expected

**GREEN:**
4. Write minimal code to pass the test
5. Run pytest: verify test passes
6. Confirm no other tests broke

**REFACTOR:**
7. Clean up code (remove duplication, improve names)
8. Keep tests green
9. No behavior changes

### Critical Rules

- **NO production code without a failing test first**
- **If test passes immediately, fix the test** (you're testing existing behavior)
- **Watch it fail** (proves test works)
- **Watch it pass** (proves code works)
- **Delete existing code** when adding tests, don't "reference" it

## Success Criteria

### Code Quality
- [ ] All tests pass (pytest)
- [ ] Coverage ≥95% (pytest-cov)
- [ ] No linting errors (flake8)
- [ ] No type errors (mypy strict mode)
- [ ] Code formatted (black, isort)

### Requirements & Traceability
- [ ] All 87 missing requirements documented
- [ ] All tests trace to requirements (SWUT_XXX → SWR_XXX)
- [ ] No orphaned tests
- [ ] All SWR tested or documented as deferred

### CI/CD
- [ ] GitHub Actions runs on all PRs
- [ ] Status checks required before merge
- [ ] All Python versions tested (3.8-3.12)
- [ ] Coverage reports generated

### Documentation
- [ ] All slash commands work correctly
- [ ] Test cases documented in docs/tests/
- [ ] Requirements traceability matrix complete
- [ ] README updated with testing instructions

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| TDD feels slow for existing code | Medium | Start with high-risk modules, value early bug detection |
| 87 requirements overwhelming | High | Extract incrementally during TDD, not all upfront |
| CI latency slows development | Low | Quality gate first, fail fast on formatting issues |
| Test maintenance burden | Medium | Focus on behavior tests, avoid implementation coupling |
| Fixtures become stale | Low | Use demo/ directory as source of truth, version control |

## Next Steps

1. ✅ Design approved
2. Create detailed implementation plan (superpowers:writing-plans)
3. Execute Phase 1: Foundation Setup
4. Begin Wave 1: Models & Parsers
5. Iterate through remaining waves
6. Final integration and polish

---

**Related Documents:**
- Implementation Plan: `docs/plans/2025-01-30-testing-cicd-plan.md` (to be created)
- Requirements Index: `docs/requirements/README.md`
- Traceability Matrix: `docs/TRACEABILITY.md`
