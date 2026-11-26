# Validation

## Gates
| Gate | When | Pass condition |
| --- | --- | --- |
| 1 | End of Experiment 1 | One pipeline and camera position meets every threshold below on at least 6 of 8 manoeuvres |
| 2 | Before any outside user | Auto-assessed criteria pass Gate 1 thresholds on a held-out set; said-only false credit ≤ 10%; upload success ≥ 95% on the device matrix; 95% of reports within 10 minutes |
| 3 | End of pilot | AI–examiner agreement ≥ examiner–examiner agreement on auto-assessed criteria |

## Experiment 1 thresholds
| Measure | Pass | Fail |
| --- | --- | --- |
| Silent manoeuvres detected (C2) | ≥ 85% | < 70% |
| False credit for said-only (C3) | ≤ 10% | > 25% |
| Correct side and zones | ≥ 90% | < 80% |
| Timestamp within ±3 s | ≥ 90% | < 75% |
| "Insufficient evidence" when blocked (C6) | ≥ 70% | < 40% |
| Same answer on 3 repeat runs | ≥ 90% | < 80% |

## Clinical validation (pilot)
40 to 60 full-station recordings, each double-marked independently by experienced examiners. Report per-criterion Cohen's κ and Gwet's AC1, ICC and Bland–Altman for total scores, and human–human agreement as the benchmark. Get ethics approval before collecting, if results are to be published.

## Results log
| Date | Experiment | Pipeline / model / prompt | Result |
| --- | --- | --- | --- |
