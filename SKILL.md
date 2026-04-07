---
name: agentic-legibility-score
description: "Score any code repository 0-100 on Agentic Legibility — how effectively autonomous AI agents can navigate, understand, build, test, and contribute to the codebase. Based on seand.ai's Agent Legibility framework and OpenAI's Harness Engineering practices. Use when the user asks to score, evaluate, audit, or assess a repo for agent readiness, agentic legibility, AI-friendliness, or wants to know how well their codebase supports autonomous AI development."
---

# Agentic Legibility Score

Score a repository 0-100 on how effectively AI agents can autonomously operate within it.

## Philosophy

> "Autonomous coding usually fails in boring ways. The model cannot find the setup command. It does not know which folder matters. It cannot tell whether the task is done." — seand.ai

Agent failures are almost always environment failures. This skill evaluates the scaffolding, not the code.

## Evaluation Workflow

### Step 1: Run the Automated Scanner

Execute the scanner script against the target repository:

```bash
python3 ~/.claude/skills/agentic-legibility-score/scripts/scan_repo.py /path/to/repo
```

If no specific repo is given, scan the current workspace root.

Capture the JSON output — it contains all mechanical signals needed for scoring.

### Step 2: Score Each Category

Read the detailed rubric at `references/scoring-rubric.md` for full criteria.

Use scanner output + qualitative assessment to score all 7 categories:

| # | Category | Max | What It Measures |
|---|---|---|---|
| 1 | Bootstrap & Environment | 15 | Can an agent set up and run the project cold? |
| 2 | Entry Points & Commands | 15 | Can it find build/test/lint without guessing? |
| 3 | Documentation & Navigation | 20 | Is there a map? Can the agent find its way? |
| 4 | Architecture & Structure | 15 | Does it understand why things are where they are? |
| 5 | Testing & Validation | 15 | Can it verify changes without a human? |
| 6 | Code Quality Enforcement | 10 | Are quality gates automated and discoverable? |
| 7 | Security & Governance | 10 | Will it avoid introducing vulnerabilities? |

Apply qualitative adjustments (±5 pts) per the rubric for factors the scanner cannot detect.

### Step 3: Generate the Scorecard

Present findings using this exact format:

```
╔══════════════════════════════════════════════════════════════════╗
║                  AGENTIC LEGIBILITY SCORECARD                   ║
║                     {repo_name}                                 ║
╚══════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────┬───────┬───────┬──────────┐
│ Category                            │ Score │  Max  │  Grade   │
├─────────────────────────────────────┼───────┼───────┼──────────┤
│ 1. Bootstrap & Environment          │  XX   │  15   │  ▓▓▓▓░░  │
│ 2. Entry Points & Commands          │  XX   │  15   │  ▓▓▓░░░  │
│ 3. Documentation & Navigation       │  XX   │  20   │  ▓▓▓▓▓░  │
│ 4. Architecture & Structure         │  XX   │  15   │  ▓▓░░░░  │
│ 5. Testing & Validation             │  XX   │  15   │  ▓▓▓▓░░  │
│ 6. Code Quality Enforcement         │  XX   │  10   │  ▓▓▓▓▓▓  │
│ 7. Security & Governance            │  XX   │  10   │  ▓▓▓░░░  │
├─────────────────────────────────────┼───────┼───────┼──────────┤
│ Qualitative Adjustment              │  ±X   │  ±5   │          │
╞═════════════════════════════════════╪═══════╪═══════╪══════════╡
│ TOTAL                               │  XX   │  100  │    ?     │
└─────────────────────────────────────┴───────┴───────┴──────────┘

GRADE: [A+/A/B/C/D/F/F-]  —  "{one-line verdict}"
```

Use 6-char progress bars: each ▓ = ~17% of category max. Round to nearest block.

### Step 4: Category Deep-Dives

For each category, output a findings block:

```
### {N}. {Category Name} — {score}/{max} ({letter})

✅ What's working:
  • {signal found}
  • {signal found}

❌ What's missing:
  • {gap identified} — {why it matters for agents}

💡 Quick wins:
  • {specific actionable fix} (est. +X pts)
```

### Step 5: Executive Summary

Close with:

```
## Agentic Legibility Summary

**Score: XX/100 ({Grade})**

**What this means:** {2-3 sentence interpretation of what agents can/cannot
do in this repo based on the grade.}

**Top 3 Improvements (highest leverage):**
1. {action} → expected impact: +X pts
2. {action} → expected impact: +X pts
3. {action} → expected impact: +X pts

**Bottom line:** {One punchy sentence. Channel the spirit of
"None of this is glamorous. That is exactly why it matters."}
```

## Grade Scale Reference

| Score | Grade | Agent Capability |
|---|---|---|
| 90-100 | A+ | Full autonomous operation |
| 80-89 | A | High autonomy, minimal guidance needed |
| 70-79 | B | Moderate autonomy, guidance for complex tasks |
| 60-69 | C | Limited autonomy, basic maintenance only |
| 40-59 | D | Minimal autonomy, frequent stalling |
| 20-39 | F | Mostly unable to operate |
| 0-19 | F- | Opaque to agents |

## Sources

- [Agent Legibility Scoring](https://seand.ai/blog/agent-legibility-scoring/) — seand.ai (2026)
- [Harness Engineering](https://openai.com/index/harness-engineering/) — OpenAI (2025)
