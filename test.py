

import pygame

pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

player_rect = pygame.Rect(50, 50, 40, 40) 

line_start = (0, 300)
line_end = (800, 300)
test_line = (line_start, line_end)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_rect.y -= 5
    if keys[pygame.K_DOWN]:
        player_rect.y += 5
    if keys[pygame.K_LEFT]:
        player_rect.x -= 5
    if keys[pygame.K_RIGHT]:
        player_rect.x += 5

    clipped_segment = player_rect.clipline(test_line)

    if clipped_segment:
        print("Collision with the line!")
        player_color = (255, 0, 0) 
    else:
        player_color = (0, 128, 255) 

    screen.fill((255, 255, 255)) 
    pygame.draw.line(screen, (0, 0, 0), line_start, line_end, 1) 
    pygame.draw.rect(screen, player_color, player_rect) 

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()