# NeuroAtlas External Clinical Review Pack

## Purpose

This pack supports independent clinical review of high-risk NeuroAtlas content before any public v1.0 claim.

The internal P3.1 evidence-governance work has been completed, including P3.1-B1 and P3.1-B2. Internal review does **not** constitute independent external clinical peer review.

The current release manifest states:

- Clinical external review: **required before public v1.0 claim**
- Accessibility external review: **recommended before public v1.0 claim**
- Legal/licensing external review: **required before public v1.0 claim**

## Reviewer role

The reviewer should independently assess whether the selected clinical and neuroscience content is:

1. Factually accurate.
2. Appropriately evidence-weighted.
3. Clinically bounded and non-diagnostic where required.
4. Free of misleading neurobiological determinism.
5. Clear about contested theories and uncertain mechanisms.
6. Appropriate for a clinical neuroscience educational atlas.
7. Supported by references that genuinely match the claims made.

The reviewer is **not** being asked to verify software engineering, accessibility certification, copyright ownership or legal compliance.

## Required review method

For each sampled concept:

- Read the canonical concept file.
- Check the substantive claims against the cited evidence.
- Identify any factual error, overstatement, ambiguity or clinically unsafe implication.
- Confirm whether uncertainty and limitations are adequately stated.
- Mark the concept as:
  - APPROVE
  - APPROVE WITH MINOR CHANGES
  - REQUIRES SUBSTANTIVE REVISION
  - NOT APPROVED
- Record specific requested changes where applicable.

## Priority review sample

Total concepts: 25

Severity distribution:
- minor: 1
- none: 1
- substantive: 23

### 1. Polyvagal Theory

- ID: `polyvagal-theory`
- File: `app/data/polyvagal-theory.json`
- Internal review batch: `P3.1-B1`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: GROSSMAN-PVT-2023, GROSSMAN-ETAL-PVT-2026, PORGES-PVT-2025, PORGES-RESPONSE-2026
- Internal note: Reframed as an active scientific dispute and removed implication that clinical usefulness validates disputed anatomy.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 2. Current Evidence Base

- ID: `current-evidence-emdr`
- File: `app/data/current-evidence-emdr.json`
- Internal review batch: `P3.1-B1`
- Internal severity: `minor`
- Internal status: `corrected`
- Evidence IDs: NICE-PTSD-NG116, WHO-PTSD-FACT-2024, WRIGHT-EMDR-IPDMA-2024, CAMBRIDGE-NEUROPSYCH-2024
- Internal note: Updated efficacy framing and separated treatment evidence from mechanism claims.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 3. Autism Applications

- ID: `autism-neurofeedback`
- File: `app/data/autism-neurofeedback.json`
- Internal review batch: `P3.1-B1`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: CRED-NF-2020, REZAEE-NF-ASD-2025, AUTISM-NEUROBIOLOGY-2023
- Internal note: Removed an ADHD-specific efficacy source and replaced it with ASD-specific evidence; retained neurodiversity-safe framing.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 4. Qeeg Adhd Evidence

- ID: `qeeg-adhd-evidence`
- File: `app/data/qeeg-adhd-evidence.json`
- Internal review batch: `P3.1-B1`
- Internal severity: `substantive`
- Internal status: `reference-corrected`
- Evidence IDs: AAN-QEEG-ADHD-2016-2025
- Internal note: Added the disorder-specific AAN practice advisory, reaffirmed in 2025; qEEG theta/beta ratio should not confirm or replace standard ADHD diagnosis.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 5. Qeeg Tbi Evidence

- ID: `qeeg-tbi-evidence`
- File: `app/data/qeeg-tbi-evidence.json`
- Internal review batch: `P3.1-B1`
- Internal severity: `substantive`
- Internal status: `reference-corrected`
- Evidence IDs: ACNS-QEEG-MTBI-2021
- Internal note: Replaced generic standards with the ACNS guideline specific to qEEG diagnosis of mild TBI.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 6. Memory Reconsolidation

- ID: `memory-reconsolidation-trauma`
- File: `app/data/memory-reconsolidation-trauma.json`
- Internal review batch: `P3.1-B1`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: WRIGHT-RECONSOLIDATION-2021, CAMBRIDGE-NEUROPSYCH-2024
- Internal note: Replaced generic PTSD guideline citations with reconsolidation-specific evidence and strengthened mechanism uncertainty.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 7. Working Memory Theory

- ID: `working-memory-theory-emdr`
- File: `app/data/working-memory-theory-emdr.json`
- Internal review batch: `P3.1-B1`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: WADJI-WM-EMDR-2022, WRIGHT-EMDR-IPDMA-2024
- Internal note: Replaced generic treatment guidelines with mechanism-specific systematic review plus comparative clinical evidence.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 8. Intergenerational Trauma

- ID: `intergenerational-trauma`
- File: `app/data/intergenerational-trauma.json`
- Internal review batch: `P3.1-B1`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: ELKHALIL-INTERGEN-2025, YOUSEF-INTERGEN-EPIGEN-2023, OXFORD-EMOTION-DYSREG-2020
- Internal note: Separated supported intergenerational associations from stronger and less secure claims of biological/epigenetic transmission.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 9. Attachment Neuroscience

- ID: `attachment-neuroscience-trauma`
- File: `app/data/attachment-neuroscience-trauma.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: ATTACH-ER-SR-2023
- Internal note: Added attachment-specific systematic review. Existing non-deterministic language retained; attachment representations are not treated as fixed neural types.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 10. Complex PTSD

- ID: `complex-ptsd-neuroscience`
- File: `app/data/complex-ptsd-neuroscience.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: CPTSD-NEUROBIOLOGY-2022
- Internal note: Added CPTSD-specific neurobiological review. Existing statement that no validated biomarker distinguishes CPTSD clinically was retained.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 11. Default Mode Network Changes

- ID: `default-mode-network-trauma`
- File: `app/data/default-mode-network-trauma.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: PTSD-RESTING-META-2016
- Internal note: Added PTSD resting-state systematic review/meta-analysis. Existing group-level, non-diagnostic network language retained.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 12. Developmental Trauma

- ID: `developmental-trauma`
- File: `app/data/developmental-trauma.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: CHILD-ADVERSITY-NEURAL-SR-2019
- Internal note: Added systematic review of childhood adversity and neural development. Existing non-deterministic developmental framing retained.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 13. Dissociation Mechanisms

- ID: `dissociation-mechanisms`
- File: `app/data/dissociation-mechanisms.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: DISSOC-AMNESIA-NEUROIMG-2023
- Internal note: Added dissociation-specific functional neuroimaging systematic review. Existing heterogeneous and non-diagnostic framing retained.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 14. The HPA Axis in Trauma

- ID: `hpa-axis-trauma`
- File: `app/data/hpa-axis-trauma.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: PTSD-HPA-META-2019
- Internal note: Added PTSD-specific HPA-axis meta-analysis. Existing cautious wording retained because direction and magnitude of endocrine findings vary across methods and samples.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 15. Qeeg Anxiety Depression Evidence

- ID: `qeeg-anxiety-depression-evidence`
- File: `app/data/qeeg-anxiety-depression-evidence.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: QEEG-DEP-FAA-META-2025
- Internal note: Added current depression-specific meta-analysis supporting cautious interpretation of frontal alpha asymmetry and non-diagnostic use.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 16. Qeeg Autism Evidence

- ID: `qeeg-autism-evidence`
- File: `app/data/qeeg-autism-evidence.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: QEEG-ASD-EEG-META-2023
- Internal note: Added autism-specific systematic review and meta-analysis supporting heterogeneous group-level EEG findings and non-diagnostic individual use.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 17. Structural Dissociation

- ID: `structural-dissociation`
- File: `app/data/structural-dissociation.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: STRUCT-DISSOC-STEELE-2005
- Internal note: Added theory-specific foundational source. Record continues to identify structural dissociation as a theoretical clinical model rather than an anatomical partition or established neural mechanism.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 18. Window of Tolerance

- ID: `window-of-tolerance`
- File: `app/data/window-of-tolerance.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: WINDOW-TOLERANCE-CORRIGAN-2011
- Internal note: Added theory-specific source and explicitly bounded the Window of Tolerance as a clinical heuristic/model rather than a validated measurable neurobiological threshold.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 19. Fear Extinction

- ID: `fear-extinction-trauma`
- File: `app/data/fear-extinction-trauma.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: PTSD-LEARNING-EXTINCTION-META-2023, PTSD-FEAR-MULTIVERSE-2023
- Internal note: Added current meta-analytic and multiverse evidence. Record should not imply that impaired extinction retention is universal in PTSD because findings vary by paradigm and analysis.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 20. Moral Injury

- ID: `moral-injury`
- File: `app/data/moral-injury.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: MORAL-INJURY-GRIFFIN-2019, MORAL-INJURY-MILITARY-2024
- Internal note: Added moral-injury-specific reviews. Moral injury is distinguished from PTSD and framed as a multidimensional psychological, social, ethical and potentially spiritual construct rather than a discrete neural disorder.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 21. Adaptive Information Processing Model

- ID: `adaptive-information-processing`
- File: `app/data/adaptive-information-processing.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: AIP-RYDBERG-2024, EMDR-STATE-SCIENCE-2024
- Internal note: Added current AIP-specific and state-of-science reviews. AIP is retained as an EMDR theoretical framework, not presented as a proven literal neural-storage mechanism.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 22. Mechanisms of Change

- ID: `mechanisms-change-emdr`
- File: `app/data/mechanisms-change-emdr.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: EMDR-STATE-SCIENCE-2024, AIP-RYDBERG-2024, WADJI-WM-EMDR-2022, WRIGHT-RECONSOLIDATION-2021
- Internal note: Reviewed competing EMDR mechanism accounts. Working-memory, memory-updating/reconsolidation and AIP explanations remain plausible or partially supported components rather than one established complete causal mechanism.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 23. Neurobiology of EMDR

- ID: `neurobiology-emdr`
- File: `app/data/neurobiology-emdr.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: EMDR-STATE-SCIENCE-2024, AIP-RYDBERG-2024, WADJI-WM-EMDR-2022
- Internal note: Reviewed neurobiological mechanism language. Clinical efficacy does not establish a unique neural mechanism, and neuroimaging findings remain group-level and mechanistically non-specific.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 24. Prediction Error

- ID: `prediction-error-trauma`
- File: `app/data/prediction-error-trauma.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `substantive`
- Internal status: `corrected`
- Evidence IDs: PTSD-LEARNING-EXTINCTION-META-2023, PTSD-FEAR-MULTIVERSE-2023
- Internal note: Reviewed prediction-error claims against current fear-learning evidence. Prediction error remains a useful learning construct, not a single established causal mechanism explaining PTSD or trauma recovery.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

### 25. Personality Disorders Neuroscience

- ID: `personality-disorders-neuroscience`
- File: `app/data/personality-disorders-neuroscience.json`
- Internal review batch: `P3.1-B2`
- Internal severity: `none`
- Internal status: `reviewed-no-change`
- Evidence IDs: ATLAS-3788F505B8, ATLAS-C1766D7F09, ATLAS-AFECB1D647
- Internal note: Reviewed against current personality-neuroscience literature. Dimensional, heterogeneous, non-localising and non-diagnostic framing remains appropriate. Disorder-specific BPD evidence was not generalised to personality disorders as a whole.

External reviewer decision:

- [ ] APPROVE
- [ ] APPROVE WITH MINOR CHANGES
- [ ] REQUIRES SUBSTANTIVE REVISION
- [ ] NOT APPROVED

Reviewer comments:

____________________________________________________________________

____________________________________________________________________

## Global review questions

Please answer after reviewing the sample.

1. Does the Atlas appropriately distinguish established findings from emerging, mixed or contested evidence?

2. Are neuroimaging, EEG, autonomic, endocrine and network findings appropriately presented as group-level evidence rather than individual diagnostic biomarkers?

3. Are trauma-related neural claims sufficiently non-deterministic?

4. Are EMDR efficacy claims appropriately separated from proposed mechanisms?

5. Are theoretical constructs such as structural dissociation, Window of Tolerance, Polyvagal Theory and AIP represented with appropriate epistemic caution?

6. Are ASD, ADHD, personality, trauma and psychiatric neuroscience claims sufficiently protected against diagnostic overreach?

7. Are there any claims that could reasonably mislead clinicians, students or members of the public?

8. Are there any missing limitations that materially affect clinical interpretation?

## Final recommendation

- [ ] APPROVE CLINICAL CONTENT FOR v1.0
- [ ] APPROVE SUBJECT TO MINOR CORRECTIONS
- [ ] REQUIRES SUBSTANTIVE RE-REVIEW BEFORE v1.0
- [ ] DO NOT APPROVE FOR v1.0

## Reviewer declaration

I confirm that I independently reviewed the material identified in this pack and that my recommendation reflects my professional judgement.

Reviewer name:

Professional qualification:

Registration / credential:

Relevant area(s) of expertise:

Organisation / affiliation, if applicable:

Date:

Signature or verifiable electronic acknowledgement:

## Governance boundary

Completion of this pack by an external reviewer can support the clinical review gate only. It does not satisfy accessibility certification, legal/licensing clearance, privacy/security review, or other release requirements.
