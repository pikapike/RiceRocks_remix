# RiceRocks remix
# press f to level up
# arrow keys and space key are obvious
# c for shotgun
# v for doomsday
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 10
time = 0
started = False
charge_prog = 0
charge_set = 2000
high_score = 0
timing = 0
level = 1
doom_bullet_rchrge = 0
reg_bullet_rchrge = 0
shotgun_rchrge = 0
timerd = 0

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2013.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
# .ogg versions of sounds are also available, just replace .mp3 by .ogg
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

def collide(rock, something):
    global score, lives, group_of_rocks, missiles, explosion_image, explosion_info, charge_prog, charge_set, level
    if dist(rock.pos, something.pos) < rock.radius*rock.size + something.radius*something.size:
        if something.radius < 10:
            if not something.doom:
                missiles.remove(something)
            score += 7+3*level
            if something.doom:
                score += int(90+20*(rock.size % 0.05))
            charge_prog += 30
            if charge_prog > charge_set:
                charge_prog = charge_set
            if (rock.size > 0.8) and (not something.doom):
                group_of_rocks.append(Sprite(rock.pos, [0.01*random.randrange(-300, 300), 0.01*random.randrange(-300, 300)],
                                             0, 0.001*random.randrange(-50, 50), asteroid_image, asteroid_info, None, rock.size*0.85))
                group_of_rocks.append(Sprite(rock.pos, [0.01*random.randrange(-200, 200), 0.01*random.randrange(-200, 200)],
                                             0, 0.001*random.randrange(-50, 50), asteroid_image, asteroid_info, None, rock.size*0.85))

        else:
            lives -= 1
        try:
            group_of_rocks.remove(rock)
            explosions.append(Sprite((rock.pos[0], rock.pos[1]), [0, 0], 0, 0, explosion_image, explosion_info, explosion_sound))
        except:
            pass

# Ship class
class Ship:

    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.size = 1
        
    def draw(self,canvas):
        image_ship_center = [45, 45]
        if self.thrust == True:
            image_ship_center[0] += 90
        canvas.draw_image(ship_image, image_ship_center, self.image_size, self.pos, self.image_size, self.angle)



    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT

        # update velocity
        if self.thrust:
            acc = angle_to_vector(self.angle)
            self.vel[0] += acc[0] * .1
            self.vel[1] += acc[1] * .1
            
        self.vel[0] *= .99
        self.vel[1] *= .99
        if self.thrust == True:
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.rewind()

    def set_thrust(self, on):
        self.thrust = on
       
    def increment_angle_vel(self):
        self.angle_vel += .05
        
    def decrement_angle_vel(self):
        self.angle_vel -= .05
        
    def shoot(self):
        global missiles, reg_bullet_rchrge
        forward = angle_to_vector(self.angle)
        missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
        missile_vel = [self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
        if reg_bullet_rchrge >= 15:
            missiles.append(Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound, 1))
            reg_bullet_rchrge -= 15
    
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None, size = None, doom = False):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        self.size = size
        self.doom = doom
        if doom:
            self.lifespan = 150
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        if self.animated:
            canvas.draw_image(self.image, [self.image_size[0]*(24.5-self.lifespan), self.image_center[1]],
                              self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                          self.pos, [self.image_size[0]*self.size, self.image_size[1]*self.size], self.angle)

    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        self.lifespan -= 1
  
        
# key handlers to control ship   
def keydown(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(True)
    elif key == simplegui.KEY_MAP['space']:
        my_ship.shoot()
    elif key == simplegui.KEY_MAP['f']:
        global charge_set, charge_prog, score, lives, level
        if charge_prog == charge_set and started:
            while group_of_rocks != []:
                for rock in group_of_rocks:
                    group_of_rocks.remove(rock)
                    explosions.append(Sprite((rock.pos[0], rock.pos[1]), [0, 0], 0, 0, explosion_image, explosion_info, explosion_sound))
                    score += 10
            score += (level * 250) + 1000
            charge_set += 600
            charge_prog = 0
            lives += 3
            level += 1
    elif key == simplegui.KEY_MAP['c']:
        global missiles, shotgun_rchrge
        if (len(missiles) < 6) and shotgun_rchrge >= 60:
            angle = my_ship.angle - 0.65
            forward = angle_to_vector(angle)
            while angle < my_ship.angle + 0.7:
                missile_pos = [my_ship.pos[0] + my_ship.radius * forward[0], my_ship.pos[1] + my_ship.radius * forward[1]]
                missile_vel = [my_ship.vel[0] + 6 * forward[0], my_ship.vel[1] + 6 * forward[1]]
                missiles.append(Sprite(missile_pos, missile_vel, angle, 0, missile_image, missile_info, missile_sound, 1))
                angle += 0.15
                shotgun_rchrge = 0
                forward = angle_to_vector(angle)
    elif key == simplegui.KEY_MAP['v']:
        global doom_bullet_rchrge
        if doom_bullet_rchrge >= 60:
            angle = my_ship.angle
            forward = angle_to_vector(angle)
            i = 0
            n = 1+0*random.randrange(10, 11)
            doom_bullet_rchrge = 0
            reg_bullet_rchrge = 0
            shotgun_rchrge = 0
            while i < n:
                missile_pos = [my_ship.pos[0] + my_ship.radius * forward[0], my_ship.pos[1] + my_ship.radius * forward[1]]
                missile_vel = [my_ship.vel[0] + 6 * forward[0], my_ship.vel[1] + 6 * forward[1]]
                missiles.append(Sprite(missile_pos, missile_vel, angle, 0, missile_image, missile_info, missile_sound, 1.6, True))
                i += 1
            
def keyup(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(False)
        
# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started, charge_prog, charge_set, score, level, lives, charge_prog, charge_set
    global doom_bullet_rchrge, reg_bullet_rchrge, shotgun_rchrge
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        score = 0
        lives = 10
        level = 1
        charge_prog = 0
        charge_set = 3000
        doom_bullet_rchrge = 0
        reg_bullet_rchrge = 0
        shotgun_rchrge = 0
        soundtrack.rewind()
        soundtrack.play()

def draw(canvas):
    global time, score, lives, group_of_rocks, missiles, my_ship, started, explosions
    global charge_prog, charge_set, high_score, timing, level, doom_bullet_rchrge, reg_bullet_rchrge, shotgun_rchrge
    if shotgun_rchrge < 60:
        shotgun_rchrge += 0.8
        colorspread = "White"
    else:
        colorspread = "Silver"
    if doom_bullet_rchrge < 60:
        doom_bullet_rchrge += 0.15
        colordoom = "White"
    else:
        colordoom = "Silver"
    if reg_bullet_rchrge < 60:
        reg_bullet_rchrge += 1.4
    if reg_bullet_rchrge < 15:
        color_reg = 'Yellow'
    elif reg_bullet_rchrge < 60:
        color_reg = 'Orange'
    else:
        color_reg = "Silver"
    if (charge_prog != charge_set) and (started):
        charge_prog += 2
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw ship and sprites
    my_ship.draw(canvas)
    for rock in group_of_rocks:
        rock.draw(canvas)
    for missile in missiles:
        missile.draw(canvas)
    for explosion in explosions:
        explosion.draw(canvas)
    canvas.draw_text("Lives:", [50, 50], 30, "White")
    canvas.draw_text(str(lives), [50, 80], 30, "White")
    if (high_score < score) and (timing % 2 == 0):
        color_1 = "Yellow"
    elif (high_score < score) and (not started):
        color_1 = "Yellow"
    else:
        color_1 = "White"
    canvas.draw_text("Score:", [675, 50], 30, color_1)
    canvas.draw_text(str(score), [675, 80], 30, color_1)
    if charge_prog == charge_set:
        color_2 = "Yellow"
    else:
        color_2 = "White"
    canvas.draw_text("Level "+str(level), [270, 50], 30, color_2)
    canvas.draw_text(str(charge_prog)+"/"+str(charge_set), [270, 80], 30, color_2)
    canvas.draw_line([450, 45], [450+reg_bullet_rchrge, 45], 15,
                     color_reg)
    canvas.draw_line([450, 75], [450+shotgun_rchrge, 75], 15,
                     colorspread)
    canvas.draw_line([450, 105], [450+doom_bullet_rchrge, 105], 15,
                     colordoom)
    canvas.draw_text("regular", [450, 35], 15, "White")
    canvas.draw_text("shotgun", [450, 65], 15, "White")
    canvas.draw_text("doomsday", [450, 95], 15, "White")
    # update shiif key == simplegui.KEY_MAP["up"]:
    my_ship.update()
    for rock in group_of_rocks:
        rock.update()
    for missile in missiles:
        missile.update()
        if missile.lifespan < 1:
            missiles.pop(0)
    for explosion in explosions:
        explosion.update()
        if explosion.lifespan < 1:
            explosions.pop(0)
    for rock in group_of_rocks:
        for missile in missiles:
            collide(rock, missile)
        collide(rock, my_ship)
        
    if (lives < 1) and (started):
        missiles = []
        group_of_rocks = []
        started = False
        if high_score < score:
            high_score = score - 10
        frame.add_label("Level "+str(level)+":  "+str(score))

    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())

# timer handler that spawns a rock    
def rock_spawner():
    global a_rock, timing, level
    timing += 1
    
    rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
    rock_vel = [random.random() * .6 - .3, random.random() * .6 - .3]
    rock_avel = random.random() * .2 - .1
    if (started) and (len(group_of_rocks) < 17+(5*level)):
        group_of_rocks.append(Sprite([(random.randrange(100, 700) + my_ship.pos[0]) % HEIGHT, (random.randrange(100, 500) + my_ship.pos[1]) % WIDTH],
                    [0.01*random.randrange(-200, 200), 0.01*random.randrange(-200, 200)],
                    random.randrange(0, 2), 0.001*random.randrange(-100, 100),
                    asteroid_image, asteroid_info, None, 1))            

# initialize stuff
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
group_of_rocks = []
missiles = []
explosions = []


# register handlers
frame.set_keyup_handler(keyup)
frame.set_keydown_handler(keydown)
frame.set_mouseclick_handler(click)
frame.set_draw_handler(draw)
frame.add_label("Scores:")
frame.add_label("_______________")

timer = simplegui.create_timer(1000.0, rock_spawner)
# get things rolling
timer.start()
frame.start()
