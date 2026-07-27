
== install ==
exit=0

== pip_check ==
No broken requirements found.
exit=0

== compile ==
exit=0

== apply ==
applied eighteen-diagram UI/UX visual delivery contract
exit=0

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

== sync_readme ==
exit=0

== sync_check ==
exit=0

== svg_parse ==
parsed 18 SVG assets
exit=0

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
..........................................                               [100%]
exit=0

== ruff ==
B033 [*] Sets should not contain duplicate item `"skills/epdm/core.py"`
  --> tests/test_repository_contracts.py:56:5
   |
54 |     "skills/epdm/STATUS.md",
55 |     "skills/epdm/__init__.py",
56 |     "skills/epdm/core.py",
   |     --------------------- Previous occurrence here
57 |     "skills/epdm/core.py",
   |     ^^^^^^^^^^^^^^^^^^^^^
58 |     "skills/epdm/kinetics.py",
59 |     "skills/epdm/process.py",
   |
help: Remove duplicate item
   |
56 |     "skills/epdm/core.py",
   -     "skills/epdm/core.py",
57 |     "skills/epdm/kinetics.py",
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
      "duration_s": 0.5661681229999971,
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
      "duration_s": 0.264341555999998,
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
      "returncode": 0,
      "timed_out": false,
      "duration_s": 7.437008106,
      "output": "........................................................................ [ 32%]\n........................................................................ [ 65%]\n........................................................................ [ 98%]\n....                                                                     [100%]\n"
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
      "duration_s": 0.3145579659999953,
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
      "duration_s": 0.03203427699999395,
      "output": ""
    },
    {
      "command": [
        "/opt/hostedtoolcache/Python/3.14.6/x64/bin/python",
        "scripts/audit_capabilities.py"
      ],
      "returncode": 0,
      "timed_out": false,
      "duration_s": 0.22316244200000313,
      "output": "{\n  \"pass\": true,\n  \"issues\": [],\n  \"gates\": 19,\n  \"workstreams\": 14,\n  \"maturity_levels\": 10,\n  \"subskills\": {\n    \"epdm\": {\n      \"files\": 34,\n      \"tests\": 3\n    },\n    \"poe\": {\n      \"files\": 115,\n      \"tests\": 8\n    },\n    \"polymer-general\": {\n      \"files\": 20,\n      \"tests\": 2\n    },\n    \"process-general\": {\n      \"files\": 30,\n      \"tests\": 2\n    }\n  },\n  \"universal_package_status\": \"EXECUTABLE_ALPHA\",\n  \"epdm_status\": \"EXECUTABLE_FLAGSHIP_ALPHA_P1_REFERENCE\",\n  \"poe_status\": \"EXECUTABLE_SPECIALIST_ALPHA_P1_REFERENCE\",\n  \"technical_approval_status\": \"NOT_EVALUATED\"\n}\n"
    },
    {
      "command": [
        "/opt/hostedtoolcache/Python/3.14.6/x64/bin/python",
        "skills/epdm/scripts/audit_epdm.py"
      ],
      "returncode": 0,
      "timed_out": false,
      "duration_s": 0.5203111510000014,
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
      "duration_s": 0.8284253079999928,
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
      "duration_s": 0.5224239329999989,
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
      "duration_s": 0.7233675089999991,
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
      "duration_s": 0.22008928300000719,
      "output": "B033 [*] Sets should not contain duplicate item `\"skills/epdm/core.py\"`\n  --> tests/test_repository_contracts.py:56:5\n   |\n54 |     \"skills/epdm/STATUS.md\",\n55 |     \"skills/epdm/__init__.py\",\n56 |     \"skills/epdm/core.py\",\n   |     --------------------- Previous occurrence here\n57 |     \"skills/epdm/core.py\",\n   |     ^^^^^^^^^^^^^^^^^^^^^\n58 |     \"skills/epdm/kinetics.py\",\n59 |     \"skills/epdm/process.py\",\n   |\nhelp: Remove duplicate item\n   |\n56 |     \"skills/epdm/core.py\",\n   -     \"skills/epdm/core.py\",\n57 |     \"skills/epdm/kinetics.py\",\n   |\n\nFound 1 error.\n[*] 1 fixable with the `--fix` option.\n"
    }
  ],
  "wall_clock_sum_s": 11.651889653999987,
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
  Created wheel for tsao-processing-skill: filename=tsao_processing_skill-0.1.0a10-py3-none-any.whl size=561907 sha256=7403a1b415fafdd190705776da0d70fcbc1514e704c0e9dbedec1d03a19d55bd
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
  "installed_skillpack_members": 202
}
exit=0

== wheel_runtime ==
{
  "wheel": "wheelhouse/tsao_processing_skill-0.1.0a10-py3-none-any.whl",
  "pass": true,
  "errors": [],
  "runtimes": {
    "PIP_TARGET": {
      "tsao_module_path": "/tmp/tsao-wheel-runtime-knpbk8_9/target-site/tsao/__init__.py",
      "epdm_module_path": "/tmp/tsao-wheel-runtime-knpbk8_9/target-site/skills/epdm/__init__.py",
      "poe_module_path": "/tmp/tsao-wheel-runtime-knpbk8_9/target-site/skills/poe/__init__.py",
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
        "root": "/tmp/tsao-wheel-runtime-knpbk8_9/target-site/share/tsao-processing-skill",
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
      "tsao_module_path": "/tmp/tsao-wheel-runtime-knpbk8_9/standard-venv/lib/python3.14/site-packages/tsao/__init__.py",
      "epdm_module_path": "/tmp/tsao-wheel-runtime-knpbk8_9/standard-venv/lib/python3.14/site-packages/skills/epdm/__init__.py",
      "poe_module_path": "/tmp/tsao-wheel-runtime-knpbk8_9/standard-venv/lib/python3.14/site-packages/skills/poe/__init__.py",
      "python_prefix": "/tmp/tsao-wheel-runtime-knpbk8_9/standard-venv",
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
        "root": "/tmp/tsao-wheel-runtime-knpbk8_9/standard-venv/share/tsao-processing-skill",
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
