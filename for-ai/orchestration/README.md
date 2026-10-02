# Internal analysis orchestration

Keep exploratory models, checks, and candidate figures here until their questions, cohort, estimands, and reporting choices are reviewed. Promote only approved, reproducible code to `../../analysis/`, final figures to `../../figures/`, and final statistical outputs to `../../results/`. The older exploratory scripts still live in the source scaffold and are not part of this release candidate.

`public_data.py` rebuilds the two public-data CSVs from an already deidentified export supplied at run time. It never stores an identity crosswalk or a source path. From the repository root:

```powershell
py for-ai/orchestration/public_data.py build <deidentified-export-folder> data/raw
py for-ai/orchestration/public_data.py check data/raw
```
