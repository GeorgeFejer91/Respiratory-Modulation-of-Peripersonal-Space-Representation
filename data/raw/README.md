# Deidentified behavioral observations

This folder contains one participant table and one primary trial table for 42 independent people. IDs run contiguously from `P000` to `P041` and are arbitrary; they encode no collection order or original source. Join the files on `participant_id`.

- `study5_participants.csv`: one row per person. It holds data availability, demographics, condition order, pictographic ratings, MAIA-2 item responses, and scored subscales. One PPS-only person has blank questionnaire fields; blank means unavailable, not zero.
- `study5_pps_trials.csv`: 17,114 retained primary-analysis trial rows. Each row has a unique `trial_id` in the form `P000_T0001`, planned position and design variables, response outcome, recorded reaction time, and two documented RT-window flags. Blank reaction times are missing observations.

These files are deidentified trial-level behavioral data from the cleared publication cohort. They are not the complete acquisition archive: original recordings, review cases, restarts, a secondary repeat session, provenance records, private identifiers, and collection dates are excluded. The exported values retain recorded responses; the trial rows have already passed the cohort and primary-analysis selection.

MAIA-2 item responses use the administered 0-5 scale; subscale means reflect reverse scoring where applicable. SpFrRef letters A-H are also encoded as 1-8. The stored RT-window flags support exploratory views. The fixed paper analysis
uses its documented participant-wide trim; it does not silently add these flags.

The project owner authorised public release after name removal and a verified
separate backup, and confirmed existing ethical approval. See
[the release record](../../workbook/DATA_RELEASE.md) for the exact field audit and
source hashes. The source repository stays private; the audited CSV pair is included
in the public companion artifact.
