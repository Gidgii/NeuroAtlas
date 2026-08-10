# P1.8 — Adaptive Mastery and Retrieval

Adds a local-first mastery layer on top of completion and spaced repetition.

## Behaviour
- Quiz accuracy and review effort are stored separately from simple completion.
- Due cards are prioritised by weakest mastery evidence rather than due timestamp alone.
- Existing concept `reviewPrompts` are used when available, rotating retrieval style across reviews.
- Progress now shows targeted retrieval priorities with one-click practice.
- Unseen concepts are not mislabeled as weak; the priority list uses concepts with learning evidence.
- All mastery data remains in browser localStorage (`cna-mastery-v1`).
