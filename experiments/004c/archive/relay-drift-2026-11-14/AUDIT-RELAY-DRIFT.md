# Relay Drift Audit — 004c

**Disposition: preservation only.** The two selected relay files were copied byte-for-byte from the specified measured inputs. They are not sealed, not console-direct verified, and not to be run as the 004c pipeline. This audit records measured facts separately from historical claims and owner-supplied corrections.

## Selected relay files: claims versus measurements

The claimed values below are historical claims recorded in the existing repository manifest; the claimed source artifacts are not present here for verification. “Delta” is measured relay value minus claimed value. Line counts use LF-terminated lines (`wc -l`).

| File | Historical claimed SHA-256 | Claimed bytes / lines | Selected measured SHA-256 | Measured bytes / lines | Delta (bytes / lines) | Status |
|---|---|---:|---|---:|---:|---|
| `server_004c_FINAL_v1_6_2_RELAY-DRIFT-UNVERIFIED.py` | `afe84dc1ad9630fafad2e2923ddb8f5ceb5e1eac9371605e28993bf785703ee6` | 14,415 / 242 | `a0886b4c70f0648da67beccf373e9bb9bc8e5a8ed5fd9183a11f4ac078066803` | 14,135 / 240 | -280 / -2 | Measured relay copy does not match historical claim. |
| `generator_004c_FINAL_v1_6_2_RELAY-DRIFT-UNVERIFIED.py` | `c24f15e655bfb7b16dc84c72198489c81fdb02005d0e5a39e7bdd61660602ec5` | 20,419 / 317 | `7f3f99d6fa7678bbce694e02465fef078b2bfbaea52c92bc136bf952d5274ded` | 20,235 / 318 | -184 / +1 | Measured relay copy does not match historical claim. |

The full claimed hashes, sizes, and line counts above are copied from the pre-existing root manifest as claims only. No claim has been upgraded to verified status.

## Generator structural finding

### Directly observed in the selected relay source

- In the archived generator copy, module-scope `measurement_failure = False` appears at line 40.
- `run_trial(...)` begins at line 156. There is no `measurement_failure = False` reset inside that function.
- This is structural, not cosmetic drift. As diagnosed by Q’s measurement, without the per-trial reset a failure can leak into subsequent trials, falsely leaving them marked `MEASUREMENT_FAILURE`. The earlier phrase “cause not fully diagnosed” is withdrawn.

### Separate chat-copy state; not substituted

The two observed chat files `Pasted_content_30.txt` and `Pasted_content_31.txt` have identical SHA-256 `a89f3f48aa6ffaa51d493a7b6483c02348d5c1eb34fdd4c2bcb95d6d2efc5e6b`, 20,418 bytes, and 316 LF-terminated lines. That distinct state has the module-scope assignment at line 38, `run_trial(...)` at line 154, and a per-trial reset at line 156. This matches the corrected structural distinction, but the chat-copy hash does not establish console-direct provenance or a seal. It is not the archive source and was not substituted for the selected 20,235-byte relay copy.

## Other measured relay variants

| Input state | SHA-256 | Bytes / LF lines | Finding and disposition |
|---|---|---:|---|
| `Pasted_content_29.txt` (selected server source) | `a0886b4c70f0648da67beccf373e9bb9bc8e5a8ed5fd9183a11f4ac078066803` | 14,135 / 240 | Selected and copied byte-for-byte. |
| `Pasted_content_37.txt` (server alternate) | `8076a9c3cdd1187441b27ea62ba1ae09eaf6e1828fda37d7e9fdb91b92331132` | 14,134 / 239 | Excluded: missing final LF; different hash and byte state. |
| `Pasted_content_33.txt` (selected generator source) | `7f3f99d6fa7678bbce694e02465fef078b2bfbaea52c92bc136bf952d5274ded` | 20,235 / 318 | Selected and copied byte-for-byte. |
| `Pasted_content_32.txt`, `Pasted_content_34.txt` | `7f3f99d6fa7678bbce694e02465fef078b2bfbaea52c92bc136bf952d5274ded` | 20,235 / 318 | Exact byte-identical copies of the selected generator state. |
| `Pasted_content_30.txt`, `Pasted_content_31.txt` | `a89f3f48aa6ffaa51d493a7b6483c02348d5c1eb34fdd4c2bcb95d6d2efc5e6b` | 20,418 / 316 | Distinct chat state with per-trial reset; documented, not substituted. |
| `Pasted_content_36.txt` | `683a727c2092929b7504b80bc714405b42471b0f55233893ceee91b26596a409` | 20,234 / 317 | Excluded: missing final LF; distinct byte state. |
| `Pasted_content_35.txt` | `fa3ac04a2dae2958e272cfcf5342aa331cad630dbb05f5a9ee505cd13a126b47` | 7,469 / 105 | Excerpt only, not a whole generator file; excluded. |

The selected source choices follow the handoff instructions: server `Pasted_content_29.txt` and generator `Pasted_content_33.txt`. The alternate inputs above were not used to create the archived source files.

## REBUILD-1 preservation inventory

All four source files under `code/` were copied byte-for-byte into `unsealed/REBUILD-1/`. The actual SHA-256, size, and line counts match the existing `docs/EXECUTION_REPORT_template.md` entries:

| File | SHA-256 | Bytes | LF lines | Preservation status |
|---|---|---:|---:|---|
| `server_004c_FINAL_REBUILD-1.py` | `57113d646488c1cefc36f4a45d9ba3fec208659253af5229f489b99a13478eda` | 14,546 | 243 | Preserved only; not sealed or console-direct verified. |
| `generator_004c_FINAL_REBUILD-1.py` | `f722de8b46cb90b448de8f4ee4ad131e7f6930ac2c6fab5f9f768a4c6f95fc9c` | 20,536 | 319 | Preserved only; not sealed or console-direct verified. |
| `aggregate_004c_REBUILD-1.py` | `81170771423418c471c2c33990000f18490bbfd004d2557600401fa9a0b4c45c` | 10,404 | 250 | Preserved only; not sealed or console-direct verified. |
| `diff_004c_REBUILD-1.py` | `05c787f759259e2bf96822575940a2f090e775d8eeb6e4666c66648192e6fc11` | 7,220 | 188 | Preserved only; not sealed or console-direct verified. |

A hash match to the report template confirms the copied bytes match the locally present files and the template entries; it does not prove a console-direct read, a seal, execution, or the authority of a missing preregistration source. The stated rebuild basis is v1.0.8 (v1.0.7 is superseded; v1.0.8 includes the `n_trials` Table A fix). The existing known-issue record contains 9 items: 7 code and 2 non-code.

## Explicit present / missing inventory

**Present:** the two selected relay source copies and this audit/README; all four original REBUILD-1 files under `code/` and byte-identical preservation copies under `unsealed/REBUILD-1/`; the report template and 9-item known-issue list.

**Missing or unresolved:** the historical claimed server/generator source artifacts are not available for direct verification; the full authoritative v1.6.1/v1.6.2 preregistration base and verbatim §1 text are missing; no console-direct verified artifact is present in `sealed/`; VM status remains **BLOCKED — VM REPORTED, NOT VERIFIED**. No §1 text was inferred, and no canonical preregistration was reconstructed from the Word bundle.

The archive and REBUILD-1 preservation can exist while §1 remains unresolved. No project code was run or tested. No commit or push was made.

