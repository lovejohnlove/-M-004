# Validation Authorization — One-Page Sign-Off (Draft)

**Repository:** `lovejohnlove/-M-004`
**Review base:** `main` at `d4ae3b2ff8e0b8546d0ed5381cbe47c34d114ec3`
**Reviewer:** ______________________________  **Date:** __________________

## Byte-state record

The recorded values below were checked against the local files and repository records.

- `experiments/004c/code/diff_004c_REBUILD-1.py` — SHA-256 `05c787f759259e2bf96822575940a2f090e775d8eeb6e4666c66648192e6fc11`; 7,220 bytes; 188 LF-terminated lines.
- `experiments/004c/code/aggregate_004c_REBUILD-1.py` — SHA-256 `81170771423418c471c2c33990000f18490bbfd004d2557600401fa9a0b4c45c`; 10,404 bytes; 250 LF-terminated lines.
- `experiments/004c/code/server_004c_FINAL_REBUILD-1.py` — SHA-256 `57113d646488c1cefc36f4a45d9ba3fec208659253af5229f489b99a13478eda`; 14,546 bytes; 243 LF-terminated lines.
- `experiments/004c/code/generator_004c_FINAL_REBUILD-1.py` — SHA-256 `f722de8b46cb90b448de8f4ee4ad131e7f6930ac2c6fab5f9f768a4c6f95fc9c`; 20,536 bytes; 319 LF-terminated lines.

## Checks performed in this preparation

- [x] Each file's SHA-256, byte count, and LF-terminated line count match the recorded values.
- [x] `cmp` confirmed each `code/` file is byte-identical to its corresponding `unsealed/REBUILD-1/` copy.
- [x] README, preregistration status, proposed sealed-status, and preservation-only notes reviewed.

## Status and limits

**SEAL STATUS: BYTE-STATE SEALED.** This status applies only to the four hash-identified local byte-states above. The owner approved this limited wording; it is not reviewer approval or a claim of provenance.

**Preregistration:** unresolved. The authoritative preregistration and verbatim §1 are not present in the status record; §12 requirements/results remain unresolved. The environment/run is recorded as blocked, and no experiment was executed.

No syntax, functional, synthetic, runtime, performance, concurrency, or reproducibility tests were performed for this sign-off. Runtime correctness, performance, concurrency, provenance, preregistration compliance, and any §12 result remain unverified.

**Documentation conflict for reviewer:** `experiments/004c/sealed/README-STATUS-PROPOSED.md` says no sealed code artifact is present, while `experiments/004c/unsealed/REBUILD-1/README-PRESERVATION-ONLY.md` says the files are not sealed. Those notes are unchanged by this proposal; reconcile the wording before treating the repository documentation as consistent.

## Reviewer determination

☐ PASS (limited claims only)  ☐ HOLD  ☐ FAIL

**Reviewer identity:** ______________________________  **Approval:** ______________________________

**Signature:** ______________________________________  **Date:** __________________
