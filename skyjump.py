import simplegui
from user305_o32FtUyCKk_0 import Vector
import random
import math
import time


# global variables
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
NUM_PLAT = 300
PLATFORM_SPACING = 100
SCORE = 0
LIVES = 5
PREV_SCORE = 0
SCORE_COLOR = "Green"
FINISHED = False

# load sounds
BOUNCE_SOUND = simplegui.load_sound("https://rpg.hamsterrepublic.com/wiki-images/7/73/Powerup.ogg")
DEATH_SOUND = simplegui.load_sound("http://rpg.hamsterrepublic.com/wiki-images/0/0b/BossDeath.ogg")
MENU_SOUND = simplegui.load_sound("http://rpg.hamsterrepublic.com/wiki-images/8/8e/Confirm8-Bit.ogg")
POWERUP_SOUND = simplegui.load_sound("http://rpg.hamsterrepublic.com/wiki-images/3/3e/Heal8-Bit.ogg")
WIN_SOUND = simplegui.load_sound("http://rpg.hamsterrepublic.com/wiki-images/d/d5/Menu8-Bit.ogg")

# classes
class Player:
    #Class for player
    def __init__(self, pos):
        #Initialise player
        self.pos = pos
        self.vel = Vector()
        self.powerNum = (random.randint(2000,5000))//100*100
        self.jump = 7
    
              
    def update(self, state):
        global SCORE, LIVES, PREV_SCORE, SCORE_COLOR, FINISHED
        #Updating player
        self.pos.x = (self.pos.x + self.vel.x) % CANVAS_WIDTH
        platform_index = int(min(self.pos.y // PLATFORM_SPACING, NUM_PLAT - 1))

        #Bounce if you collide with platform
        if self.pos.y>NUM_PLAT * PLATFORM_SPACING:#If player is at the final platform
            self.platform1 = state.finish_plat#platform1 is final platform
        else:
            self.platform1 = state.platform_list[platform_index]#platform1 is general platform
        
            
        if self.collide(self.platform1):
            if FINISHED == True:
                state.start_game()
            BOUNCE_SOUND.play()
            self.vel.y = self.jump
            SCORE_COLOR = "Green"
            self.jump=7
            
            if random.random()> 0.7: 	
                state.platform_list[platform_index].remove()
        else:
            self.pos.add(Vector(0, self.vel.y))
            if SCORE % self.powerNum == 0 and SCORE != 0 and platform_index <= NUM_PLAT-10 and self.vel.y>0:
                self.jump=14
                SCORE_COLOR = "Gold"
                self.powerNum = (random.randint(3000,9000))//100*100
                POWERUP_SOUND.play()
            
        #Gravity
        self.vel.add(Vector(0, -0.1))
        
        #If player gets in top half of the screen, update cam.y to move camera up
        if self.pos.y - state.cam.y > CANVAS_HEIGHT/2:
            state.cam.y = self.pos.y - CANVAS_HEIGHT/2
        
        #Restart if falls below screen
        if self.pos.y - state.cam.y < -50:
            state.start_game()
            LIVES -= 1
            PREV_SCORE = SCORE
        
            
    def collide(self, platform):
        global FINISHED
        #Check if player collides with a platform
        if platform.height != NUM_PLAT * PLATFORM_SPACING + PLATFORM_SPACING:
            if (self.pos.y-12 > platform.height > self.pos.y-12 + self.vel.y) and platform.exists:
                return platform.left-8 < self.pos.x < platform.right+8
            else:
                return False
        else:
            if (self.pos.y > platform.height-50 > self.pos.y + self.vel.y) and platform.exists:
                FINISHED = True
                return (CANVAS_WIDTH/2)-200 < self.pos.x < (CANVAS_WIDTH/2)+200
            else:
                return False
                
                            
    def draw_player(self, canvas, state, image):
        #Draw player
        canvas.draw_image(image,[32 // 2, 
                    32 // 2], [32, 32], 
                    [self.pos.x - state.cam.x, 
                            CANVAS_HEIGHT - (self.pos.y - state.cam.y)], [45, 45])
        
class Platform:
    #Class for platform
    def __init__(self, height):
        #Create a platform with left and right boundaries and existence flag (for when platforms disappear)
        self.width = random.randrange(90, 170)
        self.height = height
        self.left = random.randrange(25, CANVAS_WIDTH -(25 + self.width))
        self.right = self.left + self.width
        self.exists = True

    def remove(self):
        #Make a platform disappear
        self.exists = False
        
    def restore(self):
        #Restore a platform
        self.exists = True
        
    def draw_platform(self, canvas, state):
        #Draw a platform
        height_to_draw = CANVAS_HEIGHT -(self.height- state.cam.y)
        self.img = simplegui.load_image('https://www.cs.rhul.ac.uk/home/zlac319/finish.png')
        if self.exists:
            if self.height == NUM_PLAT * PLATFORM_SPACING + PLATFORM_SPACING: #If it isn't the final platform
                canvas.draw_image(self.img, (64/2, 64/2),
                                    (64, 64), 
                                    (CANVAS_WIDTH/2, height_to_draw), 
                                    (300,300))
            else:
                canvas.draw_line([self.left - state.cam.x, height_to_draw],
                             [self.right - state.cam.x,height_to_draw], 4, "RGB(139,69,0)")



class Ball:
    #Class for snowballs
    def __init__(self):
        #Create a snow ball which starts in centre and is at a random velocity
        self.pos = Vector(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2)
        self.radius = 20
        self.color = "White"
        self.velocity = Vector(random.randint(-8,8), random.randint(-8,8))

    def draw(self, canvas):
        #Draw a snowball
        canvas.draw_circle(self.pos.get_p(), self.radius, 1, self.color, self.color)

    def update(self):
        # Update the ball's position based on its velocity
        self.pos.x += self.velocity.x
        self.pos.y += self.velocity.y

        # Bounce off the left or right wall at a random velocity
        if self.pos.x <= self.radius or self.pos.x >= CANVAS_WIDTH - self.radius:
            self.velocity = Vector(-self.velocity.x, random.randint(0,8))

        # Bounce off the top or bottom wall at a random velocity
        if self.pos.y <= self.radius or self.pos.y >= CANVAS_HEIGHT - self.radius:
            self.velocity = Vector(random.randint(0,8), -self.velocity.y)
        
class Game:
    #Class for interactions
    def __init__(self):
        #Create a game
        self.frame = simplegui.create_frame("Sky Jump", CANVAS_WIDTH, CANVAS_HEIGHT)
        self.frame.start()
        self.frame.set_draw_handler(self.draw_intro)#Draw intro screen
        self.frame.set_keydown_handler(self.key_handler)#Intro screen keys
        self.intro = simplegui.load_image('https://cs.rhul.ac.uk/home/zlac319/start_screen1.png')
        self.width = 4800
        self.height = 4800
        self.columns = 6
        self.rows = 8
        self.finished = False
        
        self.frame_width = self.width / self.columns
        self.frame_height = self.height / self.rows
        self.frame_centre_x = self.frame_width / 2
        self.frame_centre_y = self.frame_height / 2

        self.frame_index = [0, 0]
        self.frame_clock = 0
        
    #For different frames of spritesheet for animated intro screen    
    def update_index(self):
        self.frame_index[0] = (self.frame_index[0] + 1) % self.columns
        if self.frame_index[0] == 0:
            self.frame_index[1] = (self.frame_index[1] + 1) % self.rows
    
    #Switch between frames of intro screen
    def draw_intro(self, canvas):
        Clock().tick()
        if Clock().transition(0.2):
            self.update_index()
    
        source_centre = (
            self.frame_width * self.frame_index[0] + self.frame_centre_x,
            self.frame_height * self.frame_index[1] + self.frame_centre_y
        )
        
        source_size = (self.frame_width, self.frame_height)
        dest_centre = [CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2]
        dest_size = [CANVAS_WIDTH, CANVAS_HEIGHT]
    
        canvas.draw_image(self.intro,
                            source_centre,
                            source_size,
                            dest_centre,
                            dest_size)
        
    def key_handler(self, key):
        self.key = key
        if key == simplegui.KEY_MAP['space']:
            MENU_SOUND.play()
            if self.finished == True:#If this is after an attempt
                self.stop()#Stop the game
                
            else:
                self.add_elements()#Else start a new game
    
    #Add all the game elements
    def add_elements(self):
        self.frame.set_keydown_handler(self.keydown)
        self.frame.set_keyup_handler(self.keyup)
        self.frame.set_draw_handler(self.draw)
        self.cam = Vector(0,0)
        self.platform_list = [Platform(x * PLATFORM_SPACING) for x in range(0, NUM_PLAT)]
        self.finish_plat = Platform(PLATFORM_SPACING * (NUM_PLAT +1))
        self.my_player = Player(Vector((self.platform_list[0].left + self.platform_list[0].right)/2 , 90))
        self.balls = [Ball() for z in range(0,4)]#4 Snow balls available
        self.penguin = simplegui.load_image('https://www.cs.rhul.ac.uk/home/zlac319/Penguin1.png')
        

    def start_game(self):
        #Start a game
        global FINISHED
        
        if LIVES <=1 or FINISHED == True:#If the player has run out of lives or has won the game
            self.finished = True
            if LIVES<=1:
                self.frame.set_draw_handler(self.over_finish)#Display game 
                DEATH_SOUND.play()
            else:
                self.frame.set_draw_handler(self.winner_finish)
                WIN_SOUND.play()
        self.cam = Vector(0,0)
        self.platform_list = [Platform(x * PLATFORM_SPACING) for x in range(0, NUM_PLAT)]
        self.my_player = Player(Vector((self.platform_list[0].left + self.platform_list[0].right)/2 , 90))
        self.balls = [Ball() for z in range(0,4)]#4 Snow balls available
        self.frame.set_keyup_handler(self.keyup_start)
        self.penguin = simplegui.load_image('https://www.cs.rhul.ac.uk/home/zlac319/Penguin1.png')
    
    #Game over screen
    def over_finish(self, canvas):
        self.image = simplegui.load_image('https://www.cs.rhul.ac.uk/home/zlac319/Cloud_Pixel_art.png')
        canvas.draw_image(self.image,[1760 // 2, 
                    1140 // 2], [1760, 1140], 
                    [CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2], [CANVAS_WIDTH, CANVAS_HEIGHT])
        canvas.draw_text("GAME OVER", [150, 100], 100, "Red", "monospace")
        canvas.draw_text("Score:"+(str)(SCORE), [250, (CANVAS_HEIGHT/2)-30], 50, "Purple", "monospace")
        canvas.draw_text("Lives remaining:"+(str)(LIVES), [160, (CANVAS_HEIGHT/2)+30], 50, "Purple", "monospace")
        canvas.draw_text("Press space to go back to menu", [150, (CANVAS_HEIGHT)-50], 30, "Black", "monospace")
        self.frame.set_keydown_handler(self.key_handler)
       
    #Winner screen
    def winner_finish(self, canvas):
        self.image = simplegui.load_image('https://www.cs.rhul.ac.uk/home/zlac319/Cloud_Pixel_art.png')
        canvas.draw_image(self.image,[1760 // 2, 
                    1140 // 2], [1760, 1140], 
                    [CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2], [CANVAS_WIDTH, CANVAS_HEIGHT])
        canvas.draw_text("WINNER", [80, CANVAS_HEIGHT/2], 200, "Gold", "monospace")
        canvas.draw_text("Score:"+(str)(SCORE), [250, (CANVAS_HEIGHT/2)+80], 50, "Green", "monospace")
        canvas.draw_text("Press space to go back to menu", [150, (CANVAS_HEIGHT)-50], 30, "Black", "monospace")
        self.frame.set_keydown_handler(self.key_handler)
    
    # define event handlers for game        
    def keydown(self, key):
        #Adjust horizontal velocity of player on keydown
        if key == simplegui.KEY_MAP["left"]:
            self.my_player.vel.add(Vector(-2.5,0))
            self.frame.set_keyup_handler(self.keyup)
            self.penguin = simplegui.load_image('https://cs.rhul.ac.uk/home/zlac319/penguin_flip.png')
        elif key == simplegui.KEY_MAP["right"]:
            self.my_player.vel.add(Vector(2.5,0))
            self.frame.set_keyup_handler(self.keyup)
            self.penguin = simplegui.load_image('https://www.cs.rhul.ac.uk/home/zlac319/Penguin1.png')
            
    def keyup(self, key):
        #Adjust horizontal velocity of player on keyup
        if key == simplegui.KEY_MAP["left"]:
            self.my_player.vel.add(Vector(2.5,0))
        elif key == simplegui.KEY_MAP["right"]:
            self.my_player.vel.add(Vector(-2.5,0))
    
    def keyup_start(self, key):
        #When game first starts to prevent throwing player one way if held down after dying
        if key == simplegui.KEY_MAP["left"]:
            self.my_player.vel.add(Vector(0,0))
            self.frame.set_keyup_handler(self.keyup)
        elif key == simplegui.KEY_MAP["right"]:
            self.my_player.vel.add(Vector(0,0))
            self.frame.set_keyup_handler(self.keyup)
       
    def draw(self, canvas):
        global SCORE, LIVES, PREV_SCORE, SCORE_COLOR
        #Update player position, draw player, draw platforms (general and finsih) that are visible and their heights, draw snowballs
        
        #Draw background
        self.image = simplegui.load_image('https://www.cs.rhul.ac.uk/home/zlac319/Cloud_Pixel_art.png')
        canvas.draw_image(self.image,[1760 // 2, 
                    1140 // 2], [1760, 1140], 
                    [CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2], [CANVAS_WIDTH, CANVAS_HEIGHT])
        #Update and draw player
        self.my_player.update(self)
        self.my_player.draw_player(canvas, self, self.penguin)
        #Update and draw ball, handle collisions with player
        for ballNum in range(0,4):
            if SCORE>=5000*ballNum:
                self.balls[ballNum].update()
                self.balls[ballNum].draw(canvas)
                
        for b in self.balls:
            if (b.pos.x-20 < self.my_player.pos.x < b.pos.x+20) and (b.pos != Vector(((CANVAS_WIDTH // 2)//100)*100, ((CANVAS_HEIGHT // 2)//100)*100)):
                if b.pos.y-20 < self.my_player.pos.y-self.cam.y < b.pos.y+20:
                    self.start_game()
                    LIVES -= 1
                    PREV_SCORE = SCORE
        
        #Draw score and lives on screen
        canvas.draw_text("Score:" +(str(SCORE)), [10, 100], 50, SCORE_COLOR, "monospace")
        canvas.draw_text("Lives:" +(str(LIVES)), [10, 50], 50, "red", "monospace")
        SCORE = PREV_SCORE + (int)(self.my_player.pos.y//100*100)
        
        #Calculate which platforms to display (in view) and draw
        for platform_index in range((int)(self.cam.y // PLATFORM_SPACING), 
                           (int)((CANVAS_HEIGHT + self.cam.y) // PLATFORM_SPACING) + 1):
            if platform_index < NUM_PLAT:
                self.platform_list[platform_index].draw_platform(canvas, self)
        self.finish_plat.draw_platform(canvas,self)
    
    #If game is over, stop game and restart intro screen
    def stop(self):
        global LIVES, PREV_SCORE, FINISHED
        self.frame.stop()
        self.__init__()
        LIVES = 5
        PREV_SCORE = 0
        FINISHED = False

#Class for intro screen animation
class Clock:
    def __init__(self):
        self.time = 0
    
    def tick(self):
        self.time += 1
    
    def transition(self, frame_duration):
        if self.time % frame_duration == 0:
            return True


# Start game at intro screen        
Game()
