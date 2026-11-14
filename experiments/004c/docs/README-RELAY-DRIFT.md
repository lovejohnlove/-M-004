# Relay Drift — Unverified Artifacts

**These files are NOT the sealed pipeline. Do not run them as 004c.**

## What happened

The four files in this folder arrived via paste/relay through a chat channel, not via console-direct read from the machine that produced them. They do not match the hashes claimed for the original artifacts.

## Measured vs claimed

| File | Claimed sha256 | Claimed size | Measured sha256 | Measured size |
|---|---|---|---|---|
| `server_004c_FINAL_v1_6_2.py` | `afe84dc1...` | 14,415 | `a0886b4c...` | 14,135 |
| `generator_004c_FINAL_v1_6_2.py` | `c24f15e6...` | 20,419 | `7f3f99d6...` | 20,235 |

The relayed copies are close in content but not byte-identical. Missing lines, differing whitespace, or truncated sections — the cause is not fully diagnosed.

## Status

- **CODE_ARTIFACTS: CLAIMED PENDING RECOVERY** — hashes recorded, artifacts unavailable, current files do not match
- **RELAY_CHANNEL_INTEGRITY: NOT VERIFIED** — relayed four-command reads are claims, not verifications

## What replaced them

The four `_REBUILD-1` files are a fresh build against the authoritative v1.6.2 prereg and v1.0.8 design-spec, sealed by console-direct four-command read:

| File | sha256 |
|---|---|
| `server_004c_FINAL_REBUILD-1.py` | `57113d64...` |
| `generator_004c_FINAL_REBUILD-1.py` | `f722de8b...` |
| `aggregate_004c_REBUILD-1.py` | `81170771...` |
| `diff_004c_REBUILD-1.py` | `05c787f7...` |

The REBUILD-1 hashes are the current artifacts. The files in *this* folder are preserved as the record of what the relay channel produced and what the drift cost.

## Do not

- Do not run files in this folder as the sealed pipeline
- Do not treat the claimed hashes as verified
- Do not edit these files to make them match the old hashes

If you want to understand the pipeline, read the REBUILD-1 files. If you want to understand the failure, read this folder.
