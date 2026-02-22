import cv2, random, pygame, time
from cvzone.HandTrackingModule import HandDetector

detector = HandDetector(maxHands=1)

class CreeperGame:
    def __init__(self):
        pygame.mixer.init()
        self.boom_sound = pygame.mixer.Sound("./asset/boom.mp3")
        self.boom_sound.set_volume(0.2)
        self.img = cv2.imread("./asset/creeper.png", cv2.IMREAD_UNCHANGED)
        self.img = cv2.resize(self.img, (80, 160)) if self.img is not None else None
        self.particles = []
        self.state = 0 # 0: Idle, 1: Fuse, 2: Boomed
        self.boom_time = 0

    def draw_creeper(self, img, cx, cy, is_red=False):
        h, w = self.img.shape[:2]
        x1, y1 = max(0, cx-w//2), max(0, cy-h//2)
        roi = img[y1:y1+h, x1:x1+w]
        if roi.shape[0] != h or roi.shape[1] != w: return
        overlay = self.img.copy()
        if is_red: overlay[:, :, 2] = 255
        alpha = overlay[:, :, 3] / 255.0
        for c in range(3):
            img[y1:y1+h, x1:x1+w, c] = alpha * overlay[:,:,c] + (1-alpha) * img[y1:y1+h, x1:x1+w, c]

    def update_logic(self, img, cx, cy, length):
        now = time.time()
        if length < 35 and self.state == 0:
            self.state = 1
            self.boom_time = now + 2.5
            self.boom_sound.play()
        
        if self.state == 1:
            self.draw_creeper(img, cx, cy, is_red=int(now*10)%2==0)
            if now >= self.boom_time:
                self.state = 2
                for _ in range(30):
                    self.particles.append([cx, cy, random.randint(-15,15), random.randint(-15,15), (0,random.randint(150,255),0), 20])
                img[:] = 255
        elif self.state == 0:
            self.draw_creeper(img, cx, cy)
        
        if length > 60 and self.state == 2: self.state = 0
        
        for p in self.particles[:]:
            p[0], p[1], p[5] = p[0]+p[2], p[1]+p[3], p[5]-1
            if p[5] > 0: cv2.rectangle(img, (int(p[0]), int(p[1])), (int(p[0]+10), int(p[1]+10)), p[4], -1)
            else: self.particles.remove(p)

    def handDetect(self, img):
        hands, img = detector.findHands(img, draw=False)

        if hands:
            lmList = hands[0]['lmList']
            # 1. Находим центр между пальцами
            cx, cy = (lmList[4][0] + lmList[8][0]) // 2, (lmList[4][1] + lmList[8][1]) // 2
            # 2. Считаем расстояние
            dist, _, _ = detector.findDistance(lmList[4][:2], lmList[8][:2])

            return cx, cy, dist
        return 0, 0, 1000
