# P1.10 — Metacognitive Confidence Calibration

## Purpose

P1.10 adds a metacognitive layer to adaptive review. Learners must rate confidence before revealing an answer, allowing the Atlas to distinguish knowledge accuracy from confidence quality.

## Behaviour

- Four confidence levels: Guessing, Unsure, Fairly sure, Certain.
- The answer remains locked until confidence is selected.
- Review outcome and pre-reveal confidence are stored together in `cna-calibration-v1`.
- High-confidence errors and low-confidence successes are tracked explicitly.
- The Progress page displays a calibration score, label, and tailored guidance.
- Calibration is kept separate from mastery and competency so confidence never substitutes for knowledge evidence.

## Clinical learning rationale

Clinical reasoning requires both accuracy and appropriately bounded confidence. P1.10 rewards learners for matching certainty to the quality of available evidence and surfaces patterns of overconfidence or underconfidence without treating confidence itself as competence.
