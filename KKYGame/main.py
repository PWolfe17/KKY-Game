import pygame, sys, random, time, asyncio
from pygame.locals import *

# --- Platform detection ---
import platform as _platform
IS_WEB = _platform.system() == "Emscripten"

# Browser local storage helper (only works when running via Pygbag in browser)
def load_best_score():
    if IS_WEB:
        try:
            import js  # js is available in Pygbag/Emscripten environments
            val = js.localStorage.getItem("kky_best_score")
            if val is not None:
                return int(val)
        except Exception:
            pass
    else:
        # Fall back to file on desktop
        try:
            with open('best_game.txt', 'r') as f:
                return int(f.readline().strip())
        except Exception:
            pass
    return 0

def save_best_score(score):
    if IS_WEB:
        try:
            import js
            js.localStorage.setItem("kky_best_score", str(score))
        except Exception:
            pass
    else:
        try:
            with open('best_game.txt', 'w') as f:
                f.write(str(score))
        except Exception:
            pass

pygame.init()
vec = pygame.math.Vector2

pygame.mixer.music.load("KKY Game Music Revamp.wav")
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
    shown_score = int(game_score / 10)
    if shown_score > 200:
        platform_y_spacing = 85
    if shown_score > 400:
        platform_y_spacing = 100
    if shown_score > 600:
        platform_y_spacing = 115
    if shown_score > 800:
        platform_y_spacing = 120
    if shown_score > 1000:
        platform_y_spacing = 125
    if shown_score > 1100:
        platform_y_spacing = 130
    if shown_score > 1200:
        platform_y_spacing = 140
    if shown_score > 1500:
        platform_y_spacing = 150
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


def reset_game():
    """Reset all game state for a new game."""
    global game_score, PT1, P1

    all_sprites.empty()
    platforms.empty()

    game_score = 0

    PT1 = Platform(WIDTH // 2, HEIGHT - 10)
    PT1.image = pygame.Surface((WIDTH, 20))
    PT1.image.fill((0, 255, 0))
    PT1.rect = PT1.image.get_rect(center=(WIDTH / 2, HEIGHT - 10))
    PT1.point = False
    all_sprites.add(PT1)
    platforms.add(PT1)

    P1 = Player()
    all_sprites.add(P1)

    initial_y = HEIGHT - 80
    for i in range(6):
        x = random.randint(200, 600)
        y = initial_y - i * 70
        pl = Platform(x, y)
        platforms.add(pl)
        all_sprites.add(pl)


# --- Sprite groups (populated by reset_game) ---
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
PT1 = None
P1 = None


async def start_screen():
    """
    Show the start screen and wait for the player to press SPACE or click.
    Fully async-friendly: yields every frame so the browser doesn't freeze.
    """
    f = pygame.font.SysFont("Verdana", 22)
    prompt = f.render("Press SPACE or click to play!", True, (255, 255, 0))
    prompt_rect = prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    spaceprompt = f.render("SPACE to Jump; Arrow Keys to Move", True, (255, 0, 255))
    space_rect = spaceprompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 180))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return  # Player is ready — exit the start screen
            if event.type == pygame.MOUSEBUTTONDOWN:
                return  # Also start on click

        displaysurface.fill((0, 0, 0))
        # Draw pillars
        displaysurface.blit(pillar, topleft_rect)
        displaysurface.blit(pillar, topright_rect)
        displaysurface.blit(pillar, bright_rect)
        displaysurface.blit(pillar, bleft_rect)
        # Draw the start button image centred on screen
        sb_rect = sb_image_scaled.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        displaysurface.blit(sb_image_scaled, sb_rect)
        displaysurface.blit(prompt, prompt_rect)
        displaysurface.blit(spaceprompt, space_rect)

        pygame.display.update()
        FramePerSec.tick(FPS)
        await asyncio.sleep(0)  # Yield control every frame — required for Pygbag


async def death_screen():
    """Play death sounds/images, then return so the loop can restart."""
    pygame.mixer.music.stop()
    pygame.mixer.Sound.play(yoda_sound)
    displaysurface.blit(you_died_scaled, (0, 0))
    pygame.display.update()
    time.sleep(2)

    # Wait ~2 seconds while still yielding to the browser
    for _ in range(FPS * 2):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        await asyncio.sleep(0)
    pygame.mixer.music.play(-1)

    displaysurface.blit(bo_scaled, (0, 0))
    pygame.display.update()

    for _ in range(int(FPS * 3.7)):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        await asyncio.sleep(0)


async def main():
    global game_score, best_score, P1

    best_score = load_best_score()

    # Outer loop: start screen → game → death → repeat
    while True:
        await start_screen()          # Wait here until player starts

        reset_game()                  # Fresh game state
           # Restart music

        # --- Inner game loop ---
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    save_best_score(best_score)
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

            # Player fell off screen → death
            if P1.rect.top > HEIGHT:
                actual_score = int(game_score / 10)
                if actual_score > best_score:
                    best_score = actual_score
                save_best_score(best_score)
                await death_screen()
                break  # Break inner loop → back to start screen

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
            g = f.render(headline, True, (123, 255, 0))
            displaysurface.blit(g, (280, 10))

            pygame.display.update()
            FramePerSec.tick(FPS)
            await asyncio.sleep(0)  # Yield every frame — required for Pygbag


asyncio.run(main())
