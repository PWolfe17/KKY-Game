import pygame, sys, random, time, asyncio
from pygame.locals import *

pygame.init()
vec = pygame.math.Vector2

pygame.mixer.music.load("KKY-Game-Music-New.ogg")
pygame.mixer.music.play(-1)

game_score = 0
HEIGHT = 450
WIDTH = 800
ACC = 0.5
FRIC = -0.12
FPS = 60

FramePerSec = pygame.time.Clock()
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("KKY Platform Game")
pillar_image = pygame.image.load("Pillar Picture.png")
start_button_image = pygame.image.load("Start Button.png")
sb_image_scaled = pygame.transform.scale(start_button_image, (400, 135))
bo_image = pygame.image.load("BoKKY.jpeg")
bo_scaled = pygame.transform.scale(bo_image, (800, 450))
yoda_sound = pygame.mixer.Sound("Lego-Yoda-death.ogg")
you_died = pygame.image.load("You Died.jpeg")
you_died_scaled = pygame.transform.scale(you_died, (800, 450))
cat_laughing = pygame.mixer.Sound("Cat-laughing-at-you.ogg")

pillar = pygame.transform.scale(pillar_image, (130, 225))
topleft_rect = pillar.get_rect(topleft=(0, 0))
topright_rect = pillar.get_rect(topright=(800, 0))
bleft_rect = pillar.get_rect(bottomleft=(0, 450))
bright_rect = pillar.get_rect(bottomright=(800, 450))

'''
class Button(object):
    def __init__(self, position, filename):
        self.image = filename
        self.rect = self.image.get_rect(midtop=position)

    def draw_button(self, surface):
        surface.draw(self.image, self.rect)

    def check_press(self, position):
        if self.rect.collidepoint(*position):
            return True
        return False
'''

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        image_load = pygame.image.load("ColorKKYCrest.png").convert_alpha()
        self.image = pygame.transform.scale(image_load, (60, 80))
        self.rect = self.image.get_rect()

        self.pos = vec((400, 300))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.jumping = False
        self.score = 0

    def move(self):
        self.acc = vec(0, 0.5)
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[K_RIGHT]:
            self.acc.x = ACC

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

    def jump(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -15

    def cancel_jump(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3

    def update(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if self.vel.y > 0:
            if hits:
                if self.pos.y < hits[0].rect.bottom:
                    if hits[0]:
                        hits[0].point = False
                        self.score += 1
                    self.pos.y = hits[0].rect.top + 1
                    self.vel.y = 0
                    self.jumping = False


class Platform(pygame.sprite.Sprite):
    def __init__(self, x=None, y=None):
        super().__init__()
        self.image = pygame.Surface((random.randint(60, 100), 12))
        self.image.fill((0, 50, 255))
        self.point = True
        if x is None:
            x = random.randint(100, WIDTH - 100)
        if y is None:
            y = random.randint(0, HEIGHT - 30)

        self.rect = self.image.get_rect(center=(x, y))

    def move(self):
        pass


def check(platform, groupies):
    if pygame.sprite.spritecollideany(platform, groupies):
        return True
    else:
        for entity in groupies:
            if entity == platform:
                continue
            if (abs(platform.rect.top - entity.rect.bottom) < 40) and (
                    abs(platform.rect.bottom - entity.rect.top) < 40):
                return True
        return False


def plat_gen():
    platform_y_spacing = 70
    last_y = 0
    if platforms:
        last_y = min([plat.rect.y for plat in platforms])

    attempts = 0
    while len(platforms) < 6 and attempts < 100:
        x = random.randint(220, 580)
        y = last_y - platform_y_spacing
        p = Platform(x, y)

        if not check(p, platforms):
            platforms.add(p)
            all_sprites.add(p)
            last_y = y
        attempts += 1


PT1 = Platform(WIDTH // 2, HEIGHT - 10)
PT1.image = pygame.Surface((WIDTH, 20))
PT1.image.fill((0, 255, 0))
PT1.rect = PT1.image.get_rect(center=(WIDTH / 2, HEIGHT - 10))
PT1.point = False
P1 = Player()
#play_button = Button((400, 225), sb_image_scaled)

all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()

all_sprites.add(PT1)
platforms.add(PT1)

all_sprites.add(P1)

# Create initial platforms spaced vertically
initial_y = HEIGHT - 80
for i in range(6):
    x = random.randint(200, 600)
    y = initial_y - i * 70
    pl = Platform(x, y)
    platforms.add(pl)
    all_sprites.add(pl)

with open('best_game.txt', 'r') as best_game:
    best_score = int(best_game.readline().strip())


def start_screen():
    while True:
        displaysurface.blit(sb_image_scaled, (400, 225))


async def main():
    global best_score
    global game_score
    # Main loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    P1.jump()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    P1.cancel_jump()

        P1.move()
        P1.update()
        if P1.rect.top <= HEIGHT / 3:
            P1.pos.y += abs(P1.vel.y)
            game_score += abs(P1.vel.y)
            for plat in platforms:
                plat.rect.y += abs(P1.vel.y)
                if plat.rect.top >= HEIGHT:
                    plat.kill()

        if P1.rect.top > HEIGHT:
            with open('best_game.txt', 'w') as best_game:
                best_game.write(str(best_score))
            pygame.mixer.music.stop()
            pygame.mixer.Sound.play(yoda_sound)
            for entity in all_sprites:
                entity.kill()
            displaysurface.blit(you_died_scaled, (0, 0))
            pygame.display.update()
            time.sleep(2)
            pygame.mixer.Sound.play(cat_laughing)
            displaysurface.blit(bo_scaled, (0, 0))
            pygame.display.update()
            time.sleep(3.7)
            pygame.quit()
            sys.exit()

        plat_gen()
        displaysurface.fill((0, 0, 0))

        for entity in all_sprites:
            displaysurface.blit(entity.image, entity.rect)
            displaysurface.blit(pillar, topleft_rect)
            displaysurface.blit(pillar, topright_rect)
            displaysurface.blit(pillar, bright_rect)
            displaysurface.blit(pillar, bleft_rect)
            if isinstance(entity, Platform):
                entity.move()

        f = pygame.font.SysFont("Verdana", 20)
        actual_score = int(game_score / 10)
        if best_score <= actual_score:
            best_score = actual_score
        headline = f'Best: {best_score} | Current: {actual_score}'
        g = f.render((str(headline)), True, (123, 255, 0))
        displaysurface.blit(g, (280, 10))
        pygame.display.update()
        FramePerSec.tick(FPS)
        start_screen()
        await asyncio.sleep(0)


asyncio.run(main())
