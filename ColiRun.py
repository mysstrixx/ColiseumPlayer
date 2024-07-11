import cv2
import pyautogui
import numpy as np
import keyboard
from time import sleep
from random import uniform
from mss import mss
import os
import time
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
    if max_val > 0.7:
        target_x, target_y = max_loc
        target_w, target_h = gray_coliseum_target.shape[::-1]
        flee_result = cv2.matchTemplate(gray_screenshot, gray_flee_button, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(flee_result)
        if max_val > 0.7:
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
def find_image(image, game_field, confidence=0.7, check_greyed=False):
    if game_field is None or image is None:
        return None
    with mss() as sct:
        monitor = {"top": game_field[1], "left": game_field[0], "width": game_field[2], "height": game_field[3]}
        screenshot = np.array(sct.grab(monitor))
    img = cv2.cvtColor(screenshot, cv2.COLOR_RGBA2BGR)
    result = cv2.matchTemplate(img, image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= confidence:
        x, y = max_loc
        w, h = image.shape[1], image.shape[0]
        if check_greyed:
            roi = img[y:y+h, x:x+w]
            avg_color = np.mean(roi, axis=(0, 1))
            if np.all(avg_color < 100):
                print(f"Button found but appears to be greyed out. Avg color: {avg_color}")
                return None
        return (x + game_field[0], y + game_field[1], w, h)
    return None
def human_like_click(loc, offset_y=0):
    if loc is None:
        return
    center_x = loc[0] + loc[2] // 2
    center_y = loc[1] + loc[3] // 2 + offset_y
    pyautogui.moveTo(center_x, center_y, duration=uniform(0.1, 0.2))  # Faster mouse movement
    pyautogui.click()
    sleep(uniform(0.05, 0.1))  # Shorter delay after clicking
def check_and_click_fight_on(game_field):
    fight_on_loc = find_image(fight_on_button, game_field, confidence=0.7)
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
        attack_menu_loc = find_image(attack_menu_button, game_field, confidence=0.7)
        if attack_menu_loc:
            print("Attack menu button found.")
            return "attack"
        target_loc = find_image(target_icon, game_field, confidence=0.7)
        if target_loc:
            print("Target icon found.")
            return "target"
        not_ready_loc = find_image(not_ready_button, game_field, confidence=0.7)
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
        not_ready_loc = find_image(not_ready_button, game_field, confidence=0.7)
        if not_ready_loc:
            print("Not ready button found, waiting...")
            sleep(uniform(1.0, 1.5))
            continue
        attack_menu_loc = find_image(attack_menu_button, game_field, confidence=0.7)
        if attack_menu_loc:
            print("Attack menu button found. Clicking...")
            human_like_click(attack_menu_loc)
            sleep(2)
            # Check all available buttons first
            available_actions = []
            shred_greyed = contuse_greyed = False
            if shred_button is not None:
                shred_loc = find_image(shred_button, game_field, confidence=0.7, check_greyed=True)
                if shred_loc:
                    available_actions.append(("shred", shred_loc))
                else:
                    print("Shred button not available or greyed out.")
                    shred_greyed = True
            if contuse_button is not None:
                contuse_loc = find_image(contuse_button, game_field, confidence=0.7, check_greyed=True)
                if contuse_loc:
                    available_actions.append(("contuse", contuse_loc))
                else:
                    print("Contuse button not available or greyed out.")
                    contuse_greyed = True
            scratch_loc = find_image(scratch_button, game_field, confidence=0.7, check_greyed=True)
            if scratch_loc:
                available_actions.append(("scratch", scratch_loc))
            else:
                print("Scratch button not available or greyed out.")
            meditate_loc = find_image(meditate_button, game_field, confidence=0.7, check_greyed=True)
            if meditate_loc:
                available_actions.append(("meditate", meditate_loc))
            else:
                print("Meditate button not available or greyed out.")
            # Choose the best available action
            action_taken = False
            if available_actions:
                if shred_greyed or contuse_greyed:
                    print("Either Shred or Contuse is greyed out. Using Scratch or Meditate instead.")
                    for action, loc in available_actions:
                        if action == "scratch":
                            print("Clicking scratch button...")
                            human_like_click(loc)
                            action_taken = True
                            break
                        elif action == "meditate":
                            print("Clicking meditate button...")
                            human_like_click(loc)
                            action_taken = True
                            break
                else:
                    # Prioritize actions: shred > contuse > scratch > meditate
                    for action, loc in available_actions:
                        if action == "shred":
                            print("Clicking shred button...")
                            human_like_click(loc)
                            action_taken = True
                            break
                        elif action == "contuse":
                            print("Clicking contuse button...")
                            human_like_click(loc)
                            action_taken = True
                            break
                        elif action == "scratch":
                            print("Clicking scratch button...")
                            human_like_click(loc)
                            action_taken = True
                            break
                        elif action == "meditate":
                            print("Clicking meditate button...")
                            human_like_click(loc)
                            action_taken = True
                            break
            if action_taken:
                target_loc = find_image(target_icon, game_field, confidence=0.7)
                if target_loc:
                    print(f"Clicking target at {target_loc}")
                    human_like_click(target_loc, offset_y=60)
                    target_click_time = time.time()
                    consecutive_target_finds = 0
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
                        elif new_battle_state == "target":
                            consecutive_target_finds += 1
                            if consecutive_target_finds >= 3:
                                print("Target icon found multiple times. Attempting fallback strategy...")
                                break
                        elif new_battle_state is None:
                            if time.time() - target_click_time > 10:  # 10-second timeout
                                print("Timeout reached. Attempting fallback strategy...")
                                break
                        else:
                            print(f"Unexpected battle state: {new_battle_state}")
                            break
                else:
                    print("Could not find target icon after clicking an attack button.")
            else:
                print("Could not find any available attack buttons.")
            # Fallback strategy
            if not action_taken or consecutive_target_finds >= 3 or (time.time() - target_click_time > 10):
                print("Executing fallback strategy...")
                fallback_action_taken = False
                # Try meditate first
                meditate_loc = find_image(meditate_button, game_field, confidence=0.7)
                if meditate_loc:
                    print("Clicking Meditate as fallback...")
                    human_like_click(meditate_loc)
                    fallback_action_taken = True
                # If meditate not available, try scratch
                if not fallback_action_taken:
                    scratch_loc = find_image(scratch_button, game_field, confidence=0.7)
                    if scratch_loc:
                        print("Clicking Scratch as fallback...")
                        human_like_click(scratch_loc)
                        fallback_action_taken = True
                        # Click enemy target after scratch
                        target_loc = find_image(target_icon, game_field, confidence=0.7)
                        if target_loc:
                            print(f"Clicking target at {target_loc}")
                            human_like_click(target_loc, offset_y=60)
                        else:
                            print("Could not find target icon after clicking Scratch.")
                # New retry mechanism
                retry_count = 0
                while retry_count < 3:
                    print(f"Checking for attack menu or not ready button (Attempt {retry_count + 1}/3)...")
                    attack_menu_loc = find_image(attack_menu_button, game_field, confidence=0.7)
                    not_ready_loc = find_image(not_ready_button, game_field, confidence=0.7)
                    if attack_menu_loc or not_ready_loc:
                        print("Found attack menu or not ready button. Continuing...")
                        break
                    sleep(uniform(0.5, 1.0))  # Short wait between attempts
                    retry_count += 1
                else:
                    print("Could not find attack menu or not ready button after 3 attempts. Ending script.")
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
