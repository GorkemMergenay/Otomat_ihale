# Scoring Rules (MVP)

## Objectives
- Keep scoring transparent and auditable.
- Make every score explainable via `match_explanation`.
- Support admin-tuned behavior through `keyword_rules`.

## Score Components
Each tender gets four scores:

1. `relevance_score` (0-100)
2. `commercial_score` (0-100)
3. `technical_score` (0-100)
4. `total_score` (0-100)

`total_score` formula:

```text
total_score = relevance_score * 0.50 + commercial_score * 0.30 + technical_score * 0.20
```

## Rule Matching
`keyword_rules` drive matching with fields:
- `keyword`
- `category` (`direct`, `related`, `commercial`, `institution_signal`, `technical`, `negative`)
- `weight`
- `matching_type` (`exact`, `contains`, `fuzzy`)
- `target_field` (`title`, `summary`, `raw_text`, `institution_name`, `city`, `any`)
- `is_negative`

Turkish-aware normalization is applied before matching (case + character normalization).

## Contribution Calculation
For each match:

```text
contribution = rule.weight * category_multiplier * field_multiplier * match_strength
```

Where:
- `match_strength = match_score / 100`
- `match_score` from exact/contains/fuzzy matching

Negative rules reduce relevance.

## Relevance Score
Inputs:
- Positive keyword contributions
- Negative keyword contributions
- Source trust bonus (`official` > `public_announcement` > `institution` > `news`)
- Official verification bonus

Output:
- Clamped to [0, 100]

## Commercial Score
Inputs:
- Commercially relevant category contributions
- High-traffic context signals (`havalimanı`, `metro`, `üniversite`, `hastane`, `terminal`, `istasyon`, `spor tesisi`)
- Modest source quality bonus

Output:
- Clamped to [0, 100]

## Technical Score
Inputs:
- Technical/direct/related category contributions
- Technical clue terms (`otomasyon`, `self servis`, `ödeme`, `pos`, `cihaz`, `kurulum`, `bakım`, `akıllı`, `kiosk`, `otomat`)

Output:
- Clamped to [0, 100]

## Classification Labels
Using `total_score`:
- `highly_relevant` >= `SCORING_HIGH_THRESHOLD` (default 75)
- `relevant` >= `SCORING_RELEVANT_THRESHOLD` (default 55)
- `maybe_relevant` >= `SCORING_MAYBE_THRESHOLD` (default 35)
- `irrelevant` otherwise

## Alert Threshold
- `%80+` skor e-posta/telegram bildirimi için `NOTIFICATION_SCORE_THRESHOLD` kullanılır (default `80`).
- Bildirim, skor eşik altından üstüne geçtiğinde bir kez tetiklenir (idempotency + cooldown uygulanır).

## Audit Trail
Each processed tender stores:
- `extracted_keywords`
- `match_explanation.positive_hits[]`
- `match_explanation.negative_hits[]`
- `match_explanation.components`
- final label and score values

This enables team review of why a tender was flagged and scored.
