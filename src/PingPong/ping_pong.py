import pygame
import sys
import random
import serial
from helper.reader import ReadLine
from button import Button
import threading

sensorData = serial.Serial('/dev/tty.usbmodem0010502839531', 115200,
                           parity=serial.PARITY_NONE,
                           stopbits=serial.STOPBITS_ONE,
                           bytesize=serial.EIGHTBITS,
                           timeout=100)

controller = ReadLine(sensorData)
pygame.init()
clock = pygame.time.Clock()
UPDATESPEEDEVENT = pygame.USEREVENT+1
pygame.time.set_timer(UPDATESPEEDEVENT, 60)

screen_width = 1280
screen_height = 560
SCREEN = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Menu")

BG = pygame.image.load("./Background_image.png")

def get_font(size):
    return pygame.font.Font("./font.ttf", size)

speed_lock = threading.Lock()
speed_value = 0

def read_speed():
    global speed_value
    while True:
        data = controller.readline()
        if len(data) > 2:
            parsedPacket = str(data, 'utf-8')
            speed = (7 * int(parsedPacket.split(",")[0])) / 1000
            with speed_lock:
                speed_value = speed

def calculate_speed():
    with speed_lock:
        return speed_value

def play():
    pygame.display.set_caption("Play")

    ball = pygame.Rect(screen_width/2 - 15, screen_height/2 - 15, 30, 30)
    player = pygame.Rect(screen_width - 20, screen_height/2 - 70, 10, 140)
    opponent = pygame.Rect(10, screen_height/2 - 70, 10, 140)
    score_font = pygame.font.Font(None, 48)

    bg_color = pygame.Color('grey12')
    player_color = (0, 0, 200)
    opponent_color = (200, 0, 0)
    WHITE = (255, 255, 255)
    black = (0, 0, 0)
    middle_line_color = (200, 200, 200)
    ball_color = (0, 200, 0)

    ball_speed_unit_x = 7 * random.choice((1, -1))
    ball_speed_unit_y = 7 * random.choice((1, -1))
    player_speed = 0
    opponent_speed = 7
    score1 = 0
    score2 = 0

    bonus = pygame.mixer.Sound("./bonus.mp3")
    Schlag = pygame.mixer.Sound("./Schlag.mp3")
    background_sound = pygame.mixer.Sound("./BrinstairRed.mp3")
    background_sound.play(loops=-1)
    SCREEN.fill("black")

    # Start the speed reading thread
    speed_thread = threading.Thread(target=read_speed)
    speed_thread.daemon = True
    speed_thread.start()

    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    background_sound.stop()
                    return  # Retour au menu
                if event.key == pygame.K_KP8 or event.key == pygame.K_DOWN:
                    player_speed = 7
                elif event.key == pygame.K_KP2 or event.key == pygame.K_UP:
                    player_speed = -7
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_KP8 or event.key == pygame.K_DOWN or event.key == pygame.K_KP2 or event.key == pygame.K_UP:
                    player_speed = 0
            if event.type == UPDATESPEEDEVENT:
                player_speed = calculate_speed()

        player.y += player_speed
        if player.top <= 0:
            player.top = 0
        if player.bottom >= screen_height:
            player.bottom = screen_height

        ball.x += ball_speed_unit_x
        ball.y += ball_speed_unit_y

        if ball.top <= 0 or ball.bottom >= screen_height:
            ball_speed_unit_y *= -1

        if ball.colliderect(player) or ball.colliderect(opponent):
            ball_speed_unit_x *= -1
            Schlag.play()

        if ball.left < 0:
            ball.center = (screen_width/2, screen_height/2)
            ball_speed_unit_y *= random.choice((1, -1))
            ball_speed_unit_x *= random.choice((1, -1))
            score1 += 1
            bonus.play()

        if ball.right >= screen_width:
            ball.center = (screen_width/2, screen_height/2)
            ball_speed_unit_y *= random.choice((1, -1))
            ball_speed_unit_x *= random.choice((1, -1))
            score2 += 1
            bonus.play()

        if opponent.top < ball.y:
            opponent.top += opponent_speed
        if opponent.bottom > ball.y:
            opponent.top -= opponent_speed
        if opponent.top <= 0:
            opponent.top = 0
        if opponent.bottom >= screen_height:
            opponent.bottom = screen_height

        SCREEN.fill(ball_color)
        pygame.draw.rect(SCREEN, player_color, player)
        pygame.draw.rect(SCREEN, opponent_color, opponent)
        pygame.draw.aaline(SCREEN, middle_line_color, (screen_width/2, 0), (screen_width/2, screen_height))
        pygame.draw.ellipse(SCREEN, bg_color, ball)

        score_text1 = score_font.render(f"Score: {score1}", True, WHITE)
        score_text2 = score_font.render(f"Score: {score2}", True, WHITE)
        SCREEN.blit(score_text1, (screen_width - 180, 10))
        SCREEN.blit(score_text2, (20, 10))

        pygame.display.update()
        clock.tick(60)


def options():
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")

        OPTIONS_TEXT = get_font(40).render("This is the OPTIONS screen.", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(screen_width / 2, screen_height / 4))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(screen_width / 2, screen_height / (15/12)),
                              text_input="BACK", font=get_font(60), base_color="Black",
                              hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        TWO_PLAYER_BUTTON = Button(image=None, pos=(screen_width / 2, screen_height / 2),
                                   text_input="2 Players", font=get_font(60), base_color="Black",
                                   hovering_color="Green")

        TWO_PLAYER_BUTTON.changeColor(OPTIONS_MOUSE_POS)
        TWO_PLAYER_BUTTON.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    return  # Retour au menu
                elif TWO_PLAYER_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    play_2_player()

        pygame.display.update()


def play_2_player():
    pygame.display.set_caption("Play - 2 Player")

    ball = pygame.Rect(screen_width / 2 - 15, screen_height / 2 - 15, 30, 30)
    player1 = pygame.Rect(screen_width - 20, screen_height / 2 - 70, 10, 140)
    player2 = pygame.Rect(10, screen_height / 2 - 70, 10, 140)
    score_font = pygame.font.Font(None, 36)

    bg_color = pygame.Color('grey12')
    player1_color = (0, 0, 200)
    player2_color = (200, 0, 0)
    WHITE = (255, 255, 255)
    black = (0, 0, 0)
    middle_line_color = (200, 200, 200)
    ball_color = (0, 200, 0)

    ball_speed_unit_x = 7 * random.choice((1, -1))
    ball_speed_unit_y = 7 * random.choice((1, -1))
    player1_speed = 0
    player2_speed = 0
    score1 = 0
    score2 = 0

    bonus = pygame.mixer.Sound("./bonus.mp3")
    Schlag = pygame.mixer.Sound("./Schlag.mp3")
    background_sound = pygame.mixer.Sound("./BrinstairRed.mp3")
    background_sound.play(loops=-1)

    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("black")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    background_sound.stop()
                    return  # Retour au menu

                if event.key == pygame.K_c:
                    player1_speed = 7
                elif event.key == pygame.K_r:
                    player1_speed = -7
                elif event.key == pygame.K_UP:
                    player2_speed = -7
                elif event.key == pygame.K_DOWN:
                    player2_speed = 7
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_c or event.key == pygame.K_r:
                    player1_speed = 0
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    player2_speed = 0

        player1.y += player1_speed
        if player1.top <= 0:
            player1.top = 0
        if player1.bottom >= screen_height:
            player1.bottom = screen_height

        player2.y += player2_speed
        if player2.top <= 0:
            player2.top = 0
        if player2.bottom >= screen_height:
            player2.bottom = screen_height

        ball.x += ball_speed_unit_x
        ball.y += ball_speed_unit_y

        if ball.top <= 0 or ball.bottom >= screen_height:
            ball_speed_unit_y *= -1

        if ball.colliderect(player1) or ball.colliderect(player2):
            ball_speed_unit_x *= -1
            Schlag.play()

        if ball.left < 0:
            ball.center = (screen_width / 2, screen_height / 2)
            ball_speed_unit_y *= random.choice((1, -1))
            ball_speed_unit_x *= random.choice((1, -1))
            score1 += 1
            bonus.play()

        if ball.right >= screen_width:
            ball.center = (screen_width / 2, screen_height / 2)
            ball_speed_unit_y *= random.choice((1, -1))
            ball_speed_unit_x *= random.choice((1, -1))
            score2 += 1
            bonus.play()

        SCREEN.fill(ball_color)
        pygame.draw.rect(SCREEN, player1_color, player1)
        pygame.draw.rect(SCREEN, player2_color, player2)
        pygame.draw.aaline(SCREEN, middle_line_color, (screen_width / 2, 0), (screen_width / 2, screen_height))
        pygame.draw.ellipse(SCREEN, bg_color, ball)

        score_font = pygame.font.Font(None, 48)


        score1_text = score_font.render("B_score: " + str(score1), True, WHITE)
        score2_text = score_font.render("R_score: " + str(score2), True, WHITE)
        SCREEN.blit(score1_text, (screen_width - 200, 10))
        SCREEN.blit(score2_text, (20, 10))

        pygame.display.update()
        clock.tick(60)



def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(50).render("PONG GAME: MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(screen_width / 2, screen_height / 4))

        PLAY_BUTTON = Button(image=pygame.image.load("./Play_Rect.png"), pos=(screen_width / 2, screen_height / (15/7) ),
                             text_input="PLAY", font=get_font(60), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("./Options_Rect.png"), pos=(screen_width / 2, screen_height / (15/10)),
                                text_input="OPTIONS", font=get_font(60), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("./Quit_Rect.png"), pos=(screen_width / 2, screen_height / (15/13)),
                             text_input="QUIT", font=get_font(60), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                elif OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                elif QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()