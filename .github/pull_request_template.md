## SafeAd Dataset Contribution Pull Request

### Contributor Information
- **Contributor**: Sourav (`@RDSOURAV05`)
- **Assigned Categories**: `SAFE_FOR_ALL`, `SAFE_14_PLUS`
- **Contribution Branch**: `feature/sourav-safe-for-all-14-plus`
- **Target Branch**: `main`

### Summary of Changes
- Added initial batch of custom advertisement samples to `manifests/sourav/contribution_manifest.json`.
- Established baseline schema (`schemas/sample_schema.json`), annotation policy (`ANNOTATION_POLICY.md`), and validation tools (`tools/ad_collector.py`, `tools/validate_manifest.py`).
- Integrated automated tests in `tests/test_collection_tools.py`.

### Sample Metrics
- **Total Samples Contributed**: 21
- **SAFE_FOR_ALL**: 11 (8 images, 3 videos)
- **SAFE_14_PLUS**: 10 (8 images, 2 videos)
- **Review Status**: 19 `PROPOSED`, 2 `NEEDS_REVIEW`
- **Duplicates**: 0 exact duplicates (SHA-256 verified)

### Pre-Submission Checklist
- [x] No binary media files (`.jpg`, `.png`, `.mp4`, etc.) are tracked in Git.
- [x] Contribution is strictly restricted to `manifests/sourav/contribution_manifest.json`.
- [x] Coordinator's public benchmark manifest and Juwel's manifest are untouched.
- [x] All records have valid SHA-256 checksums, relative paths, and permitted licenses.
- [x] All unit tests pass (`python -m unittest discover tests`).
- [x] Manifest validation passes (`python tools/validate_manifest.py manifests/sourav/contribution_manifest.json`).

### Samples Requiring Review
- `SAFEAD_SOURAV_S14P_IMG_007`: Rapid weight-loss dietary supplement ad (Borderline deceptive claims).
- `SAFEAD_SOURAV_S14P_IMG_008`: Casual dating app ad (Borderline 14+ vs 18+ policy boundary).
