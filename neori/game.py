import os
import math
import random
import pygame
import pygame_gui as gui

from pygame_gui import UIManager

from typing import List
from pygame import Surface, Rect, Color
from pygame.time import Clock

from neori import colors
from neori.food import Food, Fruit
from neori.snake import Snake
from neori.utils import Vec2i, clamp
from neori.utils import Timer
from neori.world import Cell
from neori.world import WorldGrid
from neori.interface import GameInterface, GuidInterface, MainMenu
from neori.interface import PauseMenu
from neori.interface import GameOverScreen

DIRNAME = os.path.dirname(os.path.realpath(__file__))
RESOURCES = os.path.join(DIRNAME, "resources")
THEME_FILE = os.path.join(RESOURCES, "theme.json")

class GameState:
    snake      : Snake
    world      : WorldGrid
    score      : int
    foods      : List[Food]
    infections : int
    is_paused  : bool
    is_running : bool
    is_frozen  : bool
    game_over  : bool
    charge     : float
    explosion  : Vec2i
    spawns     : List[Vec2i]
    info       : str

    def __init__(self, width, height, res) -> None:
        self.world = WorldGrid(width, height, res)
        self.snake = Snake(*self.world.rand_cell())
        self.score = 0
        self.foods = []
        self.charge = 0.0
        self.infections = 0
        self.is_frozen = False
        self.is_paused = False
        self.is_running = True
        self.game_over = False
        self.explosion = None
        self.info = ''
        self.spawns = []

class GameEvents:
    food     : Timer = Timer()
    flames   : Timer = Timer()
    infection: Timer = Timer()
    frozen   : Timer = Timer()


class NeoriGame:
    state      : GameState
    events     : GameEvents
    clock      : Clock
    timer      : Timer
    screen     : Surface
    canvas     : Surface
    screen_bg  : Surface
    frametime  : float
    # interface
    ui_manager : UIManager
    interface  : GameInterface
    main_menu  : MainMenu
    pause_menu : PauseMenu
    ui_gameover: GameOverScreen
    guide_ui   : GuidInterface

    framerate   = 15
    resolution  = 15
    screen_size = (1280, 720)
    canvas_size = (1280, 680)

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Neori")

        self.timer = Timer()
        self.clock = Clock()
        self.screen = pygame.display.set_mode(self.screen_size)
        self.screen_bg = Surface(self.screen.get_size())
        self.events = GameEvents()
        self.state = GameState(*self.canvas_size, 15)
        self.ui_manager = UIManager(self.screen.get_size(), THEME_FILE, enable_live_theme_updates=False)

        self.ui_manager.add_font_paths('silkscreen',
            bold_path=os.path.join(RESOURCES, 'fonts/Silkscreen-Bold.ttf'),
            regular_path=os.path.join(RESOURCES, 'fonts/Silkscreen-Regular.ttf'))

        self.ui_manager.preload_fonts([
            {'name': 'silkscreen', 'point_size': 24, 'style': 'regular', 'antialiased': '1'},
            {'name': 'silkscreen', 'point_size': 14, 'style': 'regular', 'antialiased': '1'},
        ])

        self.main_menu = MainMenu(self.ui_manager)
        self.pause_menu = PauseMenu(self.ui_manager)
        self.ui_gameover = GameOverScreen(self.ui_manager)
        self.interface = GameInterface(self.ui_manager)
        self.pause_menu.close()

        self.screen_bg.fill(colors.BLACK)
        self.goto_main_menu()
        self.guide_ui = GuidInterface(self.ui_manager)

    def loop(self):
        while self.state.is_running:
            self.frametime = self.clock.tick(self.framerate)/1000.0

            if not self.state.is_paused:
                self.timer.update(self.frametime)

            self.poll_events()
            self.screen.blit(self.screen_bg, (0, 0))

            self.update()
            self.draw()

            self.ui_manager.update(self.frametime)
            self.ui_manager.draw_ui(self.screen)

            # top border
            if not self.main_menu.is_open:
                width = self.screen.get_width()
                pygame.draw.rect(self.screen, colors.CELL, Rect(0, 40-2, width, 2))

            pygame.display.update()

    def quit(self):
        self.state.is_running = False

    def goto_main_menu(self):
        self.timer.reset()
        self.main_menu.open()
        self.screen_bg.fill(pygame.Color("#121212"))
        self.canvas = self.screen.subsurface(self.screen.get_rect())
        self.state = GameState(*self.canvas.get_size(), 16)
        self.interface.panel.hide()
        self.ui_gameover.hide()
        self.pause_menu.close()

    def start_game(self):
        self.timer.reset()
        self.ui_gameover.hide()
        self.main_menu.close()
        self.pause_menu.close()
        self.interface.panel.show()
        self.canvas = self.screen.subsurface(Rect(0, 40, *self.canvas_size))
        self.state = GameState(*self.canvas_size, self.resolution)
        self.screen_bg.fill(pygame.Color('#080808'))

    def poll_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                self.on_keydown(event)
            if event.type == gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.main_menu.play:
                    self.start_game()
                elif event.ui_element == self.main_menu.quit:
                    self.quit()
                elif event.ui_element == self.pause_menu.quit:
                    self.quit()
                elif event.ui_element == self.pause_menu.play:
                    self.state.is_paused = False
                    self.pause_menu.toggle()
                    if self.state.game_over:
                        self.start_game()
                elif event.ui_element == self.pause_menu.menu:
                    self.state.is_paused = False
                    self.pause_menu.close()
                    self.goto_main_menu()
                elif event.ui_element == self.pause_menu.help:
                    self.guide_ui.panel.show()
                elif event.ui_element == self.main_menu.help:
                    self.guide_ui.panel.show()
                elif event.ui_element == self.guide_ui.close:
                    self.guide_ui.panel.hide()

            self.ui_manager.process_events(event)

    def on_keydown(self, event):
        new_dir = None

        if event.key == pygame.K_LEFT:
            new_dir = (-1, 0)
        if event.key == pygame.K_RIGHT:
            new_dir = (1, 0)
        if event.key == pygame.K_UP:
            new_dir = (0, -1)
        if event.key == pygame.K_DOWN:
            new_dir = (0, 1)
        if event.key == pygame.K_ESCAPE:
            self.state.is_paused = not self.state.is_paused
            if not self.main_menu.is_open:
                self.pause_menu.toggle()
            if not self.state.game_over:
                self.pause_menu.container.set_relative_position((0, -60))

        if event.key == pygame.K_SPACE:
            self.drop_charge()

        if not new_dir == None:
            self.state.snake.change_dir(new_dir)

    def draw(self):
        self.draw_world()
        self.draw_snake()

    def draw_rect(self, i: int, j: int, color: Color):
        r = self.state.world.res
        pygame.draw.rect(self.canvas, color, Rect(i*r, j*r, r, r))

    def draw_world(self):
        for (i, j), cell in self.state.world.iterator:
            if cell == Cell.Healthy:
                self.draw_rect(i, j, colors.CELL)
            elif cell == Cell.Infected:
                self.draw_rect(i, j, colors.INFECTED)
            elif cell == Cell.Immune:
                self.draw_rect(i, j, colors.IMMUNE)
            elif cell == Cell.SpawnInfected:
                self.draw_rect(i, j, colors.SPAWN)
            elif cell == Cell.SpawnImmune:
                self.draw_rect(i, j, colors.IMMUNE)

        for food in self.state.foods:
            self.draw_rect(*food.pos, food.color)

    def draw_snake(self):
        if self.main_menu.is_open:
            return

        snake = self.state.snake
        for part in snake.body:
            self.draw_rect(*part, colors.SNAKE)

    def update(self):
        # check game over
        if self.state.game_over:
            if not self.ui_gameover.panel.visible:
                self.pause_menu.container.set_relative_position((0, 60))
                self.pause_menu.open()
                self.ui_gameover.set_state(self.state, self.timer.time)
                self.ui_gameover.show()

            return
        # check paused
        if self.state.is_paused:
            return

        self.interface.update(self)
        self.events.frozen.update(self.frametime)
        if not self.state.is_frozen:
            self.events.food.update(self.frametime)
            self.events.flames.update(self.frametime)
            self.events.infection.update(self.frametime)

        if not self.main_menu.is_open:
            self.update_snake()
            self.update_foods()

        if not self.state.is_frozen:
            self.update_world()
        elif self.events.frozen.elapsed(6):
            self.state.is_frozen = False
            self.events.frozen.stop()

    def update_world(self):
        events = self.events
        world  = self.state.world
        spawns = self.state.spawns

        for (i, j), cell in world.iterator:
            if cell == Cell.SpawnImmune and events.flames.elapsed(0.2):
                world.set_cell(i, j, Cell.Immune)
            if cell == Cell.Immune and events.flames.elapsed(5):
                world.set_cell(i, j, Cell.Healthy)
            elif cell == Cell.SpawnInfected and events.infection.elapsed(9):
                world.set_cell(i, j, Cell.Infected)
            else:
                world.update_at(i, j)

        world.update()

        # update infection
        cell_count = world.cell_count
        infections = cell_count[Cell.Infected]
        healthy = cell_count[Cell.Healthy]
        immune = cell_count[Cell.Immune]
        non_infected = healthy + immune

        if infections == 0 and self.state.infections > 0:
            self.state.score += 10

        # todas as células estão infectadas
        if infections > 0 and non_infected == 0 and not self.main_menu.is_open:
            self.state.game_over = True
            self.state.info = 'A infecção venceu!'
        if self.main_menu.is_open and healthy < 12 and self.events.flames.elapsed(5):
            self.events.flames.reset()
            world.set_circular_ring(*world.rand_cell(), Cell.SpawnImmune, size=8, th=2)

        if infections - self.state.infections < 10:
            events.infection.resume()
        elif not events.infection.elapsed(1):
            events.infection.stop()
            self.state.spawns.clear()

        # infection spawn
        if events.infection.elapsed(5):
            if len(spawns) == 0:
                for _ in range(random.randint(1, 3)):
                    spawns.append(self.state.world.rand_cell())
            else:
                percent = (events.infection.time-5) / 4
                radius  = 1 + math.floor(percent * 8)
                for spawn in spawns:
                    self.state.world.set_circular_ring(*spawn, Cell.SpawnInfected, radius, th=1)

        if events.infection.elapsed(9):
            events.infection.reset()
            spawns.clear()

        self.state.infections = infections

    def update_snake(self):
        snake = self.state.snake
        world = self.state.world
        cell = self.state.world.curr[*snake.head]
        snake.update()

        if cell == Cell.Infected:
            if self.state.is_frozen:
                self.state.charge += 0.20
                self.state.score  += 2
                world.set_cell(*snake.head, Cell.Dead)
            else:
                self.state.charge += 0.10
                self.state.score  += 1
                world.set_square_region(*snake.head, Cell.Dead, size=2)

        i, j = snake.head
        if not (0 <= i < world.cols) or not (0 <= j < world.rows):
            self.state.game_over = True
            self.state.info = 'Tentou sair do mapa'

        if snake.dir != (0, 0):
            for part in snake.body[0:-1]:
                if world.curr[*part] == Cell.Infected:
                    world.set_cell(*part, Cell.Dead)

                if snake.head == part:
                    self.state.game_over = True
                    self.state.info = 'Tentou se comer'

        self.state.charge = clamp(self.state.charge, 0, 3)

    def update_foods(self):
        world = self.state.world
        snake = self.state.snake
        foods = self.state.foods
        food_event = self.events.food

        if food_event.elapsed(10):
            foods.clear()
            food_event.reset()

        if len(foods) == 0 and food_event.elapsed(1):
            foods.append(Food(*world.rand_cell(), type=Fruit.Apple))

            if random.choice((0, 1)) == 0:
                foods.append(Food(*world.rand_cell()))
            if random.choice((0, 1)) == 0:
                foods.append(Food(*world.rand_cell()))

            food_event.reset()

        for i, food in enumerate(foods):
            if world.curr[*food.pos] == Cell.Infected:
                foods.pop(i)

            if snake.head == food.pos:
                foods.pop(i)
                if food.type == Fruit.Apple:
                    snake.grow()
                    self.state.score += 4
                    self.state.charge += 0.15
                elif food.type == Fruit.Lemon:
                    snake.grow()
                    self.state.score += 2
                    self.state.charge += 0.25
                    self.state.world.set_circular_region(*food.pos, Cell.SpawnImmune, 6)
                    self.events.flames.reset()
                elif food.type == Fruit.Amora:
                    self.state.score += 2
                    self.state.is_frozen = True
                    self.events.frozen.reset()
                    self.events.frozen.resume()

    def drop_charge(self):
        if self.state.charge >= 1:
            strength = 8

            if self.state.charge >= 3:
                self.state.charge = 0.0
                strength += 4
            else:
                self.state.charge -= 1

            self.state.world.set_circular_region(*self.state.snake.head, Cell.SpawnImmune, strength)
            self.events.flames.reset()
