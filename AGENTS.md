# Agent Guide — agentic-legibility

> Yes, a tool that scores repos on agent legibility has its own AGENTS.md. We practice what we preach.

## Repo Map

```
SKILL.md                     → Agent-facing instructions (two-pass workflow)
scripts/scan_repo.py         → Automated scanner (Python 3.9+, zero deps)
references/scoring-rubric.md → Detailed scoring criteria per category
```

## Key Commands

```bash
# Run scanner
python3 scripts/scan_repo.py /path/to/repo

# Validate scanner output
python3 scripts/scan_repo.py . | python3 -m json.tool
```

## Architecture

- **Scanner** produces raw JSON signals (pure detection, no scoring logic)
- **Rubric** defines how signals map to points (the scoring policy)
- **SKILL.md** orchestrates the two-pass workflow for AI agents:
  1. Run scanner for mechanical baseline
  2. Read actual repo files to adjust scores (the scanner uses hardcoded keywords — the qualitative pass catches what it misses)
  3. Combine both into a final scorecard

This separation means scoring criteria can change without touching the scanner, and new signals can be added without changing the rubric format.

## Conventions

- Scanner functions are 1:1 with scoring categories (`scan_bootstrap` → Category 1)
- All detection uses `file_exists()` or `glob_find()` helpers — no raw `os.path` calls
- Signals are returned as flat dicts with descriptive boolean/string/list keys
- No external dependencies — stdlib only
- Total score always sums to 100 across 7 categories

## When Modifying

- **Adding a signal**: Edit the relevant `scan_*` function, update rubric if it affects scoring
- **Changing point values**: Edit `references/scoring-rubric.md`, keep total at 100
- **Changing output format**: Edit the scorecard template in `SKILL.md`
