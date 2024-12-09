# Name: Faisal Alagil
# Title: Veloce
# Date: May 22, 2024
# Description: Movement game obstacle course

import pygame
import sys
import time
from pygame.math import Vector2

# Initialize Pygame
pygame.display.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
BLOCK_SIZE = 50

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GOLD = (255, 179, 0)

# Player settings
player_width, player_height = 40, 40
player_color = BLUE
player_gravity = 0.8
player_jump_speed = -12
player_acceleration = 1.5  # Adjust acceleration
max_player_speed = 7
max_fall_speed = 15

max_stamina = 100
dash_stamina_cost = 50
stamina_regeneration_rate = 1


# Camera settings
CAMERA_WIDTH = SCREEN_WIDTH
CAMERA_HEIGHT = SCREEN_HEIGHT

# Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Veloce")

# Clock
clock = pygame.time.Clock()

# Player class
# Camera ChatGPT "How do you create a camera in pygame and center the camera on a specific coordinate"
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = player_width
        self.height = player_height
        self.surf = pygame.Surface((self.width, self.height))
        self.surf.fill(player_color)
        self.rect = self.surf.get_rect(midbottom=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.rect.center = (600, 100)
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.friction = 1  # Adjust as needed
        self.stamina = max_stamina
        self.dash_distance = 150  # Default dash distance
        self.dash_speed = 20  # Default dash speed
        self.dash_timer = 0
        self.dash_direction = None
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                self.vel.x = 5
            elif event.key == pygame.K_a:
                self.vel.x = -5
            elif event.key == pygame.K_w:
                self.vel.y = -5
            elif event.key == pygame.K_s:
                self.vel.y = 5
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d and self.vel.x > 0:
                self.vel.x = 0
            elif event.key == pygame.K_a and self.vel.x < 0:
                self.vel.x = 0
            elif event.key == pygame.K_w:
                self.vel.y = 0
            elif event.key == pygame.K_s:
                self.vel.y = 0

    def move(self, dx):
        self.velocity_x += dx

    def jump(self):
        if self.on_ground:
            self.velocity_y = player_jump_speed

    def dash(self, direction):
        if self.stamina >= dash_stamina_cost:
            self.stamina -= dash_stamina_cost
            self.dash_timer = self.dash_distance / self.dash_speed
            self.dash_direction = direction

    def regenerate_stamina(self):
        if self.stamina < max_stamina:
            self.stamina = min(max_stamina, self.stamina + stamina_regeneration_rate)


    def apply_gravity(self):
        if self.velocity_y < max_fall_speed:
            self.velocity_y += player_gravity
            
    def update(self, blocks):
        # Save the previous position to check for collisions
        prev_x, prev_y = self.rect.x, self.rect.y

        # Update horizontal position
        self.rect.x += self.velocity_x
        self.velocity_x *= 0.9  # Apply friction

        # Cap max speed
        if abs(self.velocity_x) > max_player_speed:
            self.velocity_x = max_player_speed if self.velocity_x > 0 else -max_player_speed

        # Collision detection with walls
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.velocity_x > 0:
                    self.rect.right = block.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = block.rect.right

        # Update vertical position
        self.rect.y += self.velocity_y

        # Collision detection with floor
        self.on_ground = False
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if (block.type == 1):
                    start_time = time.time()
                    self.rect.topleft = (600, 0)  # Teleport the player to (0, 0)
                    self.velocity_x = 0
                    self.velocity_y = 0
                    self.stamina = max_stamina  # Reset stamina
                elif (block.type == 2):
                    self.rect.topleft = (5125, -100)  # Teleport the player to (0, 0)
                    self.velocity_x = 0
                    self.velocity_y = 0
                    self.stamina = max_stamina  # Reset stamina
                if self.velocity_y > 0:
                    self.rect.bottom = block.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:
                    self.rect.top = block.rect.bottom
                    self.velocity_y = 0

        # Apply gravity
        if not self.on_ground:
            self.velocity_y += player_gravity

        # If collided due to gravity, restore previous position
        if self.rect.collidelist([block.rect for block in blocks]) != -1:
            self.rect.x, self.rect.y = prev_x, prev_y


        self.regenerate_stamina()

        # Jumping logic
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]:
            self.jump()
        

        if keys[pygame.K_e]:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.dash("left")
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.dash("right")

        if self.dash_timer > 0:
            self.dash_timer -= 1
            if self.dash_direction == "left":
                self.rect.x -= self.dash_speed
            elif self.dash_direction == "right":
                self.rect.x += self.dash_speed
            if self.dash_timer <= 0:
                self.dash_timer = 0
                self.dash_direction = None


# Block class
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, type=0,):
        super().__init__()
        self.surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        if (type == 1):
            self.surf.fill(RED)
        elif (type == 2) or (type == 3):
            self.surf.fill(GOLD)
        else:
            self.surf.fill(WHITE)
        self.rect = self.surf.get_rect(topleft=(x, y))
        self.type = type    

# Camera class
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)

        # Limit scrolling to the dimensions of the level
        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - SCREEN_WIDTH), x)
        y = max(-(self.height - SCREEN_HEIGHT), y)
        # Calculate the center of the screen
        screen_center = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # Calculate the target position for the camera
        target_pos = screen_center - target.rect.center

        # Calculate the difference between the current camera position and the target position
        diff_x = target_pos.x - self.camera.x
        diff_y = target_pos.y - self.camera.y

        # Define a smoothing factor (adjust as needed)
        smoothing = 0.1

        # Update the camera position based on the smoothing factor
        self.camera.x += diff_x * smoothing
        self.camera.y += diff_y * smoothing


# Level definition using an array of objects
level = [
    {"position": "0,400", "type": 1},  # Lava floor
    {"position": "50,400", "type": 1},
    {"position": "100,400", "type": 1},
    {"position": "150,400", "type": 1},
    {"position": "200,400", "type": 1},
    {"position": "250,400", "type": 1},
    {"position": "300,400", "type": 1},
    {"position": "350,400", "type": 1},
    {"position": "400,400", "type": 1},
    {"position": "450,400", "type": 1},
    {"position": "500,400", "type": 1},
    {"position": "550,400", "type": 1},
    {"position": "600,400", "type": 1},
    {"position": "650,400", "type": 1},
    {"position": "700,400", "type": 1},
    {"position": "750,400", "type": 1},
    {"position": "800,400", "type": 1},
    {"position": "850,400", "type": 1},
    {"position": "900,400", "type": 1},
    {"position": "950,400", "type": 1},
    {"position": "1000,400", "type": 1},
    {"position": "1050,400", "type": 1},
    {"position": "1100,400", "type": 1},
    {"position": "1150,400", "type": 1},
    {"position": "1200,400", "type": 1},
    {"position": "1250,400", "type": 1},
    {"position": "1300,400", "type": 1},
    {"position": "1350,400", "type": 1},
    {"position": "1400,400", "type": 1},
    {"position": "1450,400", "type": 1},
    {"position": "1500,400", "type": 1},
    {"position": "1550,400", "type": 1},
    {"position": "1600,400", "type": 1},
    {"position": "1650,400", "type": 1},
    {"position": "1700,400", "type": 1},
    {"position": "1750,400", "type": 1},
    {"position": "1800,400", "type": 1},
    {"position": "1850,400", "type": 1},
    {"position": "1900,400", "type": 1},
    {"position": "1950,400", "type": 1},
    {"position": "2000,400", "type": 1},
    {"position": "2050,400", "type": 1},
    {"position": "2100,400", "type": 1},
    {"position": "2150,400", "type": 1},
    {"position": "2200,400", "type": 1},
    {"position": "2250,400", "type": 1},
    {"position": "2300,400", "type": 1},
    {"position": "2350,400", "type": 1},
    {"position": "2400,400", "type": 1},
    {"position": "2450,400", "type": 1},
    {"position": "2500,400", "type": 1},
    {"position": "2550,400", "type": 1},
    {"position": "2600,400", "type": 1},
    {"position": "2650,400", "type": 1},
    {"position": "2700,400", "type": 1},
    {"position": "2750,400", "type": 1},
    {"position": "2800,400", "type": 1},
    {"position": "2850,400", "type": 1},
    {"position": "2900,400", "type": 1},
    {"position": "2950,400", "type": 1},
    {"position": "3000,400", "type": 1},
    {"position": "3050,400", "type": 1},
    {"position": "3100,400", "type": 1},
    {"position": "3150,400", "type": 1},
    {"position": "3200,400", "type": 1},
    {"position": "3250,400", "type": 1},
    {"position": "3300,400", "type": 1},
    {"position": "3350,400", "type": 1},
    {"position": "3400,400", "type": 1},
    {"position": "3450,400", "type": 1},
    {"position": "3500,400", "type": 1},
    {"position": "3550,400", "type": 1},
    {"position": "3600,400", "type": 1},
    {"position": "3650,400", "type": 1},
    {"position": "3700,400", "type": 1},
    {"position": "3750,400", "type": 1},
    {"position": "3800,400", "type": 1},
    {"position": "3850,400", "type": 1},
    {"position": "3900,400", "type": 1},
    {"position": "3950,400", "type": 1},
    {"position": "4000,400", "type": 1},
    {"position": "4050,400", "type": 1},
    {"position": "4100,400", "type": 1},
    {"position": "4150,400", "type": 1},
    {"position": "4200,400", "type": 1},
    {"position": "4250,400", "type": 1},
    {"position": "4300,400", "type": 1},
    {"position": "4350,400", "type": 1},
    {"position": "4400,400", "type": 1},
    {"position": "4450,400", "type": 1},
    {"position": "4500,400", "type": 1},
    {"position": "4550,400", "type": 1},
    {"position": "4600,400", "type": 1},
    {"position": "4650,400", "type": 1},
    {"position": "4700,400", "type": 1},
    {"position": "4750,400", "type": 1},
    {"position": "4800,400", "type": 1},
    {"position": "4850,400", "type": 1},
    {"position": "4900,400", "type": 1},
    {"position": "4950,400", "type": 1},
    {"position": "5000,400", "type": 1},
    {"position": "5050,400", "type": 1},
    {"position": "5100,400", "type": 1},
    {"position": "5150,400", "type": 1},
    {"position": "5200,400", "type": 1},
    {"position": "5250,400", "type": 1},
    {"position": "5300,400", "type": 1},
    {"position": "550,100", "type": 0},
    {"position": "600,100", "type": 0},
    {"position": "650,100", "type": 0},
    {"position": "700,100", "type": 0},
    {"position": "750,100", "type": 0},
    {"position": "750,50", "type": 0},
    {"position": "850,100", "type": 0},
    {"position": "900,100", "type": 0},
    {"position": "1100,50", "type": 0},
    {"position": "1500,30", "type": 0},
    {"position": "1600,-50", "type": 0},
    {"position": "1750,30", "type": 0},
    {"position": "1850,80", "type": 0},
    {"position": "1900,80", "type": 0},
    {"position": "1950,80", "type": 0},
    {"position": "2000,80", "type": 0},
    {"position": "2000,-20", "type": 0},
    {"position": "2000,-70", "type": 0},
    {"position": "2000,-120", "type": 0},
    {"position": "2300,20", "type": 0},
    {"position": "2300,120", "type": 0},
    {"position": "2400,160", "type": 0},
    {"position": "2500,160", "type": 2},

    
    {"position": "5000,0", "type": 3},
    {"position": "5000,-50", "type": 3},
    {"position": "5050,0", "type": 3},
    {"position": "5100,0", "type": 3},
    {"position": "5150,0", "type": 3},
    {"position": "5200,0", "type": 3},
    {"position": "5250,0", "type": 3},
    {"position": "5250,-50", "type": 3},
]

blocks = pygame.sprite.Group()
for block_info in level:
    x, y = map(int, block_info["position"].split(','))
    block = Block(x, y, block_info["type"])
    blocks.add(block)

player = Player()
camera = Camera(CAMERA_WIDTH, CAMERA_HEIGHT)
# Game loop
running = True
start_time = time.time()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP:
                player.jump()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.move(-player_acceleration)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.move(player_acceleration)

    player.update(blocks)
    # Update camera position
    camera.update(player)

    # Drawing
    screen.fill((38, 204, 255))  # Clear screen with black
    for block in blocks:
        screen.blit(block.surf, camera.apply(block))  # Apply camera offset
    screen.blit(player.surf, camera.apply(player))  # Apply camera offset

    # # Drawing
    # screen.fill((38, 204, 255))  # Clear screen with black
    # for block in blocks:
    #     screen.blit(block.surf, block.rect)
    # screen.blit(player.surf, player.rect)


    player_rect = player.rect
    # Draw stamina bar at the top left corner of the screen
    stamina_bar_width = (player.stamina / max_stamina) * 200
    stamina_bar_rect = pygame.Rect(12, 12, stamina_bar_width, 15)
    empty_stamina_bar_rect = pygame.Rect(10, 10, 205, 20)
    pygame.draw.rect(screen, WHITE, empty_stamina_bar_rect)
    pygame.draw.rect(screen, BLACK, empty_stamina_bar_rect)
    pygame.draw.rect(screen, BLUE, stamina_bar_rect)

    pygame.display.flip()
    clock.tick(FPS)

    # Dynamic acceleration after 2 seconds
    if time.time() - start_time >= 2:
        max_player_speed = 10  # Increase max speed after 2 seconds

pygame.quit()
sys.exit()
