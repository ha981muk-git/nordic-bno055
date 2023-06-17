import pygame

# Initialisierung von Pygame
pygame.init()

# Fenstergröße
WIDTH = 800
HEIGHT = 400

# Farben
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Erstellen des Spielfensters
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping-Pong mit Soundeffekten")

# Laden der Soundeffekte
paddle_sound = pygame.mixer.Sound("paddle_sound.wav")
score_sound = pygame.mixer.Sound("score_sound.wav")

# Schläger
paddle_width = 15
paddle_height = 60
paddle_speed = 5

left_paddle = pygame.Rect(50, HEIGHT / 2 - paddle_height / 2, paddle_width, paddle_height)
right_paddle = pygame.Rect(WIDTH - 50 - paddle_width, HEIGHT / 2 - paddle_height / 2, paddle_width, paddle_height)

# Ball
ball_radius = 10
ball_speed_x = 3
ball_speed_y = 3

ball = pygame.Rect(WIDTH / 2 - ball_radius, HEIGHT / 2 - ball_radius, ball_radius * 2, ball_radius * 2)

# Spiel-Loop
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Bewegung der Schläger
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and left_paddle.y > 0:
        left_paddle.y -= paddle_speed
    if keys[pygame.K_s] and left_paddle.y < HEIGHT - paddle_height:
        left_paddle.y += paddle_speed
    if keys[pygame.K_UP] and right_paddle.y > 0:
        right_paddle.y -= paddle_speed
    if keys[pygame.K_DOWN] and right_paddle.y < HEIGHT - paddle_height:
        right_paddle.y += paddle_speed
    
    # Bewegung des Balls
    ball.x += ball_speed_x
    ball.y += ball_speed_y
    
    # Kollision mit Schlägern
    if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
        ball_speed_x *= -1
        paddle_sound.play()  # Soundeffekt für Schlägerkollision abspielen
    
    # Kollision mit den Wänden
    if ball.y <= 0 or ball.y >= HEIGHT - ball_radius * 2:
        ball_speed_y *= -1
    
    # Punktezählung
    if ball.x <= 0:
        score_sound.play()  # Soundeffekt für Punktgewinn abspielen
        ball_speed_x = 3
        ball_speed_y = 3
        ball.x = WIDTH / 2 - ball_radius
        ball.y = HEIGHT / 2 - ball_radius
    if ball.x >= WIDTH - ball_radius * 2:
        score_sound.play()  # Soundeffekt für Punktgewinn abspielen
        ball_speed_x = -3
        ball_speed_y = -3
        ball.x = WIDTH / 2 - ball_radius
        ball.y = HEIGHT / 2 - ball_radius
    
    # Hintergrund zeichnen
    screen.fill(BLACK)
    
    # Schläger zeichnen
    pygame.draw.rect(screen, WHITE, left_paddle)
    pygame.draw.rect(screen, WHITE, right_paddle)
    
    # Ball zeichnen
    pygame.draw.ellipse(screen, WHITE, ball)
    
    # Spielfenster aktualisieren
    pygame.display.flip()

# Pygame beenden
pygame.quit()
