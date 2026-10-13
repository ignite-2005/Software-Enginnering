# Software Engineering Mini Project — Team H6

**Project:** Hardware-Based Voice Assistant for Multimedia Controls  
**Team roster mapped from the uploaded GitHub repository-link Excel:**  
- Surjo Sarkar — PES1UG24CS484 — `@ignite-2005`  
- Shriniketh Kana — PES1UG24CS446 — `@DerpSpears`  
- Shivani B R — PES1UG24CS439 — `@shivanibr0512-cmyk`  
- Arpan Joardar — PES1UG25CS805 — `@arpan-joardar`.  
**Source of truth:** [MINI PROJECT.pdf](./MINI%20PROJECT.pdf) containing the SRS, Test Plan and SAD.

Arpan Joardar's SRN is confirmed as `PES1UG25CS805` by the student. The `PES1UG24CS805` entry in the mini-project PDF is treated as stale.

This repository contains the **Team H6 group mini-project** and its Software Engineering backlog.

## Backlog links

- [Backlog register with story points, sprint plan, requirement traceability and Jira cross-reference](./BACKLOG.md)
- [GitHub Projects V2 setup guide and team access checklist](./GITHUB_PROJECT_SETUP.md)
- [Jira H6 backlog board](https://ignite005.atlassian.net/jira/software/c/projects/SCRUM/boards/1) — Epics SCRUM-6–SCRUM-11 and Stories SCRUM-12–SCRUM-28.
- Epics: [Voice input](https://github.com/ignite-2005/Software-Enginnering/issues/1) · [Playback/navigation](https://github.com/ignite-2005/Software-Enginnering/issues/2) · [Volume](https://github.com/ignite-2005/Software-Enginnering/issues/3) · [Validation/errors](https://github.com/ignite-2005/Software-Enginnering/issues/4) · [Quality/hardware](https://github.com/ignite-2005/Software-Enginnering/issues/5) · [Automation/delivery](https://github.com/ignite-2005/Software-Enginnering/issues/6)
- Story issues: #7–#23 in the repository's Issues tab.

## Source code and tests

The application follows the modular architecture in the SAD (NFR-05); each module is
independently testable.

| Module | Responsibility | Requirements | Story |
|---|---|---|---|
| `voice_assistant/commands.py` | Predefined command vocabulary and transcript normalization | FR-02, SR-01 | #8 |
| `voice_assistant/recognition.py` | `recognize_command()` and the `SpeechSource` capture interface | FR-02, TC-01 | #8 (capture itself: #7) |
| `voice_assistant/processor.py` | `process_command()` — validates a candidate, then dispatches one operation | FR-02, FR-10, SR-01/02 | #8, #12 |
| `voice_assistant/controller.py` | Multimedia operations on the player; `pause_media()` is implemented | FR-03–FR-09 | #10 (others: #9, #11, #16–#18) |
| `voice_assistant/player.py` | `MediaPlayerBackend` interface and the in-process player used in tests | SAD 2.7 | #10 |
| `voice_assistant/errors.py` | Error types and user-facing indications | FR-11, NFR-02 | #13 |
| `voice_assistant/assistant.py` | Capture → recognize → validate → dispatch, with safe failure handling | FR-11, NFR-03 | #13 |

Unimplemented operations raise `NotImplementedError` naming their story, so an unfinished
command can never silently trigger a different multimedia action.

### Running the tests locally

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

Hardware-facing dependencies (microphone capture, speech-to-text) are kept out of
`requirements.txt` so the suite runs without audio hardware.

### Continuous integration

`.github/workflows/tests.yml` installs the declared dependencies and runs `pytest` on every
push and pull request, on Python 3.11 and 3.12. A failing test fails the workflow, so
regressions are visible before a merge (story #22, NFR-03).

## Sprint plan
- Sprint 1: 19–23 October 2026 — planned 28 points.
- Sprint 2: 26–30 October 2026 — planned 20 points.

The story estimates are proposed planning values derived from the SRS/Test Plan/SAD; confirm with the team. The source document's NFR-01 does not state a numeric latency threshold, so confirm one before using a pass/fail performance test.

## GitHub Project status
The **H6 — Hardware-Based Voice Assistant Backlog** Projects board has been created and populated with the existing 23 repository issues (6 Epics and 17 Stories). The board's Story Points, Priority and Iteration columns are populated for the Stories; all backlog issues have GitHub assignees and remain in Todo status. Planned totals are 28 points for Sprint 1 and 20 points for Sprint 2. See `GITHUB_PROJECT_SETUP.md` for the field map and final submission checks.

## Optional Jira cross-reference
The Jira board is an additional planning cross-reference; it is not named as a required deliverable in the supplied Mini-Project Deliverables Part-2 handout. The connected Jira directory currently exposes only Surjo as assignable, so teammate Jira assignees remain blank until those users are added to the Jira site/project.
