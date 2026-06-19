import cv2
import numpy as np

def find_lines(proj, threshold_ratio=0.5):
    indices = np.where(proj > np.max(proj) * threshold_ratio)[0]
    if len(indices) == 0:
        return []

    lines = []
    current = [indices[0]]

    for i in indices[1:]:
        if i - current[-1] <= 2:
            current.append(i)
        else:
            lines.append(int(np.mean(current)))
            current = [i]

    lines.append(int(np.mean(current)))
    return lines


def is_uniform(lines, expected_count, tolerance=0.2):
    if len(lines) != expected_count:
        return False

    diffs = np.diff(lines)
    avg = np.mean(diffs)

    for d in diffs:
        if abs(d - avg) > tolerance * avg:
            return False

    return True


def detect_and_crop_grid(image_path, m, n, padding=10):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # binary image
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # detect horizontal lines
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel)

    # detect vertical lines
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel)

    # projections
    h_proj = np.sum(horizontal, axis=1)
    v_proj = np.sum(vertical, axis=0)

    h_lines = find_lines(h_proj)
    v_lines = find_lines(v_proj)

    # --- VALIDATION ---
    if not is_uniform(h_lines, m + 1):
        return None, "Invalid or missing horizontal grid"

    if not is_uniform(v_lines, n + 1):
        return None, "Invalid or missing vertical grid"

    # --- BOUNDING BOX ---
    y_min, y_max = h_lines[0], h_lines[-1]
    x_min, x_max = v_lines[0], v_lines[-1]

    # --- APPLY PADDING ---
    h, w = gray.shape

    y_min = max(0, y_min - padding)
    y_max = min(h, y_max + padding)
    x_min = max(0, x_min - padding)
    x_max = min(w, x_max + padding)

    cropped = img[y_min:y_max, x_min:x_max]

    return cropped, None

def detect_galaxy_centers(cropped_img, m, n, padding=10):
    gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)

    # Blur helps blob detection
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect circles (galaxy centers)
    circles = cv2.HoughCircles(
        blur,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=10,
        param1=50,
        param2=20,
        minRadius=8,
        maxRadius=12
    )

    if circles is None:
        return []

    circles = np.uint16(np.around(circles[0]))

    h, w = gray.shape

    # Estimate cell size
    cell_w = (w- 2*padding) / n
    cell_h = (h-2*padding) / m

    centers = []

    for (px, py, r) in circles:
        # Convert pixel -> cell coordinates
        gx = (px-padding) / cell_w
        gy = (py-padding) / cell_h

        # Convert to half-cell grid
        hx = int(round(gx * 2)) - 1
        hy = int(round(gy * 2)) - 1

        centers.append((hy, hx))

    # Remove duplicates
    centers = list(set(centers))

    return centers
