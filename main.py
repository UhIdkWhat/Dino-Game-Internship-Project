"""Dino Game in Python

A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by intern: @bassemfarid, no one or nothing else. 🤖
"""
score = 0
kept_score = 0
difficulty = 1
set_score = 500
import pygame
from random import randint

# Initialize Pygame and create a window
pygame.init()
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()
running = True  # Pygame main loop, kills pygame when False

# Event timer for spawning obstacles
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 900)

# High scores file
HIGHSCORE_FILE = "highscores.txt"

# Game state variables
is_playing = False  # Whether in game or in menu
show_intro = True  # Whether the intro screen is visible
game_over = False  # Whether the death screen is visible
GROUND_Y = 300  # The Y-coordinate of the ground level
JUMP_GRAVITY_START_SPEED = -16.5  # The speed at which the player jumps
players_gravity_speed = 0  # The current speed at which the player falls
jump_count = 0  # 0 = grounded, 1 = jumped once, 2 = double-jumped
health = 3  # Player health/lives
last_hit_time = 0  # For collision cooldown
final_score = 0
final_time = 0.0

# Load level assets
SKY_SURF = pygame.image.load("graphics/level/castle.png").convert() 
GROUND_SURF = pygame.image.load("graphics/level/ground.png").convert()
game_font = pygame.font.Font(pygame.font.get_default_font(), 50)

# Sky scrolling
sky_x = 0
sky_scroll_speed = 2

# Load sprite assets
player_idle = pygame.image.load("graphics/player/e0.png").convert_alpha()
player_jump_1 = pygame.image.load("graphics/player/e1.png").convert_alpha()
player_jump_2= pygame.image.load("graphics/player/e2.png").convert_alpha()
player_jump_3 = pygame.image.load("graphics/player/e3.png").convert_alpha()
player_jump_4 = pygame.image.load("graphics/player/e4.png").convert_alpha()
player_jump_5 = pygame.image.load("graphics/player/e5.png").convert_alpha()
player_jump_6 = pygame.image.load("graphics/player/e6.png").convert_alpha()
player_jump_7 = pygame.image.load("graphics/player/e7.png").convert_alpha()
player_jump_8 = pygame.image.load("graphics/player/e8.png").convert_alpha()
player_jump = [player_jump_1, player_jump_2, player_jump_3, player_jump_4, player_jump_5, player_jump_6, player_jump_7, player_jump_8]
jump_frame_index = 0.0
jump_anim_speed = 0.35
player_image = player_idle
player_rect = player_image.get_rect(bottomleft=(25, GROUND_Y))
wall_surf = pygame.image.load("graphics/enemy/wall.png").convert_alpha() 
wall_rect = wall_surf.get_rect(bottomleft=(800, GROUND_Y))

# Load flying arrow enemy
arrow_surf = pygame.image.load("graphics/enemy/arrow.png").convert_alpha()
arrow_rect = arrow_surf.get_rect(topleft=(800, 100))
arrow_speed = 5
arrow_active = False

# Load ruby collectible
ruby_surf = pygame.image.load("graphics/enemy/ruby.png").convert_alpha()
ruby_rect = ruby_surf.get_rect(bottomleft=(800, GROUND_Y))
ruby_speed = 6
ruby_active = False

RUBY_JUMP_OFFSET = 110

# gameplay timer
start_time = pygame.time.get_ticks()

# Enemy/wall state
wall_speed = 5
wall_active = True
game_over_zoom = 1.0
zoom_speed = 0.03

# intro / end screens
start_surf = pygame.transform.scale(
    pygame.image.load("graphics/level/start.png").convert_alpha(), (800, 400)
)
end_surf = pygame.transform.scale(
    pygame.image.load("graphics/level/end.png").convert_alpha(), (800, 400)
)
# High score utilities
def load_highscores(path=HIGHSCORE_FILE):
    try:
        with open(path, "r") as f:
            lines = [int(l.strip()) for l in f.readlines() if l.strip().isdigit()]
        return sorted(lines, reverse=True)[:10]
    except FileNotFoundError:
        return []

def save_highscores(scores, path=HIGHSCORE_FILE):
    scores = sorted(scores, reverse=True)[:10]
    with open(path, "w") as f:
        for s in scores:
            f.write(f"{int(s)}\n")

highscores = load_highscores()
while running:
    # Poll for events
    for event in pygame.event.get():
        # pygame.QUIT --> user clicked X to close your window
        if event.type == pygame.QUIT:
            running = False

        elif is_playing:
            # When player wants to jump by pressing SPACE or clicking
            if (
                (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)
                or event.type == pygame.MOUSEBUTTONDOWN
            ):
                # Ground jump
                if player_rect.bottom >= GROUND_Y:
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED
                    jump_frame_index = 0.0
                    jump_count = 1
                # Allow one double-jump while airborne
                elif jump_count == 1:
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED
                    jump_frame_index = 0.0
                    jump_count = 2

        # When game is not playing (menu), start on SPACE
        if not is_playing and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            is_playing = True
            show_intro = False
            game_over = False
            wall_active = False
            arrow_active = False
            ruby_active = False
            wall_rect.left = 800
            arrow_rect.left = 800
            ruby_rect.left = 800
            score = 0
            difficulty = 1
            health = 3
            last_hit_time = 0
            sky_x = 0
            start_time = pygame.time.get_ticks()

        

        # Obstacle spawn timer: activate wall or arrow spawn when timer fires
        if event.type == obstacle_timer and is_playing:
            spawn_type = randint(0, 2)  # 0 = wall, 1 = arrow, 2 = ruby
            
            if spawn_type == 0 and not wall_active:
                # Spawn wall at ground level
                wall_active = True
                wall_rect.left = 800
                wall_speed = randint(5, 8) + (difficulty * 1.5)
            elif spawn_type == 1 and not arrow_active:
                # Spawn arrow at random sky height
                arrow_active = True
                arrow_rect.left = 800
                arrow_rect.top = randint(50, 200)  # Random height in sky
                arrow_speed = randint(5, 8) + (difficulty * 1.5)
            elif spawn_type == 2 and not ruby_active:
                # Spawn ruby collectible only when theres no enemies in the same position
                if not wall_active and not arrow_active:
                    ruby_active = True
                    ruby_speed = randint(5, 7) + (difficulty * 0.5)
                    if randint(0, 1) == 0:
                        ruby_rect.bottomleft = (800, GROUND_Y)
                    else:
                        ruby_rect.bottomleft = (800, GROUND_Y - RUBY_JUMP_OFFSET)
            
            # Schedule next spawn interval (shorter at higher difficulty)
            min_interval = max(300, 700 - (difficulty * 50))
            max_interval = max(500, 1400 - (difficulty * 100))
            pygame.time.set_timer(obstacle_timer, randint(min_interval, max_interval))

    if is_playing:
        screen.fill("black")  # Wipe the screen
        kept_score = 0
        # Update and blit scrolling sky (speed increases with difficulty)
        sky_x -= sky_scroll_speed + (difficulty * 0.3)
        if sky_x <= -800:  # Wrap sky when it scrolls off
            sky_x = 0
        screen.blit(SKY_SURF, (sky_x, 0))
        screen.blit(SKY_SURF, (sky_x + 800, 0))  # Second copy for seamless wrap
        # Blit ground
        screen.blit(GROUND_SURF, (0, GROUND_Y))
        score_surf = game_font.render(f"SCORE: {score:.0f}", False, "Black")
        score_rect = score_surf.get_rect(topleft=(10, 0))
        screen.blit(score_surf, score_rect)
        
        # Display health
        health_font = pygame.font.Font(pygame.font.get_default_font(), 36)
        health_surf = health_font.render(f"HEALTH: {health}", False, "Red")
        health_rect = health_surf.get_rect(topleft=(10, 50))
        screen.blit(health_surf, health_rect)

        # Adjust wall's horizontal location then blit it depending on whether it's active
        if wall_active:
            wall_rect.x -= wall_speed
            screen.blit(wall_surf, wall_rect)
            if wall_rect.right <= 0:
                # deactivate and schedule next spawn
                wall_active = False
                wall_rect.left = 800
                min_interval = max(300, 700 - (difficulty * 50))
                max_interval = max(500, 1400 - (difficulty * 100))
                pygame.time.set_timer(obstacle_timer, randint(min_interval, max_interval))

        # Adjust arrow's horizontal location then blit it
        if arrow_active:
            arrow_rect.x -= arrow_speed
            screen.blit(arrow_surf, arrow_rect)
            if arrow_rect.right <= 0:
                # deactivate and schedule next spawn
                arrow_active = False
                arrow_rect.left = 800
                min_interval = max(300, 700 - (difficulty * 50))
                max_interval = max(500, 1400 - (difficulty * 100))
                pygame.time.set_timer(obstacle_timer, randint(min_interval, max_interval))

        # Adjust ruby's horizontal location then blit it
        if ruby_active:
            ruby_rect.x -= ruby_speed
            screen.blit(ruby_surf, ruby_rect)
            if ruby_rect.right <= 0:
                # deactivate and schedule next spawn
                ruby_active = False
                ruby_rect.left = 800
                min_interval = max(300, 700 - (difficulty * 50))
                max_interval = max(500, 1400 - (difficulty * 100))
                pygame.time.set_timer(obstacle_timer, randint(min_interval, max_interval))

        # Adjust player's vertical location then blit it
        players_gravity_speed += 1
        player_rect.y += players_gravity_speed

        if player_rect.bottom < GROUND_Y:
            # In air: play jump animation
            jump_frame_index += jump_anim_speed
            if jump_frame_index >= len(player_jump):
                jump_frame_index = len(player_jump) - 1

            old_bottomleft = player_rect.bottomleft
            player_image = player_jump[int(jump_frame_index)]
            player_rect = player_image.get_rect(bottomleft=old_bottomleft)
        else:
            # On ground: reset to idle and reset jump state
            player_rect.bottom = GROUND_Y
            players_gravity_speed = 0
            jump_frame_index = 0.0
            jump_count = 0

            old_bottomleft = player_rect.bottomleft
            player_image = player_idle
            player_rect = player_image.get_rect(bottomleft=old_bottomleft)

        screen.blit(player_image, player_rect)
        # Increasing difficulty and increasing the amount of score you get
        if score == 500:
            difficulty += 1
        elif score == set_score * difficulty:
            difficulty +=1
        if score < 500:
            score += 0.5
        else:
            score += 1
        
        # Collect ruby pickups independently of the damage cooldown
        if ruby_active and ruby_rect.colliderect(player_rect):
            score += 50
            ruby_active = False
            ruby_rect.left = 800

        # When player collides with wall or arrow enemy, lose health
        current_time = pygame.time.get_ticks()
        if (current_time - last_hit_time > 500):
            if wall_active and wall_rect.colliderect(player_rect):
                health -= 1
                last_hit_time = current_time
                wall_active = False
            elif arrow_active and arrow_rect.colliderect(player_rect):
                health -= 1
                last_hit_time = current_time
                arrow_active = False
        
        if health <= 0:
            is_playing = False
            game_over = True
            final_score = int(score)
            hs = load_highscores()
            hs.append(final_score)
            save_highscores(hs)
            highscores = load_highscores()
            kept_score += score
            score = 0
            difficulty = 1
            # reset transition zoom
            game_over_zoom = 1.0
            # record final time
            final_time = (pygame.time.get_ticks() - start_time) / 1000


    # When game is not playing, show either the intro or the game over screen
    elif show_intro:
        screen.fill("purple")
        screen.blit(start_surf, (0, 0))

        small = pygame.font.Font(pygame.font.get_default_font(), 24)
        title = small.render("Press SPACE to start", False, "Black")
        title_rect = title.get_rect(center=(400, 320))
        screen.blit(title, title_rect)

    else:
        screen.fill("purple")
        screen.blit(end_surf, (0, 0))

        # show previous high score
        hs_font = pygame.font.Font(pygame.font.get_default_font(), 28)
        if highscores:
            prev_score = highscores[0]  # highest score saved
            hs_txt = hs_font.render(f"Previous Best: {prev_score}", False, "Black")
            screen.blit(hs_txt, (520, 30))
        # show final score/time and restart hint
        small = pygame.font.Font(pygame.font.get_default_font(), 24)
        final_txt = small.render(f"Final: {int(kept_score)}  Time: {final_time:.1f}s", False, "Black")
        screen.blit(final_txt, (40, 40))
        hint = small.render("Press SPACE to play again", False, "Black")
        screen.blit(hint, (40, 80))

    # flip the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # Limits game loop to 60 FPS

pygame.quit()
