# Crosswords

A small, standalone crossword-filling app. Upload a photo or PDF of a puzzle,
drag to align a grid over it, and type answers directly on top of the image.
No OCR, no AI at runtime — just plain browser code.

**Live app:** https://lleviraz.github.io/crosswords/

## How it works
- Everything runs client-side. Puzzle images, grid alignment, and your typed
  answers are stored in the browser's `localStorage`, tied to this page's URL.
- Nothing is ever uploaded anywhere — your data stays on your device.
- Use the **Share** button to export a copy with your puzzles baked in for
  someone else to open directly, or **Backup**/**Import** to move data
  between browsers/devices as a small `.json` file.

## Local development
It's a single self-contained `index.html` — no build step. Open it directly
in a browser, or serve the folder with any static file server.
