import cv2, random, pygame, time
from cvzone.HandTrackingModule import HandDetector

# Инициализируем детектор рук (максимум 1 рука для стабильности)
detector = HandDetector(maxHands=1)

class CreeperGame:
    def __init__(self):
        # Инициализация звукового движка Pygame
        pygame.mixer.init()
        self.boom_sound = pygame.mixer.Sound("./asset/boom.mp3")
        self.boom_sound.set_volume(0.2)
        
        # Загрузка текстуры Крипера с сохранением прозрачности (UNCHANGED)
        self.img = cv2.imread("./asset/creeper.png", cv2.IMREAD_UNCHANGED)
        # Подгоняем размер под пропорции Minecraft (высокий и узкий)
        self.img = cv2.resize(self.img, (80, 160)) if self.img is not None else None
        
        self.particles = []  # Список для частиц взрыва
        self.state = 0       # Состояния игры: 0 - Спокоен, 1 - Шипит (запал), 2 - Взорван
        self.boom_time = 0   # Таймер до момента взрыва

    def draw_creeper(self, img, cx, cy, is_red=False):
        """Метод для отрисовки Крипера поверх кадра камеры"""
        h, w = self.img.shape[:2]
        # Вычисляем верхний левый угол для вставки картинки
        x1, y1 = max(0, cx-w//2), max(0, cy-h//2)
        roi = img[y1:y1+h, x1:x1+w] # Область интереса на кадре
        
        if roi.shape[0] != h or roi.shape[1] != w: return
        
        overlay = self.img.copy()
        # Если Крипер "мигает", заменяем красный канал на максимум
        if is_red: overlay[:, :, 2] = 255
        
        # Работа с альфа-каналом (прозрачностью) для плавного наложения
        alpha = overlay[:, :, 3] / 255.0
        for c in range(3):
            img[y1:y1+h, x1:x1+w, c] = alpha * overlay[:,:,c] + (1-alpha) * img[y1:y1+h, x1:x1+w, c]

    def update_logic(self, img, cx, cy, length):
        """Основная механика: проверка жестов, таймеры и эффекты"""
        now = time.time()
        
        # Если пальцы сжаты (щипок) и Крипер спокоен — запускаем фитиль
        if length < 35 and self.state == 0:
            self.state = 1
            self.boom_time = now + 2.5 # Даем 2.5 секунды до взрыва
            self.boom_sound.play()
        
        if self.state == 1:
            # Эффект мигания красным (каждые 0.1 сек)
            self.draw_creeper(img, cx, cy, is_red=int(now*10)%2==0)
            
            # Если время вышло — взрываем!
            if now >= self.boom_time:
                self.state = 2
                # Генерируем 30 частиц (квадратиков) разного направления
                for _ in range(30):
                    self.particles.append([cx, cy, random.randint(-15,15), random.randint(-15,15), (0,random.randint(150,255),0), 20])
                img[:] = 255 # Эффект белой вспышки на весь экран
                
        elif self.state == 0:
            # Обычное состояние — просто рисуем Крипера в центре пальцев
            self.draw_creeper(img, cx, cy)
        
        # Если пальцы разжали — сбрасываем состояние взрыва (чтобы заспавнить нового)
        if length > 60 and self.state == 2: 
            self.state = 0
        
        # Логика полета частиц (движение по X и Y, уменьшение жизни)
        for p in self.particles[:]:
            p[0], p[1], p[5] = p[0]+p[2], p[1]+p[3], p[5]-1 # Двигаем и старим частицу
            if p[5] > 0: 
                # Рисуем частицу (квадрат), пока она "жива" (p[5] > 0)
                cv2.rectangle(img, (int(p[0]), int(p[1])), (int(p[0]+10), int(p[1]+10)), p[4], -1)
            else: 
                self.particles.remove(p)

    def handDetect(self, img):
        """Служебный метод для поиска руки и расчета координат"""
        hands, img = detector.findHands(img, draw=False)

        if hands:
            lmList = hands[0]['lmList'] # Список всех точек руки
            # Находим центральную точку между кончиками большого и указательного пальцев
            cx, cy = (lmList[4][0] + lmList[8][0]) // 2, (lmList[4][1] + lmList[8][1]) // 2
            # Считаем расстояние между ними для определения "клика"
            dist, _, _ = detector.findDistance(lmList[4][:2], lmList[8][:2])

            return cx, cy, dist
        return 0, 0, 1000 # Если руки нет, возвращаем дефолтные значения