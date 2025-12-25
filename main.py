"""
snake.py — Simple Snake game using pygame

Controls:
- Arrow keys or WASD to move
- P to pause/unpause
- R to restart after game over
- Q or ESC to quit

Install pygame:
    pip install pygame

Run:
    python snake.py
"""

import random
import sys
import pygame

# Configuration
CELL_SIZE = 20
GRID_WIDTH = 30  # number of cells horizontally
GRID_HEIGHT = 20  # number of cells vertically
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10  # base speed; speed increases with score

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (20, 20, 20)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 155, 0)
RED = (200, 0, 0)
YELLOW = (255, 200, 0)
BLUE = (0, 150, 255)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def draw_cell(surface, pos, color):
    x, y = pos
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, color, rect)


def random_food_position(snake):
    while True:
        pos = (random.randrange(0, GRID_WIDTH), random.randrange(0, GRID_HEIGHT))
        if pos not in snake:
            return pos


class SnakeGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.large_font = pygame.font.SysFont("consolas", 36)
        self.reset()

    def reset(self):
        # Start snake in the middle
        mid_x = GRID_WIDTH // 2
        mid_y = GRID_HEIGHT // 2
        self.snake = [(mid_x, mid_y), (mid_x - 1, mid_y), (mid_x - 2, mid_y)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.food = random_food_position(self.snake)
        self.score = 0
        self.game_over = False
        self.paused = False
        self.tick_count = 0

    def change_direction(self, new_dir):
        # Prevent reversing directly
        if (new_dir[0] * -1, new_dir[1] * -1) == self.direction:
            return
        self.next_direction = new_dir

    def update(self):
        if self.game_over or self.paused:
            return

        # Apply buffered direction change
        self.direction = self.next_direction

        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Check collisions with walls
        if (
            new_head[0] < 0
            or new_head[0] >= GRID_WIDTH
            or new_head[1] < 0
            or new_head[1] >= GRID_HEIGHT
        ):
            self.game_over = True
            return

        # Check self-collision
        if new_head in self.snake:
            self.game_over = True
            return

        # Move snake
        self.snake.insert(0, new_head)

        # Eat food?
        if new_head == self.food:
            self.score += 1
            self.food = random_food_position(self.snake)
            # Increase speed slightly as score grows
        else:
            # Remove tail
            self.snake.pop()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.change_direction(UP)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.change_direction(DOWN)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.change_direction(LEFT)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.change_direction(RIGHT)
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    self.terminate()

    def draw_grid(self):
        # Optional subtle grid
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (0, y), (WINDOW_WIDTH, y))

    def draw(self):
        self.screen.fill(BLACK)
        # draw grid for nicer visuals
        self.draw_grid()

        # Draw food
        # draw a little circle in the center of the cell
        fx, fy = self.food
        food_center = (
            fx * CELL_SIZE + CELL_SIZE // 2,
            fy * CELL_SIZE + CELL_SIZE // 2,
        )
        pygame.draw.circle(self.screen, RED, food_center, CELL_SIZE // 2 - 2)

        # Draw snake
        # head
        draw_cell(self.screen, self.snake[0], BLUE)
        # body
        for segment in self.snake[1:]:
            draw_cell(self.screen, segment, GREEN)
            inner = pygame.Rect(
                segment[0] * CELL_SIZE + 3,
                segment[1] * CELL_SIZE + 3,
                CELL_SIZE - 6,
                CELL_SIZE - 6,
            )
            pygame.draw.rect(self.screen, DARK_GREEN, inner)

        # Draw score
        score_surf = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_surf, (10, 10))

        # Draw pause or game over
        if self.paused:
            pause_surf = self.large_font.render("PAUSED", True, YELLOW)
            rect = pause_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(pause_surf, rect)
        if self.game_over:
            over_surf = self.large_font.render("GAME OVER", True, RED)
            rect = over_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
            self.screen.blit(over_surf, rect)
            info_surf = self.font.render("Press R to restart or Q to quit", True, WHITE)
            info_rect = info_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
            self.screen.blit(info_surf, info_rect)

        pygame.display.flip()

    def terminate(self):
        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            self.handle_events()
            # control update rate relative to FPS and score (slightly faster as score increases)
            speed = FPS + self.score // 5
            self.update()
            self.draw()
            self.clock.tick(speed)


if __name__ == "__main__":
    game = SnakeGame()
    game.run()