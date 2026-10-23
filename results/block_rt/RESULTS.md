# Does baseline-corrected RT decline across blocks?

**The analysis does not establish a systematic corrected-RT decline across the session.**

Exploratory native analysis of baseline-corrected RT (AT − Baseline); original cleaning and primary40. Both conditions occurred consecutively.

N = 39 participants, 8280 retained AT trials. Incomplete-block exclusions: ['P008'].

![Participant RT trajectories across 12 chronological blocks: blue solid Control segments, red dashed Viscereality segments, and black overall means](block_rt.png)

Blue solid lines are corrected participant block means during Control; red dashed lines show Viscereality. Subtract each trial's retained participant × condition × phase baseline mean (baseline SOAs pooled), then aggregate within person/block. Each person's segments stop at the switch between blocks 6/7. Black points are equal-person means with pointwise marginal 95% t CIs, not paired-change CIs. The vertical dotted line marks the switch. No smoothing or normalization. Negative values and an explicit zero reference are retained. Raw block means and matched baseline contributions remain in participant_blocks.csv; the complete raw three-test family is labelled raw_reference in results.json. This baseline-correction amendment supersedes the earlier raw primary result.

| Test | Mean coefficient | 95% t CI | t(38) | Two-sided p | dz | Bootstrap 95% CI |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| linear_ms_per_block | -0.120 | [-1.321, 1.081] | -0.203 | 0.840249 | -0.032 | [-1.298, 1.038] |
| quadratic_ms_per_block_squared | 0.081 | [-0.527, 0.689] | 0.271 | 0.787984 | 0.043 | [-0.566, 0.586] |
| condition_adjusted_ms_per_block | -0.077 | [-2.892, 2.738] | -0.055 | 0.956358 | -0.009 | [-2.784, 2.624] |

Paired block 12 minus block 1: -15.36 ms, 95% CI [-39.37, 8.65]. No separate endpoint p test.

Negative linear coefficients indicate speeding; positive indicate slowing. Quadratic coefficients are in ms/block² and describe curvature, not a monotonic decrease. The condition-adjusted coefficient estimates within-condition change assuming a shared linear slope and a level shift at the switch. Unadjusted exploratory p values for the full three-test family follow the owner's policy; all CIs are pointwise.

## Block means

| Block | Mean ms | SD ms | n | 95% CI ms |
| --- | ---: | ---: | ---: | --- |
| 1 | -13.49 | 74.01 | 39 | [-37.48, 10.50] |
| 2 | -22.81 | 37.96 | 39 | [-35.12, -10.51] |
| 3 | -20.27 | 34.72 | 39 | [-31.52, -9.01] |
| 4 | -8.99 | 46.77 | 39 | [-24.15, 6.17] |
| 5 | -20.49 | 43.81 | 39 | [-34.69, -6.29] |
| 6 | -27.75 | 55.54 | 39 | [-45.75, -9.75] |
| 7 | -39.58 | 49.41 | 39 | [-55.60, -23.56] |
| 8 | -16.20 | 52.57 | 39 | [-33.24, 0.84] |
| 9 | -7.99 | 42.34 | 39 | [-21.72, 5.73] |
| 10 | -7.76 | 40.39 | 39 | [-20.85, 5.34] |
| 11 | -18.26 | 43.92 | 39 | [-32.50, -4.02] |
| 12 | -28.85 | 42.91 | 39 | [-42.76, -14.94] |

The descriptive table above uses the same 39 complete participants at every block. To retain every available person, available_primary40_summary.csv separately includes all 40 primary participants wherever observed (n=39 at block 7, n=40 otherwise). This descriptive companion was added after observing the missing block; the inferential specification was unchanged.

## Sensitivities and limits

- Excluding ['P011']: n=40, linear slope 0.056 ms/block, 95% CI [-1.167, 1.279], p=0.926469. All three tests are retained in results.json.
- Excluding ['P033']: n=40, linear slope 0.056 ms/block, 95% CI [-1.167, 1.279], p=0.926469. All three tests are retained in results.json.

P008 has no retained AT responses in chronological block 7 (18 misses and two hits with missing RT) and is excluded only from complete-block inference; their other block means remain in participant_blocks.csv and the available40 table. P016 has a partial recorded session but usable RTs in every block and is retained. Complete-case inference does not correct informative missing responses or misses. Full42 descriptive means are in results.json; it is not 42 independent recordings. Original participant/trial exclusions and missingness counts are preserved there. Pooling retained trials can reflect changing phase/SOA composition; condition order, practice, carryover and fatigue are not causally separated. Block number is not elapsed time. These results concern overall RT, not a drift-diffusion parameter or a PPS boundary.

All three participant-coefficient Q–Q plots are in diagnostics.png. Quadratic coefficients retain a strong lower-tail outlier (Shapiro p < .001), making that t approximation particularly uncertain. All corrected coefficient bootstrap intervals include zero. Shapiro p values, leave-one-out mean ranges and fixed-seed whole-person bootstrap CIs are retained in results.json. Whole-person resampling preserves each participant's jointly estimated baseline contribution and block covariance; no extra trial-level baseline refit is claimed. Normality screens do not establish independence or justify post hoc cleaning. No diagnostic-driven method switch. Specifications, code/data/output hashes and runtime versions accompany the results.

Reproduce: `.venv/Scripts/python.exe for-ai/orchestration/block_rt.py`; independently verify: add `--check`. Native saved outputs are displayed in Segment 3; the historical manuscript is unchanged.
