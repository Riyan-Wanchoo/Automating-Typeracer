import pyautogui
import time
import cv2
import pytesseract
from PIL import Image
from ultralytics import YOLO
from pathlib import Path
import numpy as np
import re



# Smaller interval => faster typewrite
interval = 0.1




pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

script_dir = Path(__file__).resolve().parent
last_frame = script_dir / "last_saved_frame/lastframe.png"
crop_text_frame_path = script_dir / "last_saved_frame/crop_text_frame.png"
crop_textbox_frame_path = script_dir / "last_saved_frame/crop_textbox_frame.png"
weights_path = script_dir / "weights.pt"

model = YOLO(str(weights_path))

def YOLO_cropper() -> bool:
  global bgr, h_img, w_img
  bgr = cv2.imread(str(last_frame))
  if bgr is None:
    print(f"Failed to load image from: {last_frame}")
    return False

  h_img, w_img = bgr.shape[:2]
  results = model.predict(
      source=bgr,
      imgsz=1280,
      conf=0.25,
      iou=0.65,  # higher iou keeps the wider overlapping Text box so we can merge both
      verbose=False,
  )

  text_boxes = []
  textbox_boxes = []

  for box in results[0].boxes:
    cls_name = model.names[int(box.cls[0])].strip().lower()
    score = float(box.conf[0])
    xyxy = tuple(map(int, box.xyxy[0].tolist()))
    if cls_name == "text":
      text_boxes.append((score, xyxy))
    elif cls_name == "textbox":
      textbox_boxes.append((score, xyxy))

  if not text_boxes or not textbox_boxes:
    return False

  # Union all detected Text boxes first
  tx1 = min(b[0] for _, b in text_boxes)
  ty1 = min(b[1] for _, b in text_boxes)
  tx2 = max(b[2] for _, b in text_boxes)
  ty2 = max(b[3] for _, b in text_boxes)

  by1 = min(b[1] for _, b in textbox_boxes)
  by2 = max(b[3] for _, b in textbox_boxes)
  bx1 = min(tx1, min(b[0] for _, b in textbox_boxes))
  bx2_raw = max(tx2, max(b[2] for _, b in textbox_boxes))

  # Snap right edge to the real <input> box border so "stopped and" / "crazily on its" aren't cut off
  full_x2 = find_full_right_edge(bgr, bx1, (by1 + by2) // 2, bx2_raw)

  save_crop(tx1, ty1, full_x2, ty2, crop_text_frame_path, pad=4)
  save_crop(bx1, by1, full_x2, by2, crop_textbox_frame_path, pad=4)

  return True

def find_full_right_edge(bgr_img: np.ndarray, x1: int, y_mid: int, fallback_x2: int) -> int:
  """Scan right along the input box row to find its grey right border."""
  row = bgr_img[max(0, y_mid - 2) : min(h_img, y_mid + 3), x1:]
  gray_row = cv2.cvtColor(row, cv2.COLOR_BGR2GRAY).mean(axis=0)
  # Inside the white input field, pixels are near 255; the right border drops below ~220
  # Start scanning past fallback_x2 - x1 (or past the placeholder text)
  start_offset = max(10, fallback_x2 - x1 - 10)
  for offset in range(start_offset, len(gray_row)):
    if gray_row[offset] < 220:
      return x1 + offset
  return fallback_x2

def save_crop(x1: int, y1: int, x2: int, y2: int, out_file: Path, pad: int = 4) -> None:
  cx1 = max(0, x1 - pad)
  cy1 = max(0, y1 - pad)
  cx2 = min(w_img, x2 + pad)
  cy2 = min(h_img, y2 + pad)
  crop = bgr[cy1:cy2, cx1:cx2]
  cv2.imwrite(str(out_file), crop)
  # print(f"Saved {out_file.name}: ({cx1}, {cy1}, {cx2}, {cy2})")

last_frame.parent.mkdir(parents=True, exist_ok=True)

while True:
    screenshot = pyautogui.screenshot()
    screenshot.save(f"last_saved_frame/lastframe.png")

    typeracer_box_detected = YOLO_cropper()

    if typeracer_box_detected:
        crop_text_frame = Image.open(crop_text_frame_path)
        crop_textbox_frame = Image.open(crop_textbox_frame_path)

        text = pytesseract.image_to_string(crop_textbox_frame, config=r'-l eng --oem 3 --psm 6' )

        keysentence = "Type the above text here when the race begins"

        if keysentence not in text:
            typewriting_raw_text = pytesseract.image_to_string(crop_text_frame, config="--psm 6")


            clean_text = re.sub(r"\s+", " ", typewriting_raw_text).strip()
            clean_text = (
                clean_text.replace("“", '"')
                .replace("”", '"')
                .replace("’", "'")
                .replace("‘", "'")
                .replace("—", "-")
                .replace("–", "-")
            )
            pyautogui.write(clean_text, interval)
    time.sleep(0.1)