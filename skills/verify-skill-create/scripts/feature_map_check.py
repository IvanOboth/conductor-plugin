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
Errors: broken index, malformed feature files, new routes in the diff that no feature covers, and
features whose sources changed on this branch while their feature file did not. Acknowledge a
feature whose user path really is unchanged with --allow-unchanged <id> (repeatable), or with a line
`map unchanged: <id> — <reason>` in a file passed as --allow-unchanged-from (CI passes the PR body).
Warnings: routes no feature covers that already existed on the base (pre-existing gaps).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

VERSION = "5"
REQUIRED_H2 = ["Sub-features", "How to get to it (user POV)", "Driving it with", "Gotchas"]
JOURNEY_H2 = ["Goal and context", "Steps the user expects", "Path in the app", "Driving it with", "Gotchas"]


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
    """Tracked files plus untracked ones that are not ignored, so a new uncommitted route counts.
    NUL-delimited, so non-ASCII paths are not quoted and escaped."""
    out = git(repo, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    return sorted({p for p in out.split("\0") if p})


def changed_files(repo: Path, base: str) -> tuple[list[str], list[str]]:
    """Files changed between the merge base and the working tree, and the subset that are new."""
    merge_base = git(repo, "merge-base", base, "HEAD").strip()
    changed, added = set(), set()
    fields = git(repo, "diff", "-z", "--name-status", merge_base).split("\0")
    i = 0
    while i < len(fields) and fields[i]:
        status = fields[i]
        if status[0] in "RC":
            old, new = fields[i + 1], fields[i + 2]
            changed.update({old, new})  # the feature losing the file is touched too
            added.add(new)
            i += 3
        else:
            path = fields[i + 1]
            changed.add(path)
            if status.startswith("A"):
                added.add(path)
            i += 2
    for path in git(repo, "ls-files", "-z", "--others", "--exclude-standard").split("\0"):
        if path:
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


def load_journeys(map_dir: Path, harness: str, feature_ids: set[str], errors: list[str]) -> list[Feature]:
    """Journey files (features/journeys/*.md): a persona's job across features, used by journey-review."""
    journeys = []
    for path in sorted((map_dir / "journeys").glob("*.md")):
        rel = f"journeys/{path.name}"
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        if meta.get("id") != path.stem:
            errors.append(f"{rel}: front matter id is {meta.get('id')!r}, expected {path.stem!r}")
        if not meta.get("persona"):
            errors.append(f"{rel}: front matter needs persona")
        listed = meta.get("features")
        if isinstance(listed, str):
            listed = [f.strip().strip("'\"") for f in listed.strip("[]").split(",") if f.strip().strip("'\"")]
        if not listed:
            errors.append(f"{rel}: front matter needs the features it crosses")
        for fid in listed or []:
            if fid not in feature_ids:
                errors.append(f"{rel}: lists feature {fid!r}, which has no feature file")
        sources = meta.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{rel}: front matter needs a non-empty sources list")
            sources = []
        if not re.search(r"^# \S", body, re.M):
            errors.append(f"{rel}: missing the H1 title")
        h2 = re.findall(r"^## (.+?)\s*$", body, re.M)
        expected = [h if h != "Driving it with" else f"Driving it with {harness}" for h in JOURNEY_H2]
        if h2 != expected:
            errors.append(f"{rel}: H2 sections are {h2}, expected exactly {expected}")
        journeys.append(Feature(str(path.stem), path, list(sources), [glob_to_regex(x) for x in sources]))
    return journeys


def index_links(readme: Path, prefix: str = "") -> list[str]:
    """Index links to map files: top-level feature files, or those under `prefix` (e.g. "journeys/")."""
    links = re.findall(r"\]\((?:\./)?([^)#\s]+\.md)\)", readme.read_text(encoding="utf-8"))
    if prefix:
        return [link for link in links if link.startswith(prefix) and "/" not in link[len(prefix):]]
    return [link for link in links if "/" not in link]


def read_allowances(path: Path | None) -> set[str]:
    """Feature ids acknowledged as unchanged by `map unchanged: <id>` lines (e.g. in a PR body)."""
    if not path or not path.exists():
        return set()
    text = path.read_text(encoding="utf-8", errors="replace")
    return {m.group(1) for m in re.finditer(r"map unchanged:\s*`?([a-z0-9][a-z0-9-]*)`?", text, re.I)}


def check(map_dir: Path, base: str | None, allow_unchanged: set[str] | None = None) -> dict[str, object]:
    allow_unchanged = allow_unchanged or set()
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
    journeys = load_journeys(map_dir, harness, {f.id for f in features}, errors)
    for clash in sorted({j.id for j in journeys} & {f.id for f in features}):
        errors.append(f"journeys/{clash}.md has the same id as {clash}.md; give the journey its own id "
                      f"(a map-unchanged acknowledgement must name exactly one file)")
    if readme.exists():
        jlinked = index_links(readme, "journeys/")
        jfiles = sorted(f"journeys/{p.name}" for p in (map_dir / "journeys").glob("*.md"))
        for name in sorted(set(jlinked) - set(jfiles)):
            errors.append(f"README.md links {name}, which does not exist")
        for name in sorted(set(jfiles) - set(jlinked)):
            errors.append(f"{name} is not listed in README.md")
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
        changed_maps = {c[len(map_rel) + 1:] for c in changed if c.startswith(map_rel + "/")}
        for feat in features + journeys:
            key = str(feat.path.resolve().relative_to(map_dir.resolve()))
            hits = [c for c in changed if matches_any(c, feat.patterns)]
            if hits and key not in changed_maps:
                acknowledged = feat.id in allow_unchanged
                touched.append({"feature": key, "changed_sources": hits[:10], "acknowledged": acknowledged})
                if not acknowledged:
                    errors.append(
                        f"{key}: {len(hits)} source file(s) changed on this branch but the map "
                        f"file did not (e.g. {hits[0]}). Update it, or, if a user reaches, sees and does "
                        f"everything exactly as before, acknowledge with --allow-unchanged {feat.id} "
                        f"(CI: a line 'map unchanged: {feat.id} — <reason>' in the PR description)"
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
            "version": VERSION,
            "features": len(features),
            "journeys": len(journeys),
            "routes": len(routes),
            "covered_routes": len(routes) - len(uncovered) - len(new_uncovered),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("map_dir", type=Path)
    parser.add_argument("--base", help="git ref to diff against (merge base with HEAD), e.g. origin/develop")
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors (use at handover: every route mapped)")
    parser.add_argument("--allow-unchanged", action="append", default=[], metavar="ID",
                        help="feature id whose sources changed but whose user path did not (repeatable)")
    parser.add_argument("--allow-unchanged-from", type=Path, metavar="FILE",
                        help="read 'map unchanged: <id>' lines from FILE, e.g. the PR description")
    parser.add_argument("--version", action="version", version=f"feature_map_check {VERSION}")
    args = parser.parse_args(argv)
    if not args.map_dir.is_dir():
        print(f"feature_map_check: {args.map_dir} is not a directory", file=sys.stderr)
        return 2
    try:
        allow = set(args.allow_unchanged) | read_allowances(args.allow_unchanged_from)
        result = check(args.map_dir, args.base, allow)
    except subprocess.CalledProcessError as exc:
        print(f"feature_map_check: git failed: {exc.stderr.strip()}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        s = result["summary"]
        if s:
            print(f"feature_map_check {s['version']}  features {s['features']}  journeys {s.get('journeys', 0)}  "
                  f"routes {s['routes']}  covered {s['covered_routes']}")
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
