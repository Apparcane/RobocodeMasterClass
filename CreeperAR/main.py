import cv2
from creeperLib import CreeperGame # Импортируем наш игровой движок

# 1. Подключаемся к камере и создаем объект игры
cap = cv2.VideoCapture(0)
game = CreeperGame()

while True:
    # 2. Считываем кадр с камеры
    success, img = cap.read()
    if not success: break
    
    # 3. Зеркально отражаем изображение для удобства
    img = cv2.flip(img, 1)

    # 4. Просим библиотеку найти руку и вернуть нам координаты (cx, cy) и расстояние (dist)
    cx, cy, dist = game.handDetect(img)
    
    # 5. Если рука найдена (координаты не нулевые)
    if cx != 0 and cy != 0:
        # Запускаем логику Крипера: он будет следовать за рукой и проверять, не "кликнули" ли по нему
        game.update_logic(img, cx, cy, dist)

    # 6. Выводим результат в окно
    cv2.imshow("Robocode Masterclass", img)
    
    # 7. Условие выхода из игры при нажатии клавиши 'Q'
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

# Освобождаем ресурсы после закрытия
cap.release()
cv2.destroyAllWindows()