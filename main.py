import pygame
import sys
import numpy as np
from settings import CAMERA_WIDTH, CAMERA_HEIGHT, FPS, GAME_DURATION, FRUIT_SPAWN_RATE, PLAYER_COLORS, PLAYER_NAMES, BLACK, WHITE
from camera import TrackerCamera
from game import GameManager

def main():
    pygame.init()
    screen = pygame.display.set_mode((CAMERA_WIDTH, CAMERA_HEIGHT))
    pygame.display.set_caption("Fruit Ninja AR - Sting Sword Edition")
    clock = pygame.time.Clock()
    font_large = pygame.font.SysFont(None, 72)
    font_medium = pygame.font.SysFont(None, 48)

    camera = TrackerCamera()
    game = GameManager()

    frame_count = 0
    start_ticks = pygame.time.get_ticks()
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        if not game_over:
            # Calculate remaining time
            seconds = (pygame.time.get_ticks() - start_ticks) // 1000
            time_left = GAME_DURATION - seconds
            if time_left <= 0:
                time_left = 0
                game_over = True

            # Camera & Tracking Update
            rgb_frame, player_keypoints = camera.update()
            
            if rgb_frame is not None:
                # Convert frame to Pygame surface and draw as background
                # OpenCV image is (H, W, C), Pygame needs (W, H)
                surface = pygame.surfarray.make_surface(np.rot90(rgb_frame))
                surface = pygame.transform.flip(surface, False, True)
                screen.blit(surface, (0, 0))
            else:
                screen.fill(BLACK)

            # Game Logic Update
            frame_count += 1
            if frame_count % FRUIT_SPAWN_RATE == 0:
                game.spawn_fruit()

            game.update(player_keypoints)
            game.draw(screen, player_keypoints)

            # Draw Scores
            for pid, name in PLAYER_NAMES.items():
                color = PLAYER_COLORS.get(pid, WHITE)
                score_text = font_medium.render(f"{name}: {game.scores.get(pid, 0)}", True, color)
                # Position them across the top
                x_pos = 50 + (pid - 1) * (CAMERA_WIDTH // 3)
                screen.blit(score_text, (x_pos, 20))

            # Draw Timer
            timer_color = WHITE if time_left > 10 else (255, 50, 50)
            timer_text = font_large.render(f"Time: {time_left}", True, timer_color)
            screen.blit(timer_text, (CAMERA_WIDTH // 2 - timer_text.get_width() // 2, 80))

        else:
            # Game Over Screen
            screen.fill((30, 30, 30))
            go_text = font_large.render("GAME OVER", True, WHITE)
            screen.blit(go_text, (CAMERA_WIDTH // 2 - go_text.get_width() // 2, 200))
            
            # Show Final Scores
            y_offset = 300
            for pid, name in PLAYER_NAMES.items():
                color = PLAYER_COLORS.get(pid, WHITE)
                score_text = font_large.render(f"{name}: {game.scores.get(pid, 0)}", True, color)
                screen.blit(score_text, (CAMERA_WIDTH // 2 - score_text.get_width() // 2, y_offset))
                y_offset += 80

        pygame.display.flip()
        clock.tick(FPS)

    camera.release()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
