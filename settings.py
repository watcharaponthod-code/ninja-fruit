# settings.py
import pygame

# Camera Settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
FPS = 30

# Game Settings
GAME_DURATION = 60 # seconds
FRUIT_SPAWN_RATE = 30 # Frames between spawns
FRUIT_SIZE = 60

# Physics
GRAVITY = 0.4
MAX_FALL_SPEED = 15
INITIAL_UPWARD_VELOCITY = -18 # For fruits jumping up

# Slashing
SLASH_THRESHOLD = 15 # Minimum movement to count as a slash
SWORD_LENGTH = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

PLAYER_COLORS = {
    1: RED,
    2: GREEN,
    3: BLUE
}

PLAYER_NAMES = {
    1: "Player 1 (Left)",
    2: "Player 2 (Center)",
    3: "Player 3 (Right)"
}
