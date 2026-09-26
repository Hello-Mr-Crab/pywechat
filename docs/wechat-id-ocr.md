# WeChat ID extraction: OCR first, UIA second

## Why

The previous `Contacts.get_friends_detail()` implementation read the text
tree and treated the Text control after `微信号：` as the ID. Newer WeChat
versions can expose an incomplete UIA subtree, and positional controls can
belong to other fields. The ID path now reads pixels first. UIA remains in the
library for the rest of its automation features and supplies only a later
cross-check.

## Architecture and result rules

`pyweixin.Contacts.get_friends_detail()` preserves its existing list/JSON
return shape and contact fields. It adds `微信号状态`, `微信号来源`,
`微信号置信度`, `微信号原因`, and `微信号候选`. The `微信号` field contains
only a `CONFIRMED` value; the legacy missing-value sentinel is `无`.

The path is: screenshot of the profile panel (or a right-side ROI based on the
WeChat window rectangle) → two conservative image views → label-anchored
PP-OCRv6 recognition → syntax check → two-view consensus → optional UIA
cross-check → `CONFIRMED`, `NEED_REVIEW`, `NOT_FOUND`, or `OCR_FAILED`.
The OCR package does not depend on the UIA text subtree to produce its image.
The fallback ROI uses window-relative proportions, so it scales with window
size, maximized/windowed layout, and DPI; its expected panel placement still
needs validation against each WeChat layout.

The label anchors are Chinese and English `WeChat ID` forms. A value must be
on the same line to the right, or close below the label. Other ID-like text
on the page is ignored. Values are never concatenated across OCR boxes.

Only agreement between two views with a confidence at or above the configured
`0.99` threshold confirms OCR alone. This initial threshold sits below the
`0.9998` reading from the local synthetic probe, but it is not calibrated
against a representative labeled set of real WeChat profiles. Matching UIA can
confirm an otherwise agreeing low-confidence OCR result. Different OCR views,
OCR/UIA disagreement, UIA-only results, missing values, invalid syntax, or
failed OCR never fill the export `wechat_id` column. No O/0, I/l/1, S/5,
8/B, hyphen/underscore, or similar substitutions occur.

The exporter performs a second fail-closed check. Inputs without explicit
`微信号状态=CONFIRMED` are written with an empty `wechat_id` and their raw
candidate, if any, is placed in the separate `wechat_id_candidate` column.
Status, source, confidence, reason, and candidate columns were appended to
the existing CSV field order. TXT also identifies status and source.

## Install and prepare models

The OCR runtime is optional for existing installations:

```powershell
python -m pip install -r src/requirements-ocr.txt
```

Pinned and locally verified versions are `rapidocr==3.9.2` and
`onnxruntime==1.30.0`. Detection, recognition, and classification explicitly
select RapidOCR's `ONNXRUNTIME` engine with CUDA disabled, so ONNX Runtime uses
the CPU path. RapidOCR currently brings `opencv-python` as a declared transitive
dependency; the project does not import or use OpenCV directly. PaddlePaddle,
PyTorch, CUDA, Windows.Media.Ocr, and cloud OCR are not used.

The default is PP-OCRv6 medium detector + medium recognizer. The model source
is the RapidAI v3.9.2 ONNX release on ModelScope:

- [PP-OCRv6 medium detector](https://www.modelscope.cn/models/RapidAI/RapidOCR/resolve/v3.9.2/onnx/PP-OCRv6/det/PP-OCRv6_det_medium.onnx) — SHA256 `92078b7355007ccfffcd4c8cd441a3afd4538904d06881b29a155e1e679907c2`
- [PP-OCRv6 medium recognizer](https://www.modelscope.cn/models/RapidAI/RapidOCR/resolve/v3.9.2/onnx/PP-OCRv6/rec/PP-OCRv6_rec_medium.onnx) — SHA256 `eef444829dbbe18d7fea59a3f6eb75647518d2b3a9568d27c92e42940204894b`

These hashes are RapidOCR 3.9.2's published model manifest values and match
the locally installed model files. RapidOCR keeps its ONNX files in its
`models` cache (under the installed package by default).
The first initialization needs internet access to fetch missing official
RapidOCR model assets; subsequent runs reuse validated local assets and can
run offline. To prewarm the models before going offline, initialize
`get_ocr_engine()` once in the target Python environment. Never copy model
binaries into the source repository. RapidOCR maintains the model URLs and
file-integrity metadata; the installed package version pins that manifest.

The configured OCR engine is created lazily and cached per process/model
configuration. Missing runtime, model initialization, and inference errors
surface as `OCR_RUNTIME_UNAVAILABLE`, `OCR_MODEL_LOAD_FAILED`, and
`OCR_INFERENCE_FAILED`, then as an `OCR_FAILED` extraction result. They are
not converted to a successful UIA result.

## Configuration and diagnostics

`pyweixin.ocr.config.WeChatIdOcrConfig` centralizes model type, labels,
confidence, view geometry, length checks, and relative fallback ROI. Keep the
medium recognizer as the default; do not change model size based only on speed.
`mask_wechat_id()` masks ID values in diagnostics. Contact names and complete
IDs are not written to OCR debug logs, and profile screenshots are processed
in memory only (not saved).

## Performance and limitations

Local benchmark (2026-09-25, Windows, Python 3.13, 20 logical processors,
700×420 synthetic profile image; models already present and hash-validated):

| Metric | Measured |
| --- | ---: |
| Medium det + rec model construction | 1.204 s |
| Cold process, load + two-view extraction | 21.022 s |
| Warm view A / view B | 10.345 s / 9.738 s |
| Warm two-view total | 19.940 s |
| Process CPU during warm extraction | 84.734 CPU-s (424.9%, about 4.25 logical cores) |
| RSS after model load / after extraction | 268.6 MiB / 276.7 MiB |
| Synthetic candidate confidence | 0.9998 in both views |

Performance should be measured on the target Windows host after model warmup.
This synthetic probe validates that the pinned stack runs but is not a
representative, consented real-profile image set; real-world accuracy and a
confidence threshold are not established. The actual Windows client smoke test
is only valid if the user is already logged in. This feature does not promise that OCR
is always correct. Multiple views, confidence, syntax, spatial anchoring,
UIA cross-checking, and fail-closed output reduce the chance of a wrong ID;
uncertain reads remain `NEED_REVIEW` rather than being guessed.

Troubleshooting: install the optional pinned dependencies; run once online to
prepare the official model cache; check that a profile panel is visible and
large enough in the screenshot; inspect only masked status/reason diagnostics.
If the ROI or ID is not confidently confirmed, review it manually.
