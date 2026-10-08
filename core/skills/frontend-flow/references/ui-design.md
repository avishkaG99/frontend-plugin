---
title: Designing UI inside an existing product
tags: ui, design, layout, copy, motion, states, screenshots, design-system
---

## Designing UI inside an existing product

The goal is a screen that looks like it was always part of the app. In a product with a
design system, consistency is what makes it look designed. Distinctiveness is a property
of the brand, decided once, in the tokens, not reinvented per feature.

So the design system the profile names is the brief. Its tokens, primitives, patterns and
recipes are the vocabulary; this file is only the method for using them well. When this
file and the project's design documents disagree, the project wins.

Generic "make it distinctive" design advice (new typefaces, bold palettes, avoiding
"SaaS card" looks) is for greenfield work: a marketing page, a new document design, a
standalone prototype. It does not apply to screens in this app, even where the app's own
choices match a pattern such advice calls generic.

### 1. Plan the UI before the code

Write a short UI plan into the spec's UI/UX section before `fe-plan` runs, so the person
approves the look with the behaviour:

- **Shell**: which page layout or admin layout the screen sits in.
- **Building blocks**: the primitives and patterns it is made of, by name, from the
  design system. A block that does not exist yet is a decision, not a detail — say so.
- **Layout**: one sentence and a small ASCII wireframe of the main state.
- **States**: loading, empty (no data yet vs. no results for a filter), error with retry,
  permission-denied, success feedback. Each one named, each one designed.
- **Emphasis**: the one primary action per block, and the one thing on the screen that
  should draw the eye. Everything else stays quiet.

Then review it once against the design system: anything not built from an existing token,
primitive or pattern is either justified in the Decisions section or replaced.

### 2. Build from the system, not around it

- Tokens only. No new hex values, radii, shadows or font sizes inside a feature. If the
  system lacks something, extending the token or primitive is its own plan step.
- Use the primitive's variants rather than restyling it with copied classes.
- Find the nearest existing screen of the same kind (list, detail, form, wizard,
  dashboard) and match its spacing, header and toolbar arrangement.
- Watch selector specificity: a feature class that fights a primitive's styles is a sign
  to use a variant instead.

### 3. Words are part of the design

Every string a person reads is designed content, and it goes through the i18n layer in
every locale at once.

- **Say what happens.** A button names its result: "Save changes", "Add room", not
  "Submit" or "OK".
- **Keep the name through the flow.** "Publish" on the button, "Published" in the toast,
  "Published" in the list. A renamed action reads as a different one.
- **Use the user's words**, not the system's: "notifications", not "webhook config";
  "project", not whatever the API calls it.
- **Errors say what went wrong and how to fix it.** No apology, no vague "Something went
  wrong" when the cause is known, never an internal code or stack trace.
- **Empty is an invitation.** Say why it is empty and offer the action that fills it.
  "No data yet" and "No results for this filter" are different states with different
  copy.
- **Plain and short.** Sentence case, active voice, no filler, one job per element. Avoid
  decorative labels above content and all-caps labels unless the design system uses them.

### 4. Motion only when it explains something

Motion is welcome when it answers an action — a panel opening, a row expanding, a save
confirming — because it shows what changed. Avoid decoration: entrance animations on every
section, hover effects on every card. Respect `prefers-reduced-motion` for anything larger
than a small transition.

### 5. The quality floor

Built in, not announced:

- Works at the narrowest supported width without horizontal scroll.
- Every interactive element reachable and operable by keyboard, with visible focus.
- Contrast meets the project's target; state is never carried by colour alone.
- Reduced motion respected.
- Loading, empty and error states real, not placeholders.

### 6. Look at it

A screen nobody has looked at is not finished. Where the change is visible, the test plan
carries a not-automated case for each main state, so `fe-e2e` captures a screenshot of
each. Critique against the UI plan and the design system: alignment with neighbouring
screens, one clear primary action, nothing decorative that serves no purpose. Before
calling it done, remove one thing.

### Who uses this

| Agent | Uses |
| --- | --- |
| `fe-spec` | §1 for the UI plan; §3 for the copy in acceptance criteria |
| `fe-plan` | §2: a missing token or primitive becomes its own step |
| `fe-test` | §1 states and §6 screenshots become cases |
| `fe-build` | §2–§5 while writing screens |
| `fe-audit` | §5 as part of the review, alongside security and performance |
| `fe-e2e` | §6: screenshots of each main state, checked against the UI plan |
