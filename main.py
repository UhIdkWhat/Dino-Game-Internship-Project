"""Dino Game in Python

A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by intern: @bassemfarid, no one or nothing else. 🤖
"""
score = 0
kept_score = 0
difficulty = 1
set_score = 500
import pygame
x = 1
# Initialize Pygame and create a window
pygame.init()
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()
running = True  # Pygame main loop, kills pygame when False

# Game state variables
is_playing = True  # Whether in game or in menu
GROUND_Y = 300  # The Y-coordinate of the ground level
JUMP_GRAVITY_START_SPEED = -20  # The speed at which the player jumps
players_gravity_speed = 0  # The current speed at which the player falls
increase_gravity = -25 #change in gravity 
# Load level assets
SKY_SURF = pygame.image.load("graphics/level/sky.png").convert()
GROUND_SURF = pygame.image.load("graphics/level/ground.png").convert()
game_font = pygame.font.Font(pygame.font.get_default_font(), 50)

# Load sprite assets
player_surf = pygame.image.load("graphics/player/player_walk_1.png").convert_alpha()
player_rect = player_surf.get_rect(bottomleft=(25, GROUND_Y))
egg_surf = pygame.image.load("graphics/egg/egg_1.png").convert_alpha()
egg_rect = egg_surf.get_rect(bottomleft=(800, GROUND_Y))


while running:
    # Poll for events
    for event in pygame.event.get():
        # pygame.QUIT --> user clicked X to close your window
        if event.type == pygame.QUIT:
            running = False

        elif is_playing:
            # When player wants to jump by pressing SPACE
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
                or event.type == pygame.MOUSEBUTTONDOWN
            ) and player_rect.bottom >= GROUND_Y:
                players_gravity_speed = JUMP_GRAVITY_START_SPEED

        else:
            # When player wants to play again by pressing SPACE
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                is_playing = True
                egg_rect.left = 800

    if is_playing:
        screen.fill("purple")  # Wipe the screen
        kept_score = 0
        # Blit the level assets
        screen.blit(SKY_SURF, (0, 0))
        screen.blit(GROUND_SURF, (0, GROUND_Y))
        score_surf = game_font.render(f"SCORE: {score:.0f}", False, "Black")
        score_rect = score_surf.get_rect(topleft=(10, 0))
        pygame.draw.rect(screen, "#c0e8ec", score_rect)
        pygame.draw.rect(screen, "#c0e8ec", score_rect, 10)
        screen.blit(score_surf, score_rect)

        # Adjust egg's horizontal location then blit it depending on difficulty
        if difficulty == 1:
            egg_rect.x -= 5 * difficulty
            if egg_rect.right <= 0:
                egg_rect.left = 800
            screen.blit(egg_surf, egg_rect)
        elif difficulty > 1 and difficulty < 4:
            egg_rect.x -= 5 * (difficulty/1.5)
            if egg_rect.right <= 0:
                egg_rect.left = 800
            screen.blit(egg_surf, egg_rect)
        else:
            egg_rect.x -= 5 * difficulty
            if egg_rect.right <= 0:
                egg_rect.left = 800
            screen.blit(egg_surf, egg_rect)

        # Adjust player's vertical location then blit it
        players_gravity_speed += 1
        player_rect.y += players_gravity_speed
        if player_rect.bottom > GROUND_Y:
            player_rect.bottom = GROUND_Y
        screen.blit(player_surf, player_rect)
        # Increasing difficulty and increasing the amount of score you get
        if score == 500:
            difficulty += 1
        elif score == set_score * difficulty:
            difficulty +=1
        if score < 500:
            score += 0.5
        else:
            score += 1
        # When player collides with enemy, game ends resets all variables
        if egg_rect.colliderect(player_rect):
            is_playing = False
            kept_score += score
            score = 0
            difficulty = 1


    # When game is over, display game over message
    else:
        screen.fill("black")

    # flip the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # Limits game loop to 60 FPS

pygame.quit()
