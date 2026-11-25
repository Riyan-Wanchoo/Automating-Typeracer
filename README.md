# TypeRacer Automation Bot (YOLO + OCR)

An automated typing bot for [play.typeracer.com](https://play.typeracer.com) powered by a custom-trained **Ultralytics YOLO** object detection model, **OpenCV**, **Tesseract OCR**, and **PyAutoGUI**.

Unlike coordinate-based bots that break whenever you resize your browser or change screen resolutions, this bot dynamically locates the text passage and typing box on screen in real time, waits patiently until a race actually begins, reads the passage via OCR, and types it automatically.

---

## Key Features

* **Hands-Off Idle Monitoring:** No need to rush to your browser the second you start the script. Launch `main.py` whenever you want—it stays quietly idle in the background until it spots an active TypeRacer screen and detects that the race countdown has ended.
* **No Fixed Screen Coordinates:** Uses a custom YOLO model (`weights.pt`) to locate the `Text` passage and `Textbox` input field anywhere on the screen.
* **Zoom & Resolution Flexible:** Works across different window sizes, monitor resolutions, and browser zoom levels (as long as the zoom isn't extreme).
* **Full-Width Edge Snapping:** Combines bounding-box union logic with an OpenCV pixel-intensity scan along the input bar to snap to the full right border of the passage, preventing clipped words at the end of lines.
* **Automatic Race Detection:** Continuously checks the input box and begins typing only once the placeholder text (`"Type the above text here when the race begins"`) disappears.
* **OCR Cleanup:** Normalizes line breaks into single spaces and converts non-ASCII punctuation (curly quotes, em-dashes) into standard ASCII characters compatible with `pyautogui.write()`.

---

## Requirements & Compatibility

* **Supported Website:** Works for **`play.typeracer.com` only**.
* **Visibility:** Both the **text passage** and the **typing input box** must be fully visible on your screen (not scrolled out of view or covered by another window).
* **Active Window:** Once you are ready to race, keep the TypeRacer browser tab focused so keystrokes register properly as soon as the countdown finishes.
* **Light Theme Recommended:** The right-edge border scanner expects TypeRacer's default light/white input box with a grey border. Dark-mode browser extensions (e.g., Dark Reader) may interfere with border detection.
* **OS:** Configured for Windows by default (can be adapted for Linux/macOS by updating the Tesseract executable path).

---

## Setup & Installation

### 1. Install Tesseract OCR (Required)
Download and install **Tesseract OCR** for Windows (UB Mannheim build):
* Default installation path expected by `main.py`:
  ```text
  C:\Program Files\Tesseract-OCR\tesseract.exe
  ```
* If you install Tesseract somewhere else, update the path at the top of `main.py`:
  ```python
  pytesseract.pytesseract.tesseract_cmd = r"YOUR\PATH\TO\tesseract.exe"
  ```

### 2. Install Python Dependencies
Make sure Python 3.9+ is installed, then run:
```bash
pip install ultralytics opencv-python pytesseract pillow pyautogui numpy
```

### 3. Project Structure
Ensure your trained YOLO weights file (`weights.pt`) is placed in the same directory as `main.py`:
```text
.
├── main.py
├── weights.pt
└── last_saved_frame/   # Created automatically to store temporary frame crops
```

---

## Usage

1. Run the bot at any time:
   ```bash
   python main.py
   ```
   The script will sit idle without typing anything until a live TypeRacer match is detected on screen.
2. Whenever you're ready, open [play.typeracer.com](https://play.typeracer.com) in your browser and enter a race (making sure both the passage area and typing box are visible).
3. Keep the browser tab focused—as soon as the countdown finishes and the race starts, the bot automatically reads the passage and types it out.

> **Emergency Stop:** `pyautogui` has a built-in fail-safe. Quickly move your mouse cursor to the **top-left corner `(0, 0)`** of your screen at any time to immediately stop the script.

---

## Tuning Typing Speed (`interval`)

You can adjust typing speed at the top of `main.py`:
```python
# Smaller interval = faster typing (in seconds per character)
interval = 0.1
```

* **Warning on High Speeds:** Setting `interval` below **`0.05`** seconds may cause missed characters, out-of-order input, or failed registration because the TypeRacer web interface struggles to keep up with ultra-fast simulated keystrokes. Values between `0.05` and `0.10` are generally the most reliable.

---

## Disclaimer

This project is built for educational purposes and its misuse on public servers may result in a ban.
