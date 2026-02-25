from builderLib import MinecraftAR
import cv2

game = MinecraftAR(grid_size=40)

while True:
    img = game.get_frame()
    img, info = game.update(img)

    if info and info["clicked"]:
        if not game.is_pressed:
            game.blocks[info["pos"]] = True
            game.is_pressed = True
    else:
        game.is_pressed = False

    cv2.imshow("Robocode: Minecraft AR", img)
    
    key = cv2.waitKey(1)
    if key == ord('q'): break
    if key == ord('c'): game.blocks = {}