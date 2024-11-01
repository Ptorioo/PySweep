import pygame
import random

# General
DIMENSION = 16
TILESIZE = 20
MINE_NUM = 20
RESOLUTION = (DIMENSION * TILESIZE, DIMENSION * TILESIZE)
TITLE = 'PySweep'
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
DARKGREEN = (0, 200, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.inside = pygame.Surface((size - 2, size - 2))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.image.fill(BLACK)
        self.inside.fill(LIGHTGREY)
        self.image.blit(self.inside, (2, 2))

        # Tile states
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighboring_mines = 0

    def reveal(self):
        self.is_revealed = True
        if self.is_mine:
            self.inside.fill(RED)
        else:
            self.inside.fill(WHITE)
            if self.neighboring_mines > 0:
                font = pygame.font.SysFont("calibri", 14)
                text = font.render(str(self.neighboring_mines), True, BLACK)
                self.inside.blit(text, (self.rect.width / 4, self.rect.height / 4))
        self.image.blit(self.inside, (2, 2))

    def toggle_flag(self):
        if not self.is_revealed:
            self.is_flagged = not self.is_flagged
            if self.is_flagged:
                self.inside.fill(YELLOW)
            else:
                self.inside.fill(LIGHTGREY)
        self.image.blit(self.inside, (2, 2))

class Grid(pygame.sprite.Group):
    def __init__(self, rows, cols, tile_size):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.tile_size = tile_size
        self.tiles = []

        for row in range(rows):
            tile_row = []
            for col in range(cols):
                tile = Tile(col * tile_size, row * tile_size, tile_size)
                tile_row.append(tile)
                self.add(tile)
            self.tiles.append(tile_row)

        self.place_mines()

    def place_mines(self, num_mines=MINE_NUM):
        mines_placed = 0
        while mines_placed < num_mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            tile = self.tiles[row][col]
            if not tile.is_mine:
                tile.is_mine = True
                mines_placed += 1
        self.calculate_neighbors()

    def calculate_neighbors(self):
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.tiles[row][col]
                if tile.is_mine:
                    continue
                # Count neighboring mines
                mine_count = 0
                for dr, dc in directions:
                    r, c = row + dr, col + dc
                    if 0 <= r < self.rows and 0 <= c < self.cols and self.tiles[r][c].is_mine:
                        mine_count += 1
                tile.neighboring_mines = mine_count

    def reveal_tile(self, row, col):
        tile = self.tiles[row][col]
        if tile.is_flagged:
            return
        tile.reveal()
        if tile.is_mine:
            return True
        elif tile.neighboring_mines == 0:
            self.reveal_neighbors(row, col)
        return False

    def reveal_all_mines(self):
        for row in self.tiles:
            for tile in row:
                if tile.is_mine and not tile.is_revealed:
                    tile.reveal()

    def reveal_neighbors(self, row, col):
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < self.rows and 0 <= c < self.cols:
                neighbor_tile = self.tiles[r][c]
                if not neighbor_tile.is_revealed and not neighbor_tile.is_flagged:
                    neighbor_tile.reveal()
                    if neighbor_tile.neighboring_mines == 0:
                        self.reveal_neighbors(r, c)

    def check_win(self):
        for row in self.tiles:
            for tile in row:
                if not tile.is_mine and not tile.is_revealed:
                    return False
        return True

class Game:
    def __init__(self):
        pygame.init()  # Initialize pygame in the constructor
        self.screen = pygame.display.set_mode(RESOLUTION)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.grid = Grid(DIMENSION, DIMENSION, TILESIZE)
        self.game_over = False

    def new(self):
        self.grid = Grid(DIMENSION, DIMENSION, TILESIZE)
        self.game_over = False  # Reset game-over state

    def run(self):
        while not self.game_over:
            self.clock.tick(FPS)
            self.event()
            self.draw()

    def draw(self):
        self.screen.fill(DARKGREY)
        self.grid.draw(self.screen)
        pygame.display.flip()

    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True  # Stop the game loop
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                x, y = event.pos
                row = y // TILESIZE
                col = x // TILESIZE
                if event.button == 1:  # Left click
                    mine_hit = self.grid.reveal_tile(row, col)
                    if mine_hit:
                        self.game_over = True
                        self.grid.reveal_all_mines()
                    elif self.grid.check_win():
                        self.game_over = True
                        print("You win!")
                elif event.button == 3:  # Right click
                    self.grid.tiles[row][col].toggle_flag()

game = Game()

while True:
    game.new()
    game.run()
    pygame.quit()  # Ensure pygame quits after the game loop ends
    break  # Exit the while loop
