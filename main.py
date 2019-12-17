import pygame
import math
import random

# initialize the pygame package
pygame.init()
pygame.mixer.init()


# region game classes

class ImageInfo:
    def __init__(self, center, size, radius=0, lifespan=None, animated=False):
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


class SpaceRocket:
    def __init__(self, pos, vel, angle, image, image_thrust, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_thrust = image_thrust
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()

    def draw(self, screen):
        if self.thrust:
            draw_on_screen(screen, self.image_thrust, self.image_center, self.image_size, self.pos, self.image_size,
                           self.angle)
        else:
            draw_on_screen(screen, self.image, self.image_center, self.image_size, self.pos, self.image_size,
                           self.angle)

    def update(self):
        # update angle
        self.angle += self.angle_vel

        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT

        # update velocity
        if self.thrust:
            acc = angle_to_vector(-self.angle)
            self.vel[0] += acc[0] * .1
            self.vel[1] += acc[1] * .1

        self.vel[0] *= .98
        self.vel[1] *= .98

    def set_thrust(self, on):
        self.thrust = on
        if on:
            mscSpaceRocketThrust.play()
        else:
            mscSpaceRocketThrust.stop()

    def increment_angle_vel(self):
        self.angle_vel -= .05

    def decrement_angle_vel(self):
        self.angle_vel += .05

    def shoot(self, missile_group):
        forward = angle_to_vector(-self.angle)
        missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
        missile_vel = [self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
        a_missile = Sprite(missile_pos, missile_vel, self.angle, 0, imgMissile, imgInfoMissile, mscMissileShot)
        missile_group.add(a_missile)
        pass

    def get_position(self):
        return self.pos
        pass

    def get_radius(self):
        return self.radius
        pass


class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound=None):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.play()
            pass
        pass

    def get_position(self):
        return self.pos
        pass

    def get_radius(self):
        return self.radius
        pass

    def collide(self, object2):
        r1 = self.get_radius()
        r2 = object2.get_radius()
        pos1 = self.get_position()
        pos2 = object2.get_position()
        return dist(pos1, pos2) < (r1 + r2)
        pass

    def draw(self, screen):
        factor = 1
        if self.animated:
            factor *= self.age
            draw_on_screen(screen, self.image,
                           [self.image_center[0] + (factor * self.image_size[0]), self.image_center[1]],
                           self.image_size, self.pos, self.image_size, self.angle, True)
            pass
        else:
            draw_on_screen(screen, self.image, self.image_center, self.image_size, self.pos, self.image_size,
                           self.angle)
            pass

    def update(self):
        # update angle
        self.angle += self.angle_vel

        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT

        # increase age
        self.age += 1

        return self.age >= self.lifespan

        pass


# endregion

# region game functions

def asteroid_spawner():
    global asteroids_group, running, spaceRocket

    if running and len(asteroids_group) < MAX_ASTEROIDS:
        rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
        rock_vel = [random.random() * .6 - .3, random.random() * .6 - .3]
        rock_avel = random.random() * .2 - .1
        a_rock = Sprite(rock_pos, rock_vel, 0, rock_avel, imgAsteroidBlack, imgInfoAsteroidBlack)
        if a_rock.collide(spaceRocket) == False:
            asteroids_group.add(a_rock)
            pass
        pass
    pass


def process_sprite_group(sprite_group, screen):
    for sprite in list(sprite_group):
        if sprite.update():
            sprite_group.remove(sprite)
            pass
        sprite.draw(screen)
        pass
    pass


def group_collide(sp_group, sprite):
    global explosion_group
    collision_happended = False

    for sp in list(sp_group):
        if sp.collide(sprite):
            sp_group.remove(sp)
            collision_happended = True
            an_explosion = Sprite(sprite.get_position(), [0, 0], 0, 0, imgSpriteExplosion, imgInfoSpriteExplosion,
                                  mscExplosion)
            explosion_group.add(an_explosion)
            pass
        pass
    return collision_happended
    pass


def group_group_collide(sp_group1, sp_group2):
    no_of_collisions = 0
    for sp1 in list(sp_group1):

        if group_collide(sp_group2, sp1):
            no_of_collisions += 1
            sp_group1.discard(sp1)
            pass
        pass
    return no_of_collisions
    pass


# endregion

# region initialize images

# space world(background) image
imgInfoSpaceWorld = ImageInfo([400, 300], [800, 600])
imgSpaceWorld = pygame.image.load('images/imgSpaceWorld.png')

# intro image
imgInfoIntroUltimateAsteroids = ImageInfo([200, 150], [400, 300])
imgIntroUltimateAsteroids = pygame.image.load("images/imgIntroUltimateAsteroids.png")

# space rocket image
imgInfoSpaceRocket = ImageInfo([30, 30], [60, 60], 35)
imgSpaceRocketNoThrust = pygame.image.load("images/imgSpaceRocketNoThrust.png")
imgSpaceRocketThrust = pygame.image.load("images/imgSpaceRocketThrust.png")

# asteroid image
imgInfoAsteroidBlack = ImageInfo([45, 45], [90, 90], 40)
imgAsteroidBlack = pygame.image.load('images/imgAsteroidBlack.png')

# missile image
imgInfoMissile = ImageInfo([5, 5], [10, 10], 3, 50)
imgMissile = pygame.image.load("images/imgMissile.png")

# explosion image
imgInfoSpriteExplosion = ImageInfo([64, 64], [128, 128], 17, 24, True)
imgSpriteExplosion = pygame.image.load("images/imgSpriteExplosion.png")

# endregion

# region initialize sounds

# game background theme music
mscBackgroundTheme = pygame.mixer.Sound('sounds/mscBackgroundTheme.wav')
mscBackgroundTheme.set_volume(0.2)
if mscBackgroundTheme:
    mscBackgroundTheme.play(100)

# space rocket thrust sound
mscSpaceRocketThrust = pygame.mixer.Sound("sounds/mscSpaceRocketThrust.wav")
mscSpaceRocketThrust.set_volume(0.9)

# missile shot sound
mscMissileShot = pygame.mixer.Sound('sounds/mscMissileShot.wav')
mscMissileShot.set_volume(0.2)

# explosion sound (both asteroid and space rocket)
mscExplosion = pygame.mixer.Sound("sounds/mscExplosion.wav")
mscExplosion.set_volume(0.8)

# endregion

# region initialize fonts

font = pygame.font.Font('fonts/Kenney Space.ttf', 15)


# endregion

# region helper functions

def draw_on_screen(screen, image, center_source, width_height_source, center_dest, width_height_dest, rotation=0,
                   issprite=False):
    if issprite:
        left_dest = center_dest[0] - (width_height_dest[0] / 2)
        top_dest = center_dest[1] - (width_height_dest[1] / 2)
        width_dest = width_height_dest[0]
        height_dest = width_height_dest[1]
        rect_dest = pygame.Rect(left_dest, top_dest, width_dest, height_dest)

        left_src = center_source[0] - (width_height_source[0] / 2)
        top_src = center_source[1] - (width_height_source[1] / 2)
        width_src = width_height_source[0]
        height_src = width_height_source[1]
        rect_src = pygame.Rect(left_src, top_src, width_src, height_src)
        screen.blit(image, rect_dest, rect_src)
        pass
    else:

        rotation_degrees = math.degrees(rotation)
        rotation_degrees %= 360
        rotated = pygame.transform.rotate(image, rotation_degrees)
        rect_dest = rotated.get_rect(center=(center_dest[0], center_dest[1]))
        screen.blit(rotated, rect_dest)
        pass


def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]


def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


# endregion

# game display width & height
WIDTH = 800
HEIGHT = 600

# create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# set title and icon
pygame.display.set_caption("Ultimate Asteroids")
icon = pygame.image.load('images/iconUltimateAsteroids.png')
pygame.display.set_icon(icon)

# region game variables initializations
running = True
spaceRocket = SpaceRocket([WIDTH / 2, HEIGHT / 2], [0, 0], 0, imgSpaceRocketNoThrust, imgSpaceRocketThrust,
                          imgInfoSpaceRocket)
asteroids_group = set([])
missile_group = set([])
explosion_group = set([])
score = 0
lives = 9
MAX_ASTEROIDS = 12

ROCK_SPAWN = pygame.USEREVENT + 1
pygame.time.set_timer(ROCK_SPAWN, 1000)

# endregion

# game loop
while running:

    # draw background image
    screen.blit(imgSpaceWorld, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pass
        pass

        if event.type == ROCK_SPAWN:
            if lives > 0:
                asteroid_spawner()
            pass
        pass

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                spaceRocket.decrement_angle_vel()
            elif event.key == pygame.K_RIGHT:
                spaceRocket.increment_angle_vel()
            elif event.key == pygame.K_UP:
                spaceRocket.set_thrust(True)
            elif event.key == pygame.K_SPACE:
                spaceRocket.shoot(missile_group)
            elif event.key == pygame.K_RETURN:
                if lives <= 0:
                    lives = 3
                    score = 0
                    pass
                pass
            pass
        pass

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                spaceRocket.increment_angle_vel()
            elif event.key == pygame.K_RIGHT:
                spaceRocket.decrement_angle_vel()
            elif event.key == pygame.K_UP:
                spaceRocket.set_thrust(False)
            pass
        pass

    pass

    # collisions
    if group_collide(asteroids_group, spaceRocket):
        lives -= 1
        pass

    spaceRocket.draw(screen)
    process_sprite_group(asteroids_group, screen)
    process_sprite_group(missile_group, screen)
    score += group_group_collide(asteroids_group, missile_group)
    process_sprite_group(explosion_group, screen)

    # update ship
    spaceRocket.update()

    if lives <= 0:
        draw_on_screen(screen, imgIntroUltimateAsteroids, imgInfoIntroUltimateAsteroids.get_center(),
                       imgInfoIntroUltimateAsteroids.get_size(), [WIDTH / 2, HEIGHT / 2],
                       imgInfoIntroUltimateAsteroids.get_size())

        for asteroid in list(asteroids_group):
            asteroids_group.remove(asteroid)
            pass
        pass
    pass

    # draw UI
    score_render = font.render("Score: " + str(score), True, (255, 255, 255))
    screen.blit(score_render, (10, 10))
    lives_render = font.render("Lives: " + str(lives), True, (255, 255, 255))
    screen.blit(lives_render, (685, 10))

    pygame.display.update()

pass
