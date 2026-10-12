# SafeAd AI / SAFE-VISION Annotation Policy & Guidelines

This document specifies the shared annotation standard for labeling advertisement examples in the SafeAd AI dataset.

## Label Taxonomy

All advertisement samples must be labeled with exactly one of the four core classes, or flagged for further review:

### 1. `SAFE_FOR_ALL`
- **Audience**: General audiences of all ages, including young children.
- **Criteria**:
  - Wholesome, non-offensive creative presentation.
  - Zero depictions or references to violence, weapons, gore, or physical threats.
  - Zero sexualized imagery, nudity, suggestive postures, or double entendres.
  - Zero tobacco, alcohol, pharmaceuticals, or controlled substances.
  - Zero gambling, betting, get-rich-quick, or predatory financial claims.
  - Clear, non-deceptive disclosures.
- **Examples**: Family food & beverage products, educational apps, toys, family electronics, hygiene & everyday household goods.

### 2. `SAFE_14_PLUS`
- **Audience**: Adolescents aged 14 and above and adults.
- **Criteria**:
  - Mild fantasy or stylized action violence (e.g. superhero games, action film trailers) without graphic gore.
  - Mild suggestive themes, dating services for general audiences, cosmetic / fashion advertising with modest swimwear or activewear.
  - Intense humor, mild profanity, or spooky/thriller themes not suitable for young children.
  - No adult products (alcohol, tobacco, regulated gambling, explicit adult products).
- **Examples**: PG-13 style mobile games, teen apparel, fitness supplements, horror/action entertainment trailers.

### 3. `SAFE_18_PLUS`
- **Audience**: Verified legal adults (18+).
- **Criteria**:
  - Regulated adult products and services: alcoholic beverages, regulated sportsbooks/casinos, adult nightlife, mature dating apps, age-restricted gaming (ESRB M/18+).
  - Must still adhere to regulatory standards (no promotions targeting minors, clear legal disclaimers).
- **Note**: Handled by Juwel.

### 4. `UNSAFE_FOR_ALL`
- **Audience**: Prohibited across all ad platforms.
- **Criteria**:
  - Explicit sexual content, pornography, illegal drugs, severe gore/violence, hate speech, malware/phishing distribution, fraudulent scams, illegal weapons.
- **Note**: Handled by Juwel.

### 5. `UNASSIGNED` (Component Research Only)
- **Audience**: Submodule benchmarking and algorithmic calibration.
- **Criteria**:
  - Samples from pre-existing public and research datasets (e.g., UTKFace/FairFace facial age crops, text-only comments, benign control memes) that serve component-level research rather than commercial advertising.
  - Prevents forcing non-ad or ambiguous research samples into commercial ad publishing categories without defensible justification.
- **Note**: Maintained by Project Coordinator / Member 1 under `manifests/coordinator/public_datasets.json`.

---

## Evaluation Workflow & Review States

### Review Status
- `PROPOSED`: Assigned by sample collectors (Sourav / Juwel) during initial ingestion.
- `NEEDS_REVIEW`: Flagged whenever an ad has borderline attributes, dual-meaning text, ambiguous claims, or unconfirmed licensing.
- `ACCEPTED`: Marked only by the Project Coordinator after secondary review.
- `REJECTED`: Sample rejected due to policy breach, corrupted media, or unacceptable licensing.

### Holistic Context Inspection
Do not evaluate images or video frames in isolation:
1. **Text & Copy**: Inspect headlines, disclaimers, slogans, and overlay text.
2. **Imagery & Visuals**: Examine backgrounds, costumes, gestures, and visual metaphors.
3. **Claims & Intent**: Detect deceptive clickbait, hyperbolic health guarantees, or counterfeit promotions.
4. **License & Provenance**: Only collect samples with documented legal permission, CC-licensing, or authorized public fair-use research status.
