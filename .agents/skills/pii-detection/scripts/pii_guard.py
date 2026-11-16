#!/usr/bin/env python3
"""Local PII detection, obfuscation, and deletion tool (zero external dependencies)."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable

DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
    "graphify-out",
    ".grafeando",
}

DEFAULT_EXCLUDED_PREFIXES = (
    ".agents/skills/pii-detection/",
)

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg",
    ".pdf", ".zip", ".tar", ".gz", ".whl", ".pyc", ".so",
    ".dylib", ".dll", ".exe", ".db", ".sqlite", ".sqlite3",
    ".mp3", ".mp4", ".mov", ".woff", ".woff2", ".ttf",
}

SAFE_EMAIL_DOMAINS = {
    "example.com",
    "example.org",
    "example.net",
    "users.noreply.github.com",
}

SAFE_IPS = {
    "0.0.0.0",
    "127.0.0.1",
    "255.255.255.0",
    "255.255.255.255",
}


@dataclass(frozen=True)
class Finding:
    file: str
    line: int
    category: str
    masked_value: str


@dataclass(frozen=True)
class Rule:
    category: str
    pattern: re.Pattern[str]
    replacement: str
    validator: Callable[[str], bool] | None = None


def _luhn_valid(digits_only: str) -> bool:
    if not (13 <= len(digits_only) <= 19) or not digits_only.isdigit():
        return False
    total = 0
    reverse_digits = digits_only[::-1]
    for idx, ch in enumerate(reverse_digits):
        n = int(ch)
        if idx % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def _validate_email(value: str) -> bool:
    domain = value.rsplit("@", 1)[-1].lower()
    return domain not in SAFE_EMAIL_DOMAINS


def _validate_ip(value: str) -> bool:
    if value in SAFE_IPS or value.endswith(".0.0.0"):
        return False
    octets = value.split(".")
    if len(octets) != 4:
        return False
    return all(0 <= int(o) <= 255 for o in octets)


def _validate_phone(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    # Require 10-15 digits to avoid matching dates, years, or short IDs.
    return 10 <= len(digits) <= 15


def _validate_card(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    return _luhn_valid(digits)


PII_RULES: tuple[Rule, ...] = (
    Rule(
        category="email",
        pattern=re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        replacement="[REDACTED_EMAIL]",
        validator=_validate_email,
    ),
    Rule(
        category="ip",
        pattern=re.compile(r"(?<![\d./])\b(?:\d{1,3}\.){3}\d{1,3}\b(?![\d.])"),
        replacement="[REDACTED_IP]",
        validator=_validate_ip,
    ),
    Rule(
        category="phone",
        pattern=re.compile(
            r"(?<!\w)(?:\+\d{1,3}[\s.-]?)?(?:\(\d{2,4}\)[\s.-]?|\d{3}[\s.-])\d{3,4}[\s.-]?\d{4}(?!\w)"
        ),
        replacement="[REDACTED_PHONE]",
        validator=_validate_phone,
    ),
    Rule(
        category="credit_card",
        pattern=re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
        replacement="[REDACTED_CARD]",
        validator=_validate_card,
    ),
    Rule(
        category="passport_id",
        pattern=re.compile(
            r"(?i)\b(?:passport|pasaporte|c[eé]dula|dni|ssn)\s*(?:no\.?|num\.?|number|#|:)?\s*(?=[A-Z0-9-]*\d)[A-Z0-9-]{6,15}\b"
        ),
        replacement="[REDACTED_ID]",
    ),
    Rule(
        category="secret",
        pattern=re.compile(
            r"\b(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AIza[0-9A-Za-z\-_]{35}|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,})\b"
        ),
        replacement="[REDACTED_SECRET]",
    ),
)


def mask_preview(value: str) -> str:
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:2]}{'*' * min(8, len(value) - 4)}{value[-2:]}"


def is_text_file(path: Path) -> bool:
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return False
    try:
        with path.open("rb") as fh:
            chunk = fh.read(2048)
        return b"\x00" not in chunk
    except OSError:
        return False


def iter_target_files(root: Path, paths: list[str]) -> Iterable[Path]:
    if paths:
        candidates = [root / p if not Path(p).is_absolute() else Path(p) for p in paths]
    else:
        candidates = [root]

    for target in candidates:
        if target.is_file():
            rel = target.relative_to(root).as_posix() if target.is_relative_to(root) else target.as_posix()
            if not rel.startswith(DEFAULT_EXCLUDED_PREFIXES) and is_text_file(target):
                yield target
            continue

        if not target.is_dir():
            continue

        for dirpath, dirnames, filenames in os.walk(target):
            dirnames[:] = sorted(d for d in dirnames if d not in DEFAULT_EXCLUDED_DIRS)
            for name in sorted(filenames):
                file_path = Path(dirpath) / name
                rel = file_path.relative_to(root).as_posix()
                if rel.startswith(DEFAULT_EXCLUDED_PREFIXES):
                    continue
                if is_text_file(file_path):
                    yield file_path


def process_file(
    file_path: Path,
    root: Path,
    rules: tuple[Rule, ...],
    mode: str,
    delete_lines: bool,
) -> list[Finding]:
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    rel_path = file_path.relative_to(root).as_posix() if file_path.is_relative_to(root) else str(file_path)
    lines = content.splitlines(keepends=True)
    findings: list[Finding] = []
    updated_lines: list[str] = []
    modified = False

    for line_no, line in enumerate(lines, start=1):
        new_line = line
        line_matched = False

        for rule in rules:
            def _replace(match: re.Match[str]) -> str:
                nonlocal line_matched
                matched_text = match.group(0)
                if rule.validator and not rule.validator(matched_text):
                    return matched_text
                line_matched = True
                findings.append(
                    Finding(
                        file=rel_path,
                        line=line_no,
                        category=rule.category,
                        masked_value=mask_preview(matched_text),
                    )
                )
                if mode == "obfuscate":
                    return rule.replacement
                if mode == "delete":
                    return ""
                return matched_text

            new_line = rule.pattern.sub(_replace, new_line)

        if line_matched and mode != "check":
            modified = True
            if mode == "delete" and delete_lines:
                continue

        updated_lines.append(new_line)

    if modified and mode in {"obfuscate", "delete"}:
        file_path.write_text("".join(updated_lines), encoding="utf-8")

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Local PII detector and sanitizer.")
    parser.add_argument("paths", nargs="*", help="Optional files or directories to scan.")
    parser.add_argument(
        "--mode",
        choices=("check", "obfuscate", "delete"),
        default="check",
        help="check: report only; obfuscate: replace with [REDACTED_*]; delete: remove PII.",
    )
    parser.add_argument(
        "--delete-lines",
        action="store_true",
        help="When --mode delete is used, remove entire lines containing PII.",
    )
    parser.add_argument(
        "--categories",
        default="",
        help="Pipe- or comma-separated categories to scan (default: all).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit findings as JSON.",
    )
    args = parser.parse_args()

    root = Path.cwd()
    selected_categories = {
        c.strip().lower()
        for c in re.split(r"[|,]", args.categories)
        if c.strip()
    }
    active_rules = tuple(
        r for r in PII_RULES if not selected_categories or r.category in selected_categories
    )

    all_findings: list[Finding] = []
    for file_path in iter_target_files(root, args.paths):
        all_findings.extend(
            process_file(file_path, root, active_rules, args.mode, args.delete_lines)
        )

    if args.json:
        print(json.dumps([asdict(f) for f in all_findings], indent=2))
    else:
        for f in all_findings:
            print(f"{f.file}:{f.line}: [{f.category}] {f.masked_value}")
        print(f"Total PII findings ({args.mode}): {len(all_findings)}")

    if args.mode == "check" and all_findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
