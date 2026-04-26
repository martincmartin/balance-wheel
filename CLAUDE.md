# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Goal

Estimate the amplitude (swing angle) of a mechanical watch's balance wheel from a video of its movement. The user records a video of the balance wheel, and the tool analyzes it to compute amplitude.

## Running

```bash
python balance-wheel.py
```

Dependencies: `opencv-python` (cv2) and `PySide6`. The script hardcodes `VIDEO_PATH = "PXL_20260417_113052141.mp4"` — change this to point at the video you want to analyze.

## Architecture

Single-file script (`balance-wheel.py`) with two phases:

1. **Video loading** — reads all frames upfront into memory using OpenCV (`read_frames`).
2. **Interactive UI** — PySide6/Qt app (`ImageViewer`) that displays the first frame with a `MovableLine` overlay: a yellow line with two cyan draggable `Handle` endpoints (child `QGraphicsEllipseItem`s of the line item). The user positions this line over the balance wheel's axis of rotation to define the reference.

The `cv_to_pixmap` helper converts OpenCV BGR frames to Qt `QPixmap` for display. `ImageViewer.update_frame` exists for future video playback.

The amplitude estimation logic (tracking the wheel across frames) has not yet been implemented.
