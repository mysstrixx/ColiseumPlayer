import sys
import subprocess
import importlib
def check_and_install_requirements():
    required_packages = ['opencv-python', 'pyautogui', 'numpy', 'keyboard']
    for package in required_packages:
        try:
            if package == 'opencv-python':
                importlib.import_module('cv2')
            else:
                importlib.import_module(package)
            print(f"{package} is already installed.")
        except ImportError:
            print(f"{package} not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} has been installed.")
# Run the check at the start of the script
check_and_install_requirements()
# Now import the required packages
import cv2
import pyautogui
import numpy as np
import random
import keyboard
from time import sleep
from random import uniform
# Load images to detect
attack_menu_button = cv2.imread('attackmenu_button.png', cv2.IMREAD_UNCHANGED)
meditate_button = cv2.imread('meditate_button.png', cv2.IMREAD_UNCHANGED)
scratch_button = cv2.imread('scratch_button.png', cv2.IMREAD_UNCHANGED)
target_icon = cv2.imread('target_icon.png', cv2.IMREAD_UNCHANGED)
not_ready_button = cv2.imread('notready_button.png', cv2.IMREAD_UNCHANGED)
fight_on_button = cv2.imread('fighton_button.png', cv2.IMREAD_UNCHANGED)
# Try to load the remaining images
try:
    shred_button = cv2.imread('shred_button.png', cv2.IMREAD_UNCHANGED)
    print("Shred ability is available.")
except:
    print("Error loading 'shred_button.png'. Shred ability is not available.")
    shred_button = None
try:
    contuse_button = cv2.imread('contuse_button.png', cv2.IMREAD_UNCHANGED)
    print("Contuse ability is available.")
except:
    print("Error loading 'contuse_button.png'. Contuse ability is not available.")
    contuse_button = None
def find_image(image, confidence=0.9):
    img = pyautogui.screenshot(region=(1158, 344, 717, 607))
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    result = cv2.matchTemplate(img, image[:,:,:3], cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= confidence:
        top_left = (max_loc[0] + 1158, max_loc[1] + 344)
        bottom_right = (top_left[0] + image.shape[1], top_left[1] + image.shape[0])
        print(f"Found image at {(top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])} with confidence {max_val}")
        return (top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])
    print(f"Could not find image (highest confidence: {max_val})")
    return None
def human_like_click(loc, offset_y=0):
    center_x = loc[0] + loc[2] // 2
    center_y = loc[1] + loc[3] // 2 + offset_y
    x = center_x + random.randint(-5, 5)
    y = center_y + random.randint(-5, 5)
    pyautogui.moveTo(x, y, duration=uniform(0.2, 0.4))
    pyautogui.click()
    sleep(uniform(0.1, 0.3))
def check_and_click_fight_on():
    fight_on_loc = find_image(fight_on_button)
    if fight_on_loc:
        print("Fight On button found. Clicking...")
        human_like_click(fight_on_loc)
        return True
    return False
def wait_for_battle_state():
    attempts = 0
    while attempts < 5:
        if keyboard.is_pressed('esc'):
            print("Escape key pressed, exiting script...")
            sys.exit()
        attack_menu_loc = find_image(attack_menu_button)
        if attack_menu_loc:
            print("Attack menu button found.")
            return "attack"
        target_loc = find_image(target_icon, confidence=0.8)
        if target_loc:
            print("Target icon found.")
            return "target"
        not_ready_loc = find_image(not_ready_button)
        if not_ready_loc:
            print("Not ready button found, waiting...")
            sleep(uniform(1.0, 1.5))
        else:
            print("No recognizable battle state found. Waiting...")
            sleep(uniform(0.5, 1.0))
        if check_and_click_fight_on():
            return "fight_on"
        attempts += 1
    print("Warning: No recognizable battle state found after 5 attempts.")
    return None
def battle_loop():
    meditate_count = 0
    scratch_count = 0
    consecutive_waits = 0
    while True:
        print("\nStarting loop iteration")
        if keyboard.is_pressed('esc'):
            print("Escape key pressed, exiting script...")
            break
        battle_state = wait_for_battle_state()
        if battle_state is None:
            consecutive_waits += 1
            if consecutive_waits > 5:
                print("Error: Had to wait more than 5 times in a row. Checking for fight on button.")
                if check_and_click_fight_on():
                    consecutive_waits = 0
                    continue
                else:
                    print("Error: Could not find fight on button. Stopping script.")
                    break
            continue
        else:
            consecutive_waits = 0
        if battle_state == "fight_on":
            print("Clicked Fight On button. Waiting for next battle...")
            sleep(5)  # Wait for the next battle to start
            continue
        if battle_state == "attack":
            print("Clicking attack menu button...")
            human_like_click(find_image(attack_menu_button))
            sleep(uniform(0.5, 0.7))
            action_taken = False
            meditate_used = False
            # Check for contuse or shred first
            if contuse_button is not None:
                contuse_loc = find_image(contuse_button)
                if contuse_loc:
                    print("Clicking contuse button...")
                    human_like_click(contuse_loc)
                    action_taken = True
            if not action_taken and shred_button is not None:
                shred_loc = find_image(shred_button)
                if shred_loc:
                    print("Clicking shred button...")
                    human_like_click(shred_loc)
                    action_taken = True
            # If contuse and shred are not available or not found, use meditate or scratch
            if not action_taken:
                if meditate_count < 2:
                    meditate_loc = find_image(meditate_button)
                    if meditate_loc:
                        print("Clicking meditate button...")
                        human_like_click(meditate_loc)
                        meditate_count += 1
                        scratch_count = 0
                        action_taken = True
                        meditate_used = True
                if not action_taken:
                    scratch_loc = find_image(scratch_button)
                    if scratch_loc:
                        print("Clicking scratch button...")
                        human_like_click(scratch_loc)
                        scratch_count += 1
                        meditate_count = 0
                        action_taken = True
            # Reset counters if a special ability was used
            if action_taken and (contuse_button is not None or shred_button is not None):
                meditate_count = 0
                scratch_count = 0
        if (battle_state == "target" or (battle_state == "attack" and action_taken)) and not meditate_used:
            target_loc = find_image(target_icon, confidence=0.8)
            if target_loc:
                print(f"Clicking target at {target_loc}")
                human_like_click(target_loc, offset_y=60)
            else:
                print("Could not find target icon")
        sleep(uniform(0.7, 1.2))
print("Press 'Esc' to exit the script at any time.")
battle_loop()
