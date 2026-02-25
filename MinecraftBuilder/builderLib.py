import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector

class MinecraftAR:
    def __init__(self, grid_size=40, asset_path="./asset/dirt.png"):
        self.GRID_SIZE = grid_size
        self.blocks = {}
        self.is_pressed = False
        self.cap = cv2.VideoCapture(0)
        self.detector = HandDetector(detectionCon=0.7, maxHands=1)
        self.block_img = self._prepare_asset(asset_path)

    def _prepare_asset(self, path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is not None:
            if img.shape[2] == 4:
                alpha = img[:,:,3]
                coords = cv2.findNonZero(alpha)
                if coords is not None:
                    x, y, w, h = cv2.boundingRect(coords)
                    img = img[y:y+h, x:x+w]
            return cv2.resize(img, (self.GRID_SIZE, self.GRID_SIZE), interpolation=cv2.INTER_AREA)
        return None

    def overlay_block(self, background, x, y):
        if self.block_img is None:
            cv2.rectangle(background, (x, y), (x + self.GRID_SIZE, y + self.GRID_SIZE), (34, 139, 34), cv2.FILLED)
            return
        
        h, w = self.block_img.shape[:2]
        y1, y2 = max(0, y), min(background.shape[0], y + h)
        x1, x2 = max(0, x), min(background.shape[1], x + w)
        overlay_roi = self.block_img[max(0, -y):min(h, background.shape[0]-y), max(0, -x):min(w, background.shape[1]-x)]
        img_roi = background[y1:y2, x1:x2]

        if self.block_img.shape[2] == 4:
            alpha = overlay_roi[:, :, 3] / 255.0
            for c in range(3):
                img_roi[:, :, c] = (alpha * overlay_roi[:, :, c] + (1 - alpha) * img_roi[:, :, c])
        else:
            img_roi[:, :] = overlay_roi[:, :, :3]

    def get_frame(self):
        success, img = self.cap.read()
        if not success: return None
        return cv2.flip(img, 1)

    def update(self, img):
        hands, img = self.detector.findHands(img, draw=False)
        data = None
        if hands:
            lmList = hands[0]['lmList']
            p1, p2 = lmList[4][0:2], lmList[8][0:2]
            cx, cy = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2
            snap_x, snap_y = (cx // self.GRID_SIZE) * self.GRID_SIZE, (cy // self.GRID_SIZE) * self.GRID_SIZE
            
            length, _, _ = self.detector.findDistance(p1, p2)
            cv2.rectangle(img, (snap_x, snap_y), (snap_x + self.GRID_SIZE, snap_y + self.GRID_SIZE), (255, 255, 255), 2)
            data = {"pos": (snap_x, snap_y), "clicked": length < 45}
        
        for (bx, by) in self.blocks:
            self.overlay_block(img, bx, by)
        return img, data