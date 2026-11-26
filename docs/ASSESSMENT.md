# Assessment method

Three layers that never mix:

1. **Criteria:** what should happen. Written and reviewed by clinicians, versioned YAML in `content/stations/`.
2. **Observations:** what the system saw or heard. Timestamped, with a source and a strength.
3. **Rules:** how observations become statuses and marks. Deterministic and unit-tested.

AI only ever produces observations.

## Criterion fields
`id`, `domain`, `text`, `marks`, `scoring` (binary | 0-1-2 | global), `evidence` (required observation types, sides and zones), `verbal_sufficient` (false for every physical step), `observability` (video | audio | both | not_observable), `sequence`, `critical`, `feedback`, `references`.

## Observation fields
`id`, `type`, `actor` (examiner | patient), `side`, `zone`, `region`, `t_start`, `t_end`, `source` (pose_rules | gemini | transcript | student | partner), `strength` (seen_clearly | seen_partly | heard_only | reported), `visibility`, `quote` or `keyframe`, `model`, `prompt_version`.

## Physical criteria: status rules
| Visual evidence | Speech | Region visible | Status |
| --- | --- | --- | --- |
| Yes | any | — | Achieved (partial if sides or zones are incomplete) |
| No | Yes | No | Insufficient evidence ("verbalised, not seen") |
| No | Yes | Yes | Not achieved ("verbalised, not seen") |
| No | No | Yes | Not achieved |
| No | No | No | Insufficient evidence |

## Scores
- Assessed performance = marks awarded ÷ marks on assessable criteria.
- Coverage = marks on assessable criteria ÷ total marks.
- Always shown together. Attempts are only compared when they use the same rubric version and both have coverage of at least 70%.
- No confidence percentages; show the evidence strength in words.
- Student- or partner-confirmed criteria are counted and labelled separately.
