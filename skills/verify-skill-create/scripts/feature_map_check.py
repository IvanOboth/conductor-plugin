#!/usr/bin/env python3
"""Check a verification skill's feature map against the code it describes.

    feature_map_check.py <map-dir>                      hygiene + route coverage
    feature_map_check.py <map-dir> --base origin/main   also: what this branch changed that the map should follow
    feature_map_check.py <map-dir> --json               machine-readable result

<map-dir> is the skill's features/ directory. It holds README.md (the index), one Markdown file
per feature, and map.json:

    {
      "repo_root": "../../../..",                  # relative to <map-dir>
      "harness": "verify-mikono",                  # third H2 must read "Driving it with <harness>"
      "route_globs": ["apps/web/app/**/page.tsx"], # user-facing entry points that must be mapped
      "route_ignore": ["apps/web/app/**/test*/**"] # routes that are deliberately not mapped
    }

Each feature file starts with front matter:

    ---
    id: sales-quotes                     # equals the file name without .md
    sources:                             # globs, repo-relative, for the code behind the feature
      - apps/web/app/**/dashboard/sales/quotes/**
      - packages/backend/convex/quotations*.ts
    ---

Exit status: 0 clean (warnings allowed), 1 errors, 2 usage. --strict turns warnings into errors.
Errors: broken index, malformed feature files, and new routes in the diff that no feature covers.
Warnings: routes no feature covers (pre-existing gaps), and features whose sources changed on this
branch while their feature file did not.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REQUIRED_H2 = ["Sub-features", "How to get to it (user POV)", "Driving it with", "Gotchas"]


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a repo-relative glob (`**`, `*`, `?`) into an anchored regex over POSIX paths."""
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def matches_any(path: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(p.match(path) for p in patterns)


@dataclass
class Feature:
    id: str
    path: Path
    sources: list[str] = field(default_factory=list)
    patterns: list[re.Pattern[str]] = field(default_factory=list)


def parse_front_matter(text: str) -> tuple[dict[str, object], str]:
    """Parse the small YAML subset the map uses: `key: value` and `key:` followed by `- item` lines."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    meta: dict[str, object] = {}
    key = None
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = re.match(r"^\s+-\s+(.*?)\s*(?:#.*)?$", line)
        if item and key:
            value = item.group(1).strip().strip("'\"")
            current = meta.setdefault(key, [])
            if isinstance(current, list):
                current.append(value)
            continue
        kv = re.match(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*(?:#.*)?$", line)
        if kv:
            key = kv.group(1)
            meta[key] = kv.group(2).strip("'\"") if kv.group(2) else []
    return meta, text[end + 4 :]


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


def tracked_files(repo: Path) -> list[str]:
    """Tracked files plus untracked ones that are not ignored, so a new uncommitted route counts."""
    return sorted({p for p in git(repo, "ls-files", "--cached", "--others", "--exclude-standard").splitlines() if p})


def changed_files(repo: Path, base: str) -> tuple[list[str], list[str]]:
    """Files changed between the merge base and the working tree, and the subset that are new."""
    merge_base = git(repo, "merge-base", base, "HEAD").strip()
    changed, added = set(), set()
    for line in git(repo, "diff", "--name-status", merge_base).splitlines():
        parts = line.split("\t")
        status, path = parts[0], parts[-1]
        changed.add(path)
        if status.startswith("A") or status.startswith("R"):
            added.add(path)
    for path in git(repo, "ls-files", "--others", "--exclude-standard").splitlines():
        changed.add(path)
        added.add(path)
    return sorted(changed), sorted(added)


def load_features(map_dir: Path, harness: str, errors: list[str]) -> list[Feature]:
    features = []
    for path in sorted(map_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(text)
        rel = path.name
        fid = meta.get("id")
        if fid != path.stem:
            errors.append(f"{rel}: front matter id is {fid!r}, expected {path.stem!r}")
        sources = meta.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{rel}: front matter needs a non-empty sources list")
            sources = []
        if not re.search(r"^# \S", body, re.M):
            errors.append(f"{rel}: missing the H1 title")
        h2 = re.findall(r"^## (.+?)\s*$", body, re.M)
        expected = [h if h != "Driving it with" else f"Driving it with {harness}" for h in REQUIRED_H2]
        if h2 != expected:
            errors.append(f"{rel}: H2 sections are {h2}, expected exactly {expected}")
        features.append(Feature(str(path.stem), path, list(sources), [glob_to_regex(s) for s in sources]))
    return features


def index_links(readme: Path) -> list[str]:
    links = re.findall(r"\]\((?:\./)?([^)#\s]+\.md)\)", readme.read_text(encoding="utf-8"))
    return [link for link in links if "/" not in link]


def check(map_dir: Path, base: str | None) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    config_path = map_dir / "map.json"
    if not config_path.exists():
        return {"errors": [f"{config_path} is missing"], "warnings": [], "summary": {}}
    config = json.loads(config_path.read_text(encoding="utf-8"))
    repo = (map_dir / config.get("repo_root", ".")).resolve()
    harness = config.get("harness", "")
    if not harness:
        errors.append("map.json: harness is required")

    readme = map_dir / "README.md"
    if not readme.exists():
        errors.append("README.md (the index) is missing")
        linked: list[str] = []
    else:
        linked = index_links(readme)
    files = sorted(p.name for p in map_dir.glob("*.md") if p.name != "README.md")
    for name in sorted(set(linked) - set(files)):
        errors.append(f"README.md links {name}, which does not exist")
    for name in sorted(set(files) - set(linked)):
        errors.append(f"{name} is not listed in README.md")
    for name in sorted({n for n in linked if linked.count(n) > 1}):
        errors.append(f"README.md lists {name} more than once")

    features = load_features(map_dir, harness, errors)
    all_files = tracked_files(repo)
    for feat in features:
        if feat.patterns and not any(matches_any(f, feat.patterns) for f in all_files):
            warnings.append(f"{feat.path.name}: no tracked file matches its sources (stale glob?)")

    route_res = [glob_to_regex(g) for g in config.get("route_globs", [])]
    ignore_res = [glob_to_regex(g) for g in config.get("route_ignore", [])]
    feature_res = [p for feat in features for p in feat.patterns]

    def mapped_route(path: str) -> bool:
        return matches_any(path, route_res) and not matches_any(path, ignore_res)

    routes = [f for f in all_files if mapped_route(f)]
    uncovered = [r for r in routes if not matches_any(r, feature_res)]

    touched: list[dict[str, object]] = []
    new_uncovered: list[str] = []
    if base:
        changed, added = changed_files(repo, base)
        map_rel = str(map_dir.resolve().relative_to(repo))
        changed_maps = {Path(c).name for c in changed if c.startswith(map_rel + "/")}
        for feat in features:
            hits = [c for c in changed if matches_any(c, feat.patterns)]
            if hits and feat.path.name not in changed_maps:
                touched.append({"feature": feat.path.name, "changed_sources": hits[:10]})
                warnings.append(
                    f"{feat.path.name}: {len(hits)} source file(s) changed on this branch but the feature "
                    f"file did not (e.g. {hits[0]}); update it, or say in the PR why the user path is unchanged"
                )
        uncovered_set = set(uncovered)
        new_uncovered = [a for a in added if a in uncovered_set]
        for route in new_uncovered:
            errors.append(f"new route {route} is not covered by any feature's sources; add it to a feature file")
        uncovered = [r for r in uncovered if r not in set(new_uncovered)]

    if uncovered:
        warnings.append(f"{len(uncovered)} route(s) not covered by any feature: " + ", ".join(uncovered[:15])
                        + (" …" if len(uncovered) > 15 else ""))

    return {
        "errors": errors,
        "warnings": warnings,
        "touched_features": touched,
        "uncovered_routes": uncovered,
        "new_uncovered_routes": new_uncovered,
        "summary": {
            "features": len(features),
            "routes": len(routes),
            "covered_routes": len(routes) - len(uncovered) - len(new_uncovered),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("map_dir", type=Path)
    parser.add_argument("--base", help="git ref to diff against (merge base with HEAD), e.g. origin/develop")
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args(argv)
    if not args.map_dir.is_dir():
        print(f"feature_map_check: {args.map_dir} is not a directory", file=sys.stderr)
        return 2
    try:
        result = check(args.map_dir, args.base)
    except subprocess.CalledProcessError as exc:
        print(f"feature_map_check: git failed: {exc.stderr.strip()}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        s = result["summary"]
        if s:
            print(f"features {s['features']}  routes {s['routes']}  covered {s['covered_routes']}")
        for e in result["errors"]:
            print(f"ERROR   {e}")
        for w in result["warnings"]:
            print(f"WARNING {w}")
        if not result["errors"] and not result["warnings"]:
            print("OK")
    failed = bool(result["errors"]) or (args.strict and bool(result["warnings"]))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
