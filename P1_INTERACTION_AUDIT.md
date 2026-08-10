# P1 Interaction & UX Audit — First Pass

## Scope

This pass targets interaction discoverability and active learning. It deliberately does not redesign the locked front entrance or begin the final artwork overhaul.

## Current interaction inventory

- 249 curriculum concepts
- 69 concepts currently expose a usable explorer model
- 38 concepts expose a live animated concept scene
- 25 explorer models include a pathway/stage sequence
- 25 explorer models include overlays
- 3 explorer models include explicit comparison modes
- 16 explorer models contain 7 or more selectable components; the remaining explorer-capable models contain 4–6 components

## P1 changes implemented in this pass

### 1. Interaction discoverability

Explorer-capable concept cards now carry an **Interactive** marker so learners can see where active models exist before opening a concept.

### 2. Direct model entry point

Explorer-capable concept pages now provide an **Explore interactive model** control near the concept heading. It jumps directly to the model rather than requiring the learner to discover it below the seven explanation-depth tabs.

### 3. Active-recall clinical prediction

The generic system explorer no longer immediately gives away clinical relevance. When a selected component has clinical content, the learner is prompted to predict the consequence of disruption and then deliberately reveal the clinical relevance. This converts passive inspection into retrieval/prediction practice while preserving the existing clinical content.

### 4. Accessibility and mobile behaviour

The new controls use normal buttons, 44px minimum interaction targets, explicit state/labels, and responsive stacking on narrow viewports. Existing reduced-motion behaviour remains intact.

## Validation

- Repository validation: PASS
- pytest: 16/16 PASS
- Injected browser runtime QA: 23/23 PASS
- All 249 concepts render
- All 38 live scenes still open/close
- No uncaught JavaScript exceptions
- No console errors
- Mobile horizontal overflow remains 0 px in the runtime smoke tests

The local sandbox cannot execute the real HTTP/service-worker route because localhost navigation is administratively blocked. The existing GitHub Actions HTTP runtime job remains the authoritative final gate after this patch is pushed.

## Main remaining P1 gap

The 69 explorer-capable concepts are structurally interactive, but most generic system explorers still operate as selectable text/component cards rather than spatially interactive neuroanatomy. The next high-value build should add **diagram-linked hit targets, overlays and pathway highlighting** to the highest-yield atlas concepts, starting with the integrated whole-brain capstone and core neuroanatomy maps. This can use the existing artwork as the substrate; the final visual-art overhaul should remain later.


## P1.2 spatial atlas engine

A reusable spatial-map layer now links anatomical locations on the existing illustrations to the explorer detail model. The first production maps are:

- Integrated Whole-Brain Explorer and Capstone
- Cerebral Lobes Atlas
- Basal Ganglia Circuit Explorer

Selecting a map hotspot synchronises the corresponding component card and clinical detail panel. Labels can be hidden to support self-testing, and the ordinary component list remains available as an accessible keyboard/touch fallback. This establishes the interaction architecture without replacing the existing artwork.
