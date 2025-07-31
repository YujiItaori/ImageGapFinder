import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

INPUT_DIR = 'input'
OUTPUT_DIR = 'output'

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Find all valid before-after pairs
def get_image_pairs(input_dir):
    before_after_pairs = []
    files = os.listdir(input_dir)
    for file in files:
        if file.endswith('.jpg') and '~2' not in file and '~3' not in file:
            before = file
            after = file.replace('.jpg', '~2.jpg')
            if after in files:
                before_after_pairs.append((before, after))
    return before_after_pairs

# Compare images and highlight changes
def highlight_changes(before_img, after_img):
    gray_before = cv2.cvtColor(before_img, cv2.COLOR_BGR2GRAY)
    gray_after = cv2.cvtColor(after_img, cv2.COLOR_BGR2GRAY)

    score, diff = ssim(gray_before, gray_after, full=True)
    diff = (diff * 255).astype("uint8")

    _, thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        if cv2.contourArea(cnt) > 100:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(after_img, (x, y), (x + w, y + h), (0, 0, 255), 2)

    return after_img

def process_images():
    pairs = get_image_pairs(INPUT_DIR)
    print(f"Found {len(pairs)} image pairs.")

    for before_name, after_name in pairs:
        before_path = os.path.join(INPUT_DIR, before_name)
        after_path = os.path.join(INPUT_DIR, after_name)

        before_img = cv2.imread(before_path)
        after_img = cv2.imread(after_path)

        if before_img is None or after_img is None:
            print(f"Error reading: {before_name} or {after_name}")
            continue

        result_img = highlight_changes(before_img, after_img)

        # Save as X~3.jpg
        output_name = before_name.replace('.jpg', '~3.jpg')
        output_path = os.path.join(OUTPUT_DIR, output_name)
        cv2.imwrite(output_path, result_img)
        print(f"Saved: {output_path}")

if __name__ == "__main__":
    process_images()
