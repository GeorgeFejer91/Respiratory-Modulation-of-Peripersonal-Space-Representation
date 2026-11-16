# Gaussian center and exponential tail sensitivity

This exploratory model describes the distribution of retained positive
audio–tactile hit latencies over the five registered probes from
10 to 100 cm. Its two shape variants place a sigmoid in the
Gaussian center or in the log mean of an additive exponential
tail. Each participant shares a Gaussian SD across phases,
conditions and probes. The analysis uses 8,478 latencies from 40
participants and conditions on the existing trial selection.
[Specification](EXPONENTIAL_TAIL_SPECIFICATION.md)

## Observed-data fits

The tail shape passed the diagnostic extension with zero
divergences, maximum midpoint R-hat 1.00436, minimum midpoint bulk
ESS 1,330 and minimum midpoint tail ESS 2,110. The full-data center
shape exhausted its extension with midpoint R-hat 1.01139, above
the declared 1.01 limit. Its shape estimates remain numerically
unresolved.

The qualified tail model's population condition estimate was
+1.46 cm (95% credible interval −62.68 to +64.97 cm). The table
shows contrasts after averaging latent midpoint differences
across the 40 sampled participants. For each contrast, positive
values denote Viscereality minus Control, inhale minus exhale, or
the difference of the two phase effects in that condition order.

| Paired latent midpoint contrast | Median (cm) | 95% credible interval (cm) |
| --- | ---: | ---: |
| Condition, averaging both phases | +1.48 | [−62.77, +64.95] |
| Phase, averaging both conditions | −2.81 | [−77.27, +63.87] |
| Condition × Phase | −9.65 | [−89.28, +69.22] |
| Phase within Control | +2.53 | [−84.97, +77.36] |
| Phase within Viscereality | −8.17 | [−89.74, +70.83] |
| Condition within exhale | +7.05 | [−62.28, +72.28] |
| Condition within inhale | −3.46 | [−86.21, +79.91] |

The fraction of latent midpoint draws within the sampled range
rose from 52.3% under the prior to 62.4% in the posterior. The
shared sigmoid width was 34.01 cm (95% credible interval 15.58
to 60.93 cm). None of the 160 participant phase-cell midpoint
intervals fit inside the sampled range. Even the shortest spanned
97.18 cm. One participant phase cell's unadjusted tail span
interval excluded zero. Its midpoint interval extended beyond the
sampled range.
Each of the four group-average tail mean changes from 10 to 100 cm
had an interval including zero. These quantities describe a
distribution component under the fitted model. Averaging latent
midpoints leaves the location of the aggregate RT curve unresolved.

## Matched-design recovery

The flat and shifted-tail simulations each used the observed trial
counts. Both fits passed the diagnostic gate. In the flat example,
all four group-average tail spans and all seven paired midpoint
contrasts had intervals including zero. No participant midpoint
interval fit inside the sampled range. In the shifted example, the
participant midpoint RMSE was 5.18 cm. All 160 intervals contained
their planted locations, and 26 cells also had a tail span interval
excluding zero. All four group-average span intervals excluded
zero. The fitted +10 cm planted condition contrast was +14.97 cm
(95% credible interval −2.26 to +31.35 cm). Each generator was run
once, so these results show recovery behavior for two simulated
datasets. They do not estimate repeated-sampling coverage.

## Held-probe prediction

The score is the held participant-by-cell block log predictive
density per trial, pooled across probes by the retained trial counts.
The five held sets contain 1,699, 1,694, 1,710, 1,691 and 1,684
latencies. The folds reuse participants and share training data.

| Model | 10 cm | 27 cm | 50 cm | 73 cm | 100 cm | All five probes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Flat | 0.90988 | 0.88272 | 0.90642 | 0.91527 | 0.85339 | 0.89361 |
| Linear tail | 0.91231 | 0.87921 | 0.90618 | 0.91471 | 0.85203 | 0.89297 |
| Tail boundary | 0.91320 | 0.88239 | 0.90664 | 0.91581 | 0.85736 | 0.89515 |
| Center boundary | 0.91308 | 0.88548 | Diagnostic failure | 0.91785 | 0.86276 | — |

The tail model qualified at all five probes. Its aggregate score
exceeds the matched flat reference by 0.00154 log units per trial.
Four folds had a higher score for the tail shape. The small
predictive gain accompanies wide component-location intervals in
the full-data fit. The center model's 50 cm refit exhausted
its planned extension with midpoint R-hat 1.60163, minimum
bulk ESS 6.72, minimum tail ESS 4.65, and zero divergences.
Its five-probe score is unavailable. The [frozen fit inventory](exponential_tail_inventory.json)
contains 36 full-budget attempts, including 26 initial fits and
10 extensions. It retains both center-model failures after
extension, for the full-data fit and the 50 cm held refit.

## Sampler source provenance

Each full-budget attempt records the SHA-256 of its sampler source.
The public results branch preserves the three corresponding source
versions in its Git history. The grouped implementation was checked
against the earlier trial-wise likelihood and gradient.
[Implementation checks](EXPONENTIAL_TAIL_SPECIFICATION.md#implementation-record)

| Sampler source | Git revision | SHA-256 recorded in fit receipts |
| --- | --- | --- |
| Initial trial-wise sampler | `50399724dab1d92b541b256e58478e34a481ee29` | `e7d0c618900d5e975750d249af99aa30366cc2f2e923d303cf1340af187ab9b8` |
| Trial-wise sampler with receipt metadata | `678ef15b5ab3786be7d2f151d06ae405f4ae163b` | `97295cd6bb4f4146701bc9c617d43f762ca24bedcc3b2bc8815b8fa21346b4b1` |
| Grouped sampler | `ffac7b1c52f242cb515daf8d5910ae57ada78c11` | `f81c8dd3c0a0db37626e3ffba50b7f9b57961cba4417af6b30e103f2ec0643ed` |

The preliminary short pilot has its own receipt. Its exact source
version was unavailable in Git history. The pilot is excluded from
the fit comparisons.

The [sampler](../../analysis/boundary_methods/exponential_tail.py)
and [reporting script](../../analysis/boundary_methods/exponential_tail_report.py)
can regenerate the fit inventory from the declared receipt grid in the
[pinned native environment](../../analysis/baseline_effects/requirements.txt).
