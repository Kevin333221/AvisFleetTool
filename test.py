import pyautogui as py
import time

alphabet = "abcdefghijklmnopqrstuvwxyz"
time.sleep(3)

for letter in alphabet:
    for letter2 in alphabet:
        py.write(letter + letter2)
        py.press("enter")
        time.sleep(1)
        py.hotkey("shift", "tab")