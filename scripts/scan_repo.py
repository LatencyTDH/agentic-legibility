#!/usr/bin/env python3
"""
Agentic Legibility Scanner — Automated repository analysis for AI agent readiness.

Scans a repository for signals that determine how effectively an autonomous AI agent
can navigate, understand, build, test, and contribute to the codebase.

Usage: python3 scan_repo.py [path-to-repo]

Outputs JSON with findings for each scoring category.
"""

import json
import os
import re
import sys
from pathlib import Path


def scan_repo(repo_path: str) -> dict:
    root = Path(repo_path).resolve()
    findings = {
        "repo_path": str(root),
        "repo_name": root.name,
        "categories": {
            "bootstrap": scan_bootstrap(root),
            "entry_points": scan_entry_points(root),
            "documentation": scan_documentation(root),
            "architecture": scan_architecture(root),
            "testing": scan_testing(root),
            "code_quality": scan_code_quality(root),
            "security": scan_security(root),
        },
        "file_stats": get_file_stats(root),
    }
    return findings


def file_exists(root: Path, *patterns: str) -> list[str]:
    """Check which files exist (case-insensitive glob)."""
    found = []
    for pattern in patterns:
        # Direct check
        target = root / pattern
        if target.exists():
            found.append(pattern)
            continue
        # Case-insensitive check in root
        parent = root / Path(pattern).parent
        name_lower = Path(pattern).name.lower()
        if parent.exists():
            for item in parent.iterdir():
                if item.name.lower() == name_lower:
                    found.append(str(item.relative_to(root)))
                    break
    return found


def glob_find(root: Path, pattern: str, max_depth: int = 4) -> list[str]:
    """Find files matching glob pattern, respecting max_depth."""
    results = []
    for path in root.rglob(pattern):
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if len(rel.parts) <= max_depth and not any(
            p.startswith(".") and p not in (".github", ".gitlab", ".circleci", ".husky")
            for p in rel.parts[:-1]
        ):
            if "node_modules" not in str(rel) and "vendor" not in str(rel) and ".git/" not in str(rel):
                results.append(str(rel))
    return results


def read_file_safe(path: Path, max_bytes: int = 50000) -> str:
    """Read file content safely."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:max_bytes]
    except Exception:
        return ""


def scan_bootstrap(root: Path) -> dict:
    """Category 1: Bootstrap & Environment Setup (15 pts)."""
    signals = {}

    # Setup documentation in README
    readme_files = file_exists(root, "README.md", "README.rst", "README.txt", "README")
    signals["readme_exists"] = len(readme_files) > 0
    signals["readme_files"] = readme_files

    readme_content = ""
    for rf in readme_files:
        readme_content += read_file_safe(root / rf).lower()

    setup_keywords = ["install", "setup", "getting started", "quick start", "quickstart", "prerequisites", "requirements"]
    signals["readme_has_setup"] = any(kw in readme_content for kw in setup_keywords)

    run_keywords = ["npm run", "yarn ", "pnpm ", "make ", "cargo ", "go run", "python ", "pip install", "poetry install", "bundle install", "docker", "./gradlew", "mvn "]
    signals["readme_has_commands"] = any(kw in readme_content for kw in run_keywords)

    # Dev environment
    signals["devcontainer"] = len(file_exists(root, ".devcontainer/devcontainer.json", ".devcontainer.json")) > 0
    signals["docker_compose"] = len(file_exists(root, "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml")) > 0
    signals["dockerfile"] = len(file_exists(root, "Dockerfile", "dockerfile")) > 0
    signals["env_example"] = len(file_exists(root, ".env.example", ".env.sample", ".env.template", "env.example")) > 0
    signals["nix_config"] = len(file_exists(root, "flake.nix", "shell.nix", "default.nix")) > 0

    # Dependency management
    signals["lockfile"] = len(file_exists(
        root, "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
        "Pipfile.lock", "poetry.lock", "uv.lock", "Cargo.lock", "go.sum",
        "Gemfile.lock", "composer.lock", "gradle.lockfile"
    )) > 0
    signals["package_manifest"] = len(file_exists(
        root, "package.json", "pyproject.toml", "Cargo.toml", "go.mod",
        "Gemfile", "composer.json", "build.gradle", "pom.xml", "setup.py",
        "setup.cfg", "requirements.txt", "Pipfile"
    )) > 0

    # Makefile / task runner
    signals["makefile"] = len(file_exists(root, "Makefile", "makefile", "GNUmakefile", "Justfile", "Taskfile.yml")) > 0

    return signals


def scan_entry_points(root: Path) -> dict:
    """Category 2: Entry Points & Commands (15 pts)."""
    signals = {}

    # Analyze package.json scripts
    pkg_json = root / "package.json"
    signals["npm_scripts"] = {}
    if pkg_json.exists():
        try:
            pkg = json.loads(read_file_safe(pkg_json))
            scripts = pkg.get("scripts", {})
            signals["npm_scripts"] = {k: v for k, v in list(scripts.items())[:30]}
            signals["has_build_script"] = any(k in scripts for k in ["build", "compile", "dist"])
            signals["has_test_script"] = any(k in scripts for k in ["test", "test:unit", "test:e2e", "test:integration"])
            signals["has_lint_script"] = any(k in scripts for k in ["lint", "lint:fix", "eslint", "check"])
            signals["has_format_script"] = any(k in scripts for k in ["format", "fmt", "prettier"])
            signals["has_dev_script"] = any(k in scripts for k in ["dev", "start", "serve"])
        except json.JSONDecodeError:
            pass

    # Analyze pyproject.toml
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        content = read_file_safe(pyproject)
        signals["pyproject_has_scripts"] = "[tool.poetry.scripts]" in content or "[project.scripts]" in content
        signals["pyproject_has_test_config"] = "[tool.pytest" in content or "[tool.tox" in content
        signals["pyproject_has_lint_config"] = any(t in content for t in ["[tool.ruff", "[tool.flake8", "[tool.pylint", "[tool.mypy"])

    # Makefile targets
    makefile_path = None
    for name in ["Makefile", "makefile", "GNUmakefile"]:
        if (root / name).exists():
            makefile_path = root / name
            break

    if makefile_path:
        content = read_file_safe(makefile_path)
        targets = re.findall(r"^([a-zA-Z_][\w-]*):", content, re.MULTILINE)
        signals["makefile_targets"] = targets[:30]
        signals["make_has_build"] = any(t in targets for t in ["build", "compile", "dist", "all"])
        signals["make_has_test"] = any(t in targets for t in ["test", "tests", "check", "verify"])
        signals["make_has_lint"] = any(t in targets for t in ["lint", "check", "fmt", "format"])

    # Justfile
    justfile = root / "Justfile"
    if justfile.exists():
        content = read_file_safe(justfile)
        recipes = re.findall(r"^([a-zA-Z_][\w-]*)(?:\s|:)", content, re.MULTILINE)
        signals["justfile_recipes"] = recipes[:30]

    # CI files (reveal available commands)
    ci_files = glob_find(root, "*.yml", max_depth=3) + glob_find(root, "*.yaml", max_depth=3)
    ci_relevant = [f for f in ci_files if any(d in f for d in [".github/workflows", ".gitlab-ci", ".circleci"])]
    signals["ci_files"] = ci_relevant

    return signals


def scan_documentation(root: Path) -> dict:
    """Category 3: Documentation & Navigation (20 pts)."""
    signals = {}

    # Agent-specific docs
    signals["agents_md"] = len(file_exists(root, "AGENTS.md", "agents.md", ".github/AGENTS.md")) > 0
    signals["copilot_instructions"] = len(file_exists(
        root, ".github/copilot-instructions.md", ".copilot-instructions.md",
        "CLAUDE.md", ".claude/CLAUDE.md", ".cursorrules", ".cursor/rules"
    )) > 0

    # Core docs
    signals["contributing"] = len(file_exists(root, "CONTRIBUTING.md", "CONTRIBUTING.rst", "CONTRIBUTING", ".github/CONTRIBUTING.md")) > 0
    signals["changelog"] = len(file_exists(root, "CHANGELOG.md", "CHANGES.md", "HISTORY.md", "RELEASES.md")) > 0
    signals["code_of_conduct"] = len(file_exists(root, "CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md")) > 0
    signals["license"] = len(file_exists(root, "LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "COPYING")) > 0

    # Documentation directory structure
    docs_dirs = file_exists(root, "docs", "doc", "documentation", "wiki")
    signals["docs_directory"] = len(docs_dirs) > 0
    signals["docs_dirs_found"] = docs_dirs

    if signals["docs_directory"]:
        all_docs = []
        for d in docs_dirs:
            all_docs.extend(glob_find(root / d, "*.md", max_depth=3))
            all_docs.extend(glob_find(root / d, "*.rst", max_depth=3))
            all_docs.extend(glob_find(root / d, "*.txt", max_depth=3))
        signals["docs_file_count"] = len(all_docs)
        signals["docs_files_sample"] = all_docs[:20]
    else:
        signals["docs_file_count"] = 0

    # Check for cross-linking in docs
    if signals["docs_directory"]:
        cross_links = 0
        for d in docs_dirs:
            for md in glob_find(root / d, "*.md", max_depth=3):
                content = read_file_safe(root / d / md)
                cross_links += len(re.findall(r"\[.*?\]\(.*?\.md\)", content))
        signals["docs_cross_links"] = cross_links
    else:
        signals["docs_cross_links"] = 0

    # README quality assessment
    readme_content = ""
    for name in ["README.md", "README.rst"]:
        p = root / name
        if p.exists():
            readme_content = read_file_safe(p)
            break
    signals["readme_length"] = len(readme_content)
    signals["readme_has_badges"] = bool(re.search(r"\[!\[", readme_content))
    signals["readme_has_toc"] = bool(re.search(r"table of contents|## contents|## toc", readme_content, re.IGNORECASE))
    signals["readme_heading_count"] = len(re.findall(r"^#{1,3}\s", readme_content, re.MULTILINE))
    signals["readme_code_blocks"] = len(re.findall(r"```", readme_content))

    # API docs
    signals["api_docs"] = len(glob_find(root, "openapi.*", max_depth=2)) > 0 or len(glob_find(root, "swagger.*", max_depth=2)) > 0
    signals["typedoc_or_jsdoc"] = len(file_exists(root, "typedoc.json", ".jsdoc.json", "jsdoc.json")) > 0

    return signals


def scan_architecture(root: Path) -> dict:
    """Category 4: Architecture & Structure (15 pts)."""
    signals = {}

    # Architecture docs
    signals["architecture_md"] = len(file_exists(
        root, "ARCHITECTURE.md", "architecture.md", "docs/ARCHITECTURE.md",
        "docs/architecture.md", "DESIGN.md", "docs/DESIGN.md"
    )) > 0

    # ADRs
    adr_dirs = file_exists(root, "docs/adr", "docs/adrs", "adr", "adrs",
                            "docs/architecture/decisions", "docs/decisions")
    signals["has_adrs"] = len(adr_dirs) > 0
    if signals["has_adrs"]:
        adr_files = []
        for d in adr_dirs:
            adr_files.extend(glob_find(root / d, "*.md", max_depth=2))
        signals["adr_count"] = len(adr_files)
    else:
        signals["adr_count"] = 0

    # Design docs
    design_dirs = file_exists(root, "docs/design-docs", "docs/design", "docs/rfcs", "rfcs")
    signals["has_design_docs"] = len(design_dirs) > 0

    # Execution plans
    signals["has_exec_plans"] = len(file_exists(root, "docs/exec-plans", "docs/plans", "PLANS.md")) > 0

    # Quality tracking
    signals["quality_score"] = len(file_exists(root, "QUALITY_SCORE.md", "docs/QUALITY_SCORE.md")) > 0
    signals["tech_debt_tracking"] = len(file_exists(
        root, "docs/tech-debt-tracker.md", "TODO.md", "TECH_DEBT.md",
        "docs/exec-plans/tech-debt-tracker.md"
    )) > 0

    # Directory structure analysis
    top_level = []
    try:
        for item in sorted(root.iterdir()):
            if item.name.startswith(".") and item.name not in (".github", ".gitlab", ".circleci", ".vscode"):
                continue
            if item.name in ("node_modules", "vendor", "__pycache__", ".git", "dist", "build", "target"):
                continue
            top_level.append(f"{'📁 ' if item.is_dir() else '📄 '}{item.name}")
    except PermissionError:
        pass
    signals["top_level_structure"] = top_level[:40]

    # Source organization
    src_dirs = file_exists(root, "src", "lib", "app", "pkg", "internal", "cmd", "packages")
    signals["has_src_dir"] = len(src_dirs) > 0
    signals["src_dirs"] = src_dirs

    # Monorepo indicators
    signals["is_monorepo"] = len(file_exists(
        root, "lerna.json", "nx.json", "turbo.json", "pnpm-workspace.yaml",
        "rush.json", "packages"
    )) > 0

    return signals


def scan_testing(root: Path) -> dict:
    """Category 5: Testing & Validation (15 pts)."""
    signals = {}

    # Test directories
    test_dirs = file_exists(root, "tests", "test", "__tests__", "spec", "specs",
                             "src/__tests__", "src/tests", "e2e", "cypress",
                             "playwright", "integration-tests")
    signals["test_dirs"] = test_dirs
    signals["has_test_dir"] = len(test_dirs) > 0

    # Test files (sample)
    test_patterns = ["*test*", "*spec*", "*_test.*", "test_*"]
    test_files = []
    for pattern in test_patterns:
        test_files.extend(glob_find(root, pattern, max_depth=5))
    # Deduplicate and filter
    test_files = list(set(f for f in test_files if not any(
        skip in f for skip in ["node_modules", "vendor", ".git", "testdata", "testutil", "testhelper"]
    )))
    signals["test_file_count"] = len(test_files)
    signals["test_files_sample"] = sorted(test_files)[:15]

    # CI/CD
    ci_configs = file_exists(
        root, ".github/workflows", ".gitlab-ci.yml", ".circleci/config.yml",
        "Jenkinsfile", ".travis.yml", "azure-pipelines.yml", "bitbucket-pipelines.yml",
        ".buildkite/pipeline.yml"
    )
    signals["ci_configured"] = len(ci_configs) > 0
    signals["ci_systems"] = ci_configs

    if (root / ".github/workflows").is_dir():
        workflows = glob_find(root / ".github/workflows", "*.yml") + glob_find(root / ".github/workflows", "*.yaml")
        signals["github_workflow_count"] = len(workflows)
        signals["github_workflows"] = [str(Path(".github/workflows") / w) for w in workflows[:10]]
    else:
        signals["github_workflow_count"] = 0

    # Test config files
    signals["jest_config"] = len(file_exists(root, "jest.config.js", "jest.config.ts", "jest.config.mjs")) > 0
    signals["vitest_config"] = len(file_exists(root, "vitest.config.ts", "vitest.config.js", "vitest.config.mts")) > 0
    signals["pytest_config"] = len(file_exists(root, "pytest.ini", "conftest.py", "setup.cfg")) > 0
    signals["playwright_config"] = len(file_exists(root, "playwright.config.ts", "playwright.config.js")) > 0
    signals["cypress_config"] = len(file_exists(root, "cypress.config.ts", "cypress.config.js", "cypress.json")) > 0

    # Coverage config
    signals["coverage_config"] = len(file_exists(
        root, ".nycrc", ".nycrc.json", ".coveragerc", "codecov.yml",
        ".codecov.yml", "coverage", ".c8rc.json"
    )) > 0

    # Check CI files for test execution
    if signals["ci_configured"]:
        ci_content = ""
        for cf in ci_configs:
            p = root / cf
            if p.is_file():
                ci_content += read_file_safe(p).lower()
            elif p.is_dir():
                for f in glob_find(p, "*.yml") + glob_find(p, "*.yaml"):
                    ci_content += read_file_safe(p / f).lower()
        signals["ci_runs_tests"] = any(kw in ci_content for kw in ["test", "pytest", "jest", "vitest", "cargo test", "go test"])
        signals["ci_runs_lint"] = any(kw in ci_content for kw in ["lint", "eslint", "ruff", "clippy", "golangci"])
        signals["ci_runs_typecheck"] = any(kw in ci_content for kw in ["typecheck", "type-check", "tsc", "mypy", "pyright"])
    else:
        signals["ci_runs_tests"] = False
        signals["ci_runs_lint"] = False
        signals["ci_runs_typecheck"] = False

    return signals


def scan_code_quality(root: Path) -> dict:
    """Category 6: Code Quality Enforcement (10 pts)."""
    signals = {}

    # Linter configs
    signals["eslint"] = len(file_exists(
        root, ".eslintrc", ".eslintrc.js", ".eslintrc.json", ".eslintrc.yml",
        ".eslintrc.cjs", "eslint.config.js", "eslint.config.mjs", "eslint.config.ts"
    )) > 0
    signals["biome"] = len(file_exists(root, "biome.json", "biome.jsonc")) > 0
    signals["ruff"] = len(file_exists(root, "ruff.toml", ".ruff.toml")) > 0
    signals["clippy"] = False  # Detected via Cargo.toml
    if (root / "Cargo.toml").exists():
        signals["clippy"] = True  # Clippy is built into Rust toolchain
    signals["golangci"] = len(file_exists(root, ".golangci.yml", ".golangci.yaml", ".golangci.json")) > 0
    signals["has_linter"] = any([signals["eslint"], signals["biome"], signals["ruff"], signals["clippy"], signals["golangci"]])

    # Formatter configs
    signals["prettier"] = len(file_exists(
        root, ".prettierrc", ".prettierrc.js", ".prettierrc.json", ".prettierrc.yml",
        ".prettierrc.cjs", "prettier.config.js", "prettier.config.mjs"
    )) > 0
    signals["editorconfig"] = len(file_exists(root, ".editorconfig")) > 0
    signals["has_formatter"] = signals["prettier"] or signals["biome"] or signals["editorconfig"]

    # Type checking
    signals["tsconfig"] = len(file_exists(root, "tsconfig.json", "tsconfig.base.json")) > 0
    if signals["tsconfig"]:
        ts_content = read_file_safe(root / "tsconfig.json")
        signals["ts_strict"] = '"strict": true' in ts_content or '"strict":true' in ts_content

    signals["mypy"] = len(file_exists(root, "mypy.ini", ".mypy.ini")) > 0
    signals["pyright"] = len(file_exists(root, "pyrightconfig.json")) > 0

    # Check pyproject.toml for type checking
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        content = read_file_safe(pyproject)
        if "[tool.mypy]" in content:
            signals["mypy"] = True
        if "[tool.ruff" in content:
            signals["ruff"] = True
            signals["has_linter"] = True

    signals["has_typecheck"] = signals.get("tsconfig", False) or signals["mypy"] or signals["pyright"]

    # Pre-commit hooks
    signals["pre_commit"] = len(file_exists(root, ".pre-commit-config.yaml", ".pre-commit-config.yml")) > 0
    signals["husky"] = len(file_exists(root, ".husky", ".husky/pre-commit")) > 0
    signals["lefthook"] = len(file_exists(root, "lefthook.yml", ".lefthook.yml")) > 0
    signals["lint_staged"] = False
    if (root / "package.json").exists():
        pkg_content = read_file_safe(root / "package.json")
        signals["lint_staged"] = "lint-staged" in pkg_content
    signals["has_git_hooks"] = any([signals["pre_commit"], signals["husky"], signals["lefthook"], signals["lint_staged"]])

    return signals


def scan_security(root: Path) -> dict:
    """Category 7: Security & Governance (10 pts)."""
    signals = {}

    # Gitignore
    signals["gitignore"] = len(file_exists(root, ".gitignore")) > 0
    if signals["gitignore"]:
        gi_content = read_file_safe(root / ".gitignore").lower()
        signals["gitignore_covers_env"] = any(p in gi_content for p in [".env", "*.env", ".env.*"])
        signals["gitignore_covers_secrets"] = any(p in gi_content for p in [".env", "secret", "credential", "*.pem", "*.key"])
    else:
        signals["gitignore_covers_env"] = False
        signals["gitignore_covers_secrets"] = False

    # Security scanning
    signals["dependabot"] = len(file_exists(root, ".github/dependabot.yml", ".github/dependabot.yaml")) > 0
    signals["renovate"] = len(file_exists(root, "renovate.json", ".renovaterc", ".renovaterc.json", "renovate.json5")) > 0
    signals["snyk"] = len(file_exists(root, ".snyk")) > 0
    signals["has_dep_updates"] = any([signals["dependabot"], signals["renovate"], signals["snyk"]])

    # Security policy
    signals["security_policy"] = len(file_exists(root, "SECURITY.md", ".github/SECURITY.md")) > 0

    # CODEOWNERS
    signals["codeowners"] = len(file_exists(root, "CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS")) > 0

    # PR template
    signals["pr_template"] = len(file_exists(
        root, ".github/pull_request_template.md", ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/PULL_REQUEST_TEMPLATE"
    )) > 0

    # Issue templates
    signals["issue_templates"] = (root / ".github/ISSUE_TEMPLATE").is_dir() or \
        len(file_exists(root, ".github/ISSUE_TEMPLATE.md")) > 0

    # Secret scanning patterns
    signals["gitleaks"] = len(file_exists(root, ".gitleaks.toml", "gitleaks.toml")) > 0
    signals["trivy"] = len(file_exists(root, "trivy.yaml", ".trivy.yaml")) > 0

    return signals


def get_file_stats(root: Path) -> dict:
    """Gather overall repository statistics."""
    stats = {"total_files": 0, "languages": {}, "total_dirs": 0}
    ext_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
        ".jsx": "JavaScript", ".rs": "Rust", ".go": "Go", ".rb": "Ruby",
        ".java": "Java", ".kt": "Kotlin", ".swift": "Swift", ".c": "C",
        ".cpp": "C++", ".cs": "C#", ".php": "PHP", ".vue": "Vue",
        ".svelte": "Svelte", ".dart": "Dart", ".ex": "Elixir", ".exs": "Elixir",
        ".zig": "Zig", ".md": "Markdown", ".yml": "YAML", ".yaml": "YAML",
        ".json": "JSON", ".toml": "TOML", ".sh": "Shell", ".bash": "Shell",
        ".css": "CSS", ".scss": "SCSS", ".html": "HTML",
    }
    skip_dirs = {"node_modules", "vendor", ".git", "__pycache__", "dist", "build",
                 "target", ".next", ".nuxt", "coverage", ".tox", ".mypy_cache",
                 ".pytest_cache", "venv", ".venv", "env", ".env"}

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune directories
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        stats["total_dirs"] += 1

        for f in filenames:
            stats["total_files"] += 1
            ext = Path(f).suffix.lower()
            if ext in ext_map:
                lang = ext_map[ext]
                stats["languages"][lang] = stats["languages"].get(lang, 0) + 1

        if stats["total_files"] > 50000:  # Safety cap
            break

    # Sort languages by count
    stats["languages"] = dict(sorted(stats["languages"].items(), key=lambda x: -x[1]))
    return stats


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    if not Path(path).is_dir():
        print(json.dumps({"error": f"Not a directory: {path}"}), file=sys.stderr)
        sys.exit(1)
    result = scan_repo(path)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
