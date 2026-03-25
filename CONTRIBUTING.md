# Contributing to The Designer

Thanks for your interest in improving the visual design specification pipeline.

## Development Setup

```bash
git clone https://github.com/sufianmypa1203-oss/the-designer.git
cd the-designer
pip install -e ".[dev]"
pytest tests/ -v
```

## Ground Rules

1. **Every design contract must have a Pydantic model** — no loose dicts
2. **Every validator check must have a test** — no uncovered edge cases
3. **Canvas scaling is ×3, always** — `font_size_canvas = prototype × 3`
4. **WCAG AA is the floor** — contrast ≥4.5:1 for all text
5. **Error messages must be actionable** — tell the agent exactly what to fix

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=src/designer

# Run a specific test class
python -m pytest tests/test_models.py::TestTextElement -v
```

All PRs must pass the full test suite (80+ tests). Zero tolerance for regressions.

## Code Style

We use `ruff` for linting:

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Architecture Decisions

Before making changes:
- Read `AGENT.md` for the architecture overview
- Understand the pipeline position (Agent 2 of 5)
- Respect scope boundaries — the Designer NEVER touches motion physics or component code
