---
name: humanizer
description: >-
  Removes AI-generated writing tells (inflation, em-dash overuse, rigid formatting,
  repetitive cadence, and filler) using a Scan -> Rewrite -> Self-Audit workflow
  while strictly preserving original facts and numbers.
---

# Humanizer Skill

Use this skill as a final editorial pass on any user-facing report or summary before saving or presenting it. The goal is direct, natural, analyst-grade writing with zero fabricated details.

## 1. Patterns to Flag and Remove

1. **Inflation & Promotional Tone**:
   - Remove hype adjectives and adverbs (*seamless, rock-solid, huge, shines, crucial, pivotal, groundbreaking, zero risk*).
   - Remove exclamation marks (`!`) from analytical reports and tables.
   - Replace promotional claims with concrete facts (e.g., instead of *"Works seamlessly with Air France!"*, write *"Single-PNR connection on Air France + airBaltic with 5h 10m in CDG."*).
2. **Em-Dash Overuse (`—`)**:
   - Limit em-dashes to at most 1–2 per document (or zero). Prefer periods, commas, colons, or parentheses.
3. **Formatting by Rule**:
   - Avoid decorative emojis in section headings and table cells (`✈️`, `🧭`, `📅`, `⭐`). Plain text or minimal ASCII markers (`[OK]`, `[WARN]`) scan better.
   - Avoid repeating `- **Bold Label**: ...` on every bullet point.
   - Avoid `<br/>` walls of text inside Markdown table cells. Keep table cells short and move multi-line explanations to bullets below the table.
4. **Rhythm by Rule & Boilerplate**:
   - Vary sentence length and structure instead of repeating identical 3-part templates in every row.
   - Cut filler transitions (*"It is important to note that"*, *"In summary"*).
5. **Strict Fact Preservation**:
   - Never invent new flight numbers, prices, timestamps, or claims during rewriting.
   - Keep `[Verified Live]` vs. `[Indicative Estimate]` labels intact.
6. **Use of lenguaje**
  - Avoid reptition or overwritting, tell clearly, using common words, and be polite but directly, use passive or active voice if is nedded
  
## 2. Three-Step Editorial Workflow

1. **Scan**: Identify hype words, exclamation marks, em-dashes, decorative emojis, and bloated table cells.
2. **Rewrite**: Replace flagged phrasing with plain, specific language. Keep all numbers, URLs, and caveats exact.
3. **Self-Audit**: Re-read the final text to confirm no new facts were added and no AI tells remain.

## Reference
- Adapted from [OneAway Humanizer Skill](https://oneaway.io/skills/humanizer) and Wikipedia's *Signs of AI Writing* guidelines.

