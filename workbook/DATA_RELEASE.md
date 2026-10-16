# Deidentified data release

On 2026-10-15 the project owner instructed publication of the participant data
after name removal and backup, and confirmed that the study already has ethical
approval. This records the owner's release instruction; the workbook does not
generate or independently certify an ethics approval document.

The supplied exports already contain arbitrary contiguous P000–P041 IDs and no
name fields. The field audit checked the exact schema, keys, known source-code
and acquisition-path patterns, categorical values, and numerical questionnaire
fields. Participant-level fields contain age, categorical gender/handedness and
condition order, availability, ratings, and MAIA responses/scores. No original
identity crosswalk, collection dates, acquisition paths, or recordings are in
the published files. Deidentification is described precisely; no claim of
zero reidentification risk is made.

Before creating the public artifact, byte-identical copies of both received CSVs
were backed up outside the repository and published-site tree in a private
directory. Each backup was verified against the source SHA-256 and a private
checksum manifest. The audited export files remain intact in this repository.
The owner separately authorised public repository visibility on 2026-10-16;
see D-0011 in `../for-ai/DECISIONS.md`. The backup and any identity records remain
outside the repository and deployment.

Released source hashes:

| File | SHA-256 |
| --- | --- |
| study5_participants.csv | 5f4aac1802f86ec8945a2676c47299b18c5e1e5bb2fdd0edb9cbdcbd79022b6d |
| study5_pps_trials.csv | 45e53d49c436474df7c9674b54fb796e3fd95ed641a6b71e807ff3ca32e25d1d |

The build copies only these allowlisted deidentified exports into the site's
public data directory. It checks their schemas and identities before copying
and verifies destination hashes. Unrecognized files, backup directories and
notebook execution caches must not enter the artifact. A new data refresh
requires repeating the audit and backup before replacing the release.
