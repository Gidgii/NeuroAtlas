v1.1.0 next 5
## 2026-08-02 — Clinical Neuroscience integrated batch (v1.2.0)
- Replaced five detached one-line stubs with complete production curriculum.
- Added Personality Disorders, Sleep Disorders, Substance Use, Neurodegenerative Disorders and Epilepsy.
- Integrated all five into Level 14 navigation, search, quizzes, spaced repetition, visual scenes and offline caching.
- Added five distinct accessible SVG hero illustrations and detailed reference/retrieval metadata.
- Validation: JSON parse, JavaScript syntax, asset references, quiz answers, service-worker cache and ZIP integrity passed.

## 1.3.0 — 2026-08-02
### Added
- - Traumatic Brain Injury Neuroscience
- Migraine Neuroscience
- Eating Disorders Neuroscience
- Tic and Tourette Neuroscience
- Intellectual Developmental Disability Neuroscience
### Changed
- Added Level 15 and expanded app detail loading, visual scenes and offline cache.

## [1.4.0] — 2026-08-02
### Added
- Level 16: Clinical Assessment and Applied Neuroscience.
- Five complete concepts covering learning disorders, communication disorders, anxiety comparison, psychopharmacology and clinical neuroanatomy.
- Five accessible chalkboard-style hero illustrations and full offline caching.

## [1.5.0] — 2026-08-02
### Added
- Five integrated Neuropsychology Foundations concepts: Attention, Processing Speed, Working Memory, Episodic Memory Assessment and Visuospatial Processing.
- Five accessible chalkboard-style hero illustrations.
- Clinical mechanism maps, three-question quiz banks, review prompts and authoritative references for each concept.
### Changed
- Added Level 17 — Neuropsychology Foundations.
- Extended app detail loading and offline service-worker caching.

- Added: Social Cognition, Executive Assessment, Language Assessment, Neuropsychological Case Formulation, Clinical Test Interpretation.

## [1.1.2] — 2026-08-02
### Added
- Five fully integrated neuropsychology interpretation and formulation concepts.
- Accessible pathway illustrations, clinical quiz banks, references and review prompts.
### Fixed
- Replaced five draft-only JSON scaffolds and connected them to navigation, search, spaced review and offline caching.

## 1.2.0 — 2026-08-02
### Added
- Completed Applied Neuropsychology curriculum: semantic and procedural memory, praxis, agnosia, neglect, validity, premorbid estimation, ecological function, state effects, paediatric and older-adult practice, and report feedback.
- Added full Neuropsychology QA report and repaired loader/cache/asset coverage.


## [2.0.0] — 2026-08-02
### Added
- Complete 53-slice EEG & QEEG curriculum (Levels 19–23).
- EEG/QEEG interactive learning sequences, quizzes, review prompts, evidence-aware references and unique illustrations.
- `EEG_QEEG_QA_REPORT.json` documenting three successful QA passes.
### Changed
- Expanded app loader, curriculum navigation and service-worker cache for the new phase.

- Added initial Neurofeedback production batch.

## [2.1.0] — Neurofeedback Phase
### Added
- 42 fully registered Neurofeedback learning slices across foundations, protocols, advanced methods, clinical applications and safety.
- 42 accessible offline SVG illustrations and a three-pass QA report.
### Changed
- Replaced detached Neurofeedback draft stubs with production content.
- Rebuilt the service-worker precache and expanded the app data loader.
### Safety
- Added evidence-strength labels, diagnostic limits, adverse-effect guidance, medication cautions and explicit QEEG boundaries.

## 2.2.0 — 2026-08-02
### Added
- Complete 40-slice Trauma & EMDR Neuroscience module.
- TRAUMA_EMDR_QA_REPORT.json with three validation passes.

## 2.3.0 — Interactive Anatomy: Cerebral Lobes, Cerebellum and Brainstem
- Added three interactive anatomy production slices with clinical localisation, pathway relationships, quizzes and accessibility metadata.

## 2.4.0 — Interactive Anatomy: Meninges, Vasculature and Limbic System
### Added
- Three production anatomy explorers with labelled structures, pathway relationships, clinical localisation, quizzes and accessible illustrations.
### Changed
- Extended Level 29 navigation, detail loading and offline cache coverage.

- Added atlas batch: Insula, Thalamus, Hypothalamus

## 2.5.0 — 2026-08-02
### Added
- Ventricular System Atlas
- Cranial Nerves Atlas
- Deep Nuclei Atlas

## 2.6.0
### Added
- Production Thalamus Atlas and Hypothalamus Atlas structures.
### Fixed
- Replaced prior detached two-field draft stubs and connected Deep Nuclei → Thalamus → Hypothalamus navigation.

## 2.7.0
- Reconciled all Interactive Anatomy atlas files with curriculum and app registration.
- Added production content and assets for Insula, Insula & Operculum, Cingulate Cortex and Reticular Activating System atlases.
- Added INTERACTIVE_ANATOMY_QA_REPORT.json.

## 2.7.0
- Completed Interactive Anatomy registration reconciliation.
- Rebuilt Insula, Insula & Operculum, Cingulate Cortex, and Reticular Activating System atlas entries.
- Normalised all present atlas details and added a verified QA report.

## 2.8.0 — 2026-08-02
### Added
- Pituitary Gland & Sella Turcica Atlas with interactive compartment explorer, pathway sequence, clinical relationships and three-question quiz bank.
### Fixed
- Atlas detail quiz-bank compatibility and rationale rendering.
- Generic system explorer support for structured anatomy records.
- Reduced-motion handling for interactive sequence playback.

## 2.9.0 — 2026-08-02
### Added
- Basal Ganglia Circuit Explorer.
- Major White-Matter Pathways Atlas.
- Neurotransmitter Pathways Atlas.
- Functional Network Overlay Atlas.
- Arterial Territories & Stroke Comparison.

### Changed
- Advanced Interactive Anatomy navigation to Brain Lateralisation Comparison.
- Expanded offline cache and loader registration to 21 verified structures.

## 2.9.1 — 2026-08-03

### Changed
- Standardised all 21 registered Interactive Anatomy records on canonical explorer schema 1.0.0.
- Updated the generic explorer for selectable anatomy, pathway playback, available clinical overlays,
  overview reset, accessible live announcements and reduced-motion operation.
- Aligned Python package, application and offline-cache versions at 2.9.1.

### Fixed
- Prevented missing stages or selectable parts from causing generic-explorer exceptions.
- Repaired the Hypothalamus Atlas forward navigation link and contradictory project-state fields.
- Prevented legacy project-management automation from silently rewriting the current authoritative
  state schema.
- Reclassified five detached title-only records as drafts instead of production content.
- Normalised quiz scoring for records using either `answer` or `correctAnswer` indexes.

### Validation
- Added automated coverage for JSON, identifiers, file alignment, loader registration, illustrations,
  offline cache entries, quizzes, navigation and canonical Interactive Anatomy schema compliance.
- Historical duplicate 2.7.0 entries remain unchanged because they describe separate recorded QA passes.
- Manual browser QA was reported across all 21 explorers and representative application workflows.
  No reproducible browser harness or execution artifacts were committed with this release.

## 2.10.0 — 2026-08-03

### Added
- Brain Lateralisation Comparison as the 22nd canonical Interactive Anatomy structure.
- Accessible paired-hemisphere illustration, seven selectable systems, four clinical overlays,
  four-question quiz bank and spaced-review metadata.

### Changed
- Advanced the application, Python package and offline cache to version 2.10.0.
- Recorded Brain Lateralisation as the 22nd implemented structure while keeping Interactive Anatomy
  in progress with three roadmap structures remaining.

### Fixed
- Included detail `searchTerms` metadata in application search results.

## 2.11.0 — 2026-08-03

### Added
- Healthy Versus Pathology Comparison as the 23rd canonical Interactive Anatomy structure.
- Accessible whole-brain comparison illustration, six selectable domains, a healthy/pathology toggle,
  four clinical overlays, four-question quiz bank and spaced-review metadata.

### Changed
- Advanced the application, Python package and offline cache to version 2.11.0.
- Advanced Interactive Anatomy navigation to Lesion and Symptom Mapping while keeping the phase in progress.
- Added optional, data-driven comparison modes to the canonical explorer with native keyboard controls,
  accessible pressed state and safe handling when comparison data is absent.

### Safety
- Distinguished variation, dysfunction, injury and disorder; qualified structural, functional,
  developmental, vascular and degenerative interpretations; and stated that imaging alone does not establish diagnosis.

## 2.12.0 — 2026-08-03

### Added
- Lesion and Symptom Mapping as the 24th canonical Interactive Anatomy structure.
- Accessible lesion-network illustration, cortical through cerebellar examples, left-right comparison,
  vascular and symptom overlays, four-question quiz bank and spaced-review metadata.

### Changed
- Advanced the application, Python package and offline cache to version 2.12.0.
- Advanced Interactive Anatomy navigation to the Integrated Whole-Brain Explorer and Capstone while
  keeping the phase in progress.
- Allowed canonical explorer comparison controls to declare a context-appropriate accessible group label.

### Safety
- Distinguished focal lesions, disconnection syndromes and distributed network dysfunction; qualified
  laterality and vascular inference; and rejected deterministic one-lesion-one-symptom mapping.

## 2.13.0 — 2026-08-03

### Added
- Integrated Whole-Brain Explorer and Capstone as the 25th and final planned Interactive Anatomy structure.
- A dedicated accessible whole-brain illustration, fourteen integrated domains, four comparison modes,
  four clinical overlays, four-question quiz bank and spaced-review metadata.
- Data-driven destination controls covering every previously completed Interactive Anatomy structure.

### Changed
- Advanced the application, Python package, curriculum and offline cache to version 2.13.0.
- Marked the Interactive Anatomy roadmap complete after all 25 structures passed static validation.
- Extended the canonical explorer with optional structure destinations that reuse existing application navigation.

### Safety
- Preserved distributed-network, pathway, laterality, vascular, developmental and clinical-context qualifications;
  overlay convergence is explicitly framed as hypothesis support rather than diagnosis or causal proof.
