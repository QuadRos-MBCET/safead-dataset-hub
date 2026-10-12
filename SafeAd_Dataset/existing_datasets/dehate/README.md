# DeHate Video Dataset

- **Identifier**: `dehate`
- **Source**: [https://github.com/Multimodal-Intelligence-Lab-MIL/DeHate](https://github.com/Multimodal-Intelligence-Lab-MIL/DeHate)
- **Paper**: "DeHate: A Holistic Hateful Video Dataset for Explicit and Implicit Hate Detection", ACM MM 2025
- **Modality**: Video + Audio + Text (Short-form videos from TikTok and BitChute)
- **Verified License**: Academic Research Only (Ethics Statement; strictly non-commercial)

## Labels & SafeAd Mapping Policy
- `Hate (Explicit)` -> `UNSAFE_FOR_ALL` (Violates platform video safety policies).
- `Hate (Implicit)` -> `UNSAFE_FOR_ALL` (Flagged for implicit hostility / slurs).
- `Non-Hate` -> `UNASSIGNED` (Social media video clips preserved for video guardrail temporal segmentation benchmark; not assumed to be safe commercial ads).

## Acquisition
- Metadata table `DeHate.xlsx` (6,689 video entries) is open on GitHub.
- Video downloads require platform tools or author access.
