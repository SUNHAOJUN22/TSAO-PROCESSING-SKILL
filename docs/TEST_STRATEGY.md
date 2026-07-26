# Test strategy

TSAO uses layered tests rather than a single happy-path demo:

- syntax and import tests;
- schema positive and negative fixtures;
- analytical known solutions and conservation;
- dimensional and limiting behaviour;
- sensitivity, identifiability, uncertainty and applicability domain;
- routing, initialization and project end-to-end tests;
- specialist migration and compatibility tests;
- Gate overreach and false-approval attacks;
- expired/contradictory evidence and MR4/MR5 review attacks;
- archive traversal, symlink, cache, secret and checksum attacks;
- deterministic-build and cleanroom-extraction tests;
- bilingual parity, XML parsing and deterministic regeneration for sixteen README SVGs;
- complete four-Skill Wheel-member verification;
- target-directory installation and a clean standard virtual-environment installation;
- import-origin checks for TSAO, EPDM, POE and Skillpack data;
- installed-root, known-solution and bilingual README-link checks in both installation modes;
- Ubuntu qualification on Python 3.11–3.14 and Windows/macOS qualification on Python 3.14.

A failing test must be fixed at its root cause. Assertions are not weakened and tests are not removed merely to achieve a green status. Software qualification never substitutes for scientific, engineering, HSE, customer or industrial approval.
