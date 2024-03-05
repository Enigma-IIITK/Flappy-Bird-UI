import  pygame
import os
import random
import time
import pickle
global score
pygame.font.init()

WIN_WID = 500
WIN_HEIGHT = 700
image_folder = "Images"
bird_image_path = os.path.join(image_folder, "bird.png")
Bird_Img = pygame.transform.scale2x(pygame.image.load(bird_image_path))
pipe_image_path = os.path.join(image_folder, "pipe.png")
Pipe_Img = pygame.transform.scale2x(pygame.image.load(pipe_image_path))
base_image_path = os.path.join(image_folder, "base.png")
Base_Img = pygame.transform.scale2x(pygame.image.load(base_image_path))
bg_image_path = os.path.join(image_folder, "BG.png")
BG_Img = pygame.transform.scale2x(pygame.image.load(bg_image_path))

bird_img_scaled = pygame.transform.scale(Bird_Img, (Bird_Img.get_width() * 0.75, Bird_Img.get_height() * 0.75))
bird_Img = bird_img_scaled

Sat_Font = pygame.font.SysFont("timesnewroman",45)


class Bird:
    Img = Bird_Img
    Max_Rotation = 25
    Rot_Vel = 20
    Ani_time = 5

    def __init__(self,x,y): #Constructor to initialize the objects
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height =  self.y
        self.img_count = 0
        self.img = self.Img

    def jump(self):
        self.vel = -10.5 #To make the bird move up
        self.tick_count = 0 #A counter to know when the last jump was made. It is similar to the time required while jumping
        self.height = self.y   

    def move(self):
        self.tick_count += 1

        d = self.vel*self.tick_count + 1.5*self.tick_count**2 #No.of pixels we are moving upwards

        if(d >= 16): #Terminal Ve
            d = 16
        if(d<0):
            d -= 2
        
        self.y = self.y + d
        if d < 0 or self.y < self.height + 50: #Tilt up
            if(self.tilt < self.Max_Rotation):
                self.tilt = self.Max_Rotation
            
        if(self.tilt > -90): #Tilt down
            self.tilt -= self.Rot_Vel

    def draw(self,win):
        self.img_count += 1
        if(self.img_count < self.Ani_time):
            self.img = self.Img
        elif(self.img_count == self.Ani_time*4 + 1):
            self.img = self.Img
            self.img_count = 0
        
        if(self.tilt <= -80):
            self.img = self.Img
            self.img_count = self.Ani_time*2
        
        rotated_image  = pygame.transform.rotate(self.img,self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x,self.y)).center)
        win.blit(rotated_image,new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    Gap = 400
    Velocity = 5

    def __init__(self,x):
        self.x = x
        self.height = 0
        self.gap = 160

        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(Pipe_Img, False, True) # Pipe that is flipped
        self.PIPE_Bottom = Pipe_Img

        self.passed = False # If the bird has already passed the pipe
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height() 
        self.bottom = self.height + self.gap

    def move(self):
        self.x -= self.Velocity#To move the pipe in each frame

    def draw(self,win):
        win.blit(self.PIPE_TOP, (self.x,self.top))
        win.blit(self.PIPE_Bottom, (self.x,self.bottom))

    def collide(self,bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_Bottom)
        
        top_offset = (self.x - bird.x , self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask,bottom_offset)#Tells us how far the bird is from the Pipe
        t_point = bird_mask.overlap(top_mask,top_offset)#Both of these return None if they are not colliding

        if b_point or t_point:
            return True
        return False

class Base:
    Velo = 5
    Width = Base_Img.get_width()
    Img = Base_Img

    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.Width
    
    def move(self):
        self.x1 -= self.Velo
        self.x2 -= self.Velo

        #We are trying to create a circular pattern of 2 imgs of the baseto make us feel that teh base is moving.
        if self.x1 + self.Width < 0: #If the 1st image os of the screen
            self.x1 = self.x2+self.Width
        
        if self.x2 + self.Width < 0:
            self.x2 = self.x1+self.Width
            
    def draw(self,win):
        win.blit(self.Img,(self.x1,self.y))
        win.blit(self.Img,(self.x2,self.y))

    
def draw_window(win,bird,pipes,base,score):
    win.blit(BG_Img,(0,0))
    for p in pipes:
        p.draw(win)

    text = Sat_Font.render("Score: "+str(score),1,(0,255,255))
    win.blit(text, (WIN_WID  - 330 - text.get_width() , 10))

    base.draw(win)
    bird.draw(win)
    pygame.display.update()


def main(): 
    pygame.init()
    bird = Bird(230,350)
    score = 0
    base = Base(630)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WID, WIN_HEIGHT))
    pygame.display.set_caption('Hopping Bird')
    clock = pygame.time.Clock()
    run = True
    global SCORE
    
    add_pipe = False
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        rem = []
        for pipe in pipes:
            if pipe.collide(bird): #The game is made to terminate when the bird hits the pipe
                run = False
                pygame.quit()
                quit()

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x + bird.Img.get_width():
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            pipes.append(Pipe(700))
            add_pipe = False 

        for r in rem:
            pipes.remove(r)

        #bird.move() #Uncomment this statement to see the effect of inverted gravity on the bird.
        base.move()
        draw_window(win, bird, pipes, base,score)


main()
