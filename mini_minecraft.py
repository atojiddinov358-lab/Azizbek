import pygame
import sys

pygame.init()

# Oyna
WIDTH = 1000
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Minecraft")

clock = pygame.time.Clock()

# Ranglar
SKY = (135, 206, 235)
GRASS = (50, 180, 50)
DIRT = (130, 80, 40)
STONE = (100, 100, 100)
WOOD = (150, 90, 40)
LEAVES = (30, 150, 50)
PLAYER_COLOR = (255, 50, 50)

# Blok o'lchami
BLOCK = 40

# Xarita
world = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
]

# Daraxt
world[7][5] = 4
world[6][5] = 4
world[5][5] = 4
world[4][5] = 4
world[5][4] = 5
world[5][6] = 5
world[4][4] = 5
world[4][5] = 5
world[4][6] = 5
world[3][5] = 5

# O'yinchi
player = pygame.Rect(200, 300, 30, 50)

velocity_y = 0
gravity = 0.8
jump = -14
on_ground = False

# Blok ranglari
colors = {
    1: GRASS,
    2: DIRT,
    3: STONE,
    4: WOOD,
    5: LEAVES
}

def draw_world():
    for y, row in enumerate(world):
        for x, block in enumerate(row):
            if block != 0:
                pygame.draw.rect(
                    screen,
                    colors[block],
                    (x * BLOCK, y * BLOCK, BLOCK, BLOCK)
                )

                pygame.draw.rect(
                    screen,
                    (0, 0, 0),
                    (x * BLOCK, y * BLOCK, BLOCK, BLOCK),
                    1
                )

def get_blocks():
    blocks = []

    for y, row in enumerate(world):
        for x, block in enumerate(row):
            if block != 0:
                blocks.append(
                    pygame.Rect(
                        x * BLOCK,
                        y * BLOCK,
                        BLOCK,
                        BLOCK
                    )
                )

    return blocks

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Sichqoncha bilan blok sindirish yoki qo'yish
        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = pygame.mouse.get_pos()

            x = mouse_x // BLOCK
            y = mouse_y // BLOCK

            if 0 <= y < len(world) and 0 <= x < len(world[0]):

                # Chap tugma = blok sindirish
                if event.button == 1:
                    world[y][x] = 0

                # O'ng tugma = blok qo'yish
                elif event.button == 3:
                    if world[y][x] == 0:
                        world[y][x] = 2

    # Klaviatura
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player.x -= 5

    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player.x += 5

    # Sakrash
    if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and on_ground:
        velocity_y = jump
        on_ground = False

    # Gravitatsiya
    velocity_y += gravity
    player.y += velocity_y

    # Yer bilan to'qnashuv
    on_ground = False

    for block in get_blocks():

        if player.colliderect(block):

            if velocity_y > 0:
                player.bottom = block.top
                velocity_y = 0
                on_ground = True

            elif velocity_y < 0:
                player.top = block.bottom
                velocity_y = 0

    # Ekrandan chiqib ketmaslik
    if player.x < 0:
        player.x = 0

    if player.right > WIDTH:
        player.right = WIDTH

    # Chizish
    screen.fill(SKY)

    draw_world()

    # O'yinchi
    pygame.draw.rect(screen, PLAYER_COLOR, player)

    # Ko'rsatmalar
    font = pygame.font.SysFont("Arial", 20)

    text = font.render(
        "A/D - Yurish | SPACE - Sakrash | Chap tugma - Sindirish | O'ng tugma - Qo'yish",
        True,
        (0, 0, 0)
    )

    screen.blit(text, (10, 10))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
