import pygame
import random
import math
from settings import CAMERA_WIDTH, CAMERA_HEIGHT, FRUIT_SIZE, GRAVITY, MAX_FALL_SPEED, PLAYER_COLORS, INITIAL_UPWARD_VELOCITY, SLASH_THRESHOLD

class Fruit:
    def __init__(self, is_bomb=False):
        # Spawn from bottom area
        self.x = random.randint(100, CAMERA_WIDTH - 100)
        self.y = CAMERA_HEIGHT + FRUIT_SIZE
        self.radius = FRUIT_SIZE // 2
        
        # Random trajectory
        self.speed_y = INITIAL_UPWARD_VELOCITY + random.uniform(-3, 1)
        self.speed_x = random.uniform(-5, 5)
        
        self.is_bomb = is_bomb
        if self.is_bomb:
            self.color = (30, 30, 30) # Dark gray for bomb
        else:
            # Color variety (Apple red, etc.)
            self.color = random.choice([(220, 20, 60), (255, 69, 0), (255, 140, 0)])
            
        self.active = True
        self.is_cut = False
        self.cut_pieces = []

    def update(self):
        if not self.is_cut:
            self.speed_y += GRAVITY
            if self.speed_y > MAX_FALL_SPEED:
                self.speed_y = MAX_FALL_SPEED
            self.x += self.speed_x
            self.y += self.speed_y
            
            # Deactivate if it falls off screen
            if self.y > CAMERA_HEIGHT + 100 and self.speed_y > 0:
                self.active = False
        else:
            # Update cut pieces
            for piece in self.cut_pieces:
                piece['x'] += piece['vx']
                piece['y'] += piece['vy']
                piece['vy'] += GRAVITY
                piece['life'] -= 8
            
            self.cut_pieces = [p for p in self.cut_pieces if p['life'] > 0]
            if not self.cut_pieces:
                self.active = False

    def draw(self, surface):
        if not self.is_cut:
            if self.is_bomb:
                # Draw bomb
                pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius)
                pygame.draw.circle(surface, (255, 0, 0), (int(self.x), int(self.y)), self.radius, 3) # Red ring
                # Fuse
                pygame.draw.line(surface, (150, 150, 150), (self.x, self.y - self.radius), (self.x + 10, self.y - self.radius - 15), 3)
            else:
                # Apple shape
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
                pygame.draw.circle(surface, (255, 255, 255), (int(self.x - self.radius//3), int(self.y - self.radius//3)), self.radius//4)
        else:
            for piece in self.cut_pieces:
                alpha = piece['life']
                s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self.color, alpha), (self.radius, self.radius), self.radius)
                surface.blit(s, (int(piece['x']) - self.radius, int(piece['y']) - self.radius))

    def slash(self, p1, p2):
        if self.is_cut or not self.active:
            return False
            
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        
        if dx == 0 and dy == 0:
            return False
            
        t = ((self.x - p1[0]) * dx + (self.y - p1[1]) * dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t))
        
        closest_x = p1[0] + t * dx
        closest_y = p1[1] + t * dy
        
        dist = math.hypot(self.x - closest_x, self.y - closest_y)
        
        if dist < self.radius + 15:
            self.is_cut = True
            if self.is_bomb:
                # Bomb explosion pieces (sparks)
                self.cut_pieces = [ {'x': self.x, 'y': self.y, 'vx': random.uniform(-10, 10), 'vy': random.uniform(-10, 10), 'life': 255} for _ in range(10) ]
                self.color = (255, 255, 0) # Flash yellow
            else:
                self.cut_pieces = [
                    {'x': self.x, 'y': self.y, 'vx': -4, 'vy': -3, 'life': 255},
                    {'x': self.x, 'y': self.y, 'vx': 4, 'vy': -5, 'life': 255}
                ]
            return True
        return False

class Particle:
    def __init__(self, x, y, color, size=6):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 255
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= 12

    def draw(self, surface):
        if self.life > 0:
            s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.life), (self.size, self.size), self.size)
            surface.blit(s, (int(self.x) - self.size, int(self.y) - self.size))

class GameManager:
    def __init__(self):
        self.scores = {1: 0, 2: 0, 3: 0}
        self.fruits = []
        self.particles = []
        self.hand_history = {1: {"L": [], "R": []}, 2: {"L": [], "R": []}, 3: {"L": [], "R": []}}
        
        # Combo system
        self.combo_count = {1: 0, 2: 0, 3: 0}
        self.combo_timer = {1: 0, 2: 0, 3: 0}
        
        self.font_combo = pygame.font.SysFont(None, 48)

    def spawn_fruit(self):
        # 20% chance of a bomb
        is_bomb = random.random() < 0.2
        self.fruits.append(Fruit(is_bomb=is_bomb))

    def update(self, player_keypoints):
        # Update combo timers
        for pid in self.combo_timer:
            if self.combo_timer[pid] > 0:
                self.combo_timer[pid] -= 1
            else:
                self.combo_count[pid] = 0

        # Update hand history and check for slashes
        for pid, data in player_keypoints.items():
            if "keypoints" in data:
                kps = data["keypoints"]
                # Try to find wrists (9, 10 in COCO)
                left_hand = kps[9] if len(kps) > 9 else None
                right_hand = kps[10] if len(kps) > 10 else None
                
                for side, hand_pos in [("L", left_hand), ("R", right_hand)]:
                    if hand_pos:
                        history = self.hand_history[pid][side]
                        history.append(hand_pos)
                        if len(history) > 6: history.pop(0)
                        
                        if len(history) >= 2:
                            p1, p2 = history[-2], history[-1]
                            slash_dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
                            
                            if slash_dist > SLASH_THRESHOLD:
                                for fruit in self.fruits:
                                    if fruit.slash(p1, p2):
                                        if fruit.is_bomb:
                                            self.scores[pid] = max(0, self.scores[pid] - 5)
                                            self.combo_count[pid] = 0
                                            # Big explosion particles
                                            for _ in range(30):
                                                self.particles.append(Particle(fruit.x, fruit.y, (255, 100, 0), size=10))
                                        else:
                                            # Combo logic
                                            self.combo_count[pid] += 1
                                            self.combo_timer[pid] = 45 # 1.5 seconds at 30fps
                                            
                                            points = 1 + (self.combo_count[pid] // 3) # Bonus for every 3 fruits
                                            self.scores[pid] += points
                                            
                                            # Juice!
                                            color = PLAYER_COLORS.get(pid, (255, 255, 255))
                                            # Critical slash effect
                                            num_particles = 15 if slash_dist < 50 else 30
                                            for _ in range(num_particles):
                                                self.particles.append(Particle(fruit.x, fruit.y, fruit.color))

        # Update fruits & particles
        for fruit in self.fruits: fruit.update()
        self.fruits = [f for f in self.fruits if f.active]
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surface, player_keypoints):
        for fruit in self.fruits: fruit.draw(surface)
        for p in self.particles: p.draw(surface)
            
        # Draw "Sting Sword" & Combos
        for pid, sides in self.hand_history.items():
            color = PLAYER_COLORS.get(pid, (255, 255, 255))
            
            # Draw Combo text
            if self.combo_count[pid] >= 2:
                combo_text = self.font_combo.render(f"COMBO x{self.combo_count[pid]}", True, color)
                # Display near the last hand position
                last_pos = None
                if sides["R"]: last_pos = sides["R"][-1]
                elif sides["L"]: last_pos = sides["L"][-1]
                
                if last_pos:
                    surface.blit(combo_text, (last_pos[0] - 50, last_pos[1] - 80))

            for side, history in sides.items():
                if len(history) >= 2:
                    # Draw a trail
                    for i in range(len(history) - 1):
                        width = (i + 1) * 3
                        pygame.draw.line(surface, color, history[i], history[i+1], width)
                    
                    # Draw a "Sword" tip
                    tip, prev = history[-1], history[-2]
                    angle = math.atan2(tip[1] - prev[1], tip[0] - prev[0])
                    blade_len = 80
                    bx, by = tip[0] + math.cos(angle) * blade_len, tip[1] + math.sin(angle) * blade_len
                    pygame.draw.line(surface, (220, 220, 255), tip, (bx, by), 6) # Sword blade
                    pygame.draw.circle(surface, (255, 255, 255), tip, 10) # Hilt
