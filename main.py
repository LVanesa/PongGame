import sys,pygame,random
#STEPS:
        # 1. DEFINE RECTANGLES
        # 2. ADD INCREMENTAL CHANGES - used for animations
        # 3. DRAW RECTANGLES
        # Game Rectangles
        # Rect(x,y,width,height) -> these are empty rectangles
        # to actually visualize this rectangles we need to draw them -> pygame.draw(surface,color,rect)
class Button():
	def __init__(self, image, pos, text_input, font, base_color, hovering_color):
		self.image = image
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)
class Block(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos, obj_width, obj_height):
        super().__init__()
        self.image = pygame.Surface((obj_width, obj_height))  # Create a surface for the image
        self.image.fill(players_color)
        self.rect = pygame.Rect(x_pos,y_pos,obj_width,obj_height)       
class Player(Block):
    def __init__(self,x_pos,y_pos,obj_width,obj_height,speed):
        super().__init__(x_pos,y_pos,obj_width,obj_height)
        self.speed = speed
        self.movement = 0
        
    def screen_limits(self):
        if self.rect.top<=0:
            self.rect.top = 0
        if self.rect.bottom>=screen_height:
            self.rect.bottom = screen_height
            
    def update(self,ball_group): 
        # it was neccessary to add ball_group as a parameter because this function needs to match the update function from the Opponent Class
        # Player and Opponent are used as a group in this game (see run_game function from GameManager class)
        self.rect.y+=self.movement
        self.screen_limits()
class Ball(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos, radius, direction_x, direction_y, paddles):
        super().__init__()
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)  # Create a transparent surface
        self.image.fill((0, 0, 0, 0))  # Fill the surface with a transparent color
        pygame.draw.circle(self.image, players_color, (radius, radius), radius)  # Draw a circle on the surface
        self.rect = self.image.get_rect(center=(x_pos, y_pos))  # Set the position of the sprite
        self.direction_x = direction_x * random.choice((1, -1))
        self.direction_y = direction_y * random.choice((1, -1))
        self.paddles = paddles
        self.active = False
        self.score_time = 0
    
    def update(self):
        if self.active:
            self.rect.x += self.direction_x
            self.rect.y += self.direction_y
            self.collisions()
        else:
            self.restart_counter()
            
    def collisions(self):
        # if the ball hits the screen limits, make it change the direction
        if self.rect.top <= 0 or self.rect.bottom >= screen_height:
            self.direction_y *= -1

        # if the ball hits the paddles (i.e. player, opponent)
        if pygame.sprite.spritecollide(self,self.paddles,False):
            pygame.mixer.Sound.play(pong_sound)
            collision_paddle = pygame.sprite.spritecollide(self,self.paddles,False)[0].rect
            # this function checks for collision between a sprite (i.e. the ball) and a group of sprites (i.e the paddles)
            # it returns a list of sprites that collide with the 'self' sprite
            # False is used to indicate that the collided sprites should not be removed from the group
            # the index [0] takes the first (and presumamble the only) item of the returned list of collided sprites 
            # rect is used to acces the rect attribute of the collided sprite
            if abs(self.rect.right - collision_paddle.left) < 10 and self.direction_x > 0:
                # the ball hits the right paddle
                self.direction_x *= -1
            if abs(self.rect.left - collision_paddle.right) < 10 and self.direction_x < 0:
                # the ball hits the left paddle
                self.direction_x *= -1
            if abs(self.rect.top - collision_paddle.bottom) < 10 and self.direction_y < 0:
                # the ball hits the bottom of any the paddles
                self.rect.top = collision_paddle.bottom
                self.direction_y *= -1
            if abs(self.rect.bottom - collision_paddle.top) < 10 and self.direction_y > 0:
                # the ball hits the bottom of any the paddles
                self.rect.bottom = collision_paddle.top
                self.direction_y *= -1
    
    def reset_ball(self):
        self.active = False
        self.direction_x *= random.choice((1,-1))
        self.direction_y *= random.choice((1,-1))
        self.score_time = pygame.time.get_ticks()
        self.rect.center = (screen_width/2,screen_height/2)
        pygame.mixer.Sound.play(score_sound)
        
    def restart_counter(self):
        current_time = pygame.time.get_ticks()
        countdown_message = None 
        
        if current_time - self.score_time < 700:
            countdown_message = "READY.."
            
        if 700 < current_time - self.score_time < 1400:
            countdown_message = "SET.."

            
        if 1400 < current_time - self.score_time <= 2100:
            countdown_message = "  GO.."
            
        if current_time - self.score_time >= 2100:
            self.active = True
            
        time_counter = text_font.render(countdown_message,True,text_color)
        time_counter_rect=time_counter.get_rect(center = (screen_width/2,screen_height/2-250))
        pygame.draw.rect(screen,bg_color,time_counter_rect)
        screen.blit(time_counter,time_counter_rect)    
class Opponent(Block):
    def __init__(self, x_pos, y_pos,obj_width,obj_height,speed):
        super().__init__(x_pos, y_pos,obj_width,obj_height)
        self.speed = speed
    
    def update(self,ball_group):
        # the opponent moves parallel to the ball
        if self.rect.top < ball_group.sprite.rect.y:
            self.rect.y += self.speed
        if self.rect.bottom > ball_group.sprite.rect.y:
            self.rect.y -=self.speed
            
    def screen_limits(self):
        # if the opponent reaches the limits of the screen it should stop 
        # (the paddles should not exceed the limits of the screen/display)
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= screen_height:
            self.rect.bottom = screen_height       
class GameManager:
    def __init__(self,ball_group,paddle_group):
        self.player_score = 0
        self.opponent_score = 0
        self.ball_group = ball_group
        self.paddle_group = paddle_group
        
    def run_game(self):
        # DRAW THE OBJECTS OF THE GAME
        self.paddle_group.draw(screen)
        self.ball_group.draw(screen)
    
        # UPDATE THE OBJECTS OF THE GAME 
        self.paddle_group.update(self.ball_group)
        self.ball_group.update()
        self.reset_ball()
        self.draw_score()
    
    def reset_ball(self):
        if self.ball_group.sprite.rect.right >= screen_width:
            self.opponent_score += 1
            self.ball_group.sprite.reset_ball()
        if self.ball_group.sprite.rect.left <= 0:
            self.player_score += 1
            self.ball_group.sprite.reset_ball()
            
    def draw_score(self):
        player_score = score_font.render(str(self.player_score),True,text_color)
        opponent_score = score_font.render(str(self.opponent_score),True,text_color)
        
        player_score_rect = player_score.get_rect(midleft = (screen_width / 2 + 40, screen_height/2))
        opponent_score_rect = opponent_score.get_rect(midright = (screen_width / 2 - 40, screen_height/2))
        
        screen.blit(player_score,player_score_rect)
        screen.blit(opponent_score,opponent_score_rect)

def main_menu():
    global play_mode
    menu_bg_color = pygame.Color("#432818")
    menu_title_font = pygame.font.SysFont("PokemonGb",80)
    menu_text_font = pygame.font.SysFont("PokemonGb",50)
    while True:
        screen.fill(menu_bg_color)
        menu_mouse_position=pygame.mouse.get_pos()
        menu_text = menu_title_font.render("MAIN MENU", True,"#bb9457")
        menu_rect = menu_text.get_rect(center=(640,200))
        
        player1_button = Button(None, pos=(640, 400), 
                            text_input="1 PLAYER", font=menu_text_font, base_color="#ffe6a7", hovering_color="White")
        player2_button = Button(None, pos=(640, 500), 
                            text_input="2 PLAYERS", font=menu_text_font, base_color="#ffe6a7", hovering_color="White")
        quit_button = Button(None, pos=(640, 600), 
                            text_input="QUIT", font=menu_text_font, base_color="#ffe6a7", hovering_color="White")

        screen.blit(menu_text,menu_rect)
        
        for button in [player1_button, player2_button, quit_button]:
            button.changeColor(menu_mouse_position)
            button.update(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if player1_button.checkForInput(menu_mouse_position):
                    play_mode = 1
                    return
                if player2_button.checkForInput(menu_mouse_position):
                    play_mode = 2
                    return
                if quit_button.checkForInput(menu_mouse_position):
                    pygame.quit()
                    sys.exit()
                    
        pygame.display.update()

# GENERAL SETUP
pygame.mixer.pre_init(44100,-16,2,512)
pygame.init()
clock=pygame.time.Clock()

# MAIN WINDOW SETUP
screen_width = 1280
screen_height =  960
screen = pygame.display.set_mode((screen_width,screen_height)) #create a display surface
pygame.display.set_caption('Menu')
play_mode = None
main_menu()

middle_strip = pygame.Rect(screen_width / 2 - 2, 0, 4, screen_height) #draw the line that separates the players

# GLOBAL VARIABLES
# 1. COLORS
bg_color=pygame.Color("#432818")
players_color=pygame.Color("#BB9457")
strip_color=pygame.Color("#99582A")
text_color = pygame.Color("#FFE6A7")


# 3. FONTS
score_font = pygame.font.SysFont("lucidasanstypewriterregular",50)
text_font = pygame.font.SysFont("lucidasanstypewriterregular",100)

# 4. SOUNDS
pong_sound = pygame.mixer.Sound("pong.ogg")
score_sound = pygame.mixer.Sound("score.ogg")

# GAME OBJECTS
if play_mode==1:
    player = Player(screen_width - 20, screen_height / 2 - 70, 10, 140, 7)
    opponent = Opponent(10, screen_height / 2 - 70, 10, 140, 5)
    paddle_group = pygame.sprite.Group()
    paddle_group.add(player)
    paddle_group.add(opponent)

    ball = Ball(screen_width/2, screen_height/2, 20, 5, 5, paddle_group)

    ball_sprite = pygame.sprite.GroupSingle()
    ball_sprite.add(ball)

    game_manager = GameManager(ball_sprite,paddle_group)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                #this event is triggerred when a key on the keyboard is pressed down
                if event.key == pygame.K_DOWN:
                    player.movement+=player.speed
                if event.key == pygame.K_UP:
                    player.movement-=player.speed
                
            if event.type == pygame.KEYUP:
                #this event is triggered when a key on the keyboard is released
                if event.key == pygame.K_DOWN:
                    player.movement-=player.speed
                if event.key == pygame.K_UP:
                    player.movement+=player.speed
        # VISUALS
        screen.fill(bg_color)
        pygame.draw.rect(screen,strip_color,middle_strip)
        
        # START GAME
        game_manager.run_game()

        # RENDERING
        pygame.display.flip()
        clock.tick(60)  # limits how fast a loop runs, 60 frames per second in this case
                        # we need to control the speed because python tends to run code as fast as possible

else:
    player1 = Player(screen_width - 20, screen_height / 2 - 70, 10, 140, 7)
    player2 = Player(10, screen_height / 2 - 70, 10, 140, 7)
    paddle_group = pygame.sprite.Group()
    paddle_group.add(player1)
    paddle_group.add(player2)

    ball = Ball(screen_width/2, screen_height/2, 20, 5, 5, paddle_group)

    ball_sprite = pygame.sprite.GroupSingle()
    ball_sprite.add(ball)

    game_manager = GameManager(ball_sprite,paddle_group)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                #this event is triggerred when a key on the keyboard is pressed down
                if event.key == pygame.K_DOWN:
                    player1.movement+=player1.speed
                if event.key == pygame.K_UP:
                    player1.movement-=player1.speed
                if event.key == pygame.K_s:  # "S" key for Player 2
                    player2.movement += player2.speed
                if event.key == pygame.K_w:  # "W" key for Player 2
                    player2.movement -= player2.speed
            if event.type == pygame.KEYUP:
                #this event is triggered when a key on the keyboard is released
                if event.key == pygame.K_DOWN:
                    player1.movement-=player1.speed
                if event.key == pygame.K_UP:
                    player1.movement+=player1.speed
                if event.key == pygame.K_s:  # "S" key for Player 2
                    player2.movement -= player2.speed
                if event.key == pygame.K_w:  # "W" key for Player 2
                    player2.movement += player2.speed
        # VISUALS
        screen.fill(bg_color)
        pygame.draw.rect(screen,strip_color,middle_strip)
        
        # START GAME
        game_manager.run_game()

        # RENDERING
        pygame.display.flip()
        clock.tick(60)  # limits how fast a loop runs, 60 frames per second in this case
                        # we need to control the speed because python tends to run code as fast as possible
    
            

    
