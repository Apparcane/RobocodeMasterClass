import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector

# --- НАСТРОЙКИ ---
GRID_SIZE = 40 
blocks = {}
is_pressed = False 

cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.7, maxHands=1)

# Загрузка и подготовка текстуры
block_img = cv2.imread("./asset/dirt.png", cv2.IMREAD_UNCHANGED)
if block_img is not None:
    # Обрезаем прозрачные края
    if block_img.shape[2] == 4:
        alpha = block_img[:,:,3]
        coords = cv2.findNonZero(alpha)
        if coords is not None:
            x_img, y_img, w_img, h_img = cv2.boundingRect(coords)
            block_img = block_img[y_img:y_img+h_img, x_img:x_img+w_img]
    
    # Ресайз строго в размер сетки
    block_img = cv2.resize(block_img, (GRID_SIZE, GRID_SIZE), interpolation=cv2.INTER_AREA)

def overlay_block(background, overlay, x, y):
    h, w = overlay.shape[:2]
    y1, y2 = max(0, y), min(background.shape[0], y + h)
    x1, x2 = max(0, x), min(background.shape[1], x + w)
    
    overlay_y1, overlay_y2 = max(0, -y), min(h, background.shape[0] - y)
    overlay_x1, overlay_x2 = max(0, -x), min(w, background.shape[1] - x)

    if x2 <= x1 or y2 <= y1: return background

    img_roi = background[y1:y2, x1:x2]
    overlay_roi = overlay[overlay_y1:overlay_y2, overlay_x1:overlay_x2]

    if overlay.shape[2] == 4:
        alpha = overlay_roi[:, :, 3] / 255.0
        for c in range(3):
            img_roi[:, :, c] = (alpha * overlay_roi[:, :, c] + (1 - alpha) * img_roi[:, :, c])
    else:
        img_roi[:, :] = overlay_roi[:, :, :3]
    return background

while True:
    success, img = cap.read()
    if not success: break
    img = cv2.flip(img, 1)
    
    hands, img = detector.findHands(img, draw=False)

    if hands:
        lmList = hands[0]['lmList']
        x1, y1 = lmList[4][0:2]
        x2, y2 = lmList[8][0:2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        snap_x = (cx // GRID_SIZE) * GRID_SIZE
        snap_y = (cy // GRID_SIZE) * GRID_SIZE

        cv2.rectangle(img, (snap_x, snap_y), (snap_x + GRID_SIZE, snap_y + GRID_SIZE), (255, 255, 255), 2)

        length, _, _ = detector.findDistance((x1, y1), (x2, y2))

        if length < 45:
            if not is_pressed:
                if (snap_x, snap_y) not in blocks:
                    blocks[(snap_x, snap_y)] = True
                is_pressed = True 
        else:
            is_pressed = False 

    for (bx, by) in blocks:
        if block_img is not None:
            overlay_block(img, block_img, bx, by)
        else:
            cv2.rectangle(img, (bx, by), (bx + GRID_SIZE, bx + GRID_SIZE), (34, 139, 34), cv2.FILLED)

    cv2.imshow("Robocode: Minecraft AR", img)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): break
    if key == ord('c'): blocks = {}

cap.release()
cv2.destroyAllWindows()