import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector

class MinecraftAR:
    def __init__(self, grid_size=40, asset_path="./asset/dirt.png"):
        # Настройки сетки и хранилище для поставленных блоков
        self.GRID_SIZE = grid_size
        self.blocks = {}  # Словарь вида {(x, y): True}
        self.is_pressed = False # Флаг для предотвращения "дребезга" клика
        
        # Настройка камеры и детектора руки
        self.cap = cv2.VideoCapture(0)
        self.detector = HandDetector(detectionCon=0.7, maxHands=1)
        
        # Загружаем и подготавливаем текстуру блока
        self.block_img = self._prepare_asset(asset_path)

    def _prepare_asset(self, path):
        """Загрузка PNG, обрезка лишней прозрачности и ресайз под сетку"""
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is not None:
            # Если у картинки есть альфа-канал (прозрачность)
            if img.shape[2] == 4:
                alpha = img[:,:,3]
                # Находим все непрозрачные пиксели
                coords = cv2.findNonZero(alpha)
                if coords is not None:
                    # Обрезаем картинку строго по границам видимого объекта
                    x, y, w, h = cv2.boundingRect(coords)
                    img = img[y:y+h, x:x+w]
            
            # Масштабируем блок точно под размер ячейки сетки
            return cv2.resize(img, (self.GRID_SIZE, self.GRID_SIZE), interpolation=cv2.INTER_AREA)
        return None

    def overlay_block(self, background, x, y):
        """Метод для наложения текстуры блока на кадр камеры (с поддержкой прозрачности)"""
        # Если текстура не загрузилась, рисуем обычный зеленый квадрат
        if self.block_img is None:
            cv2.rectangle(background, (x, y), (x + self.GRID_SIZE, y + self.GRID_SIZE), (34, 139, 34), cv2.FILLED)
            return
        
        h, w = self.block_img.shape[:2]
        # Определяем границы рисования (чтобы не вылететь за края экрана)
        y1, y2 = max(0, y), min(background.shape[0], y + h)
        x1, x2 = max(0, x), min(background.shape[1], x + w)
        
        # Вырезаем нужные области для смешивания
        overlay_roi = self.block_img[max(0, -y):min(h, background.shape[0]-y), max(0, -x):min(w, background.shape[1]-x)]
        img_roi = background[y1:y2, x1:x2]

        # Математическое наложение через альфа-канал (формула Alpha Blending)
        if self.block_img.shape[2] == 4:
            alpha = overlay_roi[:, :, 3] / 255.0
            for c in range(3):
                img_roi[:, :, c] = (alpha * overlay_roi[:, :, c] + (1 - alpha) * img_roi[:, :, c])
        else:
            # Если прозрачности нет, просто заменяем пиксели
            img_roi[:, :] = overlay_roi[:, :, :3]

    def get_frame(self):
        """Захват кадра с камеры и его зеркальное отражение"""
        success, img = self.cap.read()
        if not success: return None
        return cv2.flip(img, 1)

    def update(self, img):
        """Поиск рук, расчет координат сетки и отрисовка всех блоков"""
        hands, img = self.detector.findHands(img, draw=False)
        data = None
        
        if hands:
            lmList = hands[0]['lmList']
            # Координаты кончиков большого (4) и указательного (8) пальцев
            p1, p2 = lmList[4][0:2], lmList[8][0:2]
            
            # Находим центр между пальцами (курсор)
            cx, cy = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2
            
            # Магия сетки: округляем координаты до ближайшего шага GRID_SIZE
            snap_x, snap_y = (cx // self.GRID_SIZE) * self.GRID_SIZE, (cy // self.GRID_SIZE) * self.GRID_SIZE
            
            # Считаем расстояние для фиксации "клика"
            length, _, _ = self.detector.findDistance(p1, p2)
            
            # Рисуем белый квадрат-предпросмотр (сетку)
            cv2.rectangle(img, (snap_x, snap_y), (snap_x + self.GRID_SIZE, snap_y + self.GRID_SIZE), (255, 255, 255), 2)
            
            # Собираем данные для файла main.py
            data = {"pos": (snap_x, snap_y), "clicked": length < 45}
        
        # Отрисовываем все блоки, которые хранятся в памяти (словаре)
        for (bx, by) in self.blocks:
            self.overlay_block(img, bx, by)
            
        return img, data