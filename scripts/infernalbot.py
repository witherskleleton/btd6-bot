import time
from pynput.mouse import Controller, Button
from pynput.keyboard import Controller as KeyboardController

# Konstanten
COORDINATES = {
    'start': (832, 923),
    'click_1': (1339, 965),
    'click_2': (1390, 558),
    'click_3': (617, 417),
    'click_4': (1270, 438),
    'move_1': (1568, 481),
    'moab_select': (85, 369),
    'moab_confirm': (1534, 609),
    'hero': (833, 732),
    'final_1': (957, 889),
    'final_2': (957, 886),
    'final_3': (719, 843),
}

TIMINGS = {
    'initial': 3,
    'default': 0.5,
    'long': 1,
    'very_long': 2,
    'extreme': 100,
}

# Controller initialisieren
mouse = Controller()
keyboard = KeyboardController()


def click_and_wait(x, y, wait_time=TIMINGS['default']):
    """Klick auf Koordinaten und warten"""
    mouse.click(Button.left, 1)
    time.sleep(wait_time)


def move_and_wait(x, y, wait_time=TIMINGS['default']):
    """Maus bewegen und warten"""
    mouse.position = (x, y)
    time.sleep(wait_time)


def press_key(key, wait_time=TIMINGS['default']):
    """Taste drücken und warten"""
    keyboard.press(key)
    keyboard.release(key)
    time.sleep(wait_time)


def press_key_multiple(key, count, wait_time=TIMINGS['default']):
    """Taste mehrmals drücken"""
    for _ in range(count):
        press_key(key, wait_time)


def main():
    """Hauptfunktion des Bots"""

    # Initiale Wartezeit
    time.sleep(TIMINGS['initial'])

    # ---- STARTSEQUENZ ----
    mouse.position = COORDINATES['start']
    mouse.click(Button.left, 1)
    time.sleep(TIMINGS['long'])

    mouse.position = COORDINATES['click_1']
    mouse.click(Button.left, 1)
    time.sleep(TIMINGS['default'])

    mouse.position = COORDINATES['click_2']
    mouse.click(Button.left, 1)
    time.sleep(TIMINGS['default'])

    mouse.position = COORDINATES['click_3']
    mouse.click(Button.left, 1)
    time.sleep(TIMINGS['default'])

    mouse.position = COORDINATES['click_4']
    mouse.click(Button.left, 1)
    time.sleep(TIMINGS['very_long'])

    mouse.click(Button.left, 1)
    time.sleep(TIMINGS['very_long'])

    move_and_wait(*COORDINATES['move_1'])
    press_key('y')
    mouse.click(Button.left, 1)
    time.sleep(TIMINGS['default'])
    mouse.click(Button.left, 1)
    time.sleep(TIMINGS['default'])

    # ---- MOAB MONKEY ----
    mouse.position = COORDINATES['moab_select']
    mouse.click(Button.left, 1)
    time.sleep(TIMINGS['long'])

    press_key_multiple('1', 4, TIMINGS['default'])
    time.sleep(TIMINGS['long'])

    press_key_multiple('2', 2, TIMINGS['default'])
    time.sleep(TIMINGS['long'])

    move_and_wait(*COORDINATES['moab_confirm'])
    press_key('y')
    mouse.click(Button.left, 1)
    time.sleep(TIMINGS['default'])
    mouse.click(Button.left, 1)
    time.sleep(TIMINGS['default'])

    # ---- BLOONS MONKEY ----
    press_key_multiple('3', 5, TIMINGS['default'])
    press_key_multiple('2', 2, TIMINGS['default'])
    time.sleep(TIMINGS['long'])

    # ---- HERO ----
    move_and_wait(*COORDINATES['hero'])
    press_key('u')
    mouse.click(Button.left, 1)
    time.sleep(TIMINGS['default'])

    press_key_multiple('space', 2, TIMINGS['default'])
    time.sleep(TIMINGS['extreme'])

    mouse.position = COORDINATES['final_1']
    mouse.click(Button.left, 1)
    time.sleep(TIMINGS['extreme'])

    mouse.click(Button.left, 1)
    time.sleep(TIMINGS['extreme'])

    mouse.position = COORDINATES['final_2']
    mouse.click(Button.left, 1)
    time.sleep(TIMINGS['default'])

    mouse.position = COORDINATES['final_3']
    mouse.click(Button.left, 1)
    time.sleep(TIMINGS['long'])


if __name__ == '__main__':
    main()
