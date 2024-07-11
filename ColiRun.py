import cv2
import pyautogui
import numpy as np
import keyboard
from time import sleep
from random import uniform
from mss import mss
import os
# Screen resolution
screen_width, screen_height = pyautogui.size()
print(f"Screen resolution: {screen_width}x{screen_height}")
def load_image(file_name):
    img = cv2.imread(file_name, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Error loading '{file_name}'. File not found or invalid image.")
        return None
    if len(img.shape) == 3 and img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    return img
# Load images
attack_menu_button = load_image('attackmenu_button.png')
meditate_button = load_image('meditate_button.png')
scratch_button = load_image('scratch_button.png')
target_icon = load_image('target_icon.png')
not_ready_button = load_image('notready_button.png')
fight_on_button = load_image('fighton_button.png')
contuse_button = load_image('contuse_button.png')
shred_button = load_image('shred_button.png')
coliseum_target = load_image('ColiseumTarget.png')
flee_button = load_image('Flee_button.png')
def save_debug_image(image, filename):
    debug_dir = "debug_images"
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
    cv2.imwrite(os.path.join(debug_dir, filename), image)
def find_game_field():
    with mss() as sct:
        monitor = {"top": 0, "left": 0, "width": screen_width, "height": screen_height}
        screenshot = np.array(sct.grab(monitor))
    save_debug_image(screenshot, "full_screenshot.png")
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    gray_coliseum_target = cv2.cvtColor(coliseum_target, cv2.COLOR_BGR2GRAY)
    gray_flee_button = cv2.cvtColor(flee_button, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(gray_screenshot, gray_coliseum_target, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val > 0.7:  # Lowered threshold
        target_x, target_y = max_loc
        target_w, target_h = gray_coliseum_target.shape[::-1]
        flee_result = cv2.matchTemplate(gray_screenshot, gray_flee_button, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(flee_result)
        if max_val > 0.7:  # Lowered threshold
            flee_x, flee_y = max_loc
            flee_w, flee_h = gray_flee_button.shape[::-1]
            game_field_x = target_x
            game_field_y = target_y
            game_field_w = flee_x + flee_w - target_x
            game_field_h = flee_y + flee_h - target_y
            print(f"Game field found at: x={game_field_x}, y={game_field_y}, width={game_field_w}, height={game_field_h}")
            return (game_field_x, game_field_y, game_field_w, game_field_h)
    print("Game field not found.")
    return None
def find_image(image, game_field, confidence=0.7):  # Lowered default confidence
    if game_field is None or image is None:
        return None
    with mss() as sct:
        monitor = {"top": game_field[1], "left": game_field[0], "width": game_field[2], "height": game_field[3]}
        screenshot = np.array(sct.grab(monitor))
    img = cv2.cvtColor(screenshot, cv2.COLOR_RGBA2BGR)
    result = cv2.matchTemplate(img, image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= confidence:
        return (max_loc[0] + game_field[0], max_loc[1] + game_field[1], image.shape[1], image.shape[0])
    return None
def human_like_click(loc, offset_y=0):
    if loc is None:
        return
    center_x = loc[0] + loc[2] // 2
    center_y = loc[1] + loc[3] // 2 + offset_y
    pyautogui.moveTo(center_x, center_y, duration=uniform(0.2, 0.4))
    pyautogui.click()
    sleep(uniform(0.1, 0.3))
def check_and_click_fight_on(game_field):
    fight_on_loc = find_image(fight_on_button, game_field, confidence=0.7)  # Lowered confidence
    if fight_on_loc:
        print("Fight On button found. Clicking...")
        human_like_click(fight_on_loc)
        return True
    return False
def wait_for_battle_state(game_field):
    attempts = 0
    while attempts < 5:
        if keyboard.is_pressed('esc'):
            print("Escape key pressed, exiting script...")
            return None
        attack_menu_loc = find_image(attack_menu_button, game_field, confidence=0.7)  # Lowered confidence
        if attack_menu_loc:
            print("Attack menu button found.")
            return "attack"
        target_loc = find_image(target_icon, game_field, confidence=0.7)  # Lowered confidence
        if target_loc:
            print("Target icon found.")
            return "target"
        not_ready_loc = find_image(not_ready_button, game_field, confidence=0.7)  # Lowered confidence
        if not_ready_loc:
            print("Not ready button found, waiting...")
            sleep(uniform(1.0, 1.5))
        else:
            print("No recognizable battle state found. Waiting...")
            sleep(uniform(0.5, 1.0))
        if check_and_click_fight_on(game_field):
            return "fight_on"
        attempts += 1
    print("Warning: No recognizable battle state found after 5 attempts.")
    return None
def battle_loop(game_field):
    while True:
        print("\nStarting loop iteration")
        if keyboard.is_pressed('esc'):
            print("Escape key pressed, exiting script...")
            break
        not_ready_loc = find_image(not_ready_button, game_field, confidence=0.7)  # Lowered confidence
        if not_ready_loc:
            print("Not ready button found, waiting...")
            sleep(uniform(1.0, 1.5))
            continue
        attack_menu_loc = find_image(attack_menu_button, game_field, confidence=0.7)  # Lowered confidence
        if attack_menu_loc:
            print("Attack menu button found. Clicking...")
            human_like_click(attack_menu_loc)
            sleep(2)
            action_taken = False
            if shred_button is not None:
                shred_loc = find_image(shred_button, game_field, confidence=0.7)  # Lowered confidence
                if shred_loc:
                    print("Clicking shred button...")
                    human_like_click(shred_loc)
                    action_taken = True
            if not action_taken and contuse_button is not None:
                contuse_loc = find_image(contuse_button, game_field, confidence=0.7)  # Lowered confidence
                if contuse_loc:
                    print("Clicking contuse button...")
                    human_like_click(contuse_loc)
                    action_taken = True
            if not action_taken:
                scratch_loc = find_image(scratch_button, game_field, confidence=0.7)  # Lowered confidence
                if scratch_loc:
                    print("Clicking scratch button...")
                    human_like_click(scratch_loc)
                    action_taken = True
            if not action_taken:
                meditate_loc = find_image(meditate_button, game_field, confidence=0.7)  # Lowered confidence
                if meditate_loc:
                    print("Clicking meditate button...")
                    human_like_click(meditate_loc)
                    action_taken = True
            if action_taken:
                target_loc = find_image(target_icon, game_field, confidence=0.7)  # Lowered confidence
                if target_loc:
                    print(f"Clicking target at {target_loc}")
                    human_like_click(target_loc, offset_y=60)
                    while True:
                        sleep(uniform(0.7, 1.2))
                        new_battle_state = wait_for_battle_state(game_field)
                        if new_battle_state == "attack":
                            print("Attack successful, continuing...")
                            break
                        elif new_battle_state == "fight_on":
                            print("Clicked Fight On button. Waiting for next battle...")
                            sleep(5)
                            break
                        elif new_battle_state is None:
                            print("Error: Could not determine the next battle state.")
                            break
                else:
                    print("Could not find target icon after clicking an attack button.")
            else:
                print("Could not find any attack buttons.")
            if not action_taken or (action_taken and not target_loc):
                if check_and_click_fight_on(game_field):
                    print("Clicked Fight On button. Waiting for next battle...")
                    sleep(5)
                else:
                    print("Error: Could not find fight on button. Stopping script.")
                    return
        else:
            print("Could not find attack menu button.")
            if check_and_click_fight_on(game_field):
                print("Clicked Fight On button. Waiting for next battle...")
                sleep(5)
            else:
                print("Error: Could not find fight on button. Stopping script.")
                return
print("Press 'Esc' to exit the script at any time.")
game_field = find_game_field()
if game_field is None:
    print("Unable to locate the game field. Exiting script.")
else:
    print(f"Game field found at: x={game_field[0]}, y={game_field[1]}, width={game_field[2]}, height={game_field[3]}")
    battle_loop(game_field)
print("Script ended.")
