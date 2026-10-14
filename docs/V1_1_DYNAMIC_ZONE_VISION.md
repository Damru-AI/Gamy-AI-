# Gamy AI v1.1 — Dynamic Zone & Vision Lab

## What changed
- Added a separate simulator/gamy_ai_v1_1_vision_lab.html candidate. The v1.0 simulator remains unchanged.
- Six deterministic safe-zone phases shrink the radius over a 150-step episode.
- Simulated awareness contacts are reduced by phase: 54, 40, 28, 16, 8, then 3.
- Added simulator-only manual movement controls, keyboard arrows, regrouping, teammate-support and recovery actions.
- Added a local video-file input and browser playback. A selected file is read locally by the browser; the tool samples the current frame and reports brightness, contrast, and a simple horizontal edge-change score.
- Added a JSON session export with simulation state, the latest frame summary, and the research log.

## Vision limitations
The browser analyzer is a deliberately simple image-statistics baseline. It does not perform trained object detection, identify game objects, infer intent, or recognize opponents. A genuine learned vision model should be a separate next phase trained and evaluated on properly licensed, annotated footage with held-out recordings.

## Safety and scope
- This is an offline toy simulator and local recorded-video research tool, not a Free Fire client or faithful replica.
- It does not connect to game servers, inject inputs, or send actions to another application.
- Recommendations are informational; movement controls only affect the toy simulator.
- Contacts are awareness markers; no automated target selection or combat actions are implemented.
- Only load recordings you have permission to use. The browser does not upload the selected video.

## Manual validation checklist
1. Open simulator/gamy_ai_v1_1_vision_lab.html in a modern browser.
2. Confirm the zone phase changes at steps 25, 50, 75, 100, and 125.
3. Confirm contact count decreases to 40, 28, 16, 8, and 3.
4. Use buttons and arrow keys; verify they only move the toy simulator agent.
5. Test regroup/recovery actions and the session JSON export.
6. Load a permitted local video, seek to a frame, click Analyze current frame, and confirm timestamp and image statistics update.
7. Compare behavior across repeated episodes. Do not claim generalization based on one seed or this rule-based prototype.
