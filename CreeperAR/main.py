import cv2
from creeperLib import CreeperGame # Наша самописная библиотека

cap = cv2.VideoCapture(0)
game = CreeperGame()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    cx, cy, dist = game.handDetect(img)
    if cx != 0 and cy != 0:
        game.update_logic(img, cx, cy, dist)

    cv2.imshow("Robocode Masterclass", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break