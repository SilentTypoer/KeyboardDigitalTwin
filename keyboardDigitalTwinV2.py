import pygame
from pynput import keyboard
import cv2
import numpy as np
from pathlib import Path


class Key:
    def __init__(self, pos, size, symbol):
        self.pos = pos
        self.size = size
        self.mainbgColor = WHITE
        self.bgColor = WHITE
        self.fgColor = BLACK
        self.symbol = symbol
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.font = pygame.font.SysFont("arial", int(size[1] * 0.35))
        self.simplifySymbol()

    def simplifySymbol(self):
        if self.symbol.__contains__("CTRL"):
            self.symbol = "CTRL"
        elif self.symbol.__contains__("SHIFT"):
            self.symbol = "SHIFT"
        elif self.symbol.__contains__("BACKSPACE"):
            self.symbol = "<--"
        elif self.symbol.__contains__("SPACE"):
            self.symbol = " "
        elif self.symbol.__contains__("CAPS_LOCK"):
            self.symbol = "CAPS"
        elif self.symbol.__contains__("ALT"):
            self.symbol = "ALT"
        elif self.symbol.__contains__("FUNC"):
            self.symbol = "FN"
        elif self.symbol.__contains__("SILENT"):
            self.mainbgColor = BLUE
            self.bgColor = BLUE
            self.fgColor = WHITE
            self.symbol = "SilentTypœr"
            self.font = pygame.font.SysFont("arial", int(self.size[1] * 0.4))

    def setColor(self, bgColor, fgColor):
        self.bgColor = bgColor
        self.fgColor = fgColor

    def draw(self, screen):
        pygame.draw.rect(screen, self.bgColor, self.rect)
        text = self.font.render(self.symbol, True, self.fgColor)
        screen.blit(
            text,
            (
                self.pos[0] + ((self.size[0] - text.get_width())) / 2,
                self.pos[1] + ((self.size[1] - text.get_height())) / 2,
            ),
        )

    def rescale(self):
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        # self.font = pygame.font.SysFont("arial", int(self.size[1] * 0.45))


pygame.init()
clock = pygame.time.Clock()

BLACK, WHITE = (0, 0, 0), (255, 255, 255)

GRAY = (150, 150, 150)
BLUE = (0, 0, 128)

SCREEN_SIZE = 1500
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE / 2), pygame.RESIZABLE)
pygame.display.set_caption("Keyboard Digital Twin"), screen.fill(GRAY)

isRecording = False

hasStartedRecording = False

closeWindow = False


layout = [
    ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "backspace"],
    ["tab", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\"],
    ["caps_lock", "a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "enter"],
    ["shift", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "shift_r"],
    [
        "ctrl_l",
        "func_l",
        "cmd",
        "alt_l",
        "space",
        "alt_gr",
        "func_r",
        "ctrl_r",
        "SilentTypœr",
    ],
]

# Match layout names
keySizeRatio = {
    "`": 1,
    "1": 1,
    "2": 1,
    "3": 1,
    "4": 1,
    "5": 1,
    "6": 1,
    "7": 1,
    "8": 1,
    "9": 1,
    "0": 1,
    "-": 1,
    "=": 1,
    "backspace": 2,
    "tab": 1.66,
    "q": 1,
    "w": 1,
    "e": 1,
    "r": 1,
    "t": 1,
    "y": 1,
    "u": 1,
    "i": 1,
    "o": 1,
    "p": 1,
    "[": 1,
    "]": 1,
    "\\": 1.33,
    "caps_lock": 2,
    "a": 1,
    "s": 1,
    "d": 1,
    "f": 1,
    "g": 1,
    "h": 1,
    "j": 1,
    "k": 1,
    "l": 1,
    ";": 1,
    "'": 1,
    "enter": 2.33,
    "shift": 2.66,
    "z": 1,
    "x": 1,
    "c": 1,
    "v": 1,
    "b": 1,
    "n": 1,
    "m": 1,
    ",": 1,
    ".": 1,
    "/": 1,
    "shift_r": 3,
    "ctrl_l": 1.33,
    "func_l": 1,
    "cmd": 1,
    "alt_l": 1,
    "space": 6,
    "alt_gr": 1,
    "func_r": 1,
    "ctrl_r": 1,
    "SilentTypœr": 2,
}
width = 0
spacing = 10

keys = {}

screenshotRegion = {
    "left": 225,
    "top": 350,
    "width": 400,
    "height": 100,
}


outputIndex = 0


def setWidthHelper(maxWidth, amountOfRegularKeys, listOfSpecialKeys):
    return (maxWidth - (amountOfRegularKeys * spacing) - spacing) / (
        sum([keySizeRatio[skey] for skey in listOfSpecialKeys]) + amountOfRegularKeys
    )


def setWidth():
    # width = (maxWidth - (amountOfRegularKeys * spacing) - spacing)/([[i=0, i < n]∑widthRatioOfSpecialKeys_i] + amountOfRegularKeys)

    row1Width = setWidthHelper(screen.get_width(), 13, ["backspace"])
    row2Width = setWidthHelper(screen.get_width(), 12, ["tab", "\\"])
    row3Width = setWidthHelper(screen.get_width(), 11, ["caps_lock", "enter"])
    row4Width = setWidthHelper(screen.get_width(), 10, ["shift", "shift_r"])
    row5Width = setWidthHelper(
        screen.get_width(), 6, ["ctrl_l", "space", "SilentTypœr"]
    )
    return min(
        row1Width,
        row2Width,
        row3Width,
        row4Width,
        row5Width,
    )


def setup():
    keys.clear()
    for y, row in enumerate(layout):
        startX = spacing * 2
        for key in row:
            keys.update(
                {
                    key: Key(
                        [startX, y * (width + spacing) + spacing * 2],
                        [width * keySizeRatio[key], width],
                        key.upper(),
                    )
                }
            )
            startX += spacing + width * keySizeRatio[key]
    minRowWidth = min([sum([keys[key].size[0] for key in row]) for row in layout])
    for i, row in enumerate(layout):
        keys[row[len(row) - 1]].size[0] = minRowWidth - sum(
            [keys[key].size[0] for i, key in enumerate(row) if i < len(row) - 1]
        )
        if i > 1:
            keys[row[len(row) - 1]].size[0] += (i - 1) * spacing
        if i == len(layout) - 1:
            keys[row[len(row) - 1]].size[0] += 2 * spacing
        keys[row[len(row) - 1]].rescale()


def on_press(key):
    global isRecording, hasStartedRecording
    try:
        [
            keys[keyTwin].setColor((0, 255, 0), keys[keyTwin].fgColor)
            for keyTwin in keys.keys()
            if keyTwin == key.char
        ]
        if not isRecording:
            hasStartedRecording = True
            isRecording = True
            print("startedRecording")
    except:
        [
            keys[keyTwin].setColor((0, 255, 0), keys[keyTwin].fgColor)
            for keyTwin in keys.keys()
            if keyTwin == str(key).split(".")[1]
        ]


def on_release(key):
    global isRecording
    try:
        [
            keys[keyTwin].setColor(keys[keyTwin].mainbgColor, keys[keyTwin].fgColor)
            for keyTwin in keys.keys()
            if keyTwin == key.char
        ]
    except:
        [
            keys[keyTwin].setColor(keys[keyTwin].mainbgColor, keys[keyTwin].fgColor)
            for keyTwin in keys.keys()
            if keyTwin == str(key).split(".")[1]
        ]

    if key == keyboard.Key.esc:
        if isRecording:
            isRecording = False
        return False


if __name__ == "__main__":
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    width = setWidth()
    setup()
    screen = pygame.display.set_mode(
        (
            screen.get_width(),
            (
                width * 5 + spacing * 8
                if width * 5 + spacing * 8 % 2 == 0
                else width * 5 + spacing * 8 + 1
            ),
        ),
        pygame.RESIZABLE,
    )
    print(screen.get_height())
    fps = 24

    outputIndex = 0

    twinRecFilePath = Path("videos/twinRec0.mp4")

    while twinRecFilePath.is_file():
        outputIndex += 1
        twinRecFilePath = Path("videos/twinRec" + str(outputIndex) + ".mp4")

    writer = cv2.VideoWriter(
        twinRecFilePath,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (screen.get_width(), screen.get_height()),
    )
    while not closeWindow:
        screen.fill(GRAY)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if not isRecording:
                    closeWindow = True
                    if not hasStartedRecording:
                        writer.release()
                        twinRecFilePath.unlink(missing_ok=True)
                    if writer.isOpened():
                        writer.release()
                else:
                    isRecording = False
                    writer.release()
                    if not hasStartedRecording:
                        twinRecFilePath.unlink(missing_ok=True)
                    closeWindow = True
            elif event.type == pygame.VIDEORESIZE:
                width = setWidth()
                setup()
                screen = pygame.display.set_mode(
                    (
                        screen.get_width(),
                        (
                            width * 5 + spacing * 8
                            if width * 5 + spacing * 8 % 2 == 0
                            else width * 5 + spacing * 8 + 1
                        ),
                    ),
                    pygame.RESIZABLE,
                )
        [key.draw(screen) for key in keys.values()]

        # borders
        pygame.draw.rect(
            screen,
            BLUE,
            pygame.Rect(screen.get_width() - spacing, 0, spacing, screen.get_height()),
        )
        pygame.draw.rect(
            screen,
            BLUE,
            pygame.Rect(0, 0, spacing, screen.get_height()),
        )
        pygame.draw.rect(
            screen,
            BLUE,
            pygame.Rect(0, 0, screen.get_width(), spacing),
        )
        pygame.draw.rect(
            screen,
            BLUE,
            pygame.Rect(0, screen.get_height() - spacing, screen.get_width(), spacing),
        )

        pygame.display.update()
        clock.tick(fps)
        if isRecording:
            # Record digital twin
            writer.write(
                cv2.cvtColor(
                    np.transpose(pygame.surfarray.array3d(screen), (1, 0, 2)),
                    cv2.COLOR_RGB2BGR,
                )
            )
