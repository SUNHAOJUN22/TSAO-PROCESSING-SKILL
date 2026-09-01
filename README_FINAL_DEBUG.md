# TSAO-PROCESSING-SKILL — Final Debug Closure

## Code changes

The public-distribution policy now has one production implementation:

```text
tsao.distribution_policy
├── audit_public_distribution(...)
├── assert_public_distribution_allowed(...)
├── evaluate_public_distribution(...)
└── public_distribution_policy_main(...)
```

`scripts/check_public_distribution_policy.py` is a compatibility adapter only. It contains no independent JSON parser, classification vocabulary, digest logic, decision parser or release verdict.

## Regression contract

```bash
python -m pytest -q -p no:cacheprovider \
  tests/test_distribution_containment_v20.py \
  tests/test_distribution_policy_single_source.py \
  tests/test_release_integrity_alpha6.py \
  tests/test_main_only_ci_policy.py \
  tests/test_public_distribution_boundary_workflow.py
python scripts/run_ci.py
```

The single-source regression proves that the compatibility CLI delegates to the canonical evaluator and that controlled records still block every requested public surface.

## Distribution boundary

```text
PUBLIC_WHEEL            = BLOCKED_CONTROLLED_METADATA_CLASSIFICATION
PUBLIC_SDIST            = BLOCKED_CONTROLLED_METADATA_CLASSIFICATION
PUBLIC_SOURCE_SNAPSHOT  = BLOCKED_CONTROLLED_METADATA_CLASSIFICATION
```

This is an intentional fail-closed result while tracked registry records remain classified as controlled. Software qualification does not reclassify source metadata and does not establish scientific, engineering, HSE, customer, legal or industrial approval.
