# Eric Chen
# Fish Game

import pygame
import math
import random

pygame.init()
pygame.font.init() # initialize font module
screen_width = 1000 # set screen_width and height for later use
screen_height = 750
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Fish RPG")
clock = pygame.time.Clock()

# Get sprites from spritesheet

def spritesheet(frame_width, frame_height, gap, image):
    image_width = image.get_width() # gets width of image
    image_height = image.get_height() # gets height of image
    rows = image_height // (frame_height + gap) # number of rows in the sheet
    columns = image_width // (frame_width + gap) # number of columns in the sheet
    frames = [] # stores each sprite 

    for row in range(rows): 
        row_frames = [] # stores frames in each row

        for col in range(columns):  
            x = col * (frame_width + gap) # gets the x coordinate for each frame
            y = row * (frame_height + gap) # gets the y coordinate for each frame
            frame = image.subsurface(pygame.Rect(x, y, frame_width, frame_height)) # creates a new image by cutting one out of a rectangle
            row_frames.append(frame) # adds the image to this row's frames

        frames.append(row_frames) # adds this row's frames to the frames 

    return frames # now we can access each image through: sheet[row][column]

# Get fish dimensions 

def get_fish_dimensions(direction):
    global fish_width, fish_height, fish_crop_x, fish_crop_y # global variables allow variables to be reassigned

    if direction == 0 or direction == 3:  # up or down
        fish_width = 60 # get width, height, crop x, crop y based on direction
        fish_height = 141 
        fish_crop_x = 44 
        fish_crop_y = 0
    else:  # left or right
        fish_width = 148
        fish_height = 45
        fish_crop_x = 0
        fish_crop_y = 40

# Bite attack function

def bite(direction, attack_time):
    global attack_dx, attack_dy, attack_progress, current_bite

    attack_progress = attack_time / attack_duration # determines progress (attack time is how long the attack has gone on for)
    current_bite = pygame.transform.scale(fish_bite[direction].subsurface(crop_rect), (scaled_width, scaled_height)) # determines what direction the current bite sprite is in and scales image to correct size

    if attack_progress > 1:
        attack_progress = 1 # makes sure attack_progress is 0 - 1

    offset = math.sin(attack_progress * math.pi) * attack_range # used trigonometry for smoother, non-linear, animation

    attack_dx = 0 # change in x
    attack_dy = 0 # change in y

    # determines direction for the bite to move in

    if direction == 2:  # right
        attack_dx = offset

    elif direction == 1:  # left
        attack_dx = -offset

    elif direction == 0:  # down
        attack_dy = offset

    elif direction == 3:  # up
        attack_dy = -offset
    

# Get attack dimensions 

def attack_properties(direction):
    global attack_width, attack_height, attack_offset_x, attack_offset_y

    if direction == 0:  # down
        attack_width = 60 # width, height, offset x, offset y based on direction for attack hitbox
        attack_height = 60 
        attack_offset_x = 0 
        attack_offset_y = 81
    elif direction == 3:  # up
        attack_width = 60 
        attack_height = 60 
        attack_offset_x = 0 
        attack_offset_y = 0
    elif direction == 1:  # left
        attack_width = 60 
        attack_height = 45 
        attack_offset_x = 0 
        attack_offset_y = 0
    elif direction == 2:  # right
        attack_width = 60 
        attack_height = 45
        attack_offset_x = 88
        attack_offset_y = 0

# Reset lazers

def reset_lazer():
    global lazer_x, lazer_y, lazer_dx, lazer_dy, lazer_lifetime
    lazer_x = []
    lazer_y = []
    lazer_dx = []
    lazer_dy = []
    lazer_lifetime = []
    
# Camera update function

def update_camera(player_pos, map_width, map_height):
    # Center camera on player
    cam_x = player_pos[0] - screen_width / 2
    cam_y = player_pos[1] - screen_height / 2
    
    # Keep within map boundaries
    if cam_x < 0: # if camera goes beyond left edge
        cam_x = 0 # set camera x to 0
    if cam_y < 0: # if camera goes beyond top edge
        cam_y = 0 # set camera y to 0
    if cam_x > map_width - screen_width: # if camera goes beyond right edge
        cam_x = map_width - screen_width # set camera x to right edge
    if cam_y > map_height - screen_height: # if camera goes beyond bottom edge
        cam_y = map_height - screen_height # set camera y to bottom edge

    return cam_x, cam_y # return camera x and y

# Collision handler

def handle_collision(fish_collider, obstacles):
    
    for obstacle in obstacles: # for each obstacle in the map
        if fish_collider.colliderect(obstacle): # if player collides with obstacle
            
            overlap_left = fish_collider.right - obstacle.left # calculate overlap on each side
            overlap_right = obstacle.right - fish_collider.left
            overlap_top = fish_collider.bottom - obstacle.top
            overlap_bottom = obstacle.bottom - fish_collider.top
            
            min_overlap = overlap_left # find the smallest overlap to get the nearest edge
            if overlap_right < overlap_left:
                min_overlap = overlap_right

            if overlap_top < min_overlap:
                min_overlap = overlap_top

            if overlap_bottom < min_overlap:
                min_overlap = overlap_bottom
            
            if min_overlap == overlap_left: # push player out in the direction of smallest overlap
                player_pos[0] -= overlap_left
            elif min_overlap == overlap_right:
                player_pos[0] += overlap_right
            elif min_overlap == overlap_top:
                player_pos[1] -= overlap_top
            else:
                player_pos[1] += overlap_bottom

# Draw collisions 

def debug_collision(obstacles):

    for obstacle in obstacles: # each obstacle given
        if obstacle.width == 10 or obstacle.height == 10: # checks if obstacle is a map changer and sets color to black
            color = BLACK 
        else: # if it's normal color is white
            color = WHITE
        pygame.draw.rect(screen, color, [obstacle.x - camera_x, obstacle.y - camera_y, obstacle.width, obstacle.height], 4) # draw rect

# Display warning 

def display_text(text, display_start, current_time, warning):
    global display_fish
    if text != "": # if text is not empty display warning
        if current_time - display_start > 2000: # display warning for 2 seconds 
            text = "" # reset text
            display_fish = False
        else: # if still displaying
            if warning: # set warning colors
                text_color = RED
                bg_color = BLACK
            else: # set normal colors
                text_color = DISPLAY_GREEN
                bg_color = WHITE
            
            if display_fish: # trophy display
                trophy_bg = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                trophy_bg.fill((255, 255, 255, 50)) # make a background for display
                screen.blit(trophy_bg, (0, 0)) # draw bg
                 
                screen.blit(trophy_fish, (screen_width / 2 - trophy_fish.get_width() / 2, screen_height / 2 - trophy_fish.get_height() / 2)) # draw trophy at center

            display_text = font_arial_warning.render(text, True, text_color) # render text
            pygame.draw.rect(screen, bg_color, [screen_width / 2 - display_text.get_width() / 2 - 5, 60 - 5, display_text.get_width() + 10, display_text.get_height() + 10]) # background for text and centered
            screen.blit(display_text, (screen_width / 2 - display_text.get_width() / 2, 60)) # center text at top of screen

# Create new enemy

def spawn_enemy(x, y, fish_type, zone_index, map_index, zone_x, zone_y, zone_width, zone_height):
    enemy_x.append(x) # add enemy x data to the lists
    enemy_y.append(y) # add enemy y data to the lists
    enemy_type.append(fish_type) # add enemy type data to the lists
    enemy_direction.append(0) # add initial direction to the lists
    enemy_frame.append(0) # add initial frame to the lists
    enemy_anim_timer.append(0) # add initial animation timer to the lists
    enemy_pause.append(False) # add initial pause to the lists
    enemy_pause_start.append(0) # add initial pause start to the lists
    enemy_alive.append(True) # add an enemy to alive and make it alive
    enemy_zone_index.append(zone_index) # add zone index
    enemy_map.append(map_index) # add map index
    enemy_zone_x.append(zone_x) # add zone's x
    enemy_zone_y.append(zone_y) # add zone's y
    enemy_zone_width.append(zone_width) # add width of zone
    enemy_zone_height.append(zone_height) # add height of zone
    enemy_attacking.append(False) # add attack bool
    enemy_attack_start.append(0) # add attack start
    enemy_attack_cooldown.append(0) # add attack cooldown
    if fish_type == 0: # if basic fish
        enemy_speed.append(0.2) # speed is 1
        enemy_health.append(200) # health is 200
        enemy_scale.append(0.5) # scale is 1.0
    elif fish_type == 1: # if medium fish and so on...
        enemy_speed.append(0.5)
        enemy_health.append(1000)
        enemy_scale.append(0.5)
    elif fish_type == 2:
        enemy_speed.append(1)
        enemy_health.append(5000)
        enemy_scale.append(0.8)
    elif fish_type == 3:
        enemy_speed.append(0.5)
        enemy_health.append(10000)
        enemy_scale.append(0.5)
    elif fish_type == 4:
        enemy_speed.append(1)
        enemy_health.append(50000)
        enemy_scale.append(0.5)
    elif fish_type == 5:
        enemy_speed.append(1.5)
        enemy_health.append(250000)
        enemy_scale.append(1)

# Update single enemy

def update_single_enemy(index, player_pos, width, height):
    if not enemy_alive[index]: # if enemy is not alive, do nothing
        return
    
    dx = player_pos[0] - enemy_x[index] - width / 2 # calculate difference in x and y (adjusted for center)
    dy = player_pos[1] - enemy_y[index] - height / 2
    distance = math.sqrt(dx ** 2 + dy ** 2) # calculate distance to player
    current_time = pygame.time.get_ticks() # get current time

    zone_x = enemy_zone_x[index] # get zone values
    zone_y = enemy_zone_y[index]
    zone_width = enemy_zone_width[index]
    zone_height = enemy_zone_height[index]

    if enemy_type[index] == 0 or enemy_type[index] == 1 or enemy_type[index] == 3 or enemy_type[index] == 4 and distance > 500 or distance > 800: # check for passive fish types or if player is out of range
        if enemy_pause[index]: # if not pausing allow chance to pause
            if current_time - enemy_pause_start[index] >= 1000:  # if time passed since pause is 1 second
                enemy_pause[index] = False # set pause to false
            else: # else don't move
                return
        
        if random.randrange(0, 100) == 0:  # 1% chance to pause
            enemy_pause[index] = True # set pause to true
            enemy_pause_start[index] = current_time # get the time that pause started
            return # immediately start pausing

        if random.randrange(0, 100) == 0:  # 1% chance to change direction randomly
            enemy_direction[index] = random.randrange(0, 4) # set direction to a random direction
        
        old_x = enemy_x[index] # get old x and y incase enemy goes out of bounds
        old_y = enemy_y[index]
        
        if enemy_direction[index] == 0:  # down
            enemy_y[index] += enemy_speed[index] # move enemy in current direction
        elif enemy_direction[index] == 1:  # left
            enemy_x[index] -= enemy_speed[index] # move enemy in current direction and so on...
        elif enemy_direction[index] == 2:  # right
            enemy_x[index] += enemy_speed[index]
        elif enemy_direction[index] == 3:  # up
            enemy_y[index] -= enemy_speed[index]

        if (enemy_x[index] < zone_x or enemy_x[index] > zone_x + zone_width or enemy_y[index] < zone_y or enemy_y[index] > zone_y + zone_height):
            enemy_x[index] = old_x # if enemy x is out of zone, then set it back to it's old x and y
            enemy_y[index] = old_y
            enemy_direction[index] = random.randrange(0, 4)  # change direction if hitting zone boundary

        # Animate 

        enemy_anim_timer[index] += 0.05 # increment timer
        if enemy_anim_timer[index] >= 1: # if timer max (so about after 20 ticks)
            enemy_anim_timer[index] = 0 # reset timer
            enemy_frame[index] = (enemy_frame[index] + 1) % 4 # move to the next frame (remainder will always be 0, 1, 2, or 3)

    elif enemy_type[index] == 4: # if jellyfish (shooter)
        old_x = enemy_x[index] # get old x and y incase enemy is out of zone
        old_y = enemy_y[index]

        if distance < 500:  # Shooting range
            if distance < 150: # if player is too close move away from player
                new_dx = -dx / distance * enemy_speed[index] # make changes in x and y opposite so they move the opposite way from the player
                new_dy = -dy / distance * enemy_speed[index]
                enemy_x[index] += new_dx
                enemy_y[index] += new_dy
            elif distance > 300: # if player is too far move closer to player
                new_dx = dx / distance * enemy_speed[index] # keep changes in x and y the same so they move closer to the player
                new_dy = dy / distance * enemy_speed[index]
                enemy_x[index] += new_dx
                enemy_y[index] += new_dy
        
            # Shoot at player
            if current_time - enemy_attack_cooldown[index] >= 2000: # if cooldown is over
                enemy_attack_start[index] = current_time # get time attack started
                projectile_alive.append(True)
                projectile_x.append(enemy_x[index]) # set projectile starting point at the enemy's x and y
                projectile_y.append(enemy_y[index])

                proj_dx = dx / distance * projectile_speed # move toward player
                proj_dy = dy / distance * projectile_speed
            
                projectile_dx.append(proj_dx) # update position and time
                projectile_dy.append(proj_dy)
                projectile_lifetime.append(current_time)
                
                enemy_attack_cooldown[index] = current_time # set cooldown time

        if (enemy_x[index] < zone_x or enemy_x[index] > zone_x + zone_width or enemy_y[index] < zone_y or enemy_y[index] > zone_y + zone_height):
            enemy_x[index] = old_x # if enemy x is out of zone, then set it back to it's old x and y
            enemy_y[index] = old_y
        
        # Update direction to face player

        if abs(dx) > abs(dy): # if moving more in x 
            if dx > 0: # if moving right
                enemy_direction[index] = 2 # set direction to right
            else: # if moving left
                enemy_direction[index] = 1 # set direction to left
        else: # moving more in y direction
            if dy > 0: # if moving down
                enemy_direction[index] = 0 # set direction to down
            else: # if moving up
                enemy_direction[index] = 3 # set direction to up
        
        # Animate

        enemy_anim_timer[index] += 0.05 # increment timer
        if enemy_anim_timer[index] >= 1: # if timer max
            enemy_anim_timer[index] = 0 # reset timer
            enemy_frame[index] = (enemy_frame[index] + 1) % 4 # move to next frame

    else: # if not a passive fish type and in range
        if distance < 100: # distance is less than 100
            if not enemy_attacking[index] and current_time - enemy_attack_cooldown[index] >= 1000: # if enemy is not attackng and cooldown is over
                enemy_attacking[index] = True # enemy can attack and set the time the attack start
                enemy_attack_start[index] = current_time
            
        if enemy_attacking[index]: # if enemy is attacking
            attack_time = current_time - enemy_attack_start[index] # get how long the attack lasted

            if attack_time >= 100: # if attack time is over stop enemy attacking and set the cooldown start
                enemy_attacking[index] = False
                enemy_attack_cooldown[index] = current_time
            else: # if enemy attacking
                if abs(dx) > abs(dy): # determine if moving more in x or y direction
                    if dx > 0: # if moving right
                        enemy_direction[index] = 2 # set direction to right
                    else: # if moving left
                        enemy_direction[index] = 1 # set direction to left
                else: # moving more in y direction
                    if dy > 0: # if moving down
                        enemy_direction[index] = 0 # set direction to down
                    else: # if moving up
                        enemy_direction[index] = 3 # set direction to up

        # Only chase if distance is greater than 150 pixels and less than 500 pixels 
        if distance < 500:
            old_x = enemy_x[index] # get old x and y incase enemy is out of zone
            old_y = enemy_y[index]

            dx = dx / distance * enemy_speed[index] # normalize movement and scale by enemy speed
            dy = dy / distance * enemy_speed[index]
            
            enemy_x[index] += dx # update enemy position
            enemy_y[index] += dy
            
            if (enemy_x[index] < zone_x or enemy_x[index] > zone_x + zone_width or enemy_y[index] < zone_y or enemy_y[index] > zone_y + zone_height):
                enemy_x[index] = old_x # if out of bounds go back to old x and y
                enemy_y[index] = old_y
            else: 
                # if not out of bounds update direction and animate
                if abs(dx) > abs(dy): # determine if moving more in x or y direction
                    if dx > 0: # if moving right
                        enemy_direction[index] = 2 # set direction to right
                    else: # if moving left
                        enemy_direction[index] = 1 # set direction to left
                else: # moving more in y direction
                    if dy > 0: # if moving down
                        enemy_direction[index] = 0 # set direction to down
                    else: # if moving up
                        enemy_direction[index] = 3 # set direction to up

                    # Animate

                    enemy_anim_timer[index] += 0.05 # increment timer
                    if enemy_anim_timer[index] >= 1: # if timer reaches max
                        enemy_anim_timer[index] = 0 # reset timer
                        enemy_frame[index] = (enemy_frame[index] + 1) % 4 # advance to next frame

# Draw single enemy

def draw_single_enemy(index, camera_x, camera_y):
    if not enemy_alive[index]: # if enemy is not alive, do nothing
        return 0, 0 # as to return 2 values for the variables that are assigned to it or it'll have a type error
    
    if enemy_type[index] == 0: # if basic enemy
        sprite = fish1_spritesheet[enemy_direction[index]][enemy_frame[index]] # get sprite based on direction and frame
    elif enemy_type[index] == 1: # if medium enemy and so on...
        sprite = fish2_spritesheet[enemy_direction[index]][enemy_frame[index]]
    elif enemy_type[index] == 2:
        sprite = fish3_spritesheet[enemy_direction[index]][enemy_frame[index]]
    elif enemy_type[index] == 3:
        sprite = fish4_spritesheet[enemy_direction[index]][enemy_frame[index]]
    elif enemy_type[index] == 4:
        sprite = fish5_spritesheet[enemy_direction[index]][enemy_frame[index]]
    elif enemy_type[index] == 5:
        sprite = fish6_spritesheet[enemy_direction[index]][enemy_frame[index]]

    scale = enemy_scale[index] # get scale of enemy
    sprite_width = int(sprite.get_width() * scale) # calculate scaled width and height
    sprite_height = int(sprite.get_height() * scale)
    sprite = pygame.transform.scale(sprite, (sprite_width, sprite_height)) # scale sprite
    draw_x = int(enemy_x[index] - camera_x) # calculate draw position with camera offset
    draw_y = int(enemy_y[index] - camera_y)
    
    screen.blit(sprite, (draw_x, draw_y)) # draw enemy sprite
    
    if enemy_type[index] == 0: # determine max health based on enemy type
        enemy_max_health = 200
    elif enemy_type[index] == 1: 
        enemy_max_health = 1000
    elif enemy_type[index] == 2:
        enemy_max_health = 5000
    elif enemy_type[index] == 3:
        enemy_max_health = 10000
    elif enemy_type[index] == 4:
        enemy_max_health = 50000
    elif enemy_type[index] == 5:
        enemy_max_health = 250000
    health_percent = enemy_health[index] / enemy_max_health # calculate health percentage
    
    pygame.draw.rect(screen, BLACK, [draw_x + (sprite_width - 50) / 2, draw_y - 10, 50, 10]) # draw health bar background on top of enemy
    pygame.draw.rect(screen, RED, [draw_x + 2 + (sprite_width - 50) / 2, draw_y - 9, int(46 * health_percent), 8]) # draw health bar foreground based on health percentage on top of enemy

    return sprite_width, sprite_height

# Count alive enemies in zone

def count_enemies_in_zone(zone_index, map_index):
    count = 0 # set count
    for i in range(len(enemy_alive)): # for each enemy
        if enemy_alive[i] and enemy_zone_index[i] == zone_index and enemy_map[i] == map_index: # if enemy is alive and in the correct zone and map
            count += 1 # increment count
    return count # return count

# Get enemy hitbox

def get_enemy_collider(index):
    enemy_rect = [0, 0, 0, 0] # if nothing then return this

    if enemy_type[index] == 0: # create hitbox based on type
        enemy_rect = pygame.Rect(enemy_x[index], enemy_y[index], fish1_spritesheet[enemy_direction[index]][enemy_frame[index]].get_width() * enemy_scale[index], fish1_spritesheet[enemy_direction[index]][enemy_frame[index]].get_height() * enemy_scale[index]) # create enemy rect
        if debug_zones:
            pygame.draw.rect(screen, BLUE, [enemy_x[index] - camera_x, enemy_y[index] - camera_y, fish1_spritesheet[enemy_direction[index]][enemy_frame[index]].get_width() * enemy_scale[index], fish1_spritesheet[enemy_direction[index]][enemy_frame[index]].get_height() * enemy_scale[index]], 4)
    elif enemy_type[index] == 1:
        enemy_rect = pygame.Rect(enemy_x[index], enemy_y[index], fish2_spritesheet[enemy_direction[index]][enemy_frame[index]].get_width() * enemy_scale[index], fish2_spritesheet[enemy_direction[index]][enemy_frame[index]].get_height() * enemy_scale[index]) # create enemy rect
        if debug_zones:
            pygame.draw.rect(screen, BLUE, [enemy_x[index] - camera_x, enemy_y[index] - camera_y, fish2_spritesheet[enemy_direction[index]][enemy_frame[index]].get_width() * enemy_scale[index], fish2_spritesheet[enemy_direction[index]][enemy_frame[index]].get_height() * enemy_scale[index]], 4)
    elif enemy_type[index] == 2:
        enemy_rect = pygame.Rect(enemy_x[index], enemy_y[index], fish3_spritesheet[enemy_direction[index]][enemy_frame[index]].get_width() * enemy_scale[index], fish3_spritesheet[enemy_direction[index]][enemy_frame[index]].get_height() * enemy_scale[index]) # create enemy rect
        if debug_zones:
            pygame.draw.rect(screen, BLUE, [enemy_x[index] - camera_x, enemy_y[index] - camera_y, fish3_spritesheet[enemy_direction[index]][enemy_frame[index]].get_width() * enemy_scale[index], fish3_spritesheet[enemy_direction[index]][enemy_frame[index]].get_height() * enemy_scale[index]], 4)
    elif enemy_type[index] == 3:
        enemy_rect = pygame.Rect(enemy_x[index], enemy_y[index], fish4_spritesheet[enemy_direction[index]][enemy_frame[index]].get_width() * enemy_scale[index], fish4_spritesheet[enemy_direction[index]][enemy_frame[index]].get_height() * enemy_scale[index]) # create enemy rect
        if debug_zones:
            pygame.draw.rect(screen, BLUE, [enemy_x[index] - camera_x, enemy_y[index] - camera_y, fish4_spritesheet[enemy_direction[index]][enemy_frame[index]].get_width() * enemy_scale[index], fish4_spritesheet[enemy_direction[index]][enemy_frame[index]].get_height() * enemy_scale[index]], 4)
    elif enemy_type[index] == 4:  
        enemy_rect = pygame.Rect(enemy_x[index], enemy_y[index], fish5_spritesheet[enemy_direction[index]][enemy_frame[index]].get_width() * enemy_scale[index], fish5_spritesheet[enemy_direction[index]][enemy_frame[index]].get_height() * enemy_scale[index])
        if debug_zones:
            pygame.draw.rect(screen, BLUE, [enemy_x[index] - camera_x, enemy_y[index] - camera_y, fish5_spritesheet[enemy_direction[index]][enemy_frame[index]].get_width() * enemy_scale[index], fish5_spritesheet[enemy_direction[index]][enemy_frame[index]].get_height() * enemy_scale[index]], 4)
    elif enemy_type[index] == 5:  
        enemy_rect = pygame.Rect(enemy_x[index], enemy_y[index], fish6_spritesheet[enemy_direction[index]][enemy_frame[index]].get_width() * enemy_scale[index], fish6_spritesheet[enemy_direction[index]][enemy_frame[index]].get_height() * enemy_scale[index])
        if debug_zones:
            pygame.draw.rect(screen, BLUE, [enemy_x[index] - camera_x, enemy_y[index] - camera_y, fish6_spritesheet[enemy_direction[index]][enemy_frame[index]].get_width() * enemy_scale[index], fish6_spritesheet[enemy_direction[index]][enemy_frame[index]].get_height() * enemy_scale[index]], 4)

    return enemy_rect # return enemy hitbox

# Update spawn zone

def update_spawn_zone(zone_x, zone_y, zone_width, zone_height, zone_max, zone_respawn, zone_last_spawn, zone_fish_type, zone_index, map_index, current_time): 

    alive_count = count_enemies_in_zone(zone_index, map_index) # count alive enemies in the zone
    time_since_spawn = current_time - zone_last_spawn # calculate time since last spawn of enemy
    
    if alive_count < zone_max and time_since_spawn >= zone_respawn: # if there is room for more enemies and enough time has passed since last spawn
        spawn_x = zone_x + random.randrange(0, zone_width) # randomly generate spawn position within zone
        spawn_y = zone_y + random.randrange(0, zone_height)
        spawn_enemy(spawn_x, spawn_y, zone_fish_type, zone_index, map_index, zone_x, zone_y, zone_width, zone_height) # spawn new enemy
        return current_time # return current time as last spawn time
    
    return zone_last_spawn # return previous last spawn time if no new enemy spawned

# Draw spawn zone debug

def draw_spawn_zone_debug(zone_x, zone_y, zone_width, zone_height, camera_x, camera_y):
    zone_rect = pygame.Rect(zone_x - camera_x, zone_y - camera_y, zone_width, zone_height) # create and draw spawn zone rectangle
    pygame.draw.rect(screen, YELLOW, zone_rect, 2)

# Spawn boss

def spawn_boss():
    global boss_exists, boss_x, boss_y, boss_health, boss_mode_shoot, boss_attacking, boss_attack_cooldown, boss_freeze_duration, boss_slash_active, tentacle_spawn_cooldown, boss_projectile_cooldown, boss_lazer_cooldown, boss_direction, boss_frame, boss_animation_timer, tentacle_warning_x, tentacle_warning_y, tentacle_warning_start, tentacle_active_x, tentacle_active_y, tentacle_active_start, boss_projectile_x, boss_projectile_y, boss_projectile_dx, boss_projectile_dy, boss_projectile_start

    boss_exists = True
    boss_x = 750  
    boss_y = 500
    boss_health = boss_max_health
    boss_mode_shoot = False
    boss_attacking = False
    boss_attack_cooldown = 0
    boss_slash_active = False
    tentacle_spawn_cooldown = 0
    boss_projectile_cooldown = 0
    boss_lazer_cooldown = 0
    boss_direction = 0
    boss_frame = 0
    boss_animation_timer = 0
    
    tentacle_warning_x = [] # clear any existing tentacles and projectiles
    tentacle_warning_y = []
    tentacle_warning_start = []
    tentacle_active_x = []
    tentacle_active_y = []
    tentacle_active_start = []
    boss_projectile_x = []
    boss_projectile_y = []
    boss_projectile_dx = []
    boss_projectile_dy = []
    boss_projectile_start = []

# Update boss

def update_boss(player_pos, current_time):
    global boss_mode_shoot, boss_direction, tentacle_spawn_cooldown, tentacle_random_spawn_cooldown, boss_x, boss_y, boss_frame, boss_attacking, boss_slash_active, boss_animation_timer, boss_attack_cooldown, boss_attack_start, boss_slash_start, boss_lazer_start, boss_projectile_random_cooldown, boss_projectile_cooldown, boss_lazer_active
    
    if not boss_exists:
        return
    
    if boss_health < boss_max_health / 2: # at half health boss changes mode
        boss_mode_shoot = True

    dx = player_pos[0] - (boss_x + 125) # find distance from player at boss center
    dy = player_pos[1] - (boss_y + 125)
    distance = math.sqrt(dx ** 2 + dy ** 2)

    if not boss_attacking: # allow getting direction when boss is not attacking
        if abs(dx) > abs(dy): # get direction of boss 
            if dx > 0:
                boss_direction = 2 
            else:
                boss_direction = 1
        else:
            if dy > 0:
                boss_direction = 0
            else:
                boss_direction = 3
    
    if not boss_mode_shoot: # if in attack mode
        if current_time - tentacle_spawn_cooldown >= tentacle_spawn_time: # if cooldown over create tentacle warning 
            tentacle_warning_x.append(player_pos[0]) 
            tentacle_warning_y.append(player_pos[1])
            tentacle_warning_start.append(current_time)
            tentacle_spawn_cooldown = current_time
        
        if boss_health < boss_max_health * 0.65: # tentacle amounts increase as boss health decreases
            tentacle_amount = 7
        elif boss_health < boss_max_health * 0.80:
            tentacle_amount = 5
        else:
            tentacle_amount = 3
        
        if current_time - tentacle_random_spawn_cooldown >= tentacle_random_spawn_time: # cooldowns for randomly generated tentacles
            for i in range(tentacle_amount): # generate based on tectacle amount
                tentacle_warning_x.append(random.randrange(100, 1400)) # random area on the map that is inside boundaries
                tentacle_warning_y.append(random.randrange(100, 1050))
                tentacle_warning_start.append(current_time) 
            tentacle_random_spawn_cooldown = current_time
        
        if not boss_attacking and not boss_slash_active: 
            if distance > 200:  # follow player if far away and while they're not attacking

                dx = dx / distance * boss_speed # normalize changes so that it can be scaled with speed
                dy = dy / distance * boss_speed
                boss_x += dx
                boss_y += dy
                
                boss_animation_timer += 0.05 # animate boss 
                if boss_animation_timer >= 1:
                    boss_animation_timer = 0
                    boss_frame = (boss_frame + 1) % 4
            
            elif current_time - boss_attack_cooldown >= 2000:  # attack every 2 seconds if boss is close enough
                boss_attacking = True
                boss_attack_start = current_time
        
        if boss_attacking:
            boss_attack_time = current_time - boss_attack_start
            
            if boss_attack_time < boss_freeze_duration: # wait for duration of freeze
                return
            elif boss_attack_time < boss_freeze_duration + 500:  # then attack for 0.5 seconds with not already attacking
                if not boss_slash_active: # attack if not already
                    boss_slash_active = True 
                    boss_slash_start = current_time
            else: # attack finished
                boss_attacking = False
                boss_slash_active = False
                boss_attack_cooldown = current_time

    else: # shoot mode
        boss_slash_active = False # incase modes switched before attack finished
        if distance < 300: # move away from player if too close
            dx_boss = -dx / distance * boss_speed
            dy_boss = -dy / distance * boss_speed
            boss_x += dx_boss
            boss_y += dy_boss
        elif distance > 500:  # move closer if too far
            dx_boss = dx / distance * boss_speed
            dy_boss = dy / distance * boss_speed
            boss_x += dx_boss
            boss_y += dy_boss
        
        boss_animation_timer += 0.05 # animate boss
        if boss_animation_timer >= 1:
            boss_animation_timer = 0
            boss_frame = (boss_frame + 1) % 4
        
        if boss_health < boss_max_health * 0.15: # projectile amounts increase as boss health decreases
            proj_amount = 7
        elif boss_health < boss_max_health * 0.30:
            proj_amount = 5
        else:
            proj_amount = 3

        if current_time - boss_projectile_random_cooldown >= boss_projectile_random_fire_rate: # if cooldown up
            for i in range(proj_amount): # generate based on proj amount
                proj_dx = random.randrange(-1000, 1000) / 1000 # random range from -1 to 1 to get a random direction
                proj_dy = random.randrange(-1000, 1000) / 1000
                proj_length = math.sqrt(proj_dx ** 2 + proj_dy ** 2) 
                proj_dx = proj_dx / proj_length * boss_projectile_speed # normalize and scale by speed
                proj_dy = proj_dy / proj_length * boss_projectile_speed
                boss_projectile_x.append(boss_x + 125) # spawn projectile and set new cooldown
                boss_projectile_y.append(boss_y + 125)
                boss_projectile_dx.append(proj_dx)
                boss_projectile_dy.append(proj_dy)
                boss_projectile_start.append(current_time)
            boss_projectile_random_cooldown = current_time
        
        if current_time - boss_projectile_cooldown >= boss_projectile_fire_rate: # if cooldown up
            proj_dx = dx / distance * boss_projectile_speed # normalize and scale by speed
            proj_dy = dy / distance * boss_projectile_speed
            boss_projectile_x.append(boss_x + 125) # spawn projectile and set new cooldown
            boss_projectile_y.append(boss_y + 125)
            boss_projectile_dx.append(proj_dx)
            boss_projectile_dy.append(proj_dy)
            boss_projectile_start.append(current_time)
            boss_projectile_cooldown = current_time
        
        if not boss_lazer_active and current_time - boss_lazer_cooldown >= boss_lazer_fire_rate:
            boss_lazer_active = True # shoot lazer if not already shooting and cooldown is up
            boss_lazer_start = current_time 

# Draw boss

def draw_boss(camera_x, camera_y):
    if not boss_exists:
        return
    
    sprite = pygame.transform.scale(boss_spritesheet[boss_direction][boss_frame], (250, 250)) # get boss sprite based on direction and frame  
    draw_x = int(boss_x - camera_x) # get coodinates to draw on screen
    draw_y = int(boss_y - camera_y)
    
    screen.blit(sprite, (draw_x, draw_y)) # draw boss

# Load Sprites

fish_sheet = spritesheet(148, 141, 0, pygame.image.load("Assets/fish.png").convert_alpha())
fish_bite = [pygame.image.load("Assets/fishBiteDown.png").convert_alpha(), pygame.image.load("Assets/fishBiteLeft.png").convert_alpha(), pygame.image.load("Assets/fishBiteRight1.png").convert_alpha(), pygame.image.load("Assets/fishBiteUp.png").convert_alpha()]
background = pygame.transform.scale(pygame.image.load("Assets/Water_Background.jpeg"), (screen_width, screen_height))
shopkeeper = pygame.transform.scale(pygame.image.load("Assets/Sus_ShopKeeper.webp"), (50, 55))
city_spritesheet = spritesheet(16, 16, 1, pygame.image.load("Assets/city_spritesheet.png").convert_alpha())
market_stall = [
    pygame.transform.scale(city_spritesheet[17][15], (50, 30)),  # base
    pygame.transform.scale(city_spritesheet[17][16], (50, 30)),  # base
    pygame.transform.scale(city_spritesheet[17][19], (50, 30)),  # base
    pygame.transform.scale(city_spritesheet[11][21], (50, 50)),  # stick
    pygame.transform.scale(city_spritesheet[11][22], (50, 50)),  # stick
    pygame.transform.scale(city_spritesheet[11][27], (50, 50)),  # top
    pygame.transform.scale(city_spritesheet[11][28], (50, 50)), # top
    pygame.transform.scale(city_spritesheet[11][29], (50, 50)), # top
    pygame.transform.scale(city_spritesheet[8][31], (50, 25)), # counter
    pygame.transform.scale(city_spritesheet[8][32], (50, 25)), # counter
    pygame.transform.scale(city_spritesheet[8][33], (50, 25))  # counter
]
fence_sprite = [
    pygame.transform.scale(city_spritesheet[14][21], (50, 50)), # fence left
    pygame.transform.scale(city_spritesheet[14][22], (50, 50)), # fence middle
    pygame.transform.scale(city_spritesheet[14][23], (50, 50)), # fence right
]
map1 = pygame.transform.scale(pygame.image.load("Assets/map1.jpeg"), (2000, 1500))
map2 = pygame.transform.scale(pygame.image.load("Assets/map2.jpeg"), (2000, 1300))
hallway = pygame.transform.scale(pygame.image.load("Assets/hallway.jpeg"), (1000, 1500))
map3 = pygame.transform.scale(pygame.image.load("Assets/map3.jpeg"), (1500, 1125))
secret_map = pygame.transform.scale(pygame.image.load("Assets/secretMap.jpeg"), (1000, 1000))
fish1_spritesheet = spritesheet(130, 119, 0, pygame.image.load("Assets/fish1.png").convert_alpha())
fish2_spritesheet = spritesheet(119, 121, 0, pygame.image.load("Assets/fish2.png").convert_alpha())
fish3_spritesheet = spritesheet(121, 110, 0, pygame.image.load("Assets/fish3.png").convert_alpha())
fish4_spritesheet = spritesheet(125, 125, 0, pygame.image.load("Assets/fish4.png").convert_alpha())
fish5_spritesheet = spritesheet(110, 111, 0, pygame.image.load("Assets/jellyfish.png").convert_alpha())
fish6_spritesheet = spritesheet(125, 150, 0, pygame.image.load("Assets/fish5.png").convert_alpha())
fish_bone = pygame.transform.scale(pygame.image.load("Assets/fishbone.png").convert_alpha(), (100, 100))
lazer_image = pygame.transform.scale(pygame.image.load("Assets/lazer.png").convert_alpha(), (200, 200))
orb_image = pygame.transform.scale(pygame.image.load("Assets/Green_Orb.png").convert_alpha(), (200, 200))
green_arrow_image = pygame.transform.scale(pygame.image.load("Assets/Green_Arrow.png").convert_alpha(), (200, 200))
red_arrow_image = pygame.transform.scale(pygame.image.load("Assets/Red_Arrow.png").convert_alpha(), (200, 200))
boss_spritesheet = spritesheet(125, 125, 0, pygame.image.load("Assets/octopus.png").convert_alpha())
tentacle_spritesheet = spritesheet(125, 184, 0, pygame.image.load("Assets/tentacle.png").convert_alpha())
slash_spritesheet = spritesheet(125, 125, 0, pygame.image.load("Assets/slash.png").convert_alpha())
treasure_spritesheet = spritesheet(32, 48, 0, pygame.image.load("Assets/treasure_chests.png").convert_alpha())
blue_chest_sheet = [treasure_spritesheet[0][7], treasure_spritesheet[1][7], treasure_spritesheet[2][7], treasure_spritesheet[3][7]]
sliver_chest_sheet = [treasure_spritesheet[4][1], treasure_spritesheet[5][1], treasure_spritesheet[6][1], treasure_spritesheet[7][1]]
trophy_fish = pygame.image.load("Assets/Golden_Fish.webp").convert_alpha()
trophy_fish = pygame.transform.scale(trophy_fish, (trophy_fish.get_width() / 2, trophy_fish.get_height() / 2))
trophy_fish_icon = pygame.transform.scale(trophy_fish, (trophy_fish.get_width() / 4, trophy_fish.get_height() / 4))
# Colors

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)  
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
EXP_BLUE = (10, 75, 195)
YELLOW = (255, 255, 0)
DISPLAY_GREEN = (70, 255, 0)
PROJ_PURPLE = (255, 100, 255)
PALE = (244, 226, 191)
SHOP_BROWN = (117, 81, 61)
STAMINA_GREEN = (110, 242, 58)
BG_STAMINA_GREEN = (46, 163, 0)
BTN_RED = (161, 0, 0)
BTN_RED_HOVER = (220, 50, 50)
LAZER_BLUE = (150, 150, 255)
LAZER_WHITE = (200, 200, 255)
INK_BLACK = (10, 10, 10)
INK_GREY = (50, 50, 50)

# Camera setup

camera_x = 0
camera_y = 0
camera_multiplier = 1

# Player data

player_pos = [500, 400]
player_speed = 5
swim_animation_speed = 0.15
attack_range = 30
attack_duration = 600 # miliseconds
attack_start = 0
attack_progress = 0
fish_x = 0
fish_y = 0
level = 100
max_level = 100
animation_timer = 0 
current_frame = 0 
xp_points = 0
xp_to_level = 1
fish_bones = 10000
health = 100
max_health = 100
regen_health = 0.05
damage = 10
stamina = 100
max_stamina = 100
stamina_regen = 0.1
lazer_unlock = False
attack_mode = True
shoot_mode = False
gameover = False

# Player actions

attacking = False
freeze = False
left = False
right = False
up = False
down = False
direction = 0 # player direction: 0 = down, 1 = left, 2 = right, 3 = up (sprite sheet arrangement)
dashing = False
shooting = False

# Player lazer data

lazer_cooldown = 0
lazer_cooldown_time = 500 
lazer_x = []
lazer_y = []
lazer_dx = []
lazer_dy = []
lazer_speed = 15
lazer_lifetime = []
lazer_max_lifetime = 3000  
lazer_damage = 30
lazer_length = 45 

# Shop data

openedShop = False
attack_cost = 5
lazer_cost = 25
stamina_cost = 10
regen_cost = 10
attack_level = 1
lazer_level = 0
regen_level = 1
stamina_level = 1
attack_max_level = False
lazer_max_level = False
regen_max_level = False
stamina_max_level = False

# Fonts

font_arial = pygame.font.SysFont("Arial", 25, True, False) 
font_arial_exp = pygame.font.SysFont("Arial", 14, True, False)
font_bogle = pygame.font.Font("Assets/BBHBogle-Regular.ttf", 25)
font_bogle_buttons = pygame.font.Font("Assets/BBHBogle-Regular.ttf", 35)
font_bogle_boss = pygame.font.Font("Assets/BBHBogle-Regular.ttf", 50)
font_bogle_title = pygame.font.Font("Assets/BBHBogle-Regular.ttf", 200)
font_arial_warning = pygame.font.SysFont("Arial", 20, True, False)
font_arial_health = pygame.font.SysFont("Arial", 40, True, False)
font_arial_upgrade = pygame.font.SysFont("Arial", 35, True, False)
font_arial_gameover = pygame.font.SysFont("Arial", 100, True, False)


# Map variables

is_lobby = True # main map 
is_map1 = False # beginner map
is_secret_map = False # secret map
is_map2 = False # advanced map
is_hallway = False # hallway to boss battle
is_map3 = False # boss battle map
gate_blocked = True 
has_entered_map1 = False
has_entered_secret_map = False
has_entered_map1_secret_map = False
has_entered_map2 = False
has_entered_map2_hallway = False
has_entered_lobby_map1 = False
has_entered_lobby_map2 = False
has_entered_hallway_map2 = False
has_entered_hallway_map3 = False
has_entered_map3 = False

# Enemy data

enemy_x = []
enemy_y = []
enemy_type = []  
enemy_direction = []
enemy_frame = []
enemy_anim_timer = []
enemy_speed = []
enemy_health = []
enemy_alive = []
enemy_zone_index = []
enemy_map = []
enemy_scale = []
enemy_pause = []
enemy_pause_start = []
enemy_zone_x = []
enemy_zone_y = []
enemy_zone_width = []
enemy_zone_height = []
enemy_attacking = []
enemy_attack_start = []
enemy_attack_cooldown = []

# Projectile data

projectile_x = []
projectile_y = []
projectile_dx = []
projectile_dy = []
projectile_alive = []
projectile_speed = 3
projectile_lifetime = []
projectile_max_lifetime = 3000  

# map1 spawn zone 1

zone1_x = 250
zone1_y = 1000
zone1_width = 600
zone1_height = 400
zone1_fish_type = 0  
zone1_max = 3
zone1_respawn = 5000
zone1_last_spawn = 0

# map1 spawn zone 2

zone2_x = 1325
zone2_y = 1150
zone2_width = 600
zone2_height = 250
zone2_fish_type = 0  
zone2_max = 3
zone2_respawn = 5000
zone2_last_spawn = 0

# map1 spawn zone 3

zone3_x = 50
zone3_y = 550
zone3_width = 900
zone3_height = 350
zone3_fish_type = 1
zone3_max = 5
zone3_respawn = 5000
zone3_last_spawn = 0

# map1 spawn zone 4

zone4_x = 50
zone4_y = 50
zone4_width = 1900
zone4_height = 400
zone4_fish_type = 2
zone4_max = 3
zone4_respawn = 5000
zone4_last_spawn = 0

# map2 spawn zone 5

zone5_x = 100
zone5_y = 500
zone5_width = 400
zone5_height = 600
zone5_fish_type = 3
zone5_max = 5
zone5_respawn = 5000
zone5_last_spawn = 0

# map2 spawn zone 6

zone6_x = 0
zone6_y = 0
zone6_width = 2000
zone6_height = 200
zone6_fish_type = 4  
zone6_max = 3
zone6_respawn = 8000
zone6_last_spawn = 0

# map2 spawn zone 7

zone7_x = 750
zone7_y = 450
zone7_width = 800
zone7_height = 750
zone7_fish_type = 5
zone7_max = 5
zone7_respawn = 1000
zone7_last_spawn = 0

# Boss data

boss_exists = False
boss_defeated = False
boss_x = 0
boss_y = 0
boss_health = 5000000
boss_max_health = 5000000
boss_direction = 0
boss_frame = 0
boss_animation_timer = 0
boss_speed = 0.8
boss_mode_shoot = False
boss_attacking = False
boss_attack_start = 0
boss_attack_cooldown = 0
boss_freeze_duration = 1000  
boss_slash_active = False
boss_slash_start = 0

# Tentacle attack data

tentacle_spawn_cooldown = 0
tentacle_spawn_time = 3000  
tentacle_random_spawn_cooldown = 0
tentacle_random_spawn_time = 1500
tentacle_warning_x = []
tentacle_warning_y = []
tentacle_warning_start = []
tentacle_indicator_duration = 1000  
tentacle_active_x = []
tentacle_active_y = []
tentacle_active_start = []
tentacle_active_duration = 500  

# Boss projectile data (ink balls)

boss_projectile_x = []
boss_projectile_y = []
boss_projectile_dx = []
boss_projectile_dy = []
boss_projectile_start = []
boss_projectile_lifetime = 5000
boss_projectile_speed = 4
boss_projectile_cooldown = 0
boss_projectile_fire_rate = 1000  
boss_projectile_random_fire_rate = 2000
boss_projectile_random_cooldown = 0

# Boss lazer data 

boss_lazer_active = False
boss_lazer_start = 0
boss_lazer_cooldown = 0
boss_lazer_fire_rate = 1000 
boss_lazer_charge_time = 500 
boss_lazer_duration = 1000  
boss_lazer_length = 2000
boss_lazer_damage = 100

# Text variables

text = ""
display_init = False
display_start = 0
warning = False

# Gameover variables

transparency = 0

# Menu variables

is_menu = True
is_instruction = False

# Chest variables

chest_open_start = 0 
blue_chest_opened = False
blue_chest_claimed = False
sliver_chest_opened = False
sliver_chest_claimed = False
display_fish = False

# Rest of the variables

debug_zones = False
done = False

# Game Loop

while not done:
    current_time = pygame.time.get_ticks() # get current time in milliseconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT: # check for window close
            done = True # exit loop
            
        if is_menu:  # menu
                if event.type == pygame.MOUSEBUTTONDOWN:
                    buttons = pygame.mouse.get_pressed()
                    
                    if buttons[0]:
                        if is_instruction: # in instructions only allow back button to be pressed
                            if back_button.collidepoint(pos):
                                is_instruction = False
                        else: # else allow the other buttons
                            if play_button.collidepoint(pos):
                                is_menu = False
                                is_lobby = True # spawn player, set stats, and close menu
                                player_pos = [500, 400]
                                health = max_health
                                stamina = max_stamina
                            
                            if instruction_button.collidepoint(pos): # instructions
                                is_instruction = True
                            
                            if exit_button.collidepoint(pos): # exit game
                                done = True
        else: # if not menu then other game functions can run
            if gameover and transparency == 255: # if gameover is fully transitioned
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    buttons = pygame.mouse.get_pressed()
                    
                    if buttons[0]:
                        if try_again_button.collidepoint(pos):
                            gameover = False # spawn player in lobby and set other maps that the player can die in to false
                            is_lobby = True
                            is_map1 = False
                            is_map2 = False
                            is_map3 = False
                            player_pos = [500, 400] # set stats
                            health = max_health
                            stamina = max_stamina
                        
                        if menu_button.collidepoint(pos):
                            is_menu = True # go to menu
                            gameover = False
                            
            if not gameover: # game is not over
                if event.type == pygame.MOUSEBUTTONDOWN: # check for mouse click 
                    buttons = pygame.mouse.get_pressed() # gets mouse button states
        
                    if buttons[0]: # if left mouse button attack
                        if not attacking and not openedShop and attack_mode: # attack mode
                            if stamina - 25 >= 0: # if enough stamina
                                attacking = True # attack, freeze the player, and take away stamina
                                freeze = True
                                attack_start = current_time
                                stamina -= 25
                            else: # else warn player low stamina
                                text = "Stamina too low!"
                                warning = True
                                display_init = True
        
                        if shoot_mode and not openedShop: # if shoot mode then player is shooting
                            shooting = True
                            
                if event.type == pygame.MOUSEBUTTONUP: # when player lets go player is not shooting
                    if shoot_mode and not openedShop: 
                            shooting = False
        
                if event.type == pygame.KEYDOWN: # check for key presses
                    if event.key == pygame.K_LSHIFT: # left shift
                        if not dashing and not openedShop: # dash
                            if stamina - 10 > 0: # stamina check
                                dashing = True # initalize dash and take stamina
                                dash_start = current_time
                                stamina -= 10
                            else: # warning
                                text = "Stamina too low!"
                                warning = True
                                display_init = True
                    
                    if event.key == pygame.K_f: # f key
                        if lazer_unlock: # lazer check
                            attack_mode = not attack_mode # switch modes
                            shoot_mode = not shoot_mode
                            shooting = False
                            attacking = False
        
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a: # left arrow or a key
                        left = True # set left movement to true
        
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d: # right arrow or d key
                        right = True # set right movement to true
        
                    if event.key == pygame.K_UP or event.key == pygame.K_w: # up arrow or w key
                        up = True # set up movement to true
        
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s: # down arrow or s key
                        down = True # set down movement to true
        
                if event.type == pygame.KEYUP: # check for key releases
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a: # left arrow or a key
                        left = False # set left movement to false3
        
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d: # right arrow or d key
                        right = False # set right movement to false
        
                    if event.key == pygame.K_UP or event.key == pygame.K_w: # up arrow or w key
                        up = False # set up movement to false
        
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s: # down arrow or s key
                        down = False # set down movement to false
                
                
                
                if openedShop: # buttons while shop is open
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        buttons = pygame.mouse.get_pressed()
        
                        if buttons[0]: # left click
                            if attack_button.collidepoint(pos): # if mouse left clicks and it's position is on a point in the button
                                if fish_bones >= attack_cost and not attack_max_level: # can buy check
                                    fish_bones -= attack_cost # upgrade and display
                                    attack_level += 1  
                                    text = "Attack Range Upgraded!"
                                    display_init = True
                                    warning = False
                                elif attack_max_level: # Max level warning
                                    text = "Stat is maxed out!"
                                    display_init = True
                                    warning = True                                
                                else: # can't buy warn player
                                    text = "Not enough fish bones!"
                                    display_init = True
                                    warning = True
                            if lazer_button.collidepoint(pos): # same thing with the others
                                if fish_bones >= lazer_cost and not lazer_max_level:
                                    fish_bones -= lazer_cost
                                    lazer_level += 1
                                    if not lazer_unlock: 
                                        text = "Shark Lazer Unlocked!"
                                        lazer_unlock = True
                                    else:
                                        text = "Shark Lazer Upgraded!"
                                    display_init = True
                                    warning = False
                                elif lazer_max_level:
                                    text = "Stat is maxed out!"
                                    display_init = True
                                    warning = True                                
                                else:
                                    text = "Not enough fish bones!"
                                    display_init = True
                                    warning = True
                            
                            if stamina_button.collidepoint(pos):
                                if fish_bones >= stamina_cost and not stamina_max_level:
                                    fish_bones -= stamina_cost
                                    stamina_level += 1
                                    text = "Stamina Capacity Upgraded!"
                                    display_init = True
                                    warning = False
                                elif stamina_max_level:
                                    text = "Stat is maxed out!"
                                    display_init = True
                                    warning = True
                                else:
                                    text = "Not enough fish bones!"
                                    display_init = True
                                    warning = True
                            
                            if regen_button.collidepoint(pos):
                                if fish_bones >= regen_cost and not regen_max_level:
                                    fish_bones -= regen_cost
                                    regen_level += 1
                                    text = "Stamina Regen Upgraded!"
                                    display_init = True
                                    warning = False
                                elif regen_max_level:
                                    text = "Stat is maxed out!"
                                    display_init = True
                                    warning = True                                
                                else:
                                    text = "Not enough fish bones!"
                                    display_init = True
                                    warning = True
    
    pos = pygame.mouse.get_pos() # get mouse positions
    mouse_x = pos[0]
    mouse_y = pos[1]
    
    if not is_menu:
        if not gameover:
        
            # Attack levels
        
            if attack_level == 1: # upgradeable stat levels to control stats at each level
                attack_range = 30
                attack_cost = 5
            elif attack_level == 2:
                attack_range = 60
                attack_cost = 10
            elif attack_level == 3:
                attack_range = 90
                attack_cost = 20
            elif attack_level == 4:
                attack_range = 120
                attack_max_level = True
        
            # Lazer levels
        
            if lazer_level == 0:
                lazer_cost = 25
                lazer_damage = 25
                lazer_cooldown_time = 500
                lazer_projectile_speed = 15
            elif lazer_level == 1:
                lazer_cost = 75
                lazer_damage = 50
                lazer_cooldown_time = 400
                lazer_projectile_speed = 18
            elif lazer_level == 2:
                lazer_cost = 250
                lazer_damage = 100
                lazer_cooldown_time = 300
                lazer_projectile_speed = 22
            elif lazer_level == 3:
                lazer_cost = 2000
                lazer_damage = 200
                lazer_cooldown_time = 200
                lazer_projectile_speed = 25
            elif lazer_level == 4:
                lazer_max_level = True
                lazer_damage = 200
                lazer_cooldown_time = 50
                lazer_projectile_speed = 25
        
            # Stamina levels
        
            if stamina_level == 1:
                max_stamina = 100
                stamina_cost = 10
            elif stamina_level == 2:
                max_stamina = 200
                stamina_cost = 20
            elif stamina_level == 3:
                max_stamina = 500
                stamina_cost = 50
            elif stamina_level == 4:
                max_stamina = 1000
                stamina_cost = 100
            elif stamina_level == 5:
                max_stamina = 5000
                stamina_max_level = True
        
            # Stamina regen levels
        
            if regen_level == 1:
                stamina_regen = 0.1
                regen_cost = 10
            elif regen_level == 2:
                stamina_regen = 0.2
                regen_cost = 20
            elif regen_level == 3:
                stamina_regen = 0.5
                regen_cost = 50
            elif regen_level == 4:
                stamina_regen = 1
                regen_cost = 100
            elif regen_level == 5:
                stamina_regen = 5
                regen_max_level = True
        
            if level < 15: # check if level is high enough for next level
                gate_blocked = True
            else: 
                gate_blocked = False
        
            if is_hallway: # camera multipler only applies to hallway
                camera_multiplier = 2
            else: 
                camera_multiplier = 1
        
            if (has_entered_lobby_map1):
                reset_lazer() # reset lazer to prevent crossing multiple maps
                player_pos = [325, 650] # set player position to entrance of lobby
                has_entered_lobby_map1 = False # makes sure this only happens once
        
            if (has_entered_lobby_map2):
                reset_lazer()
                player_pos = [180, 300] # set player position to entrance of lobby
                has_entered_lobby_map2 = False # makes sure this only happens once
        
            if (has_entered_map1): # reset player position when entering map1
                reset_lazer()
                player_pos = [1000, 1300] # set player position to entrance of map1
                has_entered_map1 = False # makes sure this only happens once
        
            if (has_entered_map1_secret_map): # reset player position when entering map1 from secret map
                reset_lazer()
                player_pos = [100, 500] # set player position to entrance of map1
                has_entered_map1_secret_map = False # makes sure this only happens once
        
            if (has_entered_hallway_map2): # reset player position when entering hallway
                reset_lazer()
                player_pos = [450, 200] # set player position to entrance of hallway
                has_entered_hallway_map2 = False # makes sure this only happens once
        
            if (has_entered_hallway_map3): # reset player position when entering hallway from map3
                reset_lazer()
                player_pos = [450, 1200] # set player position to entrance of hallway
                has_entered_hallway_map3 = False # makes sure this only happens once
        
            if (has_entered_secret_map): # reset player position when entering secret map
                reset_lazer()
                player_pos = [850, 450] # set player position to entrance of secret map
                has_entered_secret_map = False # makes sure this only happens once
        
            if (has_entered_map2): # reset player position when entering map2
                reset_lazer()
                player_pos = [300, 1100] # set player position to entrance of map2
                has_entered_map2 = False # makes sure this only happens once
        
            if (has_entered_map2_hallway): # reset player position when entering map2 from hallway
                reset_lazer()
                player_pos = [1800, 1100] # set player position to entrance of map2
                has_entered_map2_hallway = False # makes sure this only happens once
        
            if (has_entered_map3): # reset player position when entering map3
                reset_lazer()
                player_pos = [775, 100] # set player position to entrance of map3
                spawn_boss()
                has_entered_map3 = False # makes sure this only happens once
                
            if not is_map2: # clear projectiles so that they don't damage player outside of map2 (projectiles are global and not asscoiated to a map)
                projectile_x = []
                projectile_y = []
                projectile_dx = []
                projectile_dy = []
                projectile_alive = []
                projectile_lifetime = []
        
            get_fish_dimensions(direction) # set fish dimensions based on direction
            crop_rect = pygame.Rect(fish_crop_x, fish_crop_y, fish_width, fish_height) # rectangle to crop fish
            fish = fish_sheet[direction][current_frame].subsurface(crop_rect) # get current fish sprite based on direction and frame and crop it 
        
            fish_x = player_pos[0] - fish_width / 2 # center fish on player position
            fish_y = player_pos[1] - fish_height / 2
        
            scaled_width = int(fish_width * camera_multiplier) # scale collider and recenter
            scaled_height = int(fish_height * camera_multiplier)
            offset_x = (scaled_width - fish_width) / 2
            offset_y = (scaled_height - fish_height) / 2
        
            scaled_fish_x = fish_x - offset_x # apply offset
            scaled_fish_y = fish_y - offset_y
        
            fish = pygame.transform.scale(fish, (fish.get_width() * camera_multiplier, fish.get_height() * camera_multiplier)) # scale sprite
            fish_collider = pygame.Rect(scaled_fish_x, scaled_fish_y, scaled_width, scaled_height) # create collider
        
            # Variables, drawing, collisions, and debugging for each map
        
            if is_lobby: 
                map_width = 1000
                map_height = 750
                camera_x = 0
                camera_y = 0
                shop_text = font_arial.render("Shop", True, BLACK)
                market_x = 750
                market_y = 200
        
                screen.blit(background, [0, 0]) 
                screen.blit(shopkeeper, [market_x + 50, market_y - 55])
                screen.blit(market_stall[8], [market_x, market_y - 20]) # counter
                screen.blit(market_stall[9], [market_x + 50, market_y - 20]) # counter
                screen.blit(market_stall[10], [market_x + 100, market_y - 20]) # counter
                screen.blit(market_stall[0], [market_x, market_y]) # base
                screen.blit(market_stall[1], [market_x + 50, market_y]) # base
                screen.blit(market_stall[2], [market_x + 100, market_y]) # base
                screen.blit(market_stall[3], [market_x + 5, market_y - 50]) # stick
                screen.blit(market_stall[4], [market_x + 95, market_y - 50]) # stick
                screen.blit(market_stall[5], [market_x, market_y - 95]) # top
                screen.blit(market_stall[6], [market_x + 50, market_y - 95]) # top
                screen.blit(market_stall[7], [market_x + 100, market_y - 95]) # top
                screen.blit(shop_text, (market_x + 46, market_y - 90))
        
                if gate_blocked: # create fence if blocked
                    screen.blit(fence_sprite[0], [90, 120]) # left
                    screen.blit(fence_sprite[1], [140, 120]) # middle
                    screen.blit(fence_sprite[2], [190, 120]) # right
                
                collisions = [
                    pygame.Rect(90, 20, 150, 100), 
                    pygame.Rect(market_x, market_y - 100, 150, 75), 
                    pygame.Rect(300, 0, 700, 100), 
                    pygame.Rect(950, 0, 50, 420), 
                    pygame.Rect(0, 500, 500, 100)
                ]
        
                big_gate_collider = pygame.Rect(120, 170, 100, 10)
                small_gate_collider = pygame.Rect(120, 612, 119, 10)
                shop_collider = pygame.Rect(750, 175, 150, 10)
        
                if gate_blocked and fish_collider.colliderect(big_gate_collider): # if gate is unblocked and player collides with gate
                    text = "The gate is blocked by a fence! You're not strong enough to cross!"
                    display_init = True
                    warning = True
                elif not gate_blocked and fish_collider.colliderect(big_gate_collider): # if gate is unblocked and player collides with gate
                    is_lobby = False # exit to advanced map
                    is_map2 = True
                    has_entered_map2 = True
        
                if fish_collider.colliderect(small_gate_collider): # if player collides with small gate
                    is_lobby = False # exit to beginner map
                    is_map1 = True
                    has_entered_map1 = True
                
                if fish_collider.colliderect(shop_collider): # shop collisions
                    openedShop = True
                else:
                    openedShop = False
                
                if debug_zones:
                    debug_collision([big_gate_collider, small_gate_collider, shop_collider])
        
            elif is_map1: 
                map_width = 2000 
                map_height = 1500
        
                camera_x, camera_y = update_camera(player_pos, map_width, map_height)
        
                screen.blit(map1, (-camera_x, -camera_y)) # draw map1 with camera offset (negative to move map opposite of camera)
        
                # Update spawn zones
                zone1_last_spawn = update_spawn_zone(zone1_x, zone1_y, zone1_width, zone1_height, zone1_max, zone1_respawn, zone1_last_spawn, zone1_fish_type, 0, 0, current_time)
                zone2_last_spawn = update_spawn_zone(zone2_x, zone2_y, zone2_width, zone2_height, zone2_max, zone2_respawn, zone2_last_spawn, zone2_fish_type, 1, 0, current_time)
                zone3_last_spawn = update_spawn_zone(zone3_x, zone3_y, zone3_width, zone3_height, zone3_max, zone3_respawn, zone3_last_spawn, zone3_fish_type, 2, 0, current_time)
                zone4_last_spawn = update_spawn_zone(zone4_x, zone4_y, zone4_width, zone4_height, zone4_max, zone4_respawn, zone4_last_spawn, zone4_fish_type, 3, 0, current_time)
                
                # Update and draw enemies
                for i in range(len(enemy_alive)): # for each enemy alive
                    if enemy_map[i] == 0:  # if enemy is in map1
                        enemy_width, enemy_height = draw_single_enemy(i, camera_x, camera_y)
                        update_single_enemy(i, player_pos, enemy_width, enemy_height)
        
                collisions = [
                    pygame.Rect(0 , 1400 , 900, 100), 
                    pygame.Rect(1100 , 1400 , 900, 100), 
                    pygame.Rect(0 , 550 , 50, 950), 
                    pygame.Rect(0 , 0 , 50, 500),
                    pygame.Rect(1950 , 0 , 50, 1500),
                    pygame.Rect(0 , 0 , 2000, 25),
                    pygame.Rect(0 , 1325 , 250, 50),
                    pygame.Rect(0 , 925 , 250, 50),
                    pygame.Rect(550 , 975 , 200, 50),
                    pygame.Rect(600 , 775 , 50, 50),
                    pygame.Rect(375 , 575 , 100, 100),
                    pygame.Rect(575 , 575 , 400, 50),
                    pygame.Rect(950 , 575 , 50, 250),
                    pygame.Rect(750 , 825 , 250, 50),
                    pygame.Rect(1025 , 200 , 225, 150),
                    pygame.Rect(1250 , 600 , 250, 50),
                    pygame.Rect(1500 , 550 , 50, 100),
                    pygame.Rect(1250 , 600 , 50, 250),
                    pygame.Rect(1250 , 825 , 525, 50),
                    pygame.Rect(1750 , 600 , 250, 50),
                    pygame.Rect(1250 , 1000 , 50, 500),
                    pygame.Rect(1250 , 1050 , 375, 50)
                ]
        
                exit_collider = pygame.Rect(900 , 1490 , 200, 10)
                secret_collider = pygame.Rect(0 , 500 , 10, 50)
        
                if debug_zones:
                    draw_spawn_zone_debug(zone1_x, zone1_y, zone1_width, zone1_height, camera_x, camera_y)
                    draw_spawn_zone_debug(zone2_x, zone2_y, zone2_width, zone2_height, camera_x, camera_y)
                    draw_spawn_zone_debug(zone3_x, zone3_y, zone3_width, zone3_height, camera_x, camera_y)
                    draw_spawn_zone_debug(zone4_x, zone4_y, zone4_width, zone4_height, camera_x, camera_y)
                    debug_collision([exit_collider, secret_collider])
        
                if fish_collider.colliderect(exit_collider): # if player collides with exit
                    is_map1 = False # exit to lobby
                    is_lobby = True
                    has_entered_lobby_map1 = True
        
                if fish_collider.colliderect(secret_collider): # if player collides with secret entrance   
                    is_map1 = False # exit to secret map
                    is_secret_map = True
                    has_entered_secret_map = True
        
            elif is_secret_map:
                map_width = 1000 
                map_height = 1000
        
                camera_x, camera_y = update_camera(player_pos, map_width, map_height)   
        
                screen.blit(secret_map, (-camera_x, -camera_y)) # draw secret map with camera offset)
                
        
                collisions = [
                    pygame.Rect(900, 0, 100, 400),
                    pygame.Rect(875, 500, 125, 500),
                    pygame.Rect(700, 0, 300, 50),
                    pygame.Rect(750, 50, 250, 25),
                    pygame.Rect(800, 75, 200, 50),
                    pygame.Rect(0, 0, 150, 1000),
                    pygame.Rect(0, 800, 1000, 200),
                    pygame.Rect(875, 550, 125, 450),
                    pygame.Rect(850, 600, 150, 400),
                    pygame.Rect(800, 650, 200, 350),
                    pygame.Rect(750, 700, 250, 300),
                    pygame.Rect(700, 750, 300, 250),
                    pygame.Rect(150, 500, 50, 500)
                ]
        
                exit_collider = pygame.Rect(990 , 0 , 10, 1000)
                blue_chest = blue_chest_sheet[0] # get unopened chest sprite
                if blue_chest_opened:
                    blue_chest_index = int((current_time - chest_open_start) / 3000 * 4) # when it's opened animate it opening
                    
                    if blue_chest_index > 3:
                        blue_chest_index = 3
                    
                    if blue_chest_index == 3 and not blue_chest_claimed:
                        fish_bones += 250
                        blue_chest_claimed = True
                        text = "You found 250 fish bones!"
                        display_init = True
                        warning = False
                    
                    blue_chest = blue_chest_sheet[blue_chest_index] # set sprite to new image
                    
                blue_chest_collider = pygame.Rect(250, 350, blue_chest.get_width() * 2, blue_chest.get_height() * 2) # scale sprite hitbox
                blue_chest = pygame.transform.scale(blue_chest, (blue_chest_collider.width, blue_chest_collider.height)) # apply scale to drawing
                
                screen.blit(blue_chest, (blue_chest_collider.x - camera_x, blue_chest_collider.y - camera_y)) # draw
                
                if fish_collider.colliderect(exit_collider): # if player collides with exit
                    is_secret_map = False # exit to map1
                    is_map1 = True
                    has_entered_map1_secret_map = True
                
                if fish_collider.colliderect(blue_chest_collider) and not blue_chest_opened:
                    blue_chest_opened = True # open chest when player collides with chest
                    chest_open_start = current_time
                
                if debug_zones:
                    debug_collision([exit_collider])
        
            elif is_map2:
                map_width = 2000 
                map_height = 1300
        
                camera_x, camera_y = update_camera(player_pos, map_width, map_height)
        
                screen.blit(map2, (-camera_x, -camera_y)) # draw map2 with camera offset)
        
                # Update spawn zones
                zone5_last_spawn = update_spawn_zone(zone5_x, zone5_y, zone5_width, zone5_height, zone5_max, zone5_respawn, zone5_last_spawn, zone5_fish_type, 0, 1, current_time)
                zone6_last_spawn = update_spawn_zone(zone6_x, zone6_y, zone6_width, zone6_height, zone6_max, zone6_respawn, zone6_last_spawn, zone6_fish_type, 1, 1, current_time)
                zone7_last_spawn = update_spawn_zone(zone7_x, zone7_y, zone7_width, zone7_height, zone7_max, zone7_respawn, zone7_last_spawn, zone7_fish_type, 2, 1, current_time)
        
                # Update and draw enemies
                for i in range(len(enemy_alive)):
                    if enemy_map[i] == 1: # if enemy is in map2
                        enemy_width, enemy_height = draw_single_enemy(i, camera_x, camera_y)
                        update_single_enemy(i, player_pos, enemy_width, enemy_height)
        
                collisions = [
                    pygame.Rect(0 , 200 , 100, 1100),
                    pygame.Rect(0 , 1150 , 175, 150),
                    pygame.Rect(0 , 675, 200, 250),
                    pygame.Rect(0 , 300, 250, 200),
                    pygame.Rect(250, 300, 175, 225),
                    pygame.Rect(400, 1200, 1200, 100),
                    pygame.Rect(375, 1150, 300, 50),
                    pygame.Rect(375, 1100, 225, 50),
                    pygame.Rect(375, 1050, 125, 50),
                    pygame.Rect(525, 850, 100, 300),
                    pygame.Rect(600, 850, 100, 100),
                    pygame.Rect(650, 725, 125, 175),
                    pygame.Rect(700, 575, 75, 150),
                    pygame.Rect(700, 275, 75, 175),
                    pygame.Rect(750, 225, 400, 175),
                    pygame.Rect(1300, 400, 150, 150),
                    pygame.Rect(1600, 300, 100, 275),
                    pygame.Rect(1650, 250, 350, 125),
                    pygame.Rect(1700, 200, 300, 75),
                    pygame.Rect(1600, 675, 100, 600),
                    pygame.Rect(1900, 200, 100, 1100)
                ]
        
                exit_collider = pygame.Rect(200 , 1290 , 200, 10)
                hallway_collider = pygame.Rect(1700 , 1290 , 150, 10)
                
        
                if fish_collider.colliderect(exit_collider): # if player collides with exit set to lobby
                    is_map2 = False 
                    is_lobby = True
                    has_entered_lobby_map2 = True
        
                if fish_collider.colliderect(hallway_collider): # if player collides with hallway entrance set to hallway
                    is_map2 = False 
                    is_hallway = True
                    has_entered_hallway_map2 = True
        
                if debug_zones:
                    draw_spawn_zone_debug(zone5_x, zone5_y, zone5_width, zone5_height, camera_x, camera_y)
                    draw_spawn_zone_debug(zone6_x, zone6_y, zone6_width, zone6_height, camera_x, camera_y)
                    draw_spawn_zone_debug(zone7_x, zone7_y, zone7_width, zone7_height, camera_x, camera_y)
                    debug_collision([exit_collider, hallway_collider])
        
            elif is_hallway:
                map_width = 1000 
                map_height = 1500
        
                camera_x, camera_y = update_camera(player_pos, map_width, map_height)
        
                screen.blit(hallway, (-camera_x, -camera_y)) # draw hallway with camera offset)
        
                collisions = [
                    pygame.Rect(0, -10, 1000, 10),
                    pygame.Rect(0, 1500, 1000, 10),
                    pygame.Rect(150, 0, 100, 1500),
                    pygame.Rect(750, 0, 100, 1500)
                ]
        
                exit_collider = pygame.Rect(0 , 0 , 1000, 10)
                map3_collider = pygame.Rect(0 , 1490 , 1000, 10)
        
                if fish_collider.colliderect(exit_collider): # if player collides with exit set to map2
                    is_hallway = False 
                    is_map2 = True
                    has_entered_map2_hallway = True
        
                if fish_collider.colliderect(map3_collider): # if player collides with map3 entrance set to map3
                    is_hallway = False 
                    is_map3 = True
                    has_entered_map3 = True
        
                if debug_zones:
                    debug_collision([exit_collider, map3_collider])
        
            elif is_map3:
                map_width = 1500 
                map_height = 1125
                boss_sprite = pygame.transform.scale(boss_spritesheet[boss_direction][boss_frame], (250, 250)) # get boss sprite for hitboxes
        
                camera_x, camera_y = update_camera(player_pos, map_width, map_height)    
        
                screen.blit(map3, (-camera_x, -camera_y)) # draw map3 with camera offset)
                
                if not boss_exists and boss_defeated and not sliver_chest_claimed:
                    sliver_chest = sliver_chest_sheet[0] # get unopened chest sprite
                    if sliver_chest_opened:
                        sliver_chest_index = int((current_time - chest_open_start) / 3000 * 4) # when it's opened animate it opening
                        
                        if sliver_chest_index > 3:
                            sliver_chest_index = 3
                        
                        if sliver_chest_index == 3:
                            sliver_chest_claimed = True
                            text = "You found the GOLDEN FISH!"
                            display_init = True
                            warning = False
                            display_fish = True
                        
                        sliver_chest = sliver_chest_sheet[sliver_chest_index] # set sprite to new image
                        
                    sliver_chest_collider = pygame.Rect(700, 500, sliver_chest.get_width() * 2, sliver_chest.get_height() * 2) # scale sprite hitbox
                    sliver_chest = pygame.transform.scale(sliver_chest, (sliver_chest_collider.width, sliver_chest_collider.height)) # apply scale to drawing
                    
                    screen.blit(sliver_chest, (sliver_chest_collider.x - camera_x, sliver_chest_collider.y - camera_y)) # draw                
                    
                    if fish_collider.colliderect(sliver_chest_collider) and not sliver_chest_opened:
                        sliver_chest_opened = True # open chest when player collides with chest
                        chest_open_start = current_time                
        
                update_boss(player_pos, current_time) # update boss values
        
                # Update and draw boss slash attack
        
                if boss_exists and boss_slash_active: # when boss exists and slash is active
                    slash_time = current_time - boss_slash_start # time elapsed since slash started
        
                    if slash_time < 500: # slash time lasts 0.5 seconds
                        frame = int(slash_time / 500 * 4) # rotate through each frame evenly  
                        slash_sprite = pygame.transform.scale(slash_spritesheet[boss_direction][frame], (boss_sprite.get_width(), boss_sprite.get_height())) # get slash sprite based on direction and frame
        
                        if frame > 3:  # clamp to prevent out of range index
                            frame = 3
        
                        if boss_direction == 0:  # down, get x and y for slash, slash is pushed halfway toward direction boss is facing
                            slash_x = boss_x
                            slash_y = boss_y + boss_sprite.get_height() / 2
                        elif boss_direction == 1:  # left
                            slash_x = boss_x - boss_sprite.get_width() / 2 
                            slash_y = boss_y
                        elif boss_direction == 2:  # right
                            slash_x = boss_x + boss_sprite.get_width() / 2
                            slash_y = boss_y
                        else:  # up
                            slash_x = boss_x
                            slash_y = boss_y - boss_sprite.get_height() / 2
                            
                        slash_rect = pygame.Rect(slash_x, slash_y, boss_sprite.get_width(), boss_sprite.get_height()) # create collider and draw
                        screen.blit(slash_sprite, (slash_x - camera_x, slash_y - camera_y))
        
                        if debug_zones:
                            pygame.draw.rect(screen, GREEN, [slash_x - camera_x, slash_y - camera_y, boss_sprite.get_width(), boss_sprite.get_height()], 4)
                        
                        if fish_collider.colliderect(slash_rect): # deal damage when player collides with slash
                            health -= 100  
                
                # Update and draw tentacle indicators
        
                indices_to_remove = [] # get a list of indicators to remove
                for i in range(len(tentacle_warning_x)): # for each tentacle indicator
                    time_elapsed = current_time - tentacle_warning_start[i] # get time elapsed since start of warning
                    
                    if time_elapsed >= tentacle_indicator_duration: # if time passed indicator duration spawn tentacle and add indicator to remove list
                        tentacle_active_x.append(tentacle_warning_x[i])
                        tentacle_active_y.append(tentacle_warning_y[i])
                        tentacle_active_start.append(current_time)
                        indices_to_remove.append(i)
                    else: # if not then draw indicator that is from black to red based on when the attack will start
                        pygame.draw.circle(screen, (time_elapsed / tentacle_indicator_duration * 255, 0, 0), [tentacle_warning_x[i] - camera_x, tentacle_warning_y[i] - camera_y], 75)
        
                # Remove values of indicators
                for i in sorted(indices_to_remove, reverse=True): # sorted returns the value of a list in ascending order instead of going 0 - # like in range, 
                    # reverse makes the list start at the highest to lowest (this prevents the index from going out of range because the indices of each value are not changing as we iterate through each one)
                    del tentacle_warning_x[i]
                    del tentacle_warning_y[i]
                    del tentacle_warning_start[i]
        
                # Update and draw active tentacles
        
                indices_to_remove = [] # list of tentacles to removes
                for i in range(len(tentacle_active_x)): # for each tentacle
                    time_elapsed = current_time - tentacle_active_start[i] # get time elapsed since tentacle spawned
                    
                    if time_elapsed >= tentacle_active_duration: # if time passed active duration add to remove list
                        indices_to_remove.append(i)
                    else: # if tentacle is still active
                        frame = int(time_elapsed / tentacle_active_duration * 4) # get frames evenly based on the current time of the attack
        
                        if frame > 3:  # clamp to prevent out of range index
                            frame = 3
        
                        screen.blit(tentacle_spritesheet[0][frame], (tentacle_active_x[i] - 70 - camera_x, tentacle_active_y[i] - 160 - camera_y)) # draw tentacle (adjusted to align with circle)
                        
                        tentacle_rect = pygame.Rect(tentacle_active_x[i] - 75, tentacle_active_y[i] - 75, 150, 150)
        
                        if fish_collider.colliderect(tentacle_rect): # check collision with player
                            health -= 50
                        
                        if debug_zones:
                            pygame.draw.rect(screen, GREEN, [tentacle_rect.x - camera_x, tentacle_rect.y - camera_y, tentacle_rect.width, tentacle_rect.height], 4)
                        
        
                # Remove values of finished tentacles
                for i in sorted(indices_to_remove, reverse=True):
                    del tentacle_active_x[i]
                    del tentacle_active_y[i]
                    del tentacle_active_start[i]
        
                # Update boss ink ball projectiles
        
                indices_to_remove = [] # list of ink balls to remove
                for i in range(len(boss_projectile_x)): # for each ink ball
                    boss_projectile_x[i] += boss_projectile_dx[i] # move in it's corresponding direction
                    boss_projectile_y[i] += boss_projectile_dy[i]
                    time_elapsed = current_time - boss_projectile_start[i] # get time elpased since ink ball spawned
                    
                    if time_elapsed > boss_projectile_lifetime: # if past lifetime add to remove list
                        indices_to_remove.append(i)
                    else: # if not past life time
                        pygame.draw.circle(screen, INK_BLACK, [boss_projectile_x[i] - camera_x, boss_projectile_y[i] - camera_y], 12) # draw ink ball at correct position
                        pygame.draw.circle(screen, INK_GREY, [boss_projectile_x[i] - camera_x, boss_projectile_y[i] - camera_y], 8)
                        
                        proj_rect = pygame.Rect(boss_projectile_x[i] - 12, boss_projectile_y[i] - 12, 24, 24)
                        
                        if fish_collider.colliderect(proj_rect): # check collision with player
                            health -= 1000  # damage and remove
                            indices_to_remove.append(i)
        
                # Remove values of deleted projectiles
                for i in sorted(indices_to_remove, reverse=True):
                    del boss_projectile_x[i]
                    del boss_projectile_y[i]
                    del boss_projectile_dx[i]
                    del boss_projectile_dy[i]
                    del boss_projectile_start[i]
        
                # Update and draw boss lazer
        
                if boss_lazer_active and boss_exists: # when lazer is active and boss is alive
                    time_elapsed = current_time - boss_lazer_start # get time elapsed since lazer started
                    
                    if time_elapsed < boss_lazer_charge_time: # if time elapsed is in the lazer's charge duration draw warning line and have it go from black to red based on time until fire
                        pygame.draw.line(screen, (time_elapsed / boss_lazer_charge_time * 255, 0, 0), [boss_x + 125 - camera_x, boss_y + 125 - camera_y], [lazer_end_x - camera_x, lazer_end_y - camera_y], 3)
                    elif time_elapsed < boss_lazer_charge_time + boss_lazer_duration: # if time to shoot (if we want to have the exact same duration as the one we choose we have to add the previous as we don't calculate a new time elapsed)
                        # draw lazer
                        pygame.draw.line(screen, INK_BLACK, [boss_x + 125 - camera_x, boss_y + 125 - camera_y], [lazer_end_x - camera_x, lazer_end_y - camera_y], 15)
                        pygame.draw.line(screen, INK_GREY, [boss_x + 125 - camera_x, boss_y + 125 - camera_y], [lazer_end_x - camera_x, lazer_end_y - camera_y], 8)
                        
                        
                        if fish_collider.clipline([boss_x + 125, boss_y + 125], [lazer_end_x, lazer_end_y]):  # check if player is touching lazer and deal damage
                            health -= boss_lazer_damage
                        
                        if debug_zones:
                            pygame.draw.line(screen, GREEN, [boss_x + 125 - camera_x, boss_y + 125 - camera_y], [lazer_end_x - camera_x, lazer_end_y - camera_y], 4)
                    else: # if lazer duration is over reset
                        boss_lazer_active = False
                        boss_lazer_cooldown = current_time
                else: # get distances when boss is not attacking so lazer doesn't follow player while shooting
                    boss_lazer_dx = player_pos[0] - (boss_x + 125) # calculate distance to player from boss center
                    boss_lazer_dy = player_pos[1] - (boss_y + 125)
                    boss_lazer_distance = math.sqrt(boss_lazer_dx ** 2 + boss_lazer_dy ** 2)
                    lazer_end_x = boss_x + 125 + boss_lazer_dx / boss_lazer_distance * boss_lazer_length # calulate the end of the lazer (normalizing dx and dy then multipling by length)
                    lazer_end_y = boss_y + 125 + boss_lazer_dy / boss_lazer_distance * boss_lazer_length
        
                draw_boss(camera_x, camera_y) # draw boss sprite
        
                collisions = [
                    pygame.Rect(575, 0, 150, 125),
                    pygame.Rect(825, 0, 675, 125),
                    pygame.Rect(0, 0, 300, 50),
                    pygame.Rect(0, 50, 225, 50),
                    pygame.Rect(0, 100, 150, 50),
                    pygame.Rect(0, 150, 100, 50),
                    pygame.Rect(0, 150, 100, 200),
                    pygame.Rect(1150, 125, 350, 150),
                    pygame.Rect(1400, 275, 100, 150),
                    pygame.Rect(1450, 275, 50, 1025),
                    pygame.Rect(1400, 925, 100, 200),
                    pygame.Rect(1350, 975, 150, 150),
                    pygame.Rect(0, 1025, 1500, 100),
                    pygame.Rect(0, 600, 100, 525),
                    pygame.Rect(100, 750, 100, 375),
                    pygame.Rect(200, 850, 50, 275),
                    pygame.Rect(250, 900, 100, 225),
                    pygame.Rect(825, 975, 150, 350),
                    pygame.Rect(925, 925, 150, 100)
                ]
        
                exit_collider = pygame.Rect(725, 0, 100, 10)
        
                if fish_collider.colliderect(exit_collider): # if player collides with exit set to hallway
                    is_map3 = False 
                    is_hallway = True
                    has_entered_hallway_map3 = True
                    boss_exists = False # reset boss
                    tentacle_warning_x = []
                    tentacle_warning_y = []
                    tentacle_warning_start = []
                    tentacle_active_x = []
                    tentacle_active_y = []
                    tentacle_active_start = []
                    boss_projectile_x = []
                    boss_projectile_y = []
                    boss_projectile_dx = []
                    boss_projectile_dy = []
                    boss_projectile_start = []
                    boss_lazer_active = False
        
                if debug_zones:
                    debug_collision([exit_collider])
        
            indices_to_remove = [] # list of enemies to remove
            for i in range(len(enemy_alive)): # for each enemy
                if not enemy_alive[i]: # if enemy is not alive
                    indices_to_remove.append(i) # add index to list
        
            # Remove values of dead enemies
            for i in sorted(indices_to_remove, reverse=True):
                del enemy_x[i]
                del enemy_y[i]
                del enemy_type[i]
                del enemy_direction[i]
                del enemy_frame[i]
                del enemy_anim_timer[i]
                del enemy_speed[i]
                del enemy_health[i]
                del enemy_alive[i]
                del enemy_zone_index[i]
                del enemy_map[i]
                del enemy_scale[i]
                del enemy_zone_x[i]
                del enemy_zone_y[i]
                del enemy_zone_width[i]
                del enemy_zone_height[i]
                del enemy_attacking[i]
                del enemy_attack_start[i]
                del enemy_attack_cooldown[i]
        
            if debug_zones:
                debug_collision(collisions)
        
            handle_collision(fish_collider, collisions) # handle collisions with obstacles
        
            # Movement
        
            if dashing:
                freeze = True # can't move while dashing
                if current_time - dash_start <= 100: # lasts 100 ms
                    if direction == 0: # down
                        player_pos[1] += 25 # move player fast in direction they're facing
                    elif direction == 1: # left
                        player_pos[0] -= 25
                    elif direction == 2: # right
                        player_pos[0] += 25
                    else: # up
                        player_pos[1] -= 25
                else: # 100 ms over, dash is over
                    dashing = False 
                    freeze = False
        
        
            if not freeze: # only move if not frozen in place
                dx = 0 # Change in x
                dy = 0 # Change in y
        
                if left: # move left
                    dx -= 1
        
                if right: # move right
                    dx += 1
        
                if up: # move up
                    dy -= 1
        
                if down: # move down
                    dy += 1
                
                if dx != 0 or dy != 0: # if there is movement
                    length = math.sqrt(dx ** 2 + dy ** 2) # get distance
                    dx = dx / length * player_speed # normalize and scale by player speed
                    dy = dy / length * player_speed 
                    player_pos[0] += dx # update player position
                    player_pos[1] += dy
        
                    # keep player within map boundaries
        
                    if player_pos[0] > map_width - fish_width / 2: 
                        player_pos[0] = map_width - fish_width / 2
                    
                    if player_pos[0] < 0 + fish_width / 2:
                        player_pos[0] = 0 + fish_width / 2
                    
                    if player_pos[1] > map_height - fish_height / 2: 
                        player_pos[1] = map_height - fish_height / 2
                    
                    if player_pos[1] < 0 + fish_height / 2:
                        player_pos[1] = 0 + fish_height / 2
        
                    # Determine direction, this way fish faces movement instead of last key pressed (more natural, or else it looks like it's moonwalking)
        
                    if abs(dx) > abs(dy): # horizontal movement is greater than vertical
                        if dx > 0: # moving right
                            direction = 2  # right
                        else: 
                            direction = 1  # left
                    else:
                        if dy > 0: # moving down
                            direction = 0  # down
                        else:
                            direction = 3  # up
        
                    # Animate
        
                    animation_timer += swim_animation_speed # increment timer by animation speed
        
                    if animation_timer >= 1: # if timer reaches 1, change frame
                        animation_timer = 0 # reset timer
                        current_frame = (current_frame + 1) % 4 # cycle through frames 0-3
                else: # no movement
                    current_frame = 0 # reset to idle frame
        
            # make positive map indices if is a map that can spawn enemies
        
            if is_map1:
                current_map_index = 0
            elif is_map2:
                current_map_index = 1
            elif is_map3:
                current_map_index = 2
            else:
                current_map_index = -1
        
                # Player attack 
        
            if attacking: # if attacking
                attack_time = current_time - attack_start # find time elapsed
        
                if attack_time < attack_duration: # if attack is not over 
                    bite(direction, attack_time) # set attack offsets and attack progress
                    attack_dx = int(attack_dx * camera_multiplier) # scale changes by the camera multiplier
                    attack_dy = int(attack_dy * camera_multiplier)
        
                    if attack_progress < 0.5: # first half of attack, show bite sprite
                        sprite = current_bite # set sprite to bite sprite
                        attack_properties(direction) # set attack hitbox properties
                        attack_width = int(attack_width * camera_multiplier) # scale attack properties based on camera multiplier
                        attack_height = int(attack_height * camera_multiplier)
                        attack_offset_x = int(attack_offset_x * camera_multiplier)
                        attack_offset_y = int(attack_offset_y * camera_multiplier)
                        # Draw attack hitbox
                        attack_rect = pygame.Rect(scaled_fish_x + attack_dx + attack_offset_x, scaled_fish_y + attack_dy + attack_offset_y, attack_width, attack_height)
                        if debug_zones:
                            pygame.draw.rect(screen, GREEN, [scaled_fish_x + attack_dx + attack_offset_x - camera_x, scaled_fish_y + attack_dy + attack_offset_y - camera_y, attack_width, attack_height], 4)
        
                        # Check boss collision
                        if boss_exists and is_map3:
                            boss_rect = pygame.Rect(boss_x, boss_y, boss_sprite.get_width(), boss_sprite.get_height())
                            
                            if debug_zones:
                                pygame.draw.rect(screen, BLUE, [boss_x - camera_x, boss_y - camera_y, boss_sprite.get_width(), boss_sprite.get_height()], 4)
                            
                            if attack_rect.colliderect(boss_rect):
                                boss_health -= damage
                                
                                if boss_health <= 0:
                                    boss_exists = False
                                    text = "BOSS DEFEATED!"
                                    boss_defeated = True
                                    display_init = True
                                    warning = False
                        
                        if current_map_index >= 0: # only check for enemies if in a map with enemies
                            for i in range(len(enemy_alive)): # check all enemies
                                if enemy_map[i] == current_map_index: # if enemy is in current map create hitbox based on type
                                    enemy_rect = get_enemy_collider(i) # get enemy collider
        
                                    if attack_rect.colliderect(enemy_rect): # if attack collides with enemy
                                        enemy_health[i] -= damage # deal damage to enemy
                                        if enemy_health[i] <= 0: # if enemy health is 0 or less
                                            if enemy_alive[i]: # if the enemy is alive allow resources to be added, then set alive to false so that it only happens once
                                                if enemy_type[i] == 0: # how much points and bones player gains based on fish type
                                                    points_gain = 1
                                                    bones_gain = 1
                                                elif enemy_type[i] == 1:
                                                    points_gain = 10
                                                    bones_gain = 3
                                                elif enemy_type[i] == 2:
                                                    points_gain = 150
                                                    bones_gain = 10
                                                elif enemy_type[i] == 3:
                                                    points_gain = 1000
                                                    bones_gain = 25
                                                elif enemy_type[i] == 4:
                                                    points_gain = 25000
                                                    bones_gain = 100
                                                elif enemy_type[i] == 5:
                                                    points_gain = 100000
                                                    bones_gain = 350
        
                                                xp_points += points_gain # add gain to amount
                                                fish_bones += bones_gain
        
                                                if points_gain == 1 and bones_gain == 1: # make sure the grammar is correct and display text as not a warning
                                                    text = "You gained " + str(points_gain) + " point and " + str(bones_gain) + " fish bone!"
                                                elif points_gain == 1:
                                                    text = "You gained " + str(points_gain) + " point and " + str(bones_gain) + " fish bones!"
                                                elif bones_gain == 1:
                                                    text = "You gained " + str(points_gain) + " points and " + str(bones_gain) + " fish bone!"
                                                else:
                                                    text = "You gained " + str(points_gain) + " points and " + str(bones_gain) + " fish bones!"
                                                display_init = True
                                                warning = False
                                            enemy_alive[i] = False # mark enemy as dead
                    else: # second half of attack, show normal fish sprite
                        sprite = fish
                    screen.blit(sprite, (scaled_fish_x + attack_dx - camera_x, scaled_fish_y + attack_dy - camera_y)) # draw fish with attack offsets
                else: # if attack is over
                    attacking = False # stop attacking
                    freeze = False # unfreeze movement
            else: # if not attacking, just draw fish normally
                screen.blit(fish, (scaled_fish_x - camera_x, scaled_fish_y - camera_y))
        
            if debug_zones:
                pygame.draw.rect(screen, RED, [fish_x - offset_x - camera_x, fish_y - offset_y - camera_y, scaled_width, scaled_height], 4) 
        
            # Player shoot
        
            if shooting and shoot_mode and not openedShop:
                if current_time - lazer_cooldown >= lazer_cooldown_time: # if cooldown over
                    if stamina - 25 > 0: # if stamina is enough
                        world_mouse_x = mouse_x + camera_x # get mouse world coordinates
                        world_mouse_y = mouse_y + camera_y
                        
                        dx = world_mouse_x - player_pos[0] # calculate distance to player
                        dy = world_mouse_y - player_pos[1]
                        distance = math.sqrt(dx ** 2 + dy ** 2)
                        
                        if distance > 0: # if mouse is not at player center
                            dx = dx / distance * lazer_speed # normalize and scale by speed
                            dy = dy / distance * lazer_speed
                            lazer_x.append(player_pos[0]) # create lazer projectile and take stamina
                            lazer_y.append(player_pos[1])
                            lazer_dx.append(dx)
                            lazer_dy.append(dy)
                            lazer_lifetime.append(current_time)
                            lazer_cooldown = current_time
                            stamina -= 25
                    else: # else warn player low stamina
                        text = "Stamina too low!"
                        warning = True
                        display_init = True
        
            indices_to_remove = []
            for i in range(len(lazer_x)): # for each lazer
                lazer_x[i] += lazer_dx[i] # move lazer by changes
                lazer_y[i] += lazer_dy[i]
                
                if current_time - lazer_lifetime[i] > lazer_max_lifetime: # remove lazer when lifetime is up
                    indices_to_remove.append(i)
                    continue
                
                start_x = lazer_x[i] # get start positions of the line
                start_y = lazer_y[i]
                speed = math.sqrt(lazer_dx[i] ** 2 + lazer_dy[i] ** 2) # calulate lazer direction and normalize 
                direction_x = lazer_dx[i] / speed
                direction_y = lazer_dy[i] / speed
                end_x = start_x - direction_x * lazer_length # get the end position of the line
                end_y = start_y - direction_y * lazer_length
                lazer_line = [[start_x, start_y], [end_x, end_y]] # create line 
                
                pygame.draw.line(screen, LAZER_BLUE, [lazer_line[0][0] - camera_x, lazer_line[0][1] - camera_y], [lazer_line[1][0] - camera_x, lazer_line[1][1] - camera_y], 12) # draw lazer (outside)
                pygame.draw.line(screen, LAZER_WHITE, [lazer_line[0][0] - camera_x, lazer_line[0][1] - camera_y], [lazer_line[1][0] - camera_x, lazer_line[1][1] - camera_y], 4) # inside
                
                
                if debug_zones:
                    pygame.draw.line(screen, GREEN, [lazer_line[0][0] - camera_x, lazer_line[0][1] - camera_y], [lazer_line[1][0] - camera_x, lazer_line[1][1] - camera_y], 4)
        
                if boss_exists and is_map3: # boss checks
                    boss_rect = pygame.Rect(boss_x, boss_y, boss_sprite.get_width(), boss_sprite.get_height())
                    
                    if debug_zones:
                        pygame.draw.rect(screen, BLUE, [boss_x - camera_x, boss_y - camera_y, boss_sprite.get_width(), boss_sprite.get_height()], 4)
                    
                    if boss_rect.clipline(lazer_line): # if lazer collides with boss deal damage and check if defeated
                        boss_health -= lazer_damage
                        
                        if boss_health <= 0:
                            boss_exists = False
                            text = "BOSS DEFEATED!"
                            boss_defeated = True
                            display_init = True
                            warning = False
        
                if current_map_index >= 0: # if in a map with enemies
                    for j in range(len(enemy_alive)): # for each enemy alive
                        if enemy_map[j] == current_map_index: # if enemy is in the correct map 
                            enemy_rect = get_enemy_collider(j) # get collider
        
                            if enemy_rect.clipline(lazer_line): # check is lazer hit enemy
                                enemy_health[j] -= lazer_damage # deal damage
                                
                                if enemy_health[j] <= 0: # if health is less than 0 and still alive reward player and set enemy to dead
                                    if enemy_alive[j]:
                                        if enemy_type[j] == 0:
                                            points_gain = 1
                                            bones_gain = 1
                                        elif enemy_type[j] == 1:
                                            points_gain = 10
                                            bones_gain = 3
                                        elif enemy_type[j] == 2:
                                            points_gain = 150
                                            bones_gain = 10
                                        elif enemy_type[j] == 3:
                                            points_gain = 1000
                                            bones_gain = 25
                                        elif enemy_type[j] == 4:
                                            points_gain = 7500
                                            bones_gain = 75
                                        elif enemy_type[j] == 5:
                                            points_gain = 25000
                                            bones_gain = 250
                                        
                                        xp_points += points_gain 
                                        fish_bones += bones_gain
                                        
                                        if points_gain == 1 and bones_gain == 1: # make sure the grammar is correct and display text as not a warning
                                            text = "You gained " + str(points_gain) + " point and " + str(bones_gain) + " fish bone!"
                                        elif points_gain == 1:
                                            text = "You gained " + str(points_gain) + " point and " + str(bones_gain) + " fish bones!"
                                        elif bones_gain == 1:
                                            text = "You gained " + str(points_gain) + " points and " + str(bones_gain) + " fish bone!"
                                        else:
                                            text = "You gained " + str(points_gain) + " points and " + str(bones_gain) + " fish bones!"
                                        display_init = True
                                        warning = False
                                        enemy_alive[j] = False
        
            for i in sorted(indices_to_remove, reverse=True): # delete old lazers and from highest index to lowest
                del lazer_x[i]
                del lazer_y[i]
                del lazer_dx[i]
                del lazer_dy[i]
                del lazer_lifetime[i]
        
            # Enemy attack
        
            for i in range(len(enemy_alive)): # for each enemy alive
                if enemy_alive[i] and enemy_attacking[i]: # if enemy is alive and is attacking
                    if enemy_type[i] == 2: # get the sprite based on direction, frame, and type
                        sprite = fish3_spritesheet[enemy_direction[i]][enemy_frame[i]] 
                    elif enemy_type[i] == 5:
                        sprite = fish6_spritesheet[enemy_direction[i]][enemy_frame[i]]
        
                    attack_time = current_time - enemy_attack_start[i] # calculate how long attack has gone on
        
                    if attack_time < 100:  # Damage window during attack animation
                        # Get the x, y, width, and height values of the enemy attack based on direction
                        if enemy_direction[i] == 0:  # down
                            attack_x = enemy_x[i]
                            attack_y = enemy_y[i] + sprite.get_height() / 2 # making the hitbox shorter based on the way that it's facing and pushing it infront, but not all the way, so that it's still on the fish
                            enemy_attack_width = sprite.get_width()
                            enemy_attack_height = sprite.get_height() / 2
                        elif enemy_direction[i] == 1:  # left
                            attack_x = enemy_x[i] - sprite.get_width() / 2
                            attack_y = enemy_y[i]
                            enemy_attack_width = sprite.get_width() / 2
                            enemy_attack_height = sprite.get_height() 
                        elif enemy_direction[i] == 2:  # right
                            attack_x = enemy_x[i] + sprite.get_width() / 2
                            attack_y = enemy_y[i]
                            enemy_attack_width = sprite.get_width() / 2
                            enemy_attack_height = sprite.get_height()
                        else:  # up
                            attack_x = enemy_x[i]
                            attack_y = enemy_y[i] - sprite.get_height() / 2
                            enemy_attack_width = sprite.get_width()
                            enemy_attack_height = sprite.get_height() / 2
                        
                        enemy_attack_rect = pygame.Rect(attack_x, attack_y, enemy_attack_width, enemy_attack_height) # create hitbox
        
                        if debug_zones:
                            pygame.draw.rect(screen, GREEN, [attack_x - camera_x, attack_y - camera_y, enemy_attack_width, enemy_attack_height], 4)
                        
                        if fish_collider.colliderect(enemy_attack_rect): # if player collides with the enemy's attack
                            if enemy_type[i] == 2: # damage based on attack type
                                health -= 15
                            elif enemy_type[i] == 5:
                                health -= 200
        
            # Enemy shoot
        
            indices_to_remove = []
            for i in range(len(projectile_alive)): # for each projectile
        
                projectile_x[i] += projectile_dx[i] # move projectile by the changes 
                projectile_y[i] += projectile_dy[i]
                
                if current_time - projectile_lifetime[i] > projectile_max_lifetime: # if projectile lifetime is up add projectile to list of projectiles to remove and move on to next
                    indices_to_remove.append(i)
                    continue
                
                pygame.draw.circle(screen, PROJ_PURPLE, [projectile_x[i] - camera_x, projectile_y[i] - camera_y], 8) # draw projectile
                
                proj_rect = pygame.Rect(projectile_x[i] - 8, projectile_y[i] - 8, 16, 16) # offset rect by radius because circle x and y is at it's center
        
                if debug_zones:
                    pygame.draw.rect(screen, GREEN, [proj_rect.x - camera_x, proj_rect.y - camera_y, proj_rect.width, proj_rect.height], 4)
        
                if fish_collider.colliderect(proj_rect): # if player collides with projectile
                    health -= 500  # Damage player
                    indices_to_remove.append(i) # remove projectile
        
            # Remove removable projectiles
            for i in sorted(indices_to_remove, reverse=True): # sorts numerically, reverse removes largest indices first so that the index positions don't change (else the index to del make go out of range)
                del projectile_x[i] 
                del projectile_y[i]
                del projectile_dx[i]
                del projectile_dy[i]
                del projectile_lifetime[i]
                del projectile_alive[i]
        
            # Player stat handling
        
            if xp_points >= xp_to_level and not level >= max_level: # level up if xp points are greater than xp need to get tot eh next level level is not greater or equal to max 
                health = max_health # heal player to their previous max health
                level += 1
                xp_points -= xp_to_level 
                text = "You leveled up!"
                display_init = True
                warning = False
        
            if level == max_level and xp_points > xp_to_level: # if max level and xp points is greater than limit, set points to the limit
                xp_points = xp_to_level
        
            xp_to_level = 1 * (level ** 2) # calculate player stats based on level
            max_health = 10000 * (level / max_level) 
            regen_health = 1 * (level / max_level) 
            damage = 2000 * (level / max_level)
            health += regen_health # heal
        
            if health > max_health: # keep health in the correct ranges
                health = max_health
            elif health < 0: # gameover
                gameover = True
                transparency = 0
                health = 0
        
            stamina += stamina_regen # replenish stamina
            if stamina > max_stamina:
                stamina = max_stamina # keep stamina below max
        
            # Level and health display 
            
            level_display_scale = xp_points / xp_to_level
            
            if level_display_scale > 1: # make sure display doesn't go past length
                level_display_scale = 1
            
            screen.blit(font_bogle.render("Level: " + str(level), True, BLACK), (235, 22)) # level display
            pygame.draw.rect(screen, BLACK, [25, 25, 200, 25]) # background for level display
            pygame.draw.rect(screen, EXP_BLUE, [27, 27, 196 * level_display_scale, 21]) # level display
        
            pygame.draw.rect(screen, BLACK, [775, 25, 200, 25]) # background for health display
            pygame.draw.rect(screen, RED, [777, 27, 196 * (health / max_health), 21]) # health display
            screen.blit(font_arial_health.render("♥︎", True, RED), (750, 12)) # heart
            screen.blit(font_arial_exp.render(str(int(health)), True, WHITE), (783, 30)) # health text display
        
            screen.blit(font_bogle.render("Stamina: ", True, BLACK), (700, 73)) # stamina text display
            pygame.draw.rect(screen, BLACK, [775, 75, 200, 25]) # background for stamina display
            pygame.draw.rect(screen, BG_STAMINA_GREEN, [777, 77, 196, 21]) # stamina bg display
            pygame.draw.rect(screen, STAMINA_GREEN, [777, 77, 196 * (stamina / max_stamina), 21]) # stamina display
        
            screen.blit(fish_bone, (20, 50)) # fish bones display
            screen.blit(font_arial_health.render(str(fish_bones), True, PALE), (90, 60))
            
            if sliver_chest_claimed: # display trophy icon
                screen.blit(trophy_fish_icon, (900, 650))
        
            if is_map3 and boss_exists:
                screen.blit(font_bogle_boss.render("Octopus", True, BLACK), (430, 650)) # draw boss text
                health_percent = boss_health / boss_max_health # draw health bar
                pygame.draw.rect(screen, BLACK, [50, 700, 900, 25])
                pygame.draw.rect(screen, RED, [52, 702, int(896 * health_percent), 21])
        
            if openedShop: # shop display
                pygame.draw.rect(screen, SHOP_BROWN, [100, 0, 800, 750]) 
                screen.blit(fish_bone, (120, 15))
                screen.blit(font_arial_health.render(str(fish_bones), True, PALE), (190, 25))
                screen.blit(font_arial_health.render("SHOP", True, WHITE), (440, 25))
        
                # Buttons
                screen.blit(red_arrow_image, (230, 100))
                attack_button = pygame.Rect(225, 300, 200, 50)
                
                if attack_button.collidepoint(pos): # hover colors
                    attack_color = BTN_RED_HOVER
                else:
                    attack_color = BTN_RED
        
                pygame.draw.rect(screen, attack_color, attack_button)
                pygame.draw.rect(screen, BLACK, [225, 300, 200, 50], 4)
                screen.blit(font_bogle.render("Attack Range", True, WHITE), (265, 270))
        
                if not attack_max_level: # max display
                    screen.blit(font_arial_upgrade.render("UPGRADE", True, BLACK), (238, 305))
                else:
                    screen.blit(font_arial_upgrade.render("MAX", True, BLACK), (285, 305))
        
                cost_text = font_arial_health.render(str(attack_cost), True, PALE)
        
                if not attack_max_level: # cost display
                    screen.blit(cost_text, (325 - cost_text.get_width() / 2, 350))
        
                screen.blit(lazer_image, (560, 90))
                lazer_button = pygame.Rect(575, 300, 200, 50)
        
                if lazer_button.collidepoint(pos):
                    lazer_color = BTN_RED_HOVER
                else:
                    lazer_color = BTN_RED
        
                pygame.draw.rect(screen, lazer_color, lazer_button)
                pygame.draw.rect(screen, BLACK, [575, 300, 200, 50], 4)
                screen.blit(font_bogle.render("Shark Lazer", True, WHITE), (615, 270))
        
                if lazer_unlock: # unlock display
                    if not lazer_max_level:
                        screen.blit(font_arial_upgrade.render("UPGRADE", True, BLACK), (588, 305))
                    else: 
                        screen.blit(font_arial_upgrade.render("MAX", True, BLACK), (635, 305))
                else:
                    screen.blit(font_arial_upgrade.render("UNLOCK", True, BLACK), (600, 305))
        
                cost_text = font_arial_health.render(str(lazer_cost), True, PALE)
        
                if not lazer_max_level:
                    screen.blit(cost_text, (675 - cost_text.get_width() / 2, 350))
        
                screen.blit(green_arrow_image, (225, 425))
                stamina_button = pygame.Rect(575, 650, 200, 50)
        
                if stamina_button.collidepoint(pos):
                    stamina_color = BTN_RED_HOVER
                else:
                    stamina_color = BTN_RED
        
                pygame.draw.rect(screen, stamina_color, stamina_button)
                pygame.draw.rect(screen, BLACK, [575, 650, 200, 50], 4)
                screen.blit(font_bogle.render("Stamina Capacity", True, WHITE), (595, 620))
        
                if not stamina_max_level:
                    screen.blit(font_arial_upgrade.render("UPGRADE", True, BLACK), (588, 655))
                else:
                    screen.blit(font_arial_upgrade.render("MAX", True, BLACK), (635, 655))
        
                cost_text = font_arial_health.render(str(stamina_cost), True, PALE)
        
                if not stamina_max_level:
                    screen.blit(cost_text, (675 - cost_text.get_width() / 2, 700))
                screen.blit(orb_image, (570, 425))
        
                regen_button = pygame.Rect(225, 650, 200, 50)
        
                if regen_button.collidepoint(pos):
                    regen_color = BTN_RED_HOVER
                else:
                    regen_color = BTN_RED
        
                pygame.draw.rect(screen, regen_color, regen_button)
                pygame.draw.rect(screen, BLACK, [225, 650, 200, 50], 4)
                screen.blit(font_bogle.render("Stamina Regen", True, WHITE), (258, 620))
        
                if not regen_max_level:
                    screen.blit(font_arial_upgrade.render("UPGRADE", True, BLACK), (238, 655))
                else:
                    screen.blit(font_arial_upgrade.render("MAX", True, BLACK), (285, 655))
        
                cost_text = font_arial_health.render(str(regen_cost), True, PALE)
        
                if not regen_max_level:
                    screen.blit(cost_text, (325 - cost_text.get_width() / 2, 700))
                    
        
            if display_init: # initialize warning timer
                display_start = current_time
                display_init = False
        
            display_text(text, display_start, current_time, warning) # display warning
        else: # gameover
            up = False
            down = False
            right = False
            left = False            
            gameover_bg = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA) # make a surface size of the screen that supports alpha
            screen.fill(WHITE) # fill with white so that overlay doesn't fall ontop of another
            gameover_bg.fill((0, 0, 0, transparency)) # fill screen with black 
            screen.blit(gameover_bg, (0, 0)) # draw background
        
            if transparency < 255:
                transparency += 1 # increment 
            else:
                transparency = 255
                gameover_text = font_arial_gameover.render("Game Over", True, WHITE)
        
                screen.blit(gameover_text, (500 - gameover_text.get_width() / 2, 100)) # draw text
                
                try_again_button = pygame.Rect(375, 350, 250, 75)
                
                if try_again_button.collidepoint(pos): # hover colors
                    try_again_color = INK_GREY
                else:
                    try_again_color = BLACK
        
                pygame.draw.rect(screen, try_again_color, try_again_button)
                try_again_text = font_arial_health.render("Try Again?", True, WHITE) 
                screen.blit(try_again_text, (500 - try_again_text.get_width() / 2, 362.5)) # draw text
        
                menu_button = pygame.Rect(375, 475, 250, 75)
                
                if menu_button.collidepoint(pos): # hover colors
                    menu_color = INK_GREY
                else:
                    menu_color = BLACK
        
                pygame.draw.rect(screen, menu_color, menu_button)
                menu_text = font_arial_health.render("Main Menu", True, WHITE)
                screen.blit(menu_text, (500 - menu_text.get_width() / 2, 487.5))
    else: # if in menu 
        shop_text = font_arial.render("Shop", True, BLACK)
        market_x = 750
        market_y = 200
        
        screen.blit(background, [0, 0]) # draw lobby for background
        screen.blit(shopkeeper, [market_x + 50, market_y - 55])
        screen.blit(market_stall[8], [market_x, market_y - 20]) # counter
        screen.blit(market_stall[9], [market_x + 50, market_y - 20]) # counter
        screen.blit(market_stall[10], [market_x + 100, market_y - 20]) # counter
        screen.blit(market_stall[0], [market_x, market_y]) # base
        screen.blit(market_stall[1], [market_x + 50, market_y]) # base
        screen.blit(market_stall[2], [market_x + 100, market_y]) # base
        screen.blit(market_stall[3], [market_x + 5, market_y - 50]) # stick
        screen.blit(market_stall[4], [market_x + 95, market_y - 50]) # stick
        screen.blit(market_stall[5], [market_x, market_y - 95]) # top
        screen.blit(market_stall[6], [market_x + 50, market_y - 95]) # top
        screen.blit(market_stall[7], [market_x + 100, market_y - 95]) # top
        screen.blit(shop_text, (market_x + 46, market_y - 90))
        menu_bg = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        menu_bg.fill((0, 0, 0, 100)) # transparent black menu background
        screen.blit(menu_bg, (0, 0))        
        
        if not is_instruction:
            title_text = font_bogle_title.render("FISH RPG", True, WHITE)
            screen.blit(title_text, (500 - title_text.get_width() / 2, 50)) # title
            
            play_button_sprite = pygame.transform.scale(fish_sheet[2][0], (fish_sheet[2][0].get_width() * 2, fish_sheet[2][0].get_height() * 2)) # play button
            play_button_x = 500 - play_button_sprite.get_width() / 2
            play_button_y = 225
            play_button = pygame.Rect(play_button_x, play_button_y + 75, play_button_sprite.get_width(), play_button_sprite.get_height() - 180)
            
            if play_button.collidepoint(pos): # hover sprite
                play_button_sprite = pygame.transform.scale(fish_bite[2], (fish_bite[2].get_width() * 2, fish_bite[2].get_height() * 2))
                
            screen.blit(play_button_sprite, (play_button_x, play_button_y)) # draw
            screen.blit(font_bogle_buttons.render("Play", True, WHITE), (play_button_x + 140, play_button_y + 105))
            
            instruction_button_sprite = pygame.transform.scale(fish_sheet[2][0], (fish_sheet[2][0].get_width() * 2, fish_sheet[2][0].get_height() * 2)) # instruction button
            instruction_button_y = play_button_y + 150
            instruction_button = pygame.Rect(play_button_x, instruction_button_y + 75, instruction_button_sprite.get_width(), instruction_button_sprite.get_height() - 180)
            
            if instruction_button.collidepoint(pos):
                instruction_button_sprite = pygame.transform.scale(fish_bite[2], (fish_bite[2].get_width() * 2, fish_bite[2].get_height() * 2))
            
            screen.blit(instruction_button_sprite, (play_button_x, instruction_button_y))
            screen.blit(font_bogle_buttons.render("Guide", True, WHITE), (play_button_x + 130, instruction_button_y + 105))
            
            exit_button_sprite = pygame.transform.scale(fish_sheet[2][0], (fish_sheet[2][0].get_width() * 2, fish_sheet[2][0].get_height() * 2)) # exit button
            exit_button_y = instruction_button_y + 150
            exit_button = pygame.Rect(play_button_x, exit_button_y + 75, exit_button_sprite.get_width(), exit_button_sprite.get_height() - 180)
            
            if exit_button.collidepoint(pos):
                exit_button_sprite = pygame.transform.scale(fish_bite[2], (fish_bite[2].get_width() * 2, fish_bite[2].get_height() * 2))
            
            screen.blit(exit_button_sprite, (play_button_x, exit_button_y))
            screen.blit(font_bogle_buttons.render("Exit", True, WHITE), (play_button_x + 130, exit_button_y + 105))       
        else: # instruction menu
            screen.blit(font_bogle_boss.render("Movement", True, WHITE), (10, 10)) # text stuff
            screen.blit(font_bogle.render("\"w\" or up arrow key: up", True, WHITE), (10, 60))
            screen.blit(font_bogle.render("\"a\" or left arrow key: left", True, WHITE), (10, 85))
            screen.blit(font_bogle.render("\"s\" or down arrow key: down", True, WHITE), (10, 110))
            screen.blit(font_bogle.render("\"d\" or right arrow key: right", True, WHITE), (10, 135))
            screen.blit(font_bogle_boss.render("Actions", True, WHITE), (10, 160))
            screen.blit(font_bogle.render("Left shift: dash", True, WHITE), (10, 210))
            screen.blit(font_bogle.render("Left click: attack", True, WHITE), (10, 235))
            screen.blit(font_bogle.render("\"f\": switch modes (lazer unlocked)", True, WHITE), (10, 260))
            
            back_button = pygame.Rect(850, 0, 200, 50) # button to go back
            screen.blit(font_bogle_boss.render("Back", True, WHITE), (885, -5))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()