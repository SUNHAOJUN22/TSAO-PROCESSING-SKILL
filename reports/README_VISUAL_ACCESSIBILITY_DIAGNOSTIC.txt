
== install ==
exit=0

== pip_check ==
No broken requirements found.
exit=0

== compile ==
exit=0

== apply ==
capability visual verification boundary: expected exactly one source anchor, found 0
exit=1

== legacy_base ==
generated 8 README assets in /home/runner/work/TSAO-PROCESSING-SKILL/TSAO-PROCESSING-SKILL/docs/assets/readme
exit=0

== legacy_extended ==
generated 4 extended README assets in /home/runner/work/TSAO-PROCESSING-SKILL/TSAO-PROCESSING-SKILL/docs/assets/readme
exit=0

== legacy_decision ==
generated 4 decision README assets in /home/runner/work/TSAO-PROCESSING-SKILL/TSAO-PROCESSING-SKILL/docs/assets/readme
exit=0

== legacy_performance ==
generated 2 performance README assets in /home/runner/work/TSAO-PROCESSING-SKILL/TSAO-PROCESSING-SKILL/docs/assets/readme
exit=0

== uiux_master ==
generated 18 UI/UX Pro Max-aligned README assets in /home/runner/work/TSAO-PROCESSING-SKILL/TSAO-PROCESSING-SKILL/docs/assets/readme
exit=0

== harden ==
{
  "pass": true,
  "asset_count": 18,
  "changed": [
    "batch-parameter-scan.svg",
    "control-safety-cause-effect.svg",
    "epdm-catalyst-kinetics-network.svg",
    "epdm-identifiability-uncertainty.svg",
    "epdm-multiscale-chain.svg",
    "epdm-process-flowsheet.svg",
    "epdm-product-customer-bridge.svg",
    "epdm-reactor-mode-map.svg",
    "epdm-three-level-models.svg",
    "evidence-gate-system.svg",
    "performance-regression-gate.svg",
    "process-package-architecture.svg",
    "process-package-data-model.svg",
    "recovery-recycle-risk-loop.svg",
    "simulation-integration-contract.svg",
    "tsao-process-intelligence-os.svg",
    "universal-process-package.svg",
    "verification-pipeline.svg"
  ],
  "check_mode": false,
  "root_attributes": {
    "focusable": "false",
    "preserveAspectRatio": "xMidYMid meet",
    "shape-rendering": "geometricPrecision",
    "text-rendering": "optimizeLegibility",
    "data-design-system": "scientific-midnight-bento",
    "data-design-version": "2"
  },
  "errors": []
}
exit=0

== verify ==
{
  "pass": false,
  "design_system": "Scientific Midnight Bento",
  "asset_count": 18,
  "minimum_text_size_px": 12.0,
  "contrast": {
    "primary_text_on_background": {
      "ratio": 18.098,
      "minimum": 4.5,
      "pass": true
    },
    "primary_text_on_surface": {
      "ratio": 15.986,
      "minimum": 4.5,
      "pass": true
    },
    "secondary_text_on_background": {
      "ratio": 9.107,
      "minimum": 3.0,
      "pass": true
    },
    "secondary_text_on_surface": {
      "ratio": 8.044,
      "minimum": 3.0,
      "pass": true
    },
    "connector_text_on_background": {
      "ratio": 4.805,
      "minimum": 3.0,
      "pass": true
    },
    "blue_on_surface": {
      "ratio": 4.508,
      "minimum": 3.0,
      "pass": true
    },
    "cyan_on_surface": {
      "ratio": 9.255,
      "minimum": 3.0,
      "pass": true
    },
    "teal_on_surface": {
      "ratio": 8.985,
      "minimum": 3.0,
      "pass": true
    },
    "green_on_surface": {
      "ratio": 8.7,
      "minimum": 3.0,
      "pass": true
    },
    "amber_on_surface": {
      "ratio": 10.019,
      "minimum": 3.0,
      "pass": true
    },
    "orange_on_surface": {
      "ratio": 7.39,
      "minimum": 3.0,
      "pass": true
    },
    "red_on_surface": {
      "ratio": 6.215,
      "minimum": 3.0,
      "pass": true
    },
    "purple_on_surface": {
      "ratio": 6.146,
      "minimum": 3.0,
      "pass": true
    }
  },
  "forbidden_elements": [
    "a",
    "animate",
    "animateMotion",
    "animateTransform",
    "foreignObject",
    "image",
    "script",
    "set"
  ],
  "errors": [
    "batch-parameter-scan.svg: font-size 11px is below 12px",
    "process-package-data-model.svg: font-size 11px is below 12px",
    "recovery-recycle-risk-loop.svg: font-size 11px is below 12px"
  ],
  "qualification_scope": "README_VISUAL_ACCESSIBILITY_ONLY",
  "scientific_technical_approval": "NOT_EVALUATED",
  "engineering_design_approval": "NOT_EVALUATED",
  "industrial_performance_guarantee": "NOT_EVALUATED"
}
exit=2

== sync ==
Traceback (most recent call last):
  File "/home/runner/work/TSAO-PROCESSING-SKILL/TSAO-PROCESSING-SKILL/scripts/sync_readme_visuals.py", line 119, in <module>
    raise SystemExit(main())
                     ~~~~^^
  File "/home/runner/work/TSAO-PROCESSING-SKILL/TSAO-PROCESSING-SKILL/scripts/sync_readme_visuals.py", line 112, in main
    _sync(ROOT / "README.md", _english, check=args.check),
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/TSAO-PROCESSING-SKILL/TSAO-PROCESSING-SKILL/scripts/sync_readme_visuals.py", line 100, in _sync
    updated = transform(current)
  File "/home/runner/work/TSAO-PROCESSING-SKILL/TSAO-PROCESSING-SKILL/scripts/sync_readme_visuals.py", line 43, in _english
    text = _replace_once(
        text,
    ...<2 lines>...
        label="English generator commands",
    )
  File "/home/runner/work/TSAO-PROCESSING-SKILL/TSAO-PROCESSING-SKILL/scripts/sync_readme_visuals.py", line 14, in _replace_once
    raise ValueError(f"{label}: expected exactly one source anchor")
ValueError: English generator commands: expected exactly one source anchor
exit=1

== sync_check ==
Traceback (most recent call last):
  File "/home/runner/work/TSAO-PROCESSING-SKILL/TSAO-PROCESSING-SKILL/scripts/sync_readme_visuals.py", line 119, in <module>
    raise SystemExit(main())
                     ~~~~^^
  File "/home/runner/work/TSAO-PROCESSING-SKILL/TSAO-PROCESSING-SKILL/scripts/sync_readme_visuals.py", line 112, in main
    _sync(ROOT / "README.md", _english, check=args.check),
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/TSAO-PROCESSING-SKILL/TSAO-PROCESSING-SKILL/scripts/sync_readme_visuals.py", line 100, in _sync
    updated = transform(current)
  File "/home/runner/work/TSAO-PROCESSING-SKILL/TSAO-PROCESSING-SKILL/scripts/sync_readme_visuals.py", line 43, in _english
    text = _replace_once(
        text,
    ...<2 lines>...
        label="English generator commands",
    )
  File "/home/runner/work/TSAO-PROCESSING-SKILL/TSAO-PROCESSING-SKILL/scripts/sync_readme_visuals.py", line 14, in _replace_once
    raise ValueError(f"{label}: expected exactly one source anchor")
ValueError: English generator commands: expected exactly one source anchor
exit=1

== refresh_manifest ==
{
  "version": "0.1.0-alpha.10",
  "profile": "core",
  "pass": true,
  "strict_source_clean": false,
  "checks": {
    "repository": {
      "pass": true,
      "issues": []
    },
    "version": {
      "pass": true,
      "issues": []
    },
    "schemas": {
      "pass": true,
      "issues": []
    },
    "capabilities": {
      "pass": true,
      "issues": []
    },
    "provenance": {
      "pass": true,
      "issues": []
    },
    "release_identity": {
      "pass": true,
      "issues": []
    }
  },
  "issues": [],
  "warnings": [],
  "metrics": {
    "schemas": 9,
    "specialists": 4
  },
  "artifact_software_qualification": "PASS",
  "technical_approval_status": "NOT_EVALUATED",
  "scientific_technical_approval": "NOT_EVALUATED",
  "engineering_design_approval": "NOT_EVALUATED",
  "customer_qualification": "NOT_EVALUATED",
  "industrial_performance_guarantee": "NOT_EVALUATED"
}
exit=0

== targeted ==
.F.......................................                                [100%]
=================================== FAILURES ===================================
__________ test_committed_readme_visuals_pass_accessibility_contract ___________

    def test_committed_readme_visuals_pass_accessibility_contract() -> None:
        result = verify(ROOT / "docs/assets/readme")
>       assert result["pass"] is True, result["errors"]
E       AssertionError: ['batch-parameter-scan.svg: font-size 11px is below 12px', 'process-package-data-model.svg: font-size 11px is below 12px', 'recovery-recycle-risk-loop.svg: font-size 11px is below 12px']
E       assert False is True

tests/test_readme_visual_accessibility.py:32: AssertionError
=========================== short test summary info ============================
FAILED tests/test_readme_visual_accessibility.py::test_committed_readme_visuals_pass_accessibility_contract - AssertionError: ['batch-parameter-scan.svg: font-size 11px is below 12px', 'process-package-data-model.svg: font-size 11px is below 12px', 'recovery-recycle-risk-loop.svg: font-size 11px is below 12px']
assert False is True
exit=1

== ruff ==
I001 [*] Import block is un-sorted or un-formatted
  --> scripts/verify_readme_visual_accessibility.py:16:1
   |
14 |       sys.path.insert(0, str(ROOT))
15 |
16 | / from scripts.generate_uiux_readme_assets import (  # noqa: E402
17 | |     AMBER,
18 | |     ASSETS,
19 | |     BG,
20 | |     BLUE,
21 | |     CYAN,
22 | |     DIM,
23 | |     GREEN,
24 | |     H,
25 | |     MUTED,
26 | |     ORANGE,
27 | |     OUT,
28 | |     PURPLE,
29 | |     RED,
30 | |     SURFACE,
31 | |     TEAL,
32 | |     TEXT,
33 | |     W,
34 | | )
35 | | from scripts.harden_readme_svg_accessibility import ROOT_ATTRIBUTES  # noqa: E402
   | |___________________________________________________________________^
36 |
37 |   SVG_NS = "{http://www.w3.org/2000/svg}"
   |
help: Organize imports
   |
23 |     GREEN,
   -     H,
24 |     MUTED,
--------------------------------------------------------------------------------
31 |     TEXT,
32 +     H,
33 |     W,
   |

Found 1 error.
[*] 1 fixable with the `--fix` option.
exit=1

== run_ci ==
{
  "version": "0.1.0-alpha.10",
  "pass": false,
  "checks": [
    {
      "command": [
        "/opt/hostedtoolcache/Python/3.14.6/x64/bin/python",
        "-m",
        "compileall",
        "-q",
        "-j",
        "0",
        "tsao",
        "scripts",
        "skills"
      ],
      "returncode": 0,
      "timed_out": false,
      "duration_s": 0.7170923409999972,
      "output": ""
    },
    {
      "command": [
        "/opt/hostedtoolcache/Python/3.14.6/x64/bin/python",
        "-m",
        "coverage",
        "erase"
      ],
      "returncode": 0,
      "timed_out": false,
      "duration_s": 0.31481228500000213,
      "output": ""
    },
    {
      "command": [
        "/opt/hostedtoolcache/Python/3.14.6/x64/bin/python",
        "-m",
        "coverage",
        "run",
        "--branch",
        "--source=skills.poe,skills.epdm,tsao.process_package,tsao.skillpacks",
        "--omit=skills/poe/scripts/*,skills/epdm/scripts/*",
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "tests",
        "skills/process-general/tests",
        "skills/epdm/tests",
        "skills/poe/tests",
        "skills/polymer-general/tests"
      ],
      "returncode": 1,
      "timed_out": false,
      "duration_s": 7.6431307500000045,
      "output": "........................................................................ [ 32%]\n........................F............................................... [ 64%]\n........................................................................ [ 96%]\n........                                                                 [100%]\n=================================== FAILURES ===================================\n__________ test_committed_readme_visuals_pass_accessibility_contract ___________\n\n    def test_committed_readme_visuals_pass_accessibility_contract() -> None:\n        result = verify(ROOT / \"docs/assets/readme\")\n>       assert result[\"pass\"] is True, result[\"errors\"]\nE       AssertionError: ['batch-parameter-scan.svg: font-size 11px is below 12px', 'process-package-data-model.svg: font-size 11px is below 12px', 'recovery-recycle-risk-loop.svg: font-size 11px is below 12px']\nE       assert False is True\n\ntests/test_readme_visual_accessibility.py:32: AssertionError\n=========================== short test summary info ============================\nFAILED tests/test_readme_visual_accessibility.py::test_committed_readme_visuals_pass_accessibility_contract - AssertionError: ['batch-parameter-scan.svg: font-size 11px is below 12px', 'process-package-data-model.svg: font-size 11px is below 12px', 'recovery-recycle-risk-loop.svg: font-size 11px is below 12px']\nassert False is True\n"
    },
    {
      "command": [
        "/opt/hostedtoolcache/Python/3.14.6/x64/bin/python",
        "-m",
        "coverage",
        "report",
        "--fail-under=75"
      ],
      "returncode": 0,
      "timed_out": false,
      "duration_s": 0.3648710789999967,
      "output": "Name                           Stmts   Miss Branch BrPart  Cover\n----------------------------------------------------------------\nskills/epdm/__init__.py            2      0      0      0   100%\nskills/epdm/batch.py              44      5     10      3    85%\nskills/epdm/core.py                7      0      0      0   100%\nskills/epdm/kinetics.py          177     25     38     15    80%\nskills/epdm/package_audit.py      34      0     16      4    92%\nskills/epdm/process.py           172     19     40     17    83%\nskills/epdm/qualification.py      85     21     44     15    72%\nskills/poe/__init__.py             2      0      0      0   100%\nskills/poe/core.py                12      0      0      0   100%\nskills/poe/dynamics.py            67     11     26     11    76%\nskills/poe/estimation.py          94     19     36     11    72%\nskills/poe/governance.py         200     29    132     29    82%\nskills/poe/kinetics.py           134      8     26      7    91%\nskills/poe/model_passport.py      75      3     44      4    94%\nskills/poe/package_audit.py      285     65    164     37    75%\nskills/poe/properties.py          44      5     12      5    82%\nskills/poe/qualification.py      218     56    160     49    72%\nskills/poe/reactors.py            40      3      8      3    88%\nskills/poe/scaleup.py             43      5     10      3    85%\ntsao/process_package.py          253     68    148     44    72%\ntsao/skillpacks.py               123     29     40      9    73%\n----------------------------------------------------------------\nTOTAL                           2111    371    954    266    78%\n"
    },
    {
      "command": [
        "/opt/hostedtoolcache/Python/3.14.6/x64/bin/python",
        "-c",
        "from pathlib import Path; Path('.coverage').unlink(missing_ok=True); Path('coverage.xml').unlink(missing_ok=True)"
      ],
      "returncode": 0,
      "timed_out": false,
      "duration_s": 0.032131100000000856,
      "output": ""
    },
    {
      "command": [
        "/opt/hostedtoolcache/Python/3.14.6/x64/bin/python",
        "scripts/audit_capabilities.py"
      ],
      "returncode": 0,
      "timed_out": false,
      "duration_s": 0.117385775999999,
      "output": "{\n  \"pass\": true,\n  \"issues\": [],\n  \"gates\": 19,\n  \"workstreams\": 14,\n  \"maturity_levels\": 10,\n  \"subskills\": {\n    \"epdm\": {\n      \"files\": 34,\n      \"tests\": 3\n    },\n    \"poe\": {\n      \"files\": 115,\n      \"tests\": 8\n    },\n    \"polymer-general\": {\n      \"files\": 20,\n      \"tests\": 2\n    },\n    \"process-general\": {\n      \"files\": 30,\n      \"tests\": 2\n    }\n  },\n  \"universal_package_status\": \"EXECUTABLE_ALPHA\",\n  \"epdm_status\": \"EXECUTABLE_FLAGSHIP_ALPHA_P1_REFERENCE\",\n  \"poe_status\": \"EXECUTABLE_SPECIALIST_ALPHA_P1_REFERENCE\",\n  \"technical_approval_status\": \"NOT_EVALUATED\"\n}\n"
    },
    {
      "command": [
        "/opt/hostedtoolcache/Python/3.14.6/x64/bin/python",
        "skills/epdm/scripts/audit_epdm.py"
      ],
      "returncode": 0,
      "timed_out": false,
      "duration_s": 0.47091297300000434,
      "output": "{\n  \"status\": \"PASS\",\n  \"pass\": true,\n  \"errors\": [],\n  \"module_registration\": \"14/14\",\n  \"requirement_registration\": \"20/20\",\n  \"reference_case\": \"PASS\",\n  \"reference_package\": \"PASS\",\n  \"scientific_technical_approval\": \"NOT_EVALUATED\",\n  \"engineering_design_approval\": \"NOT_EVALUATED\",\n  \"customer_qualification\": \"NOT_EVALUATED\"\n}\n"
    },
    {
      "command": [
        "/opt/hostedtoolcache/Python/3.14.6/x64/bin/python",
        "skills/poe/scripts/audit_p0.py",
        "--root",
        "."
      ],
      "returncode": 0,
      "timed_out": false,
      "duration_s": 0.8237655490000009,
      "output": "{\n  \"pass\": true,\n  \"status\": \"PASS\",\n  \"checks\": {\n    \"asset_registry_schema\": {\n      \"pass\": true,\n      \"errors\": []\n    },\n    \"requirement_trace_schema\": {\n      \"pass\": true,\n      \"errors\": []\n    },\n    \"conflict_ledger_schema\": {\n      \"pass\": true,\n      \"errors\": []\n    },\n    \"asset_registry\": {\n      \"status\": \"PASS\",\n      \"pass\": true,\n      \"errors\": [],\n      \"coverage\": 1.0\n    },\n    \"requirement_trace\": {\n      \"status\": \"PASS\",\n      \"pass\": true,\n      \"errors\": [],\n      \"coverage\": 1.0\n    },\n    \"conflict_ledger\": {\n      \"status\": \"PASS\",\n      \"pass\": true,\n      \"errors\": [],\n      \"open_blockers\": 7\n    },\n    \"modules\": {\n      \"pass\": true,\n      \"errors\": []\n    },\n    \"specialist_schemas\": {\n      \"pass\": true,\n      \"errors\": []\n    },\n    \"fixtures\": {\n      \"pass\": true,\n      \"errors\": []\n    }\n  },\n  \"asset_coverage\": \"139/139\",\n  \"requirement_registration_coverage\": \"18/18\",\n  \"conflict_registration\": \"7/7\",\n  \"module_count\": 12,\n  \"fixture_domain_count\": 11,\n  \"scientific_approval\": \"NOT_EVALUATED\",\n  \"engineering_approval\": \"NOT_EVALUATED\"\n}\n"
    },
    {
      "command": [
        "/opt/hostedtoolcache/Python/3.14.6/x64/bin/python",
        "skills/poe/scripts/audit_p1.py",
        "--root",
        "."
      ],
      "returncode": 0,
      "timed_out": false,
      "duration_s": 0.5726064559999955,
      "output": "{\n  \"status\": \"PASS_WITH_EXTERNAL_HOLDS\",\n  \"pass\": true,\n  \"errors\": [],\n  \"holds\": [\n    \"model passport: POE-MODEL-001: model has not been re-executed and qualified in the active environment\",\n    \"model passport: POE-MODEL-002: model has not been re-executed and qualified in the active environment\",\n    \"model passport: POE-MODEL-003: model has not been re-executed and qualified in the active environment\"\n  ],\n  \"reference_level\": \"P1_REFERENCE_KERNEL_ALPHA\",\n  \"scientific_technical_approval\": \"NOT_EVALUATED\",\n  \"engineering_design_approval\": \"NOT_EVALUATED\",\n  \"industrial_performance_guarantee\": \"NOT_EVALUATED\"\n}\n"
    },
    {
      "command": [
        "/opt/hostedtoolcache/Python/3.14.6/x64/bin/python",
        "-m",
        "tsao.cli",
        "doctor",
        "--root",
        ".",
        "--profile",
        "core"
      ],
      "returncode": 0,
      "timed_out": false,
      "duration_s": 0.726421062,
      "output": "{\n  \"version\": \"0.1.0-alpha.10\",\n  \"profile\": \"core\",\n  \"pass\": true,\n  \"strict_source_clean\": false,\n  \"checks\": {\n    \"repository\": {\n      \"pass\": true,\n      \"issues\": []\n    },\n    \"version\": {\n      \"pass\": true,\n      \"issues\": []\n    },\n    \"schemas\": {\n      \"pass\": true,\n      \"issues\": []\n    },\n    \"capabilities\": {\n      \"pass\": true,\n      \"issues\": []\n    },\n    \"provenance\": {\n      \"pass\": true,\n      \"issues\": []\n    },\n    \"release_identity\": {\n      \"pass\": true,\n      \"issues\": []\n    }\n  },\n  \"issues\": [],\n  \"warnings\": [],\n  \"metrics\": {\n    \"schemas\": 9,\n    \"specialists\": 4\n  },\n  \"artifact_software_qualification\": \"PASS\",\n  \"technical_approval_status\": \"NOT_EVALUATED\",\n  \"scientific_technical_approval\": \"NOT_EVALUATED\",\n  \"engineering_design_approval\": \"NOT_EVALUATED\",\n  \"customer_qualification\": \"NOT_EVALUATED\",\n  \"industrial_performance_guarantee\": \"NOT_EVALUATED\"\n}\n"
    },
    {
      "command": [
        "/opt/hostedtoolcache/Python/3.14.6/x64/bin/python",
        "-m",
        "ruff",
        "check",
        "tsao",
        "tests",
        "scripts",
        "skills/process-general",
        "skills/epdm",
        "skills/poe",
        "skills/polymer-general"
      ],
      "returncode": 1,
      "timed_out": false,
      "duration_s": 0.2203573450000036,
      "output": "I001 [*] Import block is un-sorted or un-formatted\n  --> scripts/verify_readme_visual_accessibility.py:16:1\n   |\n14 |       sys.path.insert(0, str(ROOT))\n15 |\n16 | / from scripts.generate_uiux_readme_assets import (  # noqa: E402\n17 | |     AMBER,\n18 | |     ASSETS,\n19 | |     BG,\n20 | |     BLUE,\n21 | |     CYAN,\n22 | |     DIM,\n23 | |     GREEN,\n24 | |     H,\n25 | |     MUTED,\n26 | |     ORANGE,\n27 | |     OUT,\n28 | |     PURPLE,\n29 | |     RED,\n30 | |     SURFACE,\n31 | |     TEAL,\n32 | |     TEXT,\n33 | |     W,\n34 | | )\n35 | | from scripts.harden_readme_svg_accessibility import ROOT_ATTRIBUTES  # noqa: E402\n   | |___________________________________________________________________^\n36 |\n37 |   SVG_NS = \"{http://www.w3.org/2000/svg}\"\n   |\nhelp: Organize imports\n   |\n23 |     GREEN,\n   -     H,\n24 |     MUTED,\n--------------------------------------------------------------------------------\n31 |     TEXT,\n32 +     H,\n33 |     W,\n   |\n\nFound 1 error.\n[*] 1 fixable with the `--fix` option.\n"
    }
  ],
  "wall_clock_sum_s": 12.003486716000005,
  "artifact_software_qualification": "FAIL",
  "universal_process_package_status": "HOLD",
  "skillpack_delivery_status": "HOLD",
  "epdm_software_status": "HOLD",
  "poe_software_status": "HOLD",
  "poe_scientific_execution": "UNDER_DISTILLATION",
  "scientific_technical_approval": "NOT_EVALUATED",
  "engineering_design_approval": "NOT_EVALUATED",
  "customer_qualification": "NOT_EVALUATED",
  "industrial_performance_guarantee": "NOT_EVALUATED"
}
exit=1

== skillpacks ==
{
  "pass": true,
  "root": "/home/runner/work/TSAO-PROCESSING-SKILL/TSAO-PROCESSING-SKILL",
  "delivery": "SOURCE_CHECKOUT",
  "version": "0.1.0-alpha.10",
  "subskills": [
    "epdm",
    "poe",
    "polymer-general",
    "process-general"
  ],
  "process_general_modules_present": 14,
  "process_general_modules_expected": 14,
  "process_general_workflows_present": 6,
  "process_general_workflows_expected": 6,
  "polymer_general_scripts_present": 6,
  "polymer_general_scripts_expected": 6,
  "readme_svg_assets": 18,
  "readme_svg_assets_expected_minimum": 18,
  "errors": [],
  "scientific_technical_approval": "NOT_EVALUATED",
  "engineering_design_approval": "NOT_EVALUATED",
  "industrial_performance_guarantee": "NOT_EVALUATED"
}
exit=0

== wheel_build ==
Processing ./.
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Building wheels for collected packages: tsao-processing-skill
  Building wheel for tsao-processing-skill (pyproject.toml): started
  Building wheel for tsao-processing-skill (pyproject.toml): finished with status 'done'
  Created wheel for tsao-processing-skill: filename=tsao_processing_skill-0.1.0a10-py3-none-any.whl size=569507 sha256=9fa454199d7522fdd7bf92886abb9e004148b2ce1d9374f6d0246dc0720e54b6
  Stored in directory: /home/runner/.cache/pip/wheels/4c/01/48/b3d13d995607b5b8e41ce2c652da12bae8e84ed0d83d133ae1
Successfully built tsao-processing-skill
exit=0

== wheel_contents ==
{
  "wheel": "wheelhouse/tsao_processing_skill-0.1.0a10-py3-none-any.whl",
  "pass": true,
  "errors": [],
  "identity": {
    "expected_name": "tsao-processing-skill",
    "expected_version": "0.1.0a10",
    "console_scripts": {
      "tsao": "tsao.cli:main",
      "tsao-skillpacks": "tsao.skillpacks:main"
    },
    "metadata_name": "tsao-processing-skill",
    "metadata_version": "0.1.0a10"
  },
  "poe_members": 72,
  "epdm_members": 20,
  "poe_module_count": 12,
  "process_general_module_count": 14,
  "process_general_workflow_count": 6,
  "readme_asset_count": 18,
  "maintenance_script_count": 14,
  "installed_skillpack_members": 204
}
exit=0

== wheel_runtime ==
{
  "wheel": "wheelhouse/tsao_processing_skill-0.1.0a10-py3-none-any.whl",
  "pass": true,
  "errors": [],
  "runtimes": {
    "PIP_TARGET": {
      "tsao_module_path": "/tmp/tsao-wheel-runtime-gyk55lh_/target-site/tsao/__init__.py",
      "epdm_module_path": "/tmp/tsao-wheel-runtime-gyk55lh_/target-site/skills/epdm/__init__.py",
      "poe_module_path": "/tmp/tsao-wheel-runtime-gyk55lh_/target-site/skills/poe/__init__.py",
      "python_prefix": "/opt/hostedtoolcache/Python/3.14.6/x64",
      "pfr": 0.6321205588285577,
      "fit": 0.2,
      "response": [
        0.0,
        0.3934693402873666,
        0.9932620530009145
      ],
      "passport_status": "HOLD",
      "active_site": 0.6,
      "heat_margin": 0.2,
      "epdm_status": "PASS",
      "package_status": "PASS",
      "skillpacks": {
        "pass": true,
        "root": "/tmp/tsao-wheel-runtime-gyk55lh_/target-site/share/tsao-processing-skill",
        "delivery": "INSTALLED_SKILLPACK",
        "version": "0.1.0-alpha.10",
        "subskills": [
          "epdm",
          "poe",
          "polymer-general",
          "process-general"
        ],
        "process_general_modules_present": 14,
        "process_general_modules_expected": 14,
        "process_general_workflows_present": 6,
        "process_general_workflows_expected": 6,
        "polymer_general_scripts_present": 6,
        "polymer_general_scripts_expected": 6,
        "readme_svg_assets": 18,
        "readme_svg_assets_expected_minimum": 18,
        "errors": [],
        "scientific_technical_approval": "NOT_EVALUATED",
        "engineering_design_approval": "NOT_EVALUATED",
        "industrial_performance_guarantee": "NOT_EVALUATED"
      },
      "installed_readme_link_failures": []
    },
    "STANDARD_VENV": {
      "tsao_module_path": "/tmp/tsao-wheel-runtime-gyk55lh_/standard-venv/lib/python3.14/site-packages/tsao/__init__.py",
      "epdm_module_path": "/tmp/tsao-wheel-runtime-gyk55lh_/standard-venv/lib/python3.14/site-packages/skills/epdm/__init__.py",
      "poe_module_path": "/tmp/tsao-wheel-runtime-gyk55lh_/standard-venv/lib/python3.14/site-packages/skills/poe/__init__.py",
      "python_prefix": "/tmp/tsao-wheel-runtime-gyk55lh_/standard-venv",
      "pfr": 0.6321205588285577,
      "fit": 0.2,
      "response": [
        0.0,
        0.3934693402873666,
        0.9932620530009145
      ],
      "passport_status": "HOLD",
      "active_site": 0.6,
      "heat_margin": 0.2,
      "epdm_status": "PASS",
      "package_status": "PASS",
      "skillpacks": {
        "pass": true,
        "root": "/tmp/tsao-wheel-runtime-gyk55lh_/standard-venv/share/tsao-processing-skill",
        "delivery": "INSTALLED_SKILLPACK",
        "version": "0.1.0-alpha.10",
        "subskills": [
          "epdm",
          "poe",
          "polymer-general",
          "process-general"
        ],
        "process_general_modules_present": 14,
        "process_general_modules_expected": 14,
        "process_general_workflows_present": 6,
        "process_general_workflows_expected": 6,
        "polymer_general_scripts_present": 6,
        "polymer_general_scripts_expected": 6,
        "readme_svg_assets": 18,
        "readme_svg_assets_expected_minimum": 18,
        "errors": [],
        "scientific_technical_approval": "NOT_EVALUATED",
        "engineering_design_approval": "NOT_EVALUATED",
        "industrial_performance_guarantee": "NOT_EVALUATED"
      },
      "installed_readme_link_failures": []
    }
  },
  "install_modes": [
    "PIP_TARGET",
    "STANDARD_VENV"
  ],
  "import_origin_check": "ENFORCED",
  "standard_venv_isolation": "NO_SYSTEM_SITE_PACKAGES"
}
exit=0
