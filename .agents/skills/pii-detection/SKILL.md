---
name: pii-detection
description: >-
  Scans repository files locally for Personally Identifiable Information (emails,
  phone numbers, IP addresses, credit cards, passport/ID numbers, and API secrets)
  without requiring external cloud services or Azure credentials, and supports
  obfuscating or deleting detected PII before opening a pull request.
---

# Local PII Detection & Sanitization Skill

Use this skill to audit files for Personally Identifiable Information (PII) locally and sanitize findings via obfuscation (`[REDACTED_*]`) or deletion.

## Supported Categories

- `email`: Email addresses (ignores standard placeholder domains like `example.com` and `users.noreply.github.com`).
- `ip`: IPv4 addresses (ignores loopback/broadcast/netmask addresses).
- `phone`: International and local phone numbers (10–15 digits).
- `credit_card`: 13–19 digit sequences validated with the Luhn algorithm.
- `passport_id`: Labeled passport, cédula, DNI, or SSN numbers.
- `secret`: Common API keys and personal access tokens (`ghp_`, `github_pat_`, `AIza`, `AKIA`, `sk-`).

## Commands

Run from the repository root:

1. **Check / Audit (Read-Only, exits 1 if PII is found)**:
   ```bash
   python3 .agents/skills/pii-detection/scripts/pii_guard.py --mode check
   ```

2. **Obfuscate PII in-place (`[REDACTED_EMAIL]`, `[REDACTED_PHONE]`, etc.)**:
   ```bash
   python3 .agents/skills/pii-detection/scripts/pii_guard.py --mode obfuscate
   ```

3. **Delete matched PII values (or entire lines with `--delete-lines`)**:
   ```bash
   python3 .agents/skills/pii-detection/scripts/pii_guard.py --mode delete
   ```

4. **Filter specific categories or target paths**:
   ```bash
   python3 .agents/skills/pii-detection/scripts/pii_guard.py --categories "email|phone|ip" --mode check docs/
   ```

## Workflow Integration

1. Run `--mode check` to inspect all findings and verify there are no false positives.
2. Run `--mode obfuscate` (recommended) or `--mode delete` on confirmed findings.
3. Review `git diff` to ensure no valid URLs, docs, or configs were altered unintentionally.
4. Commit the sanitized changes on a feature branch and open a pull request for review.
