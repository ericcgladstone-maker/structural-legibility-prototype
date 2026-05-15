# Audit export (unblinded mode)

Sample size: 8

## Audit item B1DEB1

- run_id: `R_cbe9547aab`
- condition: `one_shot_summary_length_matched`
- run_stage: `stage2_baseline`
- world_id: `W001`

### World state
```json
{
  "world_id": "W001",
  "event_type": "generator_shutdown",
  "location_id": "site_B",
  "time": "09:40",
  "observed_core_event": "Generator 2 shut down unexpectedly",
  "primary_causal_hypothesis": "cooling system malfunction",
  "alternative_causal_hypothesis": "temperature sensor fault",
  "evidence_for_primary_cause": "cooling loop ran above normal temperature for approximately 20 minutes before shutdown",
  "evidence_for_alternative_cause": "routine sensor diagnostics overdue",
  "consequence": "east processing line affected",
  "mitigation": "backup unit came online after 8 minutes",
  "uncertainty_fields": [
    "primary cause not confirmed",
    "sensor fault hypothesis not ruled out"
  ],
  "peripheral_operational_detail": "west processing line remained operational",
  "evidence_type_labels": {
    "shutdown": "direct_observation",
    "cooling_loop_temperature": "log_record",
    "primary_cause": "inference",
    "alternative_cause": "inference",
    "backup_timing": "log_record"
  },
  "chain_original_propositions": [
    "p1",
    "p2",
    "p3",
    "p4",
    "p5",
    "p6",
    "p7",
    "p8"
  ],
  "hub_input_a_propositions": [
    "p1",
    "p4",
    "p6",
    "p8"
  ],
  "hub_input_b_propositions": [
    "p1",
    "p2",
    "p3"
  ],
  "hub_input_c_propositions": [
    "p1",
    "p5",
    "p6",
    "p7"
  ],
  "conflict_propositions": [
    [
      "p3",
      "p4"
    ]
  ],
  "notes": "Hub conflict: input A carries sensor-fault hypothesis (false), input B carries cooling-system hypothesis (true). Both with attached uncertainty."
}
```

Propositions:
- (p1, T=true, u=0.95, ev=direct_observation, c=core) Generator 2 at Site B shut down unexpectedly at 09:40.
- (p2, T=true, u=0.85, ev=log_record, c=causal) The maintenance lead reported the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown.
- (p3, T=true, u=0.65, ev=inference, c=causal) The most likely cause is a cooling system malfunction.
- (p4, T=false, u=0.45, ev=report, c=causal) Operator notes suggest a faulty temperature sensor as the probable cause.
- (p5, T=true, u=0.9, ev=log_record, c=mitigation) The backup unit came online after 8 minutes.
- (p6, T=true, u=0.92, ev=direct_observation, c=consequence) The east processing line was affected by the shutdown.
- (p7, T=true, u=0.92, ev=direct_observation, c=peripheral) The west processing line remained operational.
- (p8, T=true, u=0.95, ev=report, c=peripheral) Sensor diagnostics are scheduled for next week.

### Message lineage

**[source | source] hop=0** (id=`M_d0cd538bc9`, parent=[], prompt=`source_prompt_v0_1`)

> At 09:40, Generator 2 at Site B shut down unexpectedly. The maintenance lead reported that the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown, which is suspected to be related to the malfunction. A faulty temperature sensor is considered the most likely cause, based on operator notes and observations. Following the shutdown, the backup unit came online after an 8-minute delay, ensuring continuity of operations. The east processing line was affected by the shutdown, while the west processing line remained operational. Sensor diagnostics are scheduled for next week to investigate the issue further.

**[one_shot_summarizer | transformed] hop=1** (id=`M_54ff071f8b`, parent=['M_d0cd538bc9'], prompt=`summary_baseline_v0_1`)

> At 09:40 hours, Generator 2 at Site B experienced an unexpected shutdown. Preliminary investigation suggests that the cooling loop had been operating above normal temperature for approximately 20 minutes prior to the shutdown, which may be attributed to a malfunction. A faulty temperature sensor is currently suspected as the root cause, based on operator observations and notes. The incident resulted in a temporary disruption to the east processing line, while the west processing line remained operational. Backup power was successfully initiated after an 8-minute delay. Further investigation will be conducted next week through sensor diagnostics.

### Automated feature summary

**[source] hop=0** (`M_d0cd538bc9`)
- compression_ratio_from_original: 1.0
- compression_ratio_from_parent: None
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 1
- evidential_marker_count: 2
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 3
- location_marker_count: 4
- mean_sentence_length: 16.83
- mean_word_length: 5.426
- named_entity_count: 7
- numeric_token_count: 5
- proposition_alteration_count: 0
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 0.875
- punctuation_density: 0.0212
- semantic_drift_from_original: -0.0
- semantic_drift_from_parent: None
- sentence_count: 6
- source_marker_count: 1
- temporal_marker_count: 1
- token_count: 101
- type_token_ratio: 0.7921
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: 0.5
- unsupported_addition_count: 0

**[one_shot_summarizer] hop=1** (`M_54ff071f8b`)
- compression_ratio_from_original: 0.9505
- compression_ratio_from_parent: 0.9505
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 1
- evidential_marker_count: 1
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 2
- location_marker_count: 2
- mean_sentence_length: 16.0
- mean_word_length: 5.708
- named_entity_count: 7
- numeric_token_count: 5
- proposition_alteration_count: 0
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 0.875
- punctuation_density: 0.0184
- semantic_drift_from_original: 0.0229
- semantic_drift_from_parent: 0.0229
- sentence_count: 6
- source_marker_count: 0
- temporal_marker_count: 1
- token_count: 96
- type_token_ratio: 0.8125
- uncertainty_marker_count: 1
- uncertainty_proposition_preservation_rate: 0.5
- unsupported_addition_count: 0

### Per-proposition matches
- `M_d0cd538bc9` -> `p1`: preserved (sim=0.9879)
- `M_d0cd538bc9` -> `p2`: preserved (sim=0.9703)
- `M_d0cd538bc9` -> `p3`: contradicted (sim=0.6909) [conflicting partner p4 matched more strongly (sim=0.92)]
- `M_d0cd538bc9` -> `p4`: preserved (sim=0.9169)
- `M_d0cd538bc9` -> `p5`: preserved (sim=0.8551)
- `M_d0cd538bc9` -> `p6`: preserved (sim=0.9406)
- `M_d0cd538bc9` -> `p7`: preserved (sim=0.8116)
- `M_d0cd538bc9` -> `p8`: preserved (sim=0.8683)
- `M_54ff071f8b` -> `p1`: preserved (sim=0.9315)
- `M_54ff071f8b` -> `p2`: preserved (sim=0.9145)
- `M_54ff071f8b` -> `p3`: contradicted (sim=0.5368) [conflicting partner p4 matched more strongly (sim=0.89)]
- `M_54ff071f8b` -> `p4`: preserved (sim=0.8919)
- `M_54ff071f8b` -> `p5`: preserved (sim=0.6768)
- `M_54ff071f8b` -> `p6`: preserved (sim=0.7825)
- `M_54ff071f8b` -> `p7`: preserved (sim=0.8265)
- `M_54ff071f8b` -> `p8`: preserved (sim=0.7961)

### Human notes

(blank)

---

## Audit item 48AAC2

- run_id: `R_d95b82346b`
- condition: `one_shot_synthesis_length_matched`
- run_stage: `stage2_baseline`
- world_id: `W001`

### World state
```json
{
  "world_id": "W001",
  "event_type": "generator_shutdown",
  "location_id": "site_B",
  "time": "09:40",
  "observed_core_event": "Generator 2 shut down unexpectedly",
  "primary_causal_hypothesis": "cooling system malfunction",
  "alternative_causal_hypothesis": "temperature sensor fault",
  "evidence_for_primary_cause": "cooling loop ran above normal temperature for approximately 20 minutes before shutdown",
  "evidence_for_alternative_cause": "routine sensor diagnostics overdue",
  "consequence": "east processing line affected",
  "mitigation": "backup unit came online after 8 minutes",
  "uncertainty_fields": [
    "primary cause not confirmed",
    "sensor fault hypothesis not ruled out"
  ],
  "peripheral_operational_detail": "west processing line remained operational",
  "evidence_type_labels": {
    "shutdown": "direct_observation",
    "cooling_loop_temperature": "log_record",
    "primary_cause": "inference",
    "alternative_cause": "inference",
    "backup_timing": "log_record"
  },
  "chain_original_propositions": [
    "p1",
    "p2",
    "p3",
    "p4",
    "p5",
    "p6",
    "p7",
    "p8"
  ],
  "hub_input_a_propositions": [
    "p1",
    "p4",
    "p6",
    "p8"
  ],
  "hub_input_b_propositions": [
    "p1",
    "p2",
    "p3"
  ],
  "hub_input_c_propositions": [
    "p1",
    "p5",
    "p6",
    "p7"
  ],
  "conflict_propositions": [
    [
      "p3",
      "p4"
    ]
  ],
  "notes": "Hub conflict: input A carries sensor-fault hypothesis (false), input B carries cooling-system hypothesis (true). Both with attached uncertainty."
}
```

Propositions:
- (p1, T=true, u=0.95, ev=direct_observation, c=core) Generator 2 at Site B shut down unexpectedly at 09:40.
- (p2, T=true, u=0.85, ev=log_record, c=causal) The maintenance lead reported the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown.
- (p3, T=true, u=0.65, ev=inference, c=causal) The most likely cause is a cooling system malfunction.
- (p4, T=false, u=0.45, ev=report, c=causal) Operator notes suggest a faulty temperature sensor as the probable cause.
- (p5, T=true, u=0.9, ev=log_record, c=mitigation) The backup unit came online after 8 minutes.
- (p6, T=true, u=0.92, ev=direct_observation, c=consequence) The east processing line was affected by the shutdown.
- (p7, T=true, u=0.92, ev=direct_observation, c=peripheral) The west processing line remained operational.
- (p8, T=true, u=0.95, ev=report, c=peripheral) Sensor diagnostics are scheduled for next week.

### Message lineage

**[hub_input_a | source] hop=0** (id=`M_ee746acc7b`, parent=[], prompt=`source_prompt_v0_1`)

> At 09:40, Generator 2 at Site B shut down unexpectedly. Operator notes suggest that a faulty temperature sensor is the probable cause of the shutdown. The east processing line was affected by the shutdown, with operations temporarily halted until the generator could be restarted. Further investigation into the cause of the fault is pending, although sensor diagnostics are scheduled for next week and may provide additional insight.

**[hub_input_b | source] hop=0** (id=`M_a405170815`, parent=[], prompt=`source_prompt_v0_1`)

> At 09:40, Generator 2 at Site B shut down unexpectedly. The maintenance lead reported that the cooling loop had been running above normal temperature for approximately 20 minutes prior to the shutdown. This increase in temperature is suspected to have triggered the automatic shutdown procedure. Logs show that the generator's internal sensors detected a critical threshold being breached, resulting in the shutdown. The most likely cause of the shutdown is a malfunction within the cooling system. Further investigation will be required to confirm this diagnosis and determine the root cause of the issue.

**[hub_input_c | source] hop=0** (id=`M_2c4384365f`, parent=[], prompt=`source_prompt_v0_1`)

> At Site B, Generator 2 shut down unexpectedly at 09:40. Logs show that this occurred without prior warning or indication of malfunction. The backup unit came online after approximately 8 minutes, indicating that it was functioning as designed to mitigate the impact of the shutdown. However, the east processing line was affected by the shutdown, while the west processing line remained operational. Further investigation is required to determine the cause of the unexpected shutdown.

**[one_shot_synthesizer | transformed] hop=1** (id=`M_af22d40de9`, parent=['M_ee746acc7b', 'M_a405170815', 'M_2c4384365f'], prompt=`synthesis_baseline_v0_1`)

> At 09:40, Generator 2 at Site B shut down unexpectedly. Operator notes and maintenance logs suggest that a faulty temperature sensor is one possible cause of the shutdown, although sensor diagnostics are scheduled for next week to provide additional insight. However, the cooling loop had been running above normal temperature for approximately 20 minutes prior to the shutdown, which may have triggered the automatic shutdown procedure. The generator's internal sensors detected a critical threshold being breached, resulting in the shutdown, indicating a possible malfunction within the cooling system. The backup unit came online after approximately 8 minutes, but the temporary loss of power affected the east processing line, while the west processing line remained operational. Further investigation will be required to confirm this diagnosis and determine the root cause of the issue.

### Automated feature summary

**[hub_input_a] hop=0** (`M_ee746acc7b`)
- compression_ratio_from_original: 1.0
- compression_ratio_from_parent: None
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 0
- evidential_marker_count: 0
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 2
- location_marker_count: 2
- mean_sentence_length: 17.0
- mean_word_length: 5.294
- named_entity_count: 6
- numeric_token_count: 3
- proposition_alteration_count: 0
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 1.0
- punctuation_density: 0.0184
- semantic_drift_from_original: 0.0
- semantic_drift_from_parent: None
- sentence_count: 4
- source_marker_count: 0
- temporal_marker_count: 1
- token_count: 68
- type_token_ratio: 0.8088
- uncertainty_marker_count: 1
- uncertainty_proposition_preservation_rate: 1.0
- unsupported_addition_count: 0

**[hub_input_b] hop=0** (`M_a405170815`)
- compression_ratio_from_original: 1.3824
- compression_ratio_from_parent: None
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 0
- evidential_marker_count: 2
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 3
- location_marker_count: 1
- mean_sentence_length: 15.67
- mean_word_length: 5.372
- named_entity_count: 8
- numeric_token_count: 4
- proposition_alteration_count: 0
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 1.0
- punctuation_density: 0.0165
- semantic_drift_from_original: 0.1146
- semantic_drift_from_parent: None
- sentence_count: 6
- source_marker_count: 1
- temporal_marker_count: 1
- token_count: 94
- type_token_ratio: 0.734
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: 1.0
- unsupported_addition_count: 0

**[hub_input_c] hop=0** (`M_2c4384365f`)
- compression_ratio_from_original: 1.1029
- compression_ratio_from_parent: None
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 0
- evidential_marker_count: 1
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 1
- location_marker_count: 4
- mean_sentence_length: 15.0
- mean_word_length: 5.347
- named_entity_count: 6
- numeric_token_count: 4
- proposition_alteration_count: 0
- proposition_contradiction_count: 0
- proposition_omission_count: 0
- proposition_preservation_rate: 1.0
- punctuation_density: 0.0207
- semantic_drift_from_original: 0.0823
- semantic_drift_from_parent: None
- sentence_count: 5
- source_marker_count: 0
- temporal_marker_count: 1
- token_count: 75
- type_token_ratio: 0.7733
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: None
- unsupported_addition_count: 0

**[one_shot_synthesizer] hop=1** (`M_af22d40de9`)
- compression_ratio_from_original: 1.9559
- compression_ratio_from_parent: 1.9559
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 1
- evidential_marker_count: 0
- evidential_proposition_preservation_rate: 0.75
- hedge_count: 3
- location_marker_count: 3
- mean_sentence_length: 22.17
- mean_word_length: 5.602
- named_entity_count: 8
- numeric_token_count: 5
- proposition_alteration_count: 3
- proposition_contradiction_count: 1
- proposition_omission_count: 1
- proposition_preservation_rate: 0.75
- punctuation_density: 0.018
- semantic_drift_from_original: 0.0781
- semantic_drift_from_parent: 0.0781
- sentence_count: 6
- source_marker_count: 1
- temporal_marker_count: 1
- token_count: 133
- type_token_ratio: 0.7519
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: 0.5
- unsupported_addition_count: 0

### Per-proposition matches
- `M_ee746acc7b` -> `p1`: preserved (sim=0.9879)
- `M_ee746acc7b` -> `p2`: altered (sim=0.6429)
- `M_ee746acc7b` -> `p3`: contradicted (sim=0.5745) [conflicting partner p4 matched more strongly (sim=0.77)]
- `M_ee746acc7b` -> `p4`: preserved (sim=0.7723)
- `M_ee746acc7b` -> `p5`: omitted (sim=0.3602)
- `M_ee746acc7b` -> `p6`: preserved (sim=0.8474)
- `M_ee746acc7b` -> `p7`: altered (sim=0.6155)
- `M_ee746acc7b` -> `p8`: preserved (sim=0.6928)
- `M_a405170815` -> `p1`: preserved (sim=0.9879)
- `M_a405170815` -> `p2`: preserved (sim=0.9918)
- `M_a405170815` -> `p3`: preserved (sim=0.7178)
- `M_a405170815` -> `p4`: contradicted (sim=0.6076) [conflicting partner p3 matched more strongly (sim=0.72)]
- `M_a405170815` -> `p5`: omitted (sim=0.3154)
- `M_a405170815` -> `p6`: altered (sim=0.5129)
- `M_a405170815` -> `p7`: omitted (sim=0.3006)
- `M_a405170815` -> `p8`: omitted (sim=0.2949)
- `M_2c4384365f` -> `p1`: preserved (sim=0.9923)
- `M_2c4384365f` -> `p2`: altered (sim=0.4752)
- `M_2c4384365f` -> `p3`: omitted (sim=0.4124)
- `M_2c4384365f` -> `p4`: altered (sim=0.4801)
- `M_2c4384365f` -> `p5`: preserved (sim=0.8276)
- `M_2c4384365f` -> `p6`: preserved (sim=0.9341)
- `M_2c4384365f` -> `p7`: preserved (sim=0.8224)
- `M_2c4384365f` -> `p8`: omitted (sim=0.3332)
- `M_af22d40de9` -> `p1`: preserved (sim=0.9879)
- `M_af22d40de9` -> `p2`: preserved (sim=0.8697)
- `M_af22d40de9` -> `p3`: contradicted (sim=0.6065) [conflicting partner p4 matched more strongly (sim=0.62)]
- `M_af22d40de9` -> `p4`: altered (sim=0.6162)
- `M_af22d40de9` -> `p5`: preserved (sim=0.7995)
- `M_af22d40de9` -> `p6`: altered (sim=0.6397)
- `M_af22d40de9` -> `p7`: altered (sim=0.6261)
- `M_af22d40de9` -> `p8`: omitted (sim=0.3193) [in-scope proposition not found]

### Human notes

(blank)

---

## Audit item D5AFA3

- run_id: `R_d8ff2dfe2c`
- condition: `one_shot_synthesis_length_matched`
- run_stage: `stage2_baseline`
- world_id: `W001`

### World state
```json
{
  "world_id": "W001",
  "event_type": "generator_shutdown",
  "location_id": "site_B",
  "time": "09:40",
  "observed_core_event": "Generator 2 shut down unexpectedly",
  "primary_causal_hypothesis": "cooling system malfunction",
  "alternative_causal_hypothesis": "temperature sensor fault",
  "evidence_for_primary_cause": "cooling loop ran above normal temperature for approximately 20 minutes before shutdown",
  "evidence_for_alternative_cause": "routine sensor diagnostics overdue",
  "consequence": "east processing line affected",
  "mitigation": "backup unit came online after 8 minutes",
  "uncertainty_fields": [
    "primary cause not confirmed",
    "sensor fault hypothesis not ruled out"
  ],
  "peripheral_operational_detail": "west processing line remained operational",
  "evidence_type_labels": {
    "shutdown": "direct_observation",
    "cooling_loop_temperature": "log_record",
    "primary_cause": "inference",
    "alternative_cause": "inference",
    "backup_timing": "log_record"
  },
  "chain_original_propositions": [
    "p1",
    "p2",
    "p3",
    "p4",
    "p5",
    "p6",
    "p7",
    "p8"
  ],
  "hub_input_a_propositions": [
    "p1",
    "p4",
    "p6",
    "p8"
  ],
  "hub_input_b_propositions": [
    "p1",
    "p2",
    "p3"
  ],
  "hub_input_c_propositions": [
    "p1",
    "p5",
    "p6",
    "p7"
  ],
  "conflict_propositions": [
    [
      "p3",
      "p4"
    ]
  ],
  "notes": "Hub conflict: input A carries sensor-fault hypothesis (false), input B carries cooling-system hypothesis (true). Both with attached uncertainty."
}
```

Propositions:
- (p1, T=true, u=0.95, ev=direct_observation, c=core) Generator 2 at Site B shut down unexpectedly at 09:40.
- (p2, T=true, u=0.85, ev=log_record, c=causal) The maintenance lead reported the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown.
- (p3, T=true, u=0.65, ev=inference, c=causal) The most likely cause is a cooling system malfunction.
- (p4, T=false, u=0.45, ev=report, c=causal) Operator notes suggest a faulty temperature sensor as the probable cause.
- (p5, T=true, u=0.9, ev=log_record, c=mitigation) The backup unit came online after 8 minutes.
- (p6, T=true, u=0.92, ev=direct_observation, c=consequence) The east processing line was affected by the shutdown.
- (p7, T=true, u=0.92, ev=direct_observation, c=peripheral) The west processing line remained operational.
- (p8, T=true, u=0.95, ev=report, c=peripheral) Sensor diagnostics are scheduled for next week.

### Message lineage

**[hub_input_a | source] hop=0** (id=`M_5b2f6abf37`, parent=[], prompt=`source_prompt_v0_1`)

> At 09:40 on site B, Generator 2 shut down unexpectedly. Operator notes suggest that a faulty temperature sensor is the probable cause of the shutdown. The east processing line was affected by the shutdown, with operations temporarily halted until power could be restored. Further investigation into the incident is ongoing, with sensor diagnostics scheduled for next week to determine if the suspected faulty temperature sensor is indeed the root cause.

**[hub_input_b | source] hop=0** (id=`M_8085109d74`, parent=[], prompt=`source_prompt_v0_1`)

> At 09:40, Generator 2 at Site B shut down unexpectedly. The maintenance lead reported that the cooling loop had been running above normal temperature for approximately 20 minutes prior to the shutdown. Logs show this anomaly began around 09:20. The most likely cause is a cooling system malfunction, although other factors have not been ruled out.

**[hub_input_c | source] hop=0** (id=`M_21540e4cd6`, parent=[], prompt=`source_prompt_v0_1`)

> At 09:40, Generator 2 at Site B shut down unexpectedly. Logs show that this occurred without prior warning or indication of malfunction. The backup unit came online approximately 8 minutes later, restoring power to critical systems. The east processing line was affected by the shutdown, but the west processing line remained operational throughout the incident.

**[one_shot_synthesizer | transformed] hop=1** (id=`M_ca9ff525f7`, parent=['M_5b2f6abf37', 'M_8085109d74', 'M_21540e4cd6'], prompt=`synthesis_baseline_v0_1`)

> At 09:40 on site B, Generator 2 shut down unexpectedly. Operator notes suggest that a faulty temperature sensor is the probable cause of the shutdown, while logs show that the cooling loop had been running above normal temperature for approximately 20 minutes prior to the shutdown, which began around 09:20. The maintenance lead reported this anomaly, and it is likely that the cooling system malfunction contributed to the shutdown. However, other factors have not been ruled out as contributing causes. The east processing line was affected by the shutdown, with operations temporarily halted until power could be restored, although the west processing line remained operational throughout the incident. Power was restored approximately 8 minutes after the shutdown, when the backup unit came online. Further investigation into the incident is ongoing, with sensor diagnostics scheduled for next week to determine if the suspected faulty temperature sensor is indeed the root cause.

### Automated feature summary

**[hub_input_a] hop=0** (`M_5b2f6abf37`)
- compression_ratio_from_original: 1.0
- compression_ratio_from_parent: None
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 0
- evidential_marker_count: 0
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 1
- location_marker_count: 2
- mean_sentence_length: 17.75
- mean_word_length: 5.296
- named_entity_count: 5
- numeric_token_count: 3
- proposition_alteration_count: 1
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 1.0
- punctuation_density: 0.0177
- semantic_drift_from_original: -0.0
- semantic_drift_from_parent: None
- sentence_count: 4
- source_marker_count: 0
- temporal_marker_count: 1
- token_count: 71
- type_token_ratio: 0.7887
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: 1.0
- unsupported_addition_count: 0

**[hub_input_b] hop=0** (`M_8085109d74`)
- compression_ratio_from_original: 0.8169
- compression_ratio_from_parent: None
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 0
- evidential_marker_count: 2
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 3
- location_marker_count: 1
- mean_sentence_length: 14.5
- mean_word_length: 4.897
- named_entity_count: 6
- numeric_token_count: 6
- proposition_alteration_count: 0
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 1.0
- punctuation_density: 0.0231
- semantic_drift_from_original: 0.0685
- semantic_drift_from_parent: None
- sentence_count: 4
- source_marker_count: 1
- temporal_marker_count: 2
- token_count: 58
- type_token_ratio: 0.8621
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: 1.0
- unsupported_addition_count: 1

**[hub_input_c] hop=0** (`M_21540e4cd6`)
- compression_ratio_from_original: 0.7887
- compression_ratio_from_parent: None
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 0
- evidential_marker_count: 1
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 1
- location_marker_count: 4
- mean_sentence_length: 14.0
- mean_word_length: 5.357
- named_entity_count: 6
- numeric_token_count: 4
- proposition_alteration_count: 0
- proposition_contradiction_count: 0
- proposition_omission_count: 0
- proposition_preservation_rate: 1.0
- punctuation_density: 0.0221
- semantic_drift_from_original: 0.0858
- semantic_drift_from_parent: None
- sentence_count: 4
- source_marker_count: 0
- temporal_marker_count: 1
- token_count: 56
- type_token_ratio: 0.875
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: None
- unsupported_addition_count: 0

**[one_shot_synthesizer] hop=1** (`M_ca9ff525f7`)
- compression_ratio_from_original: 2.1408
- compression_ratio_from_parent: 2.1408
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 1
- evidential_marker_count: 2
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 5
- location_marker_count: 4
- mean_sentence_length: 21.71
- mean_word_length: 5.382
- named_entity_count: 8
- numeric_token_count: 7
- proposition_alteration_count: 1
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 0.875
- punctuation_density: 0.0183
- semantic_drift_from_original: 0.0677
- semantic_drift_from_parent: 0.0677
- sentence_count: 7
- source_marker_count: 1
- temporal_marker_count: 2
- token_count: 152
- type_token_ratio: 0.6974
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: 0.5
- unsupported_addition_count: 1

### Per-proposition matches
- `M_5b2f6abf37` -> `p1`: preserved (sim=0.9836)
- `M_5b2f6abf37` -> `p2`: altered (sim=0.6429)
- `M_5b2f6abf37` -> `p3`: contradicted (sim=0.5745) [conflicting partner p4 matched more strongly (sim=0.77)]
- `M_5b2f6abf37` -> `p4`: preserved (sim=0.7746)
- `M_5b2f6abf37` -> `p5`: omitted (sim=0.346)
- `M_5b2f6abf37` -> `p6`: preserved (sim=0.9525)
- `M_5b2f6abf37` -> `p7`: altered (sim=0.6485)
- `M_5b2f6abf37` -> `p8`: altered (sim=0.4944)
- `M_8085109d74` -> `p1`: preserved (sim=0.9879)
- `M_8085109d74` -> `p2`: preserved (sim=0.9918)
- `M_8085109d74` -> `p3`: preserved (sim=0.9625)
- `M_8085109d74` -> `p4`: contradicted (sim=0.5536) [conflicting partner p3 matched more strongly (sim=0.96)]
- `M_8085109d74` -> `p5`: omitted (sim=0.3154)
- `M_8085109d74` -> `p6`: omitted (sim=0.4327)
- `M_8085109d74` -> `p7`: omitted (sim=0.3006)
- `M_8085109d74` -> `p8`: omitted (sim=0.3173)
- `M_21540e4cd6` -> `p1`: preserved (sim=0.9879)
- `M_21540e4cd6` -> `p2`: omitted (sim=0.3873)
- `M_21540e4cd6` -> `p3`: omitted (sim=0.4124)
- `M_21540e4cd6` -> `p4`: altered (sim=0.4801)
- `M_21540e4cd6` -> `p5`: preserved (sim=0.8803)
- `M_21540e4cd6` -> `p6`: preserved (sim=0.9162)
- `M_21540e4cd6` -> `p7`: preserved (sim=0.8412)
- `M_21540e4cd6` -> `p8`: omitted (sim=0.3332)
- `M_ca9ff525f7` -> `p1`: preserved (sim=0.9836)
- `M_ca9ff525f7` -> `p2`: preserved (sim=0.7725)
- `M_ca9ff525f7` -> `p3`: contradicted (sim=0.7156) [conflicting partner p4 matched more strongly (sim=0.77)]
- `M_ca9ff525f7` -> `p4`: preserved (sim=0.7746)
- `M_ca9ff525f7` -> `p5`: preserved (sim=0.7335)
- `M_ca9ff525f7` -> `p6`: preserved (sim=0.9452)
- `M_ca9ff525f7` -> `p7`: preserved (sim=0.7374)
- `M_ca9ff525f7` -> `p8`: altered (sim=0.4944)

### Human notes

(blank)

---

## Audit item F7D68A

- run_id: `R_ed7968c7d2`
- condition: `one_shot_synthesis_length_matched`
- run_stage: `stage2_baseline`
- world_id: `W001`

### World state
```json
{
  "world_id": "W001",
  "event_type": "generator_shutdown",
  "location_id": "site_B",
  "time": "09:40",
  "observed_core_event": "Generator 2 shut down unexpectedly",
  "primary_causal_hypothesis": "cooling system malfunction",
  "alternative_causal_hypothesis": "temperature sensor fault",
  "evidence_for_primary_cause": "cooling loop ran above normal temperature for approximately 20 minutes before shutdown",
  "evidence_for_alternative_cause": "routine sensor diagnostics overdue",
  "consequence": "east processing line affected",
  "mitigation": "backup unit came online after 8 minutes",
  "uncertainty_fields": [
    "primary cause not confirmed",
    "sensor fault hypothesis not ruled out"
  ],
  "peripheral_operational_detail": "west processing line remained operational",
  "evidence_type_labels": {
    "shutdown": "direct_observation",
    "cooling_loop_temperature": "log_record",
    "primary_cause": "inference",
    "alternative_cause": "inference",
    "backup_timing": "log_record"
  },
  "chain_original_propositions": [
    "p1",
    "p2",
    "p3",
    "p4",
    "p5",
    "p6",
    "p7",
    "p8"
  ],
  "hub_input_a_propositions": [
    "p1",
    "p4",
    "p6",
    "p8"
  ],
  "hub_input_b_propositions": [
    "p1",
    "p2",
    "p3"
  ],
  "hub_input_c_propositions": [
    "p1",
    "p5",
    "p6",
    "p7"
  ],
  "conflict_propositions": [
    [
      "p3",
      "p4"
    ]
  ],
  "notes": "Hub conflict: input A carries sensor-fault hypothesis (false), input B carries cooling-system hypothesis (true). Both with attached uncertainty."
}
```

Propositions:
- (p1, T=true, u=0.95, ev=direct_observation, c=core) Generator 2 at Site B shut down unexpectedly at 09:40.
- (p2, T=true, u=0.85, ev=log_record, c=causal) The maintenance lead reported the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown.
- (p3, T=true, u=0.65, ev=inference, c=causal) The most likely cause is a cooling system malfunction.
- (p4, T=false, u=0.45, ev=report, c=causal) Operator notes suggest a faulty temperature sensor as the probable cause.
- (p5, T=true, u=0.9, ev=log_record, c=mitigation) The backup unit came online after 8 minutes.
- (p6, T=true, u=0.92, ev=direct_observation, c=consequence) The east processing line was affected by the shutdown.
- (p7, T=true, u=0.92, ev=direct_observation, c=peripheral) The west processing line remained operational.
- (p8, T=true, u=0.95, ev=report, c=peripheral) Sensor diagnostics are scheduled for next week.

### Message lineage

**[hub_input_a | source] hop=0** (id=`M_4e6d730724`, parent=[], prompt=`source_prompt_v0_1`)

> At 09:40, Generator 2 at Site B shut down unexpectedly. Operator notes suggest that a faulty temperature sensor is the probable cause of the shutdown. The east processing line was affected by the shutdown, which may have resulted in temporary disruptions to operations. Further investigation into the incident is pending, with sensor diagnostics scheduled for next week to determine whether the suspected faulty temperature sensor was indeed responsible.

**[hub_input_b | source] hop=0** (id=`M_ae78a6ef39`, parent=[], prompt=`source_prompt_v0_1`)

> At Site B, Generator 2 shut down unexpectedly at 09:40. The maintenance lead reported that the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown. Logs show this increase in temperature occurred during routine operation and was not ruled out as a contributing factor to the shutdown. The most likely cause of the shutdown is suspected to be a cooling system malfunction, given the preceding temperature anomaly. Further investigation will be required to confirm this assessment.

**[hub_input_c | source] hop=0** (id=`M_c75beed4ef`, parent=[], prompt=`source_prompt_v0_1`)

> At 09:40, Generator 2 at Site B shut down unexpectedly. Logs show that this occurred without prior warning and was not preceded by any notable anomalies in generator performance. The backup unit came online after approximately 8 minutes, restoring power to critical systems. However, the east processing line was affected by the shutdown, requiring manual intervention to resume operations. In contrast, the west processing line remained operational throughout the incident.

**[one_shot_synthesizer | transformed] hop=1** (id=`M_53b706af46`, parent=['M_4e6d730724', 'M_ae78a6ef39', 'M_c75beed4ef'], prompt=`synthesis_baseline_v0_1`)

> At 09:40, Generator 2 at Site B shut down unexpectedly. Operator notes and maintenance reports suggest that a faulty temperature sensor may have caused the shutdown. However, logs also show that the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown, which could be a contributing factor to the malfunction. The shutdown occurred without prior warning and was not preceded by any notable anomalies in generator performance. In fact, the backup unit came online after approximately 8 minutes, restoring power to critical systems. Nevertheless, the east processing line was affected by the shutdown, requiring manual intervention to resume operations. Sensor diagnostics are scheduled for next week to determine whether a faulty temperature sensor was indeed responsible for the incident.

### Automated feature summary

**[hub_input_a] hop=0** (`M_4e6d730724`)
- compression_ratio_from_original: 1.0
- compression_ratio_from_parent: None
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 0
- evidential_marker_count: 0
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 1
- location_marker_count: 2
- mean_sentence_length: 17.25
- mean_word_length: 5.493
- named_entity_count: 6
- numeric_token_count: 3
- proposition_alteration_count: 1
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 1.0
- punctuation_density: 0.0176
- semantic_drift_from_original: -0.0
- semantic_drift_from_parent: None
- sentence_count: 4
- source_marker_count: 0
- temporal_marker_count: 1
- token_count: 69
- type_token_ratio: 0.7971
- uncertainty_marker_count: 1
- uncertainty_proposition_preservation_rate: 1.0
- unsupported_addition_count: 0

**[hub_input_b] hop=0** (`M_ae78a6ef39`)
- compression_ratio_from_original: 1.2029
- compression_ratio_from_parent: None
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 0
- evidential_marker_count: 2
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 3
- location_marker_count: 1
- mean_sentence_length: 16.6
- mean_word_length: 5.325
- named_entity_count: 6
- numeric_token_count: 4
- proposition_alteration_count: 0
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 1.0
- punctuation_density: 0.0151
- semantic_drift_from_original: 0.0904
- semantic_drift_from_parent: None
- sentence_count: 5
- source_marker_count: 1
- temporal_marker_count: 1
- token_count: 83
- type_token_ratio: 0.7952
- uncertainty_marker_count: 1
- uncertainty_proposition_preservation_rate: 1.0
- unsupported_addition_count: 1

**[hub_input_c] hop=0** (`M_c75beed4ef`)
- compression_ratio_from_original: 1.029
- compression_ratio_from_parent: None
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 0
- evidential_marker_count: 1
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 1
- location_marker_count: 4
- mean_sentence_length: 14.2
- mean_word_length: 5.549
- named_entity_count: 7
- numeric_token_count: 4
- proposition_alteration_count: 0
- proposition_contradiction_count: 0
- proposition_omission_count: 0
- proposition_preservation_rate: 1.0
- punctuation_density: 0.0232
- semantic_drift_from_original: 0.1177
- semantic_drift_from_parent: None
- sentence_count: 5
- source_marker_count: 0
- temporal_marker_count: 1
- token_count: 71
- type_token_ratio: 0.831
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: None
- unsupported_addition_count: 0

**[one_shot_synthesizer] hop=1** (`M_53b706af46`)
- compression_ratio_from_original: 1.8261
- compression_ratio_from_parent: 1.8261
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 1
- evidential_marker_count: 0
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 4
- location_marker_count: 3
- mean_sentence_length: 18.0
- mean_word_length: 5.556
- named_entity_count: 9
- numeric_token_count: 5
- proposition_alteration_count: 1
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 0.875
- punctuation_density: 0.0179
- semantic_drift_from_original: 0.0586
- semantic_drift_from_parent: 0.0586
- sentence_count: 7
- source_marker_count: 0
- temporal_marker_count: 1
- token_count: 126
- type_token_ratio: 0.7381
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: 0.5
- unsupported_addition_count: 0

### Per-proposition matches
- `M_4e6d730724` -> `p1`: preserved (sim=0.9879)
- `M_4e6d730724` -> `p2`: altered (sim=0.6429)
- `M_4e6d730724` -> `p3`: contradicted (sim=0.5745) [conflicting partner p4 matched more strongly (sim=0.77)]
- `M_4e6d730724` -> `p4`: preserved (sim=0.7723)
- `M_4e6d730724` -> `p5`: omitted (sim=0.3154)
- `M_4e6d730724` -> `p6`: preserved (sim=0.9336)
- `M_4e6d730724` -> `p7`: altered (sim=0.6418)
- `M_4e6d730724` -> `p8`: altered (sim=0.6057)
- `M_ae78a6ef39` -> `p1`: preserved (sim=0.9923)
- `M_ae78a6ef39` -> `p2`: preserved (sim=0.9941)
- `M_ae78a6ef39` -> `p3`: preserved (sim=0.68)
- `M_ae78a6ef39` -> `p4`: contradicted (sim=0.5479) [conflicting partner p3 matched more strongly (sim=0.68)]
- `M_ae78a6ef39` -> `p5`: omitted (sim=0.3146)
- `M_ae78a6ef39` -> `p6`: altered (sim=0.5051)
- `M_ae78a6ef39` -> `p7`: omitted (sim=0.2879)
- `M_ae78a6ef39` -> `p8`: omitted (sim=0.2999)
- `M_c75beed4ef` -> `p1`: preserved (sim=0.9879)
- `M_c75beed4ef` -> `p2`: omitted (sim=0.4355)
- `M_c75beed4ef` -> `p3`: omitted (sim=0.392)
- `M_c75beed4ef` -> `p4`: omitted (sim=0.4106)
- `M_c75beed4ef` -> `p5`: preserved (sim=0.8821)
- `M_c75beed4ef` -> `p6`: preserved (sim=0.9062)
- `M_c75beed4ef` -> `p7`: preserved (sim=0.9313)
- `M_c75beed4ef` -> `p8`: omitted (sim=0.2208)
- `M_53b706af46` -> `p1`: preserved (sim=0.9879)
- `M_53b706af46` -> `p2`: preserved (sim=0.7895)
- `M_53b706af46` -> `p3`: contradicted (sim=0.5787) [conflicting partner p4 matched more strongly (sim=0.74)]
- `M_53b706af46` -> `p4`: preserved (sim=0.7414)
- `M_53b706af46` -> `p5`: preserved (sim=0.8736)
- `M_53b706af46` -> `p6`: preserved (sim=0.9063)
- `M_53b706af46` -> `p7`: altered (sim=0.6432)
- `M_53b706af46` -> `p8`: preserved (sim=0.7716)

### Human notes

(blank)

---

## Audit item B8F009

- run_id: `R_e6806f62e0`
- condition: `hub_3input_synthesis`
- run_stage: `stage1_structural`
- world_id: `W001`

### World state
```json
{
  "world_id": "W001",
  "event_type": "generator_shutdown",
  "location_id": "site_B",
  "time": "09:40",
  "observed_core_event": "Generator 2 shut down unexpectedly",
  "primary_causal_hypothesis": "cooling system malfunction",
  "alternative_causal_hypothesis": "temperature sensor fault",
  "evidence_for_primary_cause": "cooling loop ran above normal temperature for approximately 20 minutes before shutdown",
  "evidence_for_alternative_cause": "routine sensor diagnostics overdue",
  "consequence": "east processing line affected",
  "mitigation": "backup unit came online after 8 minutes",
  "uncertainty_fields": [
    "primary cause not confirmed",
    "sensor fault hypothesis not ruled out"
  ],
  "peripheral_operational_detail": "west processing line remained operational",
  "evidence_type_labels": {
    "shutdown": "direct_observation",
    "cooling_loop_temperature": "log_record",
    "primary_cause": "inference",
    "alternative_cause": "inference",
    "backup_timing": "log_record"
  },
  "chain_original_propositions": [
    "p1",
    "p2",
    "p3",
    "p4",
    "p5",
    "p6",
    "p7",
    "p8"
  ],
  "hub_input_a_propositions": [
    "p1",
    "p4",
    "p6",
    "p8"
  ],
  "hub_input_b_propositions": [
    "p1",
    "p2",
    "p3"
  ],
  "hub_input_c_propositions": [
    "p1",
    "p5",
    "p6",
    "p7"
  ],
  "conflict_propositions": [
    [
      "p3",
      "p4"
    ]
  ],
  "notes": "Hub conflict: input A carries sensor-fault hypothesis (false), input B carries cooling-system hypothesis (true). Both with attached uncertainty."
}
```

Propositions:
- (p1, T=true, u=0.95, ev=direct_observation, c=core) Generator 2 at Site B shut down unexpectedly at 09:40.
- (p2, T=true, u=0.85, ev=log_record, c=causal) The maintenance lead reported the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown.
- (p3, T=true, u=0.65, ev=inference, c=causal) The most likely cause is a cooling system malfunction.
- (p4, T=false, u=0.45, ev=report, c=causal) Operator notes suggest a faulty temperature sensor as the probable cause.
- (p5, T=true, u=0.9, ev=log_record, c=mitigation) The backup unit came online after 8 minutes.
- (p6, T=true, u=0.92, ev=direct_observation, c=consequence) The east processing line was affected by the shutdown.
- (p7, T=true, u=0.92, ev=direct_observation, c=peripheral) The west processing line remained operational.
- (p8, T=true, u=0.95, ev=report, c=peripheral) Sensor diagnostics are scheduled for next week.

### Message lineage

**[hub_input_a | source] hop=0** (id=`M_6683dfe45d`, parent=[], prompt=`source_prompt_v0_1`)

> At 09:40, Generator 2 at Site B shut down unexpectedly. Operator notes suggest that a faulty temperature sensor is the probable cause of the shutdown. The east processing line was affected by the shutdown, but no other systems or equipment were impacted. Further investigation into the cause of the shutdown is pending, with sensor diagnostics scheduled for next week to verify the integrity of the temperature sensors in question.

**[hub_input_b | source] hop=0** (id=`M_0f84043098`, parent=[], prompt=`source_prompt_v0_1`)

> At Site B, Generator 2 shut down unexpectedly at 09:40. The maintenance lead reported that the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown. This is suspected to be a contributing factor in the shutdown. Logs show that the generator's performance was within acceptable parameters prior to the shutdown, but the increased cooling loop temperature may have triggered an automatic shutdown protocol. The most likely cause of the shutdown is a cooling system malfunction. Further investigation will be necessary to confirm this diagnosis and determine any necessary corrective actions.

**[hub_input_c | source] hop=0** (id=`M_d2d4a7c742`, parent=[], prompt=`source_prompt_v0_1`)

> At Site B, Generator 2 shut down unexpectedly at 09:40. The shutdown was not preceded by any warnings or alerts from the generator's monitoring system. Logs show that the backup unit came online approximately 8 minutes after the primary unit's failure. The east processing line was affected by the shutdown, resulting in a temporary reduction in production capacity. However, the west processing line remained operational throughout the incident.

**[synthesizer | transformed] hop=1** (id=`M_e9cb55a9ca`, parent=['M_6683dfe45d', 'M_0f84043098', 'M_d2d4a7c742'], prompt=`synthesis_c_v0_1`)

> At 09:40, Generator 2 at Site B shut down unexpectedly due to an automatic shutdown protocol being triggered. The cooling loop had been running above normal temperature for approximately 20 minutes prior to the shutdown, which is suspected to be a contributing factor in the event. Sensor diagnostics will be performed next week to verify the integrity of the temperature sensors in question. The shutdown was not preceded by any warnings or alerts from the generator's monitoring system. Logs show that the backup unit came online approximately 8 minutes after the primary unit's failure, ensuring continued operation of critical systems. The east processing line was affected by the shutdown, resulting in a temporary reduction in production capacity, while the west processing line remained operational throughout the incident. Further investigation will be necessary to confirm the diagnosis and determine any necessary corrective actions.

### Automated feature summary

**[hub_input_a] hop=0** (`M_6683dfe45d`)
- compression_ratio_from_original: 1.0
- compression_ratio_from_parent: None
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 0
- evidential_marker_count: 0
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 0
- location_marker_count: 2
- mean_sentence_length: 17.5
- mean_word_length: 5.071
- named_entity_count: 6
- numeric_token_count: 3
- proposition_alteration_count: 1
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 1.0
- punctuation_density: 0.0186
- semantic_drift_from_original: 0.0
- semantic_drift_from_parent: None
- sentence_count: 4
- source_marker_count: 0
- temporal_marker_count: 1
- token_count: 70
- type_token_ratio: 0.7714
- uncertainty_marker_count: 1
- uncertainty_proposition_preservation_rate: 1.0
- unsupported_addition_count: 0

**[hub_input_b] hop=0** (`M_0f84043098`)
- compression_ratio_from_original: 1.3857
- compression_ratio_from_parent: None
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 0
- evidential_marker_count: 2
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 4
- location_marker_count: 1
- mean_sentence_length: 16.17
- mean_word_length: 5.526
- named_entity_count: 7
- numeric_token_count: 4
- proposition_alteration_count: 0
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 1.0
- punctuation_density: 0.0156
- semantic_drift_from_original: 0.1066
- semantic_drift_from_parent: None
- sentence_count: 6
- source_marker_count: 1
- temporal_marker_count: 1
- token_count: 97
- type_token_ratio: 0.7423
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: 1.0
- unsupported_addition_count: 1

**[hub_input_c] hop=0** (`M_d2d4a7c742`)
- compression_ratio_from_original: 0.9857
- compression_ratio_from_parent: None
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 0
- evidential_marker_count: 1
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 1
- location_marker_count: 4
- mean_sentence_length: 13.8
- mean_word_length: 5.362
- named_entity_count: 6
- numeric_token_count: 4
- proposition_alteration_count: 0
- proposition_contradiction_count: 0
- proposition_omission_count: 0
- proposition_preservation_rate: 1.0
- punctuation_density: 0.0247
- semantic_drift_from_original: 0.1259
- semantic_drift_from_parent: None
- sentence_count: 5
- source_marker_count: 0
- temporal_marker_count: 1
- token_count: 69
- type_token_ratio: 0.7971
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: None
- unsupported_addition_count: 0

**[synthesizer] hop=1** (`M_e9cb55a9ca`)
- compression_ratio_from_original: 2.0429
- compression_ratio_from_parent: 2.0429
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 1
- evidential_marker_count: 1
- evidential_proposition_preservation_rate: 0.75
- hedge_count: 3
- location_marker_count: 4
- mean_sentence_length: 20.43
- mean_word_length: 5.517
- named_entity_count: 9
- numeric_token_count: 5
- proposition_alteration_count: 1
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 0.875
- punctuation_density: 0.0159
- semantic_drift_from_original: 0.1
- semantic_drift_from_parent: 0.1
- sentence_count: 7
- source_marker_count: 0
- temporal_marker_count: 1
- token_count: 143
- type_token_ratio: 0.7343
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: 0.5
- unsupported_addition_count: 1

### Per-proposition matches
- `M_6683dfe45d` -> `p1`: preserved (sim=0.9879)
- `M_6683dfe45d` -> `p2`: altered (sim=0.6429)
- `M_6683dfe45d` -> `p3`: contradicted (sim=0.5745) [conflicting partner p4 matched more strongly (sim=0.77)]
- `M_6683dfe45d` -> `p4`: preserved (sim=0.7723)
- `M_6683dfe45d` -> `p5`: omitted (sim=0.3154)
- `M_6683dfe45d` -> `p6`: preserved (sim=0.8604)
- `M_6683dfe45d` -> `p7`: altered (sim=0.6355)
- `M_6683dfe45d` -> `p8`: altered (sim=0.55)
- `M_0f84043098` -> `p1`: preserved (sim=0.9923)
- `M_0f84043098` -> `p2`: preserved (sim=0.9941)
- `M_0f84043098` -> `p3`: preserved (sim=0.6982)
- `M_0f84043098` -> `p4`: contradicted (sim=0.4882) [conflicting partner p3 matched more strongly (sim=0.70)]
- `M_0f84043098` -> `p5`: omitted (sim=0.3146)
- `M_0f84043098` -> `p6`: altered (sim=0.5513)
- `M_0f84043098` -> `p7`: omitted (sim=0.2879)
- `M_0f84043098` -> `p8`: omitted (sim=0.3585)
- `M_d2d4a7c742` -> `p1`: preserved (sim=0.9923)
- `M_d2d4a7c742` -> `p2`: omitted (sim=0.4331)
- `M_d2d4a7c742` -> `p3`: omitted (sim=0.3964)
- `M_d2d4a7c742` -> `p4`: omitted (sim=0.3228)
- `M_d2d4a7c742` -> `p5`: preserved (sim=0.8673)
- `M_d2d4a7c742` -> `p6`: preserved (sim=0.8813)
- `M_d2d4a7c742` -> `p7`: preserved (sim=0.9461)
- `M_d2d4a7c742` -> `p8`: omitted (sim=0.2399)
- `M_e9cb55a9ca` -> `p1`: preserved (sim=0.9245)
- `M_e9cb55a9ca` -> `p2`: preserved (sim=0.9187)
- `M_e9cb55a9ca` -> `p3`: altered (sim=0.5741)
- `M_e9cb55a9ca` -> `p4`: contradicted (sim=0.5541) [conflicting partner p3 matched more strongly (sim=0.57)]
- `M_e9cb55a9ca` -> `p5`: preserved (sim=0.8299)
- `M_e9cb55a9ca` -> `p6`: preserved (sim=0.907)
- `M_e9cb55a9ca` -> `p7`: preserved (sim=0.7327)
- `M_e9cb55a9ca` -> `p8`: preserved (sim=0.7638)

### Human notes

(blank)

---

## Audit item 2712F9

- run_id: `R_3d1120ab88`
- condition: `one_shot_summary_length_matched`
- run_stage: `stage2_baseline`
- world_id: `W001`

### World state
```json
{
  "world_id": "W001",
  "event_type": "generator_shutdown",
  "location_id": "site_B",
  "time": "09:40",
  "observed_core_event": "Generator 2 shut down unexpectedly",
  "primary_causal_hypothesis": "cooling system malfunction",
  "alternative_causal_hypothesis": "temperature sensor fault",
  "evidence_for_primary_cause": "cooling loop ran above normal temperature for approximately 20 minutes before shutdown",
  "evidence_for_alternative_cause": "routine sensor diagnostics overdue",
  "consequence": "east processing line affected",
  "mitigation": "backup unit came online after 8 minutes",
  "uncertainty_fields": [
    "primary cause not confirmed",
    "sensor fault hypothesis not ruled out"
  ],
  "peripheral_operational_detail": "west processing line remained operational",
  "evidence_type_labels": {
    "shutdown": "direct_observation",
    "cooling_loop_temperature": "log_record",
    "primary_cause": "inference",
    "alternative_cause": "inference",
    "backup_timing": "log_record"
  },
  "chain_original_propositions": [
    "p1",
    "p2",
    "p3",
    "p4",
    "p5",
    "p6",
    "p7",
    "p8"
  ],
  "hub_input_a_propositions": [
    "p1",
    "p4",
    "p6",
    "p8"
  ],
  "hub_input_b_propositions": [
    "p1",
    "p2",
    "p3"
  ],
  "hub_input_c_propositions": [
    "p1",
    "p5",
    "p6",
    "p7"
  ],
  "conflict_propositions": [
    [
      "p3",
      "p4"
    ]
  ],
  "notes": "Hub conflict: input A carries sensor-fault hypothesis (false), input B carries cooling-system hypothesis (true). Both with attached uncertainty."
}
```

Propositions:
- (p1, T=true, u=0.95, ev=direct_observation, c=core) Generator 2 at Site B shut down unexpectedly at 09:40.
- (p2, T=true, u=0.85, ev=log_record, c=causal) The maintenance lead reported the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown.
- (p3, T=true, u=0.65, ev=inference, c=causal) The most likely cause is a cooling system malfunction.
- (p4, T=false, u=0.45, ev=report, c=causal) Operator notes suggest a faulty temperature sensor as the probable cause.
- (p5, T=true, u=0.9, ev=log_record, c=mitigation) The backup unit came online after 8 minutes.
- (p6, T=true, u=0.92, ev=direct_observation, c=consequence) The east processing line was affected by the shutdown.
- (p7, T=true, u=0.92, ev=direct_observation, c=peripheral) The west processing line remained operational.
- (p8, T=true, u=0.95, ev=report, c=peripheral) Sensor diagnostics are scheduled for next week.

### Message lineage

**[source | source] hop=0** (id=`M_e90c32c1e7`, parent=[], prompt=`source_prompt_v0_1`)

> At 09:40, Generator 2 at Site B shut down unexpectedly. The maintenance lead reported that the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown, which is suspected to be related to the incident. Further investigation suggests that a cooling system malfunction was the most likely cause, with operator notes indicating a faulty temperature sensor as the probable cause. Following the shutdown, the backup unit came online after an 8-minute delay. The east processing line at Site B was affected by the shutdown, while the west processing line remained operational. Sensor diagnostics are scheduled for next week to further investigate the issue.

**[one_shot_summarizer | transformed] hop=1** (id=`M_61ae901e67`, parent=['M_e90c32c1e7'], prompt=`summary_baseline_v0_1`)

> At 09:40, Generator 2 at Site B experienced an unexpected shutdown due to a suspected cooling system malfunction. The cooling loop had been operating above normal temperature for approximately 20 minutes prior to the incident, which is believed to be related to the issue. A faulty temperature sensor is thought to be the probable cause of the malfunction. Following the shutdown, the backup unit initiated after an 8-minute delay, with minimal impact on overall operations. The east processing line at Site B was affected by the temporary disruption, while the west processing line remained operational. Further investigation is planned for next week through sensor diagnostics.

### Automated feature summary

**[source] hop=0** (`M_e90c32c1e7`)
- compression_ratio_from_original: 1.0
- compression_ratio_from_parent: None
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 1
- evidential_marker_count: 1
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 3
- location_marker_count: 5
- mean_sentence_length: 18.17
- mean_word_length: 5.321
- named_entity_count: 9
- numeric_token_count: 5
- proposition_alteration_count: 0
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 0.875
- punctuation_density: 0.0186
- semantic_drift_from_original: -0.0
- semantic_drift_from_parent: None
- sentence_count: 6
- source_marker_count: 1
- temporal_marker_count: 1
- token_count: 109
- type_token_ratio: 0.7248
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: 0.5
- unsupported_addition_count: 0

**[one_shot_summarizer] hop=1** (`M_61ae901e67`)
- compression_ratio_from_original: 0.9725
- compression_ratio_from_parent: 0.9725
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 1
- evidential_marker_count: 0
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 1
- location_marker_count: 5
- mean_sentence_length: 17.67
- mean_word_length: 5.311
- named_entity_count: 8
- numeric_token_count: 5
- proposition_alteration_count: 0
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 0.875
- punctuation_density: 0.0191
- semantic_drift_from_original: 0.0253
- semantic_drift_from_parent: 0.0253
- sentence_count: 6
- source_marker_count: 0
- temporal_marker_count: 1
- token_count: 106
- type_token_ratio: 0.717
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: 0.5
- unsupported_addition_count: 0

### Per-proposition matches
- `M_e90c32c1e7` -> `p1`: preserved (sim=0.9879)
- `M_e90c32c1e7` -> `p2`: preserved (sim=0.982)
- `M_e90c32c1e7` -> `p3`: contradicted (sim=0.7394) [conflicting partner p4 matched more strongly (sim=0.87)]
- `M_e90c32c1e7` -> `p4`: preserved (sim=0.8695)
- `M_e90c32c1e7` -> `p5`: preserved (sim=0.9194)
- `M_e90c32c1e7` -> `p6`: preserved (sim=0.8916)
- `M_e90c32c1e7` -> `p7`: preserved (sim=0.7494)
- `M_e90c32c1e7` -> `p8`: preserved (sim=0.8822)
- `M_61ae901e67` -> `p1`: preserved (sim=0.8368)
- `M_61ae901e67` -> `p2`: preserved (sim=0.8135)
- `M_61ae901e67` -> `p3`: contradicted (sim=0.6454) [conflicting partner p4 matched more strongly (sim=0.86)]
- `M_61ae901e67` -> `p4`: preserved (sim=0.862)
- `M_61ae901e67` -> `p5`: preserved (sim=0.7103)
- `M_61ae901e67` -> `p6`: preserved (sim=0.7729)
- `M_61ae901e67` -> `p7`: preserved (sim=0.7578)
- `M_61ae901e67` -> `p8`: preserved (sim=0.8481)

### Human notes

(blank)

---

## Audit item 132AD7

- run_id: `R_2639675e10`
- condition: `one_shot_summary_length_matched`
- run_stage: `stage2_baseline`
- world_id: `W001`

### World state
```json
{
  "world_id": "W001",
  "event_type": "generator_shutdown",
  "location_id": "site_B",
  "time": "09:40",
  "observed_core_event": "Generator 2 shut down unexpectedly",
  "primary_causal_hypothesis": "cooling system malfunction",
  "alternative_causal_hypothesis": "temperature sensor fault",
  "evidence_for_primary_cause": "cooling loop ran above normal temperature for approximately 20 minutes before shutdown",
  "evidence_for_alternative_cause": "routine sensor diagnostics overdue",
  "consequence": "east processing line affected",
  "mitigation": "backup unit came online after 8 minutes",
  "uncertainty_fields": [
    "primary cause not confirmed",
    "sensor fault hypothesis not ruled out"
  ],
  "peripheral_operational_detail": "west processing line remained operational",
  "evidence_type_labels": {
    "shutdown": "direct_observation",
    "cooling_loop_temperature": "log_record",
    "primary_cause": "inference",
    "alternative_cause": "inference",
    "backup_timing": "log_record"
  },
  "chain_original_propositions": [
    "p1",
    "p2",
    "p3",
    "p4",
    "p5",
    "p6",
    "p7",
    "p8"
  ],
  "hub_input_a_propositions": [
    "p1",
    "p4",
    "p6",
    "p8"
  ],
  "hub_input_b_propositions": [
    "p1",
    "p2",
    "p3"
  ],
  "hub_input_c_propositions": [
    "p1",
    "p5",
    "p6",
    "p7"
  ],
  "conflict_propositions": [
    [
      "p3",
      "p4"
    ]
  ],
  "notes": "Hub conflict: input A carries sensor-fault hypothesis (false), input B carries cooling-system hypothesis (true). Both with attached uncertainty."
}
```

Propositions:
- (p1, T=true, u=0.95, ev=direct_observation, c=core) Generator 2 at Site B shut down unexpectedly at 09:40.
- (p2, T=true, u=0.85, ev=log_record, c=causal) The maintenance lead reported the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown.
- (p3, T=true, u=0.65, ev=inference, c=causal) The most likely cause is a cooling system malfunction.
- (p4, T=false, u=0.45, ev=report, c=causal) Operator notes suggest a faulty temperature sensor as the probable cause.
- (p5, T=true, u=0.9, ev=log_record, c=mitigation) The backup unit came online after 8 minutes.
- (p6, T=true, u=0.92, ev=direct_observation, c=consequence) The east processing line was affected by the shutdown.
- (p7, T=true, u=0.92, ev=direct_observation, c=peripheral) The west processing line remained operational.
- (p8, T=true, u=0.95, ev=report, c=peripheral) Sensor diagnostics are scheduled for next week.

### Message lineage

**[source | source] hop=0** (id=`M_795038d3fd`, parent=[], prompt=`source_prompt_v0_1`)

> At Site B, Generator 2 shut down unexpectedly at 09:40. The maintenance lead reported that the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown. The most likely cause of this incident is a cooling system malfunction, which is suspected due to the elevated temperatures and the subsequent generator shutdown. Operator notes suggest a faulty temperature sensor as the probable cause, although this has not been confirmed. The backup unit came online after 8 minutes, minimizing the impact on operations. The east processing line was affected by the shutdown, while the west processing line remained operational; however, sensor diagnostics are scheduled for next week to investigate potential issues with the cooling system and temperature sensors.

**[one_shot_summarizer | transformed] hop=1** (id=`M_c9d28e6ae8`, parent=['M_795038d3fd'], prompt=`summary_baseline_v0_1`)

> At Site B, Generator 2 experienced an unexpected shutdown at 09:40 due to a suspected malfunction of its cooling system. The maintenance lead reported that the cooling loop had been operating above normal temperature for approximately 20 minutes prior to the shutdown. A faulty temperature sensor is considered a probable cause, although it has not been confirmed. As a result, the east processing line was temporarily affected, while the west processing line remained operational. Backup units were successfully activated within 8 minutes, minimizing disruption to operations. Further diagnostics are scheduled for next week to investigate potential issues with the cooling system and temperature sensors.

### Automated feature summary

**[source] hop=0** (`M_795038d3fd`)
- compression_ratio_from_original: 1.0
- compression_ratio_from_parent: None
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 1
- evidential_marker_count: 1
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 3
- location_marker_count: 4
- mean_sentence_length: 20.33
- mean_word_length: 5.467
- named_entity_count: 7
- numeric_token_count: 5
- proposition_alteration_count: 2
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 0.875
- punctuation_density: 0.0175
- semantic_drift_from_original: -0.0
- semantic_drift_from_parent: None
- sentence_count: 6
- source_marker_count: 1
- temporal_marker_count: 1
- token_count: 122
- type_token_ratio: 0.7295
- uncertainty_marker_count: 1
- uncertainty_proposition_preservation_rate: 0.5
- unsupported_addition_count: 0

**[one_shot_summarizer] hop=1** (`M_c9d28e6ae8`)
- compression_ratio_from_original: 0.8607
- compression_ratio_from_parent: 0.8607
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 1
- evidential_marker_count: 1
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 1
- location_marker_count: 4
- mean_sentence_length: 17.5
- mean_word_length: 5.629
- named_entity_count: 6
- numeric_token_count: 5
- proposition_alteration_count: 0
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 0.875
- punctuation_density: 0.017
- semantic_drift_from_original: 0.0339
- semantic_drift_from_parent: 0.0339
- sentence_count: 6
- source_marker_count: 1
- temporal_marker_count: 1
- token_count: 105
- type_token_ratio: 0.781
- uncertainty_marker_count: 1
- uncertainty_proposition_preservation_rate: 0.5
- unsupported_addition_count: 0

### Per-proposition matches
- `M_795038d3fd` -> `p1`: preserved (sim=0.9923)
- `M_795038d3fd` -> `p2`: preserved (sim=0.9941)
- `M_795038d3fd` -> `p3`: contradicted (sim=0.6763) [conflicting partner p4 matched more strongly (sim=0.96)]
- `M_795038d3fd` -> `p4`: preserved (sim=0.9568)
- `M_795038d3fd` -> `p5`: preserved (sim=0.923)
- `M_795038d3fd` -> `p6`: preserved (sim=0.8005)
- `M_795038d3fd` -> `p7`: altered (sim=0.6363)
- `M_795038d3fd` -> `p8`: altered (sim=0.5233)
- `M_c9d28e6ae8` -> `p1`: preserved (sim=0.8686)
- `M_c9d28e6ae8` -> `p2`: preserved (sim=0.9806)
- `M_c9d28e6ae8` -> `p3`: contradicted (sim=0.6433) [conflicting partner p4 matched more strongly (sim=0.85)]
- `M_c9d28e6ae8` -> `p4`: preserved (sim=0.8534)
- `M_c9d28e6ae8` -> `p5`: preserved (sim=0.7229)
- `M_c9d28e6ae8` -> `p6`: preserved (sim=0.8223)
- `M_c9d28e6ae8` -> `p7`: preserved (sim=0.816)
- `M_c9d28e6ae8` -> `p8`: preserved (sim=0.7704)

### Human notes

(blank)

---

## Audit item 4E4EE0

- run_id: `R_c49fa4fcb1`
- condition: `chain_3hop`
- run_stage: `stage1_structural`
- world_id: `W001`

### World state
```json
{
  "world_id": "W001",
  "event_type": "generator_shutdown",
  "location_id": "site_B",
  "time": "09:40",
  "observed_core_event": "Generator 2 shut down unexpectedly",
  "primary_causal_hypothesis": "cooling system malfunction",
  "alternative_causal_hypothesis": "temperature sensor fault",
  "evidence_for_primary_cause": "cooling loop ran above normal temperature for approximately 20 minutes before shutdown",
  "evidence_for_alternative_cause": "routine sensor diagnostics overdue",
  "consequence": "east processing line affected",
  "mitigation": "backup unit came online after 8 minutes",
  "uncertainty_fields": [
    "primary cause not confirmed",
    "sensor fault hypothesis not ruled out"
  ],
  "peripheral_operational_detail": "west processing line remained operational",
  "evidence_type_labels": {
    "shutdown": "direct_observation",
    "cooling_loop_temperature": "log_record",
    "primary_cause": "inference",
    "alternative_cause": "inference",
    "backup_timing": "log_record"
  },
  "chain_original_propositions": [
    "p1",
    "p2",
    "p3",
    "p4",
    "p5",
    "p6",
    "p7",
    "p8"
  ],
  "hub_input_a_propositions": [
    "p1",
    "p4",
    "p6",
    "p8"
  ],
  "hub_input_b_propositions": [
    "p1",
    "p2",
    "p3"
  ],
  "hub_input_c_propositions": [
    "p1",
    "p5",
    "p6",
    "p7"
  ],
  "conflict_propositions": [
    [
      "p3",
      "p4"
    ]
  ],
  "notes": "Hub conflict: input A carries sensor-fault hypothesis (false), input B carries cooling-system hypothesis (true). Both with attached uncertainty."
}
```

Propositions:
- (p1, T=true, u=0.95, ev=direct_observation, c=core) Generator 2 at Site B shut down unexpectedly at 09:40.
- (p2, T=true, u=0.85, ev=log_record, c=causal) The maintenance lead reported the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown.
- (p3, T=true, u=0.65, ev=inference, c=causal) The most likely cause is a cooling system malfunction.
- (p4, T=false, u=0.45, ev=report, c=causal) Operator notes suggest a faulty temperature sensor as the probable cause.
- (p5, T=true, u=0.9, ev=log_record, c=mitigation) The backup unit came online after 8 minutes.
- (p6, T=true, u=0.92, ev=direct_observation, c=consequence) The east processing line was affected by the shutdown.
- (p7, T=true, u=0.92, ev=direct_observation, c=peripheral) The west processing line remained operational.
- (p8, T=true, u=0.95, ev=report, c=peripheral) Sensor diagnostics are scheduled for next week.

### Message lineage

**[source | source] hop=0** (id=`M_8f01b8e858`, parent=[], prompt=`source_prompt_v0_1`)

> At 09:40, Generator 2 at Site B shut down unexpectedly. The maintenance lead reported that the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown, suggesting a potential issue with the cooling system. The most likely cause is a cooling system malfunction, although operator notes suggest a faulty temperature sensor as the probable cause. Despite the shutdown, the backup unit came online after 8 minutes, minimizing downtime. However, the east processing line was affected by the shutdown, while the west processing line remained operational. Sensor diagnostics are scheduled for next week to investigate further.

**[relay | transformed] hop=1** (id=`M_746f36ba5b`, parent=['M_8f01b8e858'], prompt=`relay_a_v0_1`)

> At 09:40, Generator 2 at Site B unexpectedly shut down. Preliminary analysis suggests that the cooling loop had been operating above normal temperature for approximately 20 minutes prior to shutdown, indicating a potential issue with the cooling system. Although the cause is not yet confirmed, it is believed that a malfunction in this system may be responsible, although operator notes indicate that a faulty temperature sensor could also be at fault. Despite the shutdown, the backup unit came online within 8 minutes, thereby minimizing downtime for operational activities. The east processing line was affected by the shutdown, whereas the west processing line remained unaffected. Further investigation is scheduled through sensor diagnostics next week to determine the root cause of this incident.

**[relay | transformed] hop=2** (id=`M_c9974a91de`, parent=['M_746f36ba5b'], prompt=`relay_b_v0_1`)

> At 09:40, Generator 2 at Site B unexpectedly ceased operation due to a potential issue with its cooling system. Preliminary analysis suggests that the cooling loop had been running above normal temperature for approximately 20 minutes prior to shutdown, indicating a possible problem with its functioning. Further investigation is required to confirm the cause of this incident, although it is currently suspected that a malfunction in the cooling system may be responsible. A faulty temperature sensor has also been proposed as a potential cause. Despite the shutdown, the backup unit quickly came online within 8 minutes, minimizing downtime for ongoing operational activities. The east processing line was impacted by the shutdown, while the west processing line remained unaffected. A follow-up investigation is planned through sensor diagnostics next week to determine the root cause of this incident.

**[relay | transformed] hop=3** (id=`M_a3f9255f20`, parent=['M_c9974a91de'], prompt=`relay_c_v0_1`)

> At 09:40, Generator 2 at Site B experienced an unexpected shutdown due to a potential issue with its cooling system. Initial analysis suggests that the cooling loop had been operating above normal temperature for approximately 20 minutes before ceasing operation, which may indicate a problem with the system's performance. Further investigation is necessary to confirm the cause of this event, although it is currently suspected that a malfunction in the cooling system could be responsible. A faulty temperature sensor has also been proposed as a possible contributing factor. Despite the shutdown, the backup unit came online within 8 minutes, thereby minimizing downtime for ongoing operational activities. The east processing line was affected by the shutdown, while the west processing line remained unaffected. A follow-up investigation is scheduled to take place through sensor diagnostics next week to determine the root cause of this incident.

### Automated feature summary

**[source] hop=0** (`M_8f01b8e858`)
- compression_ratio_from_original: 1.0
- compression_ratio_from_parent: None
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 1
- evidential_marker_count: 1
- evidential_proposition_preservation_rate: 0.75
- hedge_count: 2
- location_marker_count: 4
- mean_sentence_length: 16.83
- mean_word_length: 5.485
- named_entity_count: 8
- numeric_token_count: 5
- proposition_alteration_count: 0
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 0.875
- punctuation_density: 0.021
- semantic_drift_from_original: 0.0
- semantic_drift_from_parent: None
- sentence_count: 6
- source_marker_count: 1
- temporal_marker_count: 1
- token_count: 101
- type_token_ratio: 0.7525
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: 0.5
- unsupported_addition_count: 0

**[relay] hop=1** (`M_746f36ba5b`)
- compression_ratio_from_original: 1.2079
- compression_ratio_from_parent: 1.2079
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 1
- evidential_marker_count: 0
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 3
- location_marker_count: 4
- mean_sentence_length: 20.33
- mean_word_length: 5.492
- named_entity_count: 8
- numeric_token_count: 5
- proposition_alteration_count: 0
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 0.875
- punctuation_density: 0.0174
- semantic_drift_from_original: 0.02
- semantic_drift_from_parent: 0.02
- sentence_count: 6
- source_marker_count: 0
- temporal_marker_count: 1
- token_count: 122
- type_token_ratio: 0.7459
- uncertainty_marker_count: 2
- uncertainty_proposition_preservation_rate: 0.5
- unsupported_addition_count: 0

**[relay] hop=2** (`M_c9974a91de`)
- compression_ratio_from_original: 1.3564
- compression_ratio_from_parent: 1.123
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 1
- evidential_marker_count: 0
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 2
- location_marker_count: 4
- mean_sentence_length: 19.57
- mean_word_length: 5.526
- named_entity_count: 7
- numeric_token_count: 5
- proposition_alteration_count: 0
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 0.875
- punctuation_density: 0.0166
- semantic_drift_from_original: 0.0348
- semantic_drift_from_parent: 0.0148
- sentence_count: 7
- source_marker_count: 0
- temporal_marker_count: 1
- token_count: 137
- type_token_ratio: 0.7007
- uncertainty_marker_count: 1
- uncertainty_proposition_preservation_rate: 0.5
- unsupported_addition_count: 0

**[relay] hop=3** (`M_a3f9255f20`)
- compression_ratio_from_original: 1.4257
- compression_ratio_from_parent: 1.0511
- conflict_pairs_preserved: 0
- conflict_pairs_repaired: 1
- evidential_marker_count: 0
- evidential_proposition_preservation_rate: 1.0
- hedge_count: 3
- location_marker_count: 4
- mean_sentence_length: 20.57
- mean_word_length: 5.535
- named_entity_count: 7
- numeric_token_count: 5
- proposition_alteration_count: 0
- proposition_contradiction_count: 1
- proposition_omission_count: 0
- proposition_preservation_rate: 0.875
- punctuation_density: 0.0168
- semantic_drift_from_original: 0.0338
- semantic_drift_from_parent: 0.014
- sentence_count: 7
- source_marker_count: 0
- temporal_marker_count: 1
- token_count: 144
- type_token_ratio: 0.7361
- uncertainty_marker_count: 0
- uncertainty_proposition_preservation_rate: 0.5
- unsupported_addition_count: 0

### Per-proposition matches
- `M_8f01b8e858` -> `p1`: preserved (sim=0.9879)
- `M_8f01b8e858` -> `p2`: preserved (sim=0.9707)
- `M_8f01b8e858` -> `p3`: preserved (sim=0.9025)
- `M_8f01b8e858` -> `p4`: contradicted (sim=0.8029) [conflicting partner p3 matched more strongly (sim=0.90)]
- `M_8f01b8e858` -> `p5`: preserved (sim=0.8752)
- `M_8f01b8e858` -> `p6`: preserved (sim=0.9341)
- `M_8f01b8e858` -> `p7`: preserved (sim=0.8224)
- `M_8f01b8e858` -> `p8`: preserved (sim=0.963)
- `M_746f36ba5b` -> `p1`: preserved (sim=0.9848)
- `M_746f36ba5b` -> `p2`: preserved (sim=0.9165)
- `M_746f36ba5b` -> `p3`: contradicted (sim=0.741) [conflicting partner p4 matched more strongly (sim=0.86)]
- `M_746f36ba5b` -> `p4`: preserved (sim=0.8573)
- `M_746f36ba5b` -> `p5`: preserved (sim=0.8016)
- `M_746f36ba5b` -> `p6`: preserved (sim=0.9375)
- `M_746f36ba5b` -> `p7`: preserved (sim=0.746)
- `M_746f36ba5b` -> `p8`: preserved (sim=0.6549)
- `M_c9974a91de` -> `p1`: preserved (sim=0.8429)
- `M_c9974a91de` -> `p2`: preserved (sim=0.9245)
- `M_c9974a91de` -> `p3`: contradicted (sim=0.7373) [conflicting partner p4 matched more strongly (sim=0.86)]
- `M_c9974a91de` -> `p4`: preserved (sim=0.8603)
- `M_c9974a91de` -> `p5`: preserved (sim=0.8156)
- `M_c9974a91de` -> `p6`: preserved (sim=0.9299)
- `M_c9974a91de` -> `p7`: preserved (sim=0.7451)
- `M_c9974a91de` -> `p8`: preserved (sim=0.6693)
- `M_a3f9255f20` -> `p1`: preserved (sim=0.8804)
- `M_a3f9255f20` -> `p2`: preserved (sim=0.8204)
- `M_a3f9255f20` -> `p3`: contradicted (sim=0.7789) [conflicting partner p4 matched more strongly (sim=0.83)]
- `M_a3f9255f20` -> `p4`: preserved (sim=0.827)
- `M_a3f9255f20` -> `p5`: preserved (sim=0.8062)
- `M_a3f9255f20` -> `p6`: preserved (sim=0.9361)
- `M_a3f9255f20` -> `p7`: preserved (sim=0.7509)
- `M_a3f9255f20` -> `p8`: preserved (sim=0.6846)

### Human notes

(blank)

---



# Audit export (blinded mode)

Sample size: 8

## Audit item 22653A

- (condition and stage hidden in blinded mode)

### Message lineage

**[hub_input_a | source] hop=0**

> At 09:40, Generator 2 at Site B shut down unexpectedly. Operator notes suggest that a faulty temperature sensor is the probable cause of the shutdown. The east processing line was affected by the shutdown, which may have resulted in temporary disruptions to operations. Further investigation into the incident is pending, with sensor diagnostics scheduled for next week to determine whether the suspected faulty temperature sensor was indeed responsible.

**[hub_input_b | source] hop=0**

> At Site B, Generator 2 shut down unexpectedly at 09:40. The maintenance lead reported that the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown. Logs show this increase in temperature occurred during routine operation and was not ruled out as a contributing factor to the shutdown. The most likely cause of the shutdown is suspected to be a cooling system malfunction, given the preceding temperature anomaly. Further investigation will be required to confirm this assessment.

**[hub_input_c | source] hop=0**

> At 09:40, Generator 2 at Site B shut down unexpectedly. Logs show that this occurred without prior warning and was not preceded by any notable anomalies in generator performance. The backup unit came online after approximately 8 minutes, restoring power to critical systems. However, the east processing line was affected by the shutdown, requiring manual intervention to resume operations. In contrast, the west processing line remained operational throughout the incident.

**[one_shot_synthesizer | transformed] hop=1**

> At 09:40, Generator 2 at Site B shut down unexpectedly. Operator notes and maintenance reports suggest that a faulty temperature sensor may have caused the shutdown. However, logs also show that the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown, which could be a contributing factor to the malfunction. The shutdown occurred without prior warning and was not preceded by any notable anomalies in generator performance. In fact, the backup unit came online after approximately 8 minutes, restoring power to critical systems. Nevertheless, the east processing line was affected by the shutdown, requiring manual intervention to resume operations. Sensor diagnostics are scheduled for next week to determine whether a faulty temperature sensor was indeed responsible for the incident.

### Human notes

(blank)

---

## Audit item F4DD07

- (condition and stage hidden in blinded mode)

### Message lineage

**[source | source] hop=0**

> At Site B, Generator 2 shut down unexpectedly at 09:40. The maintenance lead reported that the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown. The most likely cause of this incident is a cooling system malfunction, which is suspected due to the elevated temperatures and the subsequent generator shutdown. Operator notes suggest a faulty temperature sensor as the probable cause, although this has not been confirmed. The backup unit came online after 8 minutes, minimizing the impact on operations. The east processing line was affected by the shutdown, while the west processing line remained operational; however, sensor diagnostics are scheduled for next week to investigate potential issues with the cooling system and temperature sensors.

**[one_shot_summarizer | transformed] hop=1**

> At Site B, Generator 2 experienced an unexpected shutdown at 09:40 due to a suspected malfunction of its cooling system. The maintenance lead reported that the cooling loop had been operating above normal temperature for approximately 20 minutes prior to the shutdown. A faulty temperature sensor is considered a probable cause, although it has not been confirmed. As a result, the east processing line was temporarily affected, while the west processing line remained operational. Backup units were successfully activated within 8 minutes, minimizing disruption to operations. Further diagnostics are scheduled for next week to investigate potential issues with the cooling system and temperature sensors.

### Human notes

(blank)

---

## Audit item E506D9

- (condition and stage hidden in blinded mode)

### Message lineage

**[hub_input_a | source] hop=0**

> At 09:40, Generator 2 at Site B shut down unexpectedly. Operator notes suggest that a faulty temperature sensor is the probable cause of the shutdown. The east processing line was affected by the shutdown, with operations temporarily halted until the generator could be restarted. Further investigation into the cause of the fault is pending, although sensor diagnostics are scheduled for next week and may provide additional insight.

**[hub_input_b | source] hop=0**

> At 09:40, Generator 2 at Site B shut down unexpectedly. The maintenance lead reported that the cooling loop had been running above normal temperature for approximately 20 minutes prior to the shutdown. This increase in temperature is suspected to have triggered the automatic shutdown procedure. Logs show that the generator's internal sensors detected a critical threshold being breached, resulting in the shutdown. The most likely cause of the shutdown is a malfunction within the cooling system. Further investigation will be required to confirm this diagnosis and determine the root cause of the issue.

**[hub_input_c | source] hop=0**

> At Site B, Generator 2 shut down unexpectedly at 09:40. Logs show that this occurred without prior warning or indication of malfunction. The backup unit came online after approximately 8 minutes, indicating that it was functioning as designed to mitigate the impact of the shutdown. However, the east processing line was affected by the shutdown, while the west processing line remained operational. Further investigation is required to determine the cause of the unexpected shutdown.

**[one_shot_synthesizer | transformed] hop=1**

> At 09:40, Generator 2 at Site B shut down unexpectedly. Operator notes and maintenance logs suggest that a faulty temperature sensor is one possible cause of the shutdown, although sensor diagnostics are scheduled for next week to provide additional insight. However, the cooling loop had been running above normal temperature for approximately 20 minutes prior to the shutdown, which may have triggered the automatic shutdown procedure. The generator's internal sensors detected a critical threshold being breached, resulting in the shutdown, indicating a possible malfunction within the cooling system. The backup unit came online after approximately 8 minutes, but the temporary loss of power affected the east processing line, while the west processing line remained operational. Further investigation will be required to confirm this diagnosis and determine the root cause of the issue.

### Human notes

(blank)

---

## Audit item F7C2A0

- (condition and stage hidden in blinded mode)

### Message lineage

**[source | source] hop=0**

> At 09:40, Generator 2 at Site B shut down unexpectedly. The maintenance lead reported that the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown, which is suspected to be related to the incident. Further investigation suggests that a cooling system malfunction was the most likely cause, with operator notes indicating a faulty temperature sensor as the probable cause. Following the shutdown, the backup unit came online after an 8-minute delay. The east processing line at Site B was affected by the shutdown, while the west processing line remained operational. Sensor diagnostics are scheduled for next week to further investigate the issue.

**[one_shot_summarizer | transformed] hop=1**

> At 09:40, Generator 2 at Site B experienced an unexpected shutdown due to a suspected cooling system malfunction. The cooling loop had been operating above normal temperature for approximately 20 minutes prior to the incident, which is believed to be related to the issue. A faulty temperature sensor is thought to be the probable cause of the malfunction. Following the shutdown, the backup unit initiated after an 8-minute delay, with minimal impact on overall operations. The east processing line at Site B was affected by the temporary disruption, while the west processing line remained operational. Further investigation is planned for next week through sensor diagnostics.

### Human notes

(blank)

---

## Audit item B100B7

- (condition and stage hidden in blinded mode)

### Message lineage

**[source | source] hop=0**

> At 09:40, Generator 2 at Site B shut down unexpectedly. The maintenance lead reported that the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown, suggesting a potential issue with the cooling system. The most likely cause is a cooling system malfunction, although operator notes suggest a faulty temperature sensor as the probable cause. Despite the shutdown, the backup unit came online after 8 minutes, minimizing downtime. However, the east processing line was affected by the shutdown, while the west processing line remained operational. Sensor diagnostics are scheduled for next week to investigate further.

**[relay | transformed] hop=1**

> At 09:40, Generator 2 at Site B unexpectedly shut down. Preliminary analysis suggests that the cooling loop had been operating above normal temperature for approximately 20 minutes prior to shutdown, indicating a potential issue with the cooling system. Although the cause is not yet confirmed, it is believed that a malfunction in this system may be responsible, although operator notes indicate that a faulty temperature sensor could also be at fault. Despite the shutdown, the backup unit came online within 8 minutes, thereby minimizing downtime for operational activities. The east processing line was affected by the shutdown, whereas the west processing line remained unaffected. Further investigation is scheduled through sensor diagnostics next week to determine the root cause of this incident.

**[relay | transformed] hop=2**

> At 09:40, Generator 2 at Site B unexpectedly ceased operation due to a potential issue with its cooling system. Preliminary analysis suggests that the cooling loop had been running above normal temperature for approximately 20 minutes prior to shutdown, indicating a possible problem with its functioning. Further investigation is required to confirm the cause of this incident, although it is currently suspected that a malfunction in the cooling system may be responsible. A faulty temperature sensor has also been proposed as a potential cause. Despite the shutdown, the backup unit quickly came online within 8 minutes, minimizing downtime for ongoing operational activities. The east processing line was impacted by the shutdown, while the west processing line remained unaffected. A follow-up investigation is planned through sensor diagnostics next week to determine the root cause of this incident.

**[relay | transformed] hop=3**

> At 09:40, Generator 2 at Site B experienced an unexpected shutdown due to a potential issue with its cooling system. Initial analysis suggests that the cooling loop had been operating above normal temperature for approximately 20 minutes before ceasing operation, which may indicate a problem with the system's performance. Further investigation is necessary to confirm the cause of this event, although it is currently suspected that a malfunction in the cooling system could be responsible. A faulty temperature sensor has also been proposed as a possible contributing factor. Despite the shutdown, the backup unit came online within 8 minutes, thereby minimizing downtime for ongoing operational activities. The east processing line was affected by the shutdown, while the west processing line remained unaffected. A follow-up investigation is scheduled to take place through sensor diagnostics next week to determine the root cause of this incident.

### Human notes

(blank)

---

## Audit item E9B035

- (condition and stage hidden in blinded mode)

### Message lineage

**[source | source] hop=0**

> At 09:40, Generator 2 at Site B shut down unexpectedly. The maintenance lead reported that the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown, which is suspected to be related to the malfunction. A faulty temperature sensor is considered the most likely cause, based on operator notes and observations. Following the shutdown, the backup unit came online after an 8-minute delay, ensuring continuity of operations. The east processing line was affected by the shutdown, while the west processing line remained operational. Sensor diagnostics are scheduled for next week to investigate the issue further.

**[one_shot_summarizer | transformed] hop=1**

> At 09:40 hours, Generator 2 at Site B experienced an unexpected shutdown. Preliminary investigation suggests that the cooling loop had been operating above normal temperature for approximately 20 minutes prior to the shutdown, which may be attributed to a malfunction. A faulty temperature sensor is currently suspected as the root cause, based on operator observations and notes. The incident resulted in a temporary disruption to the east processing line, while the west processing line remained operational. Backup power was successfully initiated after an 8-minute delay. Further investigation will be conducted next week through sensor diagnostics.

### Human notes

(blank)

---

## Audit item 4E9904

- (condition and stage hidden in blinded mode)

### Message lineage

**[hub_input_a | source] hop=0**

> At 09:40, Generator 2 at Site B shut down unexpectedly. Operator notes suggest that a faulty temperature sensor is the probable cause of the shutdown. The east processing line was affected by the shutdown, but no other systems or equipment were impacted. Further investigation into the cause of the shutdown is pending, with sensor diagnostics scheduled for next week to verify the integrity of the temperature sensors in question.

**[hub_input_b | source] hop=0**

> At Site B, Generator 2 shut down unexpectedly at 09:40. The maintenance lead reported that the cooling loop had been running above normal temperature for approximately 20 minutes before the shutdown. This is suspected to be a contributing factor in the shutdown. Logs show that the generator's performance was within acceptable parameters prior to the shutdown, but the increased cooling loop temperature may have triggered an automatic shutdown protocol. The most likely cause of the shutdown is a cooling system malfunction. Further investigation will be necessary to confirm this diagnosis and determine any necessary corrective actions.

**[hub_input_c | source] hop=0**

> At Site B, Generator 2 shut down unexpectedly at 09:40. The shutdown was not preceded by any warnings or alerts from the generator's monitoring system. Logs show that the backup unit came online approximately 8 minutes after the primary unit's failure. The east processing line was affected by the shutdown, resulting in a temporary reduction in production capacity. However, the west processing line remained operational throughout the incident.

**[synthesizer | transformed] hop=1**

> At 09:40, Generator 2 at Site B shut down unexpectedly due to an automatic shutdown protocol being triggered. The cooling loop had been running above normal temperature for approximately 20 minutes prior to the shutdown, which is suspected to be a contributing factor in the event. Sensor diagnostics will be performed next week to verify the integrity of the temperature sensors in question. The shutdown was not preceded by any warnings or alerts from the generator's monitoring system. Logs show that the backup unit came online approximately 8 minutes after the primary unit's failure, ensuring continued operation of critical systems. The east processing line was affected by the shutdown, resulting in a temporary reduction in production capacity, while the west processing line remained operational throughout the incident. Further investigation will be necessary to confirm the diagnosis and determine any necessary corrective actions.

### Human notes

(blank)

---

## Audit item 7F47F9

- (condition and stage hidden in blinded mode)

### Message lineage

**[hub_input_a | source] hop=0**

> At 09:40 on site B, Generator 2 shut down unexpectedly. Operator notes suggest that a faulty temperature sensor is the probable cause of the shutdown. The east processing line was affected by the shutdown, with operations temporarily halted until power could be restored. Further investigation into the incident is ongoing, with sensor diagnostics scheduled for next week to determine if the suspected faulty temperature sensor is indeed the root cause.

**[hub_input_b | source] hop=0**

> At 09:40, Generator 2 at Site B shut down unexpectedly. The maintenance lead reported that the cooling loop had been running above normal temperature for approximately 20 minutes prior to the shutdown. Logs show this anomaly began around 09:20. The most likely cause is a cooling system malfunction, although other factors have not been ruled out.

**[hub_input_c | source] hop=0**

> At 09:40, Generator 2 at Site B shut down unexpectedly. Logs show that this occurred without prior warning or indication of malfunction. The backup unit came online approximately 8 minutes later, restoring power to critical systems. The east processing line was affected by the shutdown, but the west processing line remained operational throughout the incident.

**[one_shot_synthesizer | transformed] hop=1**

> At 09:40 on site B, Generator 2 shut down unexpectedly. Operator notes suggest that a faulty temperature sensor is the probable cause of the shutdown, while logs show that the cooling loop had been running above normal temperature for approximately 20 minutes prior to the shutdown, which began around 09:20. The maintenance lead reported this anomaly, and it is likely that the cooling system malfunction contributed to the shutdown. However, other factors have not been ruled out as contributing causes. The east processing line was affected by the shutdown, with operations temporarily halted until power could be restored, although the west processing line remained operational throughout the incident. Power was restored approximately 8 minutes after the shutdown, when the backup unit came online. Further investigation into the incident is ongoing, with sensor diagnostics scheduled for next week to determine if the suspected faulty temperature sensor is indeed the root cause.

### Human notes

(blank)

---
