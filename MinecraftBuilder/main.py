from builderLib import MinecraftAR
import cv2

# 1. Создаем игру. Можно менять grid_size, чтобы блоки были больше или меньше
game = MinecraftAR(grid_size=40)

while True:
    # 2. Получаем новый кадр с веб-камеры
    img = game.get_frame()
    
    # 3. Обновляем игру: ищем руки и рисуем уже поставленные блоки
    # info вернет нам координаты курсора и статус "нажатия" (сведены ли пальцы)
    img, info = game.update(img)

    # 4. Проверяем: если рука в кадре и пальцы соединены ("клик")
    if info and info["clicked"]:
        # Если это новое нажатие (а не удержание)
        if not game.is_pressed:
            # Добавляем координаты блока в память (словарь blocks)
            game.blocks[info["pos"]] = True
            game.is_pressed = True # Помечаем, что кнопка "нажата"
    else:
        # Если пальцы разжали — сбрасываем флаг нажатия
        game.is_pressed = False

    # 5. Показываем результат на экране
    cv2.imshow("Robocode: Minecraft AR", img)
    
    # 6. Управление с клавиатуры
    key = cv2.waitKey(1)
    if key == ord('q'): # Выход на 'Q'
        break
    if key == ord('c'): # Очистка мира на 'C'
        game.blocks = {}