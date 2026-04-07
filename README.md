# Agentic Legibility Score

**Score any code repository 0–100 on how effectively AI agents can autonomously operate within it.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

> "Autonomous coding usually fails in boring ways. The model cannot find the setup command. It does not know which folder matters. It cannot tell whether the task is done." — [seand.ai](https://seand.ai/blog/agent-legibility-scoring/)

---

## What This Is

A reusable **AI agent skill** that evaluates how "legible" a codebase is to autonomous coding agents. It produces a detailed scorecard across 7 categories, grades the repo A+ through F-, and gives actionable recommendations to improve agent effectiveness.

Agent performance problems are almost always **environment problems**, not model problems. This tool evaluates the scaffolding, not the code.

## Quick Start

### As a Claude Skill

Drop the `agentic-legibility-score/` folder into `~/.claude/skills/` and ask:

> "Score this repo on agentic legibility"

Claude will run the scanner, apply the rubric, and produce a full scorecard.

### Standalone Scanner

```bash
python3 scripts/scan_repo.py /path/to/your/repo
```

Outputs JSON with 100+ signals across all 7 scoring categories.

## Scoring Categories

| # | Category | Max Pts | Core Question |
|---|---|---|---|
| 1 | **Bootstrap & Environment** | 15 | Can an agent set up and run the project cold? |
| 2 | **Entry Points & Commands** | 15 | Can it find build/test/lint without guessing? |
| 3 | **Documentation & Navigation** | 20 | Is there a map? Can the agent find its way? |
| 4 | **Architecture & Structure** | 15 | Does it understand *why* things are where they are? |
| 5 | **Testing & Validation** | 15 | Can it verify changes without a human? |
| 6 | **Code Quality Enforcement** | 10 | Are quality gates automated and discoverable? |
| 7 | **Security & Governance** | 10 | Will it avoid introducing vulnerabilities? |

Plus **±5 qualitative adjustment** for progressive disclosure, tribal knowledge debt, and remediation quality.

## Grade Scale

| Score | Grade | What Agents Can Do |
|---|---|---|
| 90–100 | **A+** | Full autonomous operation — ship features independently |
| 80–89 | **A** | High autonomy, minimal guidance |
| 70–79 | **B** | Moderate autonomy, needs help on complex tasks |
| 60–69 | **C** | Basic maintenance only |
| 40–59 | **D** | Frequent stalling, constant intervention |
| 20–39 | **F** | Mostly unable to operate |
| 0–19 | **F-** | Effectively opaque to agents |

## Sample Output

```
╔══════════════════════════════════════════════════════════════════╗
║                  AGENTIC LEGIBILITY SCORECARD                   ║
║                       my-project                                ║
╚══════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────┬───────┬───────┬──────────┐
│ Category                            │ Score │  Max  │  Grade   │
├─────────────────────────────────────┼───────┼───────┼──────────┤
│ 1. Bootstrap & Environment          │  12   │  15   │  ▓▓▓▓▓░  │
│ 2. Entry Points & Commands          │  10   │  15   │  ▓▓▓▓░░  │
│ 3. Documentation & Navigation       │  14   │  20   │  ▓▓▓▓░░  │
│ 4. Architecture & Structure         │   8   │  15   │  ▓▓▓░░░  │
│ 5. Testing & Validation             │  13   │  15   │  ▓▓▓▓▓░  │
│ 6. Code Quality Enforcement         │   9   │  10   │  ▓▓▓▓▓░  │
│ 7. Security & Governance            │   6   │  10   │  ▓▓▓▓░░  │
├─────────────────────────────────────┼───────┼───────┼──────────┤
│ Qualitative Adjustment              │  +2   │  ±5   │          │
╞═════════════════════════════════════╪═══════╪═══════╪══════════╡
│ TOTAL                               │  74   │  100  │    B     │
└─────────────────────────────────────┴───────┴───────┴──────────┘

GRADE: B  —  "Solid foundation, but agents still need a guide for complex tasks"
```

## Project Structure

```
agentic-legibility-score/
├── SKILL.md                        # Agent skill instructions
├── scripts/
│   └── scan_repo.py                # Automated repository scanner
├── references/
│   └── scoring-rubric.md           # Detailed scoring criteria & rubric
├── AGENTS.md                       # Agent guide for this repo (dogfooding!)
├── CONTRIBUTING.md                 # How to contribute
├── CHANGELOG.md                    # Version history
├── LICENSE                         # MIT
└── README.md                       # You are here
```

## How It Works

1. **Scanner** (`scripts/scan_repo.py`) — Walks the repo tree and checks 100+ mechanical signals: file existence, config parsing, CI detection, documentation quality metrics, cross-linking, etc.

2. **Rubric** (`references/scoring-rubric.md`) — Detailed point breakdowns for each category and sub-criterion with full/partial/zero credit definitions.

3. **Skill** (`SKILL.md`) — Instructions for AI agents to combine scanner output with qualitative assessment and produce the formatted scorecard.

## What the Scanner Detects

- **Package manifests** — package.json, pyproject.toml, Cargo.toml, go.mod, and 10+ more
- **Build/test/lint commands** — npm scripts, Makefile targets, Justfile recipes, CI steps
- **Documentation** — README quality, AGENTS.md, CONTRIBUTING, docs/ structure, cross-linking
- **Architecture** — ADRs, design docs, exec plans, quality scores, code organization
- **Testing** — Test directories, test files, CI pipelines, coverage config, E2E setup
- **Code quality** — 15+ linter/formatter configs, type checking, pre-commit hooks
- **Security** — .gitignore coverage, Dependabot/Renovate, CODEOWNERS, security policies

## Requirements

- **Python 3.9+** (standard library only — zero dependencies)

## Sources

Built on frameworks from:

- [Agent Legibility Scoring](https://seand.ai/blog/agent-legibility-scoring/) — seand.ai (2026)
- [Harness Engineering](https://openai.com/index/harness-engineering/) — OpenAI (2025)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE)
