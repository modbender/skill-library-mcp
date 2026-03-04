# ark_compliance_badge.md

## 1. Purpose

This document defines a lightweight, standardized **ARK Compliance Declaration** and an optional **badge label** for repositories, skills, and agents that claim alignment with ARK.

It is designed to:

* Enable transparent adoption claims.
* Prevent ambiguous “ARK-compliant” marketing.
* Make deviations explicit.

ARK V1 is declarative. This compliance mechanism reports *intent and configuration*, not guaranteed enforcement.

---

## 2. Badge Labels (Text-Only)

Use one label that matches your implementation:

* **ARK V1 — Declarative**
* **ARK V1 — Enforced**

If you claim “Enforced,” you must provide the enforcement mechanism reference.

---

## 3. Required Declaration Block

Any project claiming ARK compliance must include the following block (verbatim), completed with its values:

```
ARK_COMPLIANCE_DECLARATION
- ark_version: 1.0
- implementation_type: declarative | enforced
- operational_axis: enabled
- exploratory_axis: enabled
- confidence_for_important_answers: required
- refusal_on_validation_failure: yes
- ban_unrequested_suggestions: yes
- epistemic_tagging_module: inactive | active
- known_deviations: none | <list>
- enforcement_reference: none | <link or file>
END_DECLARATION
```

---

## 4. Minimal Compliance Criteria (V1)

A claim of **ARK V1 — Declarative** requires:

* operational_axis: enabled
* exploratory_axis: enabled
* confidence_for_important_answers: required
* refusal_on_validation_failure: yes
* ban_unrequested_suggestions: yes

If any of these are not satisfied, the project must not claim ARK compliance.

---

## 5. Optional Notes

Projects may add an optional explanatory note below the declaration:

* why deviations exist
* what domains are covered
* what is treated as an “important answer” in that runtime

Optional notes must not modify the required declaration block.

---

## 6. Example (Declarative)

```
ARK_COMPLIANCE_DECLARATION
- ark_version: 1.0
- implementation_type: declarative
- operational_axis: enabled
- exploratory_axis: enabled
- confidence_for_important_answers: required
- refusal_on_validation_failure: yes
- ban_unrequested_suggestions: yes
- epistemic_tagging_module: inactive
- known_deviations: none
- enforcement_reference: none
END_DECLARATION
```

---

## 7. Example (Enforced)

```
ARK_COMPLIANCE_DECLARATION
- ark_version: 1.0
- implementation_type: enforced
- operational_axis: enabled
- exploratory_axis: enabled
- confidence_for_important_answers: required
- refusal_on_validation_failure: yes
- ban_unrequested_suggestions: yes
- epistemic_tagging_module: active
- known_deviations: none
- enforcement_reference: ./ARK_ENFORCEMENT_SPEC.md
END_DECLARATION
```

---

## 8. QC_REPORT

* Declaration block present and bounded: 100%
* Minimal compliance criteria explicit: 100%
* Declarative vs enforced labels separated: 100%
* Single language integrity: 100%
* Numbering integrity verified: 100%
