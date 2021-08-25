# Simple QT application to test interactive segmentation

## Setup
- Tested with
- python3.8
- PyQt5==5.15.4
- opencv-python-headless==4.5.3.56 (to avoid conflict with PyQt)

## General usage
- python main.py
- File -> Open
- Change brush size, and color
- Change draw mode: rectangle vs point for different stage of the algorithms

## Segment with Grabcut algorithm
- First, make sure at drawing rect mode to draw rectangle. Do process and wait for result
- Switch to drawing point mode
  - Use red color to mark wrongly classified Foreground mask as Background
  - Use green color to mark wrongly classified Background mask as Foreground
- Process and wait for result

## Segment with DL on benchmark: [Interactive Segmentation on GrabCut
](https://paperswithcode.com/sota/interactive-segmentation-on-grabcut)