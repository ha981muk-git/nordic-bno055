import pygame, sys, random                # sys to access some more funtionalities 

     

def ball_animation(): 
    global ball_speed_unit_x, ball_speed_unit_y, score1, score2
    #Geschwindigkeit des Balles
    ball.x += ball_speed_unit_x 
    ball.y += ball_speed_unit_y   

    #making the ball bounce around the four sides of the screen
    if ball.top <= 0 or ball.bottom >= screen_height: #if the top of the ball is less or equal zero and if the bottom of the ball is greater or equal the height of the screen then     
        ball_speed_unit_y *= -1   
    # if ball.left <= 0 or ball.right >= screen_width:
    #     ball_restart()
    #     score_update()

    #making the ball collide with the two-player rectangles
    if ball.colliderect(player) or ball.colliderect(opponent):
        ball_speed_unit_x *= -1

    if ball.left < 0:
        ball_restart()
        score2 += 1
        bonus.play()
    
    if ball.right >= screen_width:
        ball_restart()
        score1 += 1    

def player_animation():
    player.y += player_speed
    if player.top <= 0:
         player.top = 0
    if player.bottom >= screen_height: 
         player.bottom = screen_height    

def opponent_animation():
    if opponent.top < ball.y:
         opponent.top += opponent_speed
    if opponent.bottom > ball.y:
         opponent.top -= opponent_speed
    if opponent.top <= 0:
         opponent.top = 0
    if opponent.bottom >= screen_height:
         opponent.bottom = screen_height

def ball_restart():
    global ball_speed_unit_x, ball_speed_unit_y
    ball.center = (screen_width/2, screen_height/2) #send the ball to the center
    ball_speed_unit_y *= random.choice((1,-1))
    ball_speed_unit_x *= random.choice((1,-1))        

def score_update():
    global score1, score2
    # implementing score
    # Render the updated scores as text on the screen
    score1_t = score_font.render(f'{score1}', 1, WHITE)
    score2_t = score_font.render(f'{score2}', 1, WHITE)
    #score_text = score_font.render(str(score1) + " : " + str(score2), True, WHITE)
    screen.blit(score1_t, (screen_width // 4 - score1_t.get_width() // 2, 20))
    screen.blit(score2_t, (screen_width * (3/4) - score2_t.get_width() // 2, 20))


pygame.init()                       #initialise all the pygame module and is required before we can run any kind of game
clock = pygame.time.Clock()      #the clock function is store in the variable clock 


#we create the window for the game
screen_width = 1280
screen_height = 560 
screen = pygame.display.set_mode((screen_width, screen_height)) # it return a display surface object which is stored in the variable screen
pygame.display.set_caption('Pong') #give a title to the created window

#declaration of rectangle that will content the ball, the player and the opponent
ball = pygame.Rect(screen_width/2 - 15, screen_height/2 - 15, 30,30)
player = pygame.Rect(screen_width - 20, screen_height/2 - 70, 10, 140)
opponent = pygame.Rect(10, screen_height/2 - 70, 10, 140)
score_font = pygame.font.Font(None, 36)

#sound effect
bonus = pygame.mixer.Sound("bonus.mp3")
background_sound = pygame.mixer.Sound("BrinstairRed.mp3")

#dislikelike_sfx.play()

#declaration of color that will be use for the ball, player and opponent
bg_color = pygame.Color('grey12') 
player_color = (0, 0, 200)      # (red, green, blue) from 0 to 255. Pure black is(0,0,0). Pure white is(255,255,255). red is(255,0,0)
opponent_color = (200, 0, 0)
WHITE = (255,255,255)
middle_line_color = (200,200,200)
ball_color = (0,200,0)

#Ballbewegungseinheit bei jedem Durchlauf der Schleife
ball_speed_unit_x = 7 * random.choice((1,-1))
ball_speed_unit_y = 7 * random.choice((1,-1))
player_speed = 0
opponent_speed = 7
score1 = 0
score2 = 0




#check if the user has pressed the close button at the top of the window
while True: 
    #Handling input
    for event in pygame.event.get():  #we get the list of all user input
        if event.type == pygame.QUIT: #if the input of the user is equal pygame.QUIT(close button)
            pygame.quit()               #then call the function to initialise the pygame module
            sys.exit()                  # and close the window game

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_KP8 or event.key == pygame.K_DOWN:
                    player_speed += 7
            if event.key == pygame.K_KP8 or event.key == pygame.K_UP:
                    player_speed -= 7 
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_KP8 or event.key == pygame.K_DOWN:
                    player_speed -= 7
            if event.key == pygame.K_KP8 or event.key == pygame.K_UP:
                    player_speed += 7 
                   
    background_sound.play()   
    ball_animation()
    player_animation()
    opponent_animation() 
    
                                  

    #use the variable for surface(screen), color(bg_color and light_grey), and rectangle(ball, player and opponent) to draw the each object(ball, player and opponent)
    screen.fill(ball_color)
    pygame.draw.rect(screen, player_color, player)
    pygame.draw.rect(screen, opponent_color, opponent)
    pygame.draw.aaline(screen, middle_line_color, (screen_width/2,0), (screen_width/2, screen_height))
    pygame.draw.ellipse(screen, bg_color, ball)

    score_update()
   

    #updating the window
    pygame.display.flip()       #take everything that came before it in the loop and draw a picture from that
    clock.tick(60)              #it limit how fast the loop runs in this case 60times per second. If we don't define this line, every thingh in the loop will apend so fast at the processor time process speed and we will not be able to see anything apenning in the loop