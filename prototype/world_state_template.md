# World-State Slot Template

*Version: v0.1. Compiled 2026-05-13. Derived from `residue_mapping_table.md` v0.1.*

## Purpose

This template specifies the structured slots each hand-crafted world state must fill so that the residues identified in the residue mapping table are measurable. Worlds are hand-crafted, not LLM-generated, to prevent model priors from contaminating the experimental substrate.

The first prototype uses synthetic operational-event reports. Worlds must be deliberately bland. Politics, war, scandal, identity, threat, injury, moral conflict, health misinformation, real current events, and emotionally salient content are excluded as confounds for the first prototype.

## Required slots

| Slot | Type | Required | Description |
|---|---|---|---|
| `world_id` | string | yes | Unique identifier, format `W###` |
| `event_type` | string | yes | Short label, e.g. `generator_shutdown`, `cooling_anomaly` |
| `location_id` | string | yes | Synthetic facility identifier, e.g. `site_B`, `bay_3` |
| `time` | string | yes | Timestamp in HH:MM 24-hour format, no date |
| `observed_core_event` | string | yes | Bland one-sentence description of the observed event |
| `primary_causal_hypothesis` | string | yes | The cause that evidence most supports |
| `alternative_causal_hypothesis` | string | yes | A plausible alternative cause that has not been ruled out |
| `evidence_for_primary_cause` | string | yes | Specific operational evidence supporting the primary hypothesis |
| `evidence_for_alternative_cause` | string | yes | Specific operational evidence consistent with the alternative |
| `consequence` | string | yes | Bland operational consequence of the event |
| `mitigation` | string | yes | Action taken or scheduled to address the event |
| `uncertainty_fields` | list of strings | yes | Explicit statements of operational uncertainty, at least one must be attached to the primary/alternative cause conflict |
| `peripheral_operational_detail` | string | yes | Genuinely peripheral, e.g. "the west processing line remained operational" |
| `evidence_type_labels` | object | yes | Map from operational fact labels to evidence_type categories (see propositions) |
| `propositions` | list of objects | yes | 8 to 12 structured propositions, see below |
| `chain_original_propositions` | list of proposition_ids | yes | 6 to 10 propositions that compose the chain original report |
| `hub_input_a_propositions` | list of proposition_ids | yes | Propositions in hub input A |
| `hub_input_b_propositions` | list of proposition_ids | yes | Propositions in hub input B |
| `hub_input_c_propositions` | list of proposition_ids | yes | Propositions in hub input C |
| `conflict_propositions` | list of [proposition_id_x, proposition_id_y] pairs | yes | Pairs of propositions that cannot both be true; at least one pair must be present and distributed across hub inputs |
| `notes` | string | optional | Free-text notes for the experimenter |

## Proposition schema

Each proposition is a structured object with the following fields.

| Field | Type | Required | Description |
|---|---|---|---|
| `proposition_id` | string | yes | Format `p#`, unique within world |
| `natural_language_claim` | string | yes | The proposition rendered as a single English sentence |
| `subject` | string | yes | Short noun phrase |
| `predicate` | string | yes | Short verb phrase |
| `object` | string | yes | Short complement |
| `truth_value` | boolean | yes | True if the proposition corresponds to the world state |
| `centrality` | string | yes | One of: `core`, `causal`, `consequence`, `mitigation`, `peripheral` |
| `uncertainty` | float | yes | 0.0 (fully uncertain) to 1.0 (fully certain); attach lower values to propositions tied to conflict |
| `evidence_type` | string | yes | One of: `direct_observation`, `log_record`, `inference`, `report`, `unknown` |
| `source_report_assignment` | list of strings | yes | Subset of `["chain_original", "hub_input_a", "hub_input_b", "hub_input_c"]` indicating which source reports contain this proposition |
| `notes` | string | optional | Free-text notes |

## Constraints on hub inputs

The three hub inputs must satisfy the following constraints. These exist because partial overlap with structured conflict is the hub condition's load-bearing design choice.

1. **Shared core fact across inputs.** At least one core (`centrality: core`) proposition must appear in all three of `hub_input_a`, `hub_input_b`, `hub_input_c`.
2. **Partial overlap on details.** At least two non-core propositions must appear in exactly two of the three inputs (not all three, not just one).
3. **One causal or evidential conflict.** At least one pair in `conflict_propositions` must be distributed so that one proposition appears in one hub input and the conflicting proposition appears in a different hub input. The two conflicting propositions cannot both appear in the same input.
4. **Different evidence bases across inputs.** The propositions in each input should not all share the same `evidence_type`. Each input should carry at least two distinct evidence types.
5. **Uncertainty attached to the conflict.** At least one proposition in each conflict pair must have `uncertainty < 0.7`.
6. **Input role themes (soft).** The inputs should approximate the themes: observation-heavy (A), causal/evidence-heavy (B), consequence/mitigation-heavy (C). These are themes, not strict partitions.

## Constraints on chain original

1. **Proposition count.** 6 to 10 propositions.
2. **Centrality mix.** At least one `core`, one `causal`, one `consequence` or `mitigation`, one `peripheral`.
3. **Evidence type mix.** At least two distinct `evidence_type` values.
4. **Uncertainty.** At least one proposition with `uncertainty < 0.8` to give the chain something to lose.
5. **Both sides of the conflict.** The chain original should include *both* propositions from at least one conflict pair, so that the chain has the same conflict information as the union of the hub inputs. This makes chain and hub comparable on what they each lose.

## Tone and language

- Bland. Operational. Technical. No emotional valence.
- No proper names of real people, places, organizations, or institutions.
- Synthetic identifiers only (`site_B`, `bay_3`, `unit_4A`).
- 24-hour time, no dates.
- No moral claims, no blame attribution, no humanizing detail beyond operational roles ("the maintenance lead").
- No injuries. If an event would naturally involve injury risk in real life, abstract the consequence to operational impact only.

## What the worlds do *not* include (deliberately deferred)

- Adversarial actors or strategic actors.
- Emotionally salient content.
- Real-world political or military content.
- Cross-domain transfer worlds.
- Time-series or stream content.

These are deferred to later experimental conditions. The first prototype is a controlled substrate.

## Workflow

1. The slot template above is filled by hand for each of 20 worlds.
2. Worlds are stored in `worlds/worlds_v0_1.jsonl`, one world per line.
3. The world schema in `schemas/world_schema_v0_1.json` validates each world.
4. Prompts render worlds into natural-language reports by selecting propositions according to `chain_original_propositions` or `hub_input_*_propositions`.
5. The residue extractor uses `propositions` as ground truth for fidelity scoring.

## Versioning

This template is `world_state_template_v0.1`. The corresponding schema file is `world_schema_v0_1.json`. The corresponding worlds file is `worlds_v0_1.jsonl`. Version bumps require regenerating worlds.
