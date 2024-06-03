import time
import math
import pygame

from pygame import Rect
from pygame.transform import scale
from pygame_gui import UIManager
from pygame_gui.elements import UIButton
from pygame_gui.elements import UIPanel
from pygame_gui.elements import UILabel
from pygame_gui.elements import UITextBox
from pygame_gui.elements import UIStatusBar
from pygame_gui.core import ObjectID as ID

from neori import colors
from neori.utils import hex, clamp

class GameMenu:
    is_open : bool
    container : UIPanel

    def __init__(self, id: str, manager: UIManager, width=300, height=0) -> None:
        self.is_open = True

        self.cursor = Rect(10, 10, width-20, 60)
        self.menu_rect = Rect(0, 0, width, height)
        self.container = UIPanel(manager=manager,
            relative_rect=self.menu_rect,
            object_id=ID(f'{id}.panel', '@menu-panel'),
            anchors={'center':'center'})

    def add_button(self, manager: UIManager, id: str, text: str, **kw):
        button = UIButton(
            text=text,
            manager=manager,
            relative_rect=self.cursor,
            container=self.container,
            object_id=ID(id, '@menu-button'),
            anchors={'centerx': 'centerx'},
            **kw)

        self.cursor.top += 64
        button.normal_image=scale(button.normal_image, (280, 60))
        button.hovered_image=scale(button.hovered_image, (280, 60))
        button.selected_image=scale(button.selected_image, (280, 60))
        button.rebuild()

        return button

    def close(self):
        self.is_open = False
        self.container.hide()

    def open(self):
        self.is_open = True
        self.container.show()

    def toggle(self):
        if self.is_open:
            self.container.hide()
        else:
            self.container.show()

        self.is_open = not self.is_open

class MainMenu(GameMenu):
    play : UIButton
    help : UIButton
    quit : UIButton

    def __init__(self, manager: UIManager) -> None:
        super().__init__('#main-menu', manager, height=210)
        self.play = self.add_button(manager, '#main-menu.play', 'JOGAR')
        self.help = self.add_button(manager, '#main-menu.help', 'TUTORIAL')
        self.quit = self.add_button(manager, '#main-menu.quit', 'SAIR')

class PauseMenu(GameMenu):
    play : UIButton
    help : UIButton
    menu : UIButton
    quit : UIButton

    def __init__(self, manager: UIManager) -> None:
        super().__init__('#pause-menu', manager, height=280)
        self.play = self.add_button(manager, '#pause-menu.play', 'CONTINUAR')
        self.help = self.add_button(manager, '#pause-menu.help', 'TUTORIAL')
        self.menu = self.add_button(manager, '#pause-menu.menu', 'MENU')
        self.quit = self.add_button(manager, '#pause-menu.quit', 'SAIR')

class GameOverScreen:
    panel       : UIPanel
    title       : UILabel
    info        : UILabel
    size        : UILabel
    score       : UILabel
    time        : UILabel
    time_label  : UILabel
    size_label  : UILabel
    score_label : UILabel
    cursor      : Rect

    def __init__(self, manager: UIManager) -> None:
        self.cursor = Rect(20, 50, -1, -1)

        self.panel = UIPanel(
            manager=manager,
            visible=False,
            relative_rect=Rect(10, 60, 400, 200),
            anchors={'centerx':'centerx'},
            object_id=ID('#gameover.panel'))

        self.panel.background_image=scale(self.panel.background_image, (400, 200))
        self.panel.rebuild()

        self.title = UILabel(
            text='Fim de jogo!',
            manager=manager,
            relative_rect=Rect(20, 10, -1, -1),
            container=self.panel,
            # anchors={'centerx':'centerx'},
            object_id=ID('#gameover.title', '@text'))

        self.info = self.add_left_label(manager, 'info', '')
        self.cursor.top += 35

        self.score_label = self.add_left_label(manager, 'score-label', 'Pontuação')
        self.score = self.add_right_label(manager, 'score', '0')
        self.cursor.top += 35

        self.size_label = self.add_left_label(manager, 'size-label', 'Tamanho')
        self.size = self.add_right_label(manager, 'size', '1')
        self.cursor.top += 35

        self.time_label = self.add_left_label(manager, 'time-label', 'Tempo')
        self.time = self.add_right_label(manager, 'time', '00:00')
        self.cursor.top += 35

    def add_left_label(self, manager, id, text):
        self.cursor.left = 20
        self.cursor.width = -1
        label = UILabel(
            text=text,
            manager=manager,
            relative_rect=self.cursor,
            container=self.panel,
            object_id=ID(f'#gameover.{id}', '@text'))
        return label

    def add_right_label(self, manager, id, text):
        self.cursor.width = 80
        self.cursor.right = -20
        label = UILabel(
            text=text,
            manager=manager,
            relative_rect=self.cursor,
            container=self.panel,
            anchors={'right':'right'},
            object_id=ID(f'#gameover.{id}', '@text'))
        return label

    def set_state(self, state, elapsed):
        time_label = time.strftime('%M:%S', time.gmtime(elapsed))

        self.info.set_text(state.info)
        self.score.set_text(str(state.score))
        self.size.set_text(str(len(state.snake.body)))
        self.time.set_text(time_label)

    def show(self):
        self.panel.show()

    def hide(self):
        self.panel.hide()

class GameInterface:
    panel  : UIPanel
    score  : UILabel
    charge : UILabel
    effect : UIStatusBar

    def __init__(self, manager: UIManager) -> None:
        rect = manager.get_root_container().get_rect()

        self.panel = UIPanel(
            manager=manager,
            relative_rect=Rect(0, 0, rect.width, 40),
            visible=False,
            object_id=ID("#top-bar"))

        self.score = UILabel(
            text='0',
            manager=manager,
            container=self.panel,
            relative_rect=Rect(16, 5, -1, -1),
            object_id=ID("#score", "@text"))

        self.effect = UIStatusBar(
            manager=manager,
            relative_rect=Rect(60, 15, 120, 8),
            container=self.panel,
            object_id=ID("#effect-bar"))

        self.charge = UILabel(
            text='',
            manager=manager,
            container=self.panel,
            relative_rect=Rect(210, 5, -1, -1),
            object_id=ID("#charge", "@text"))

    def update(self, game):
        self.score.set_text(str(game.state.score))

        percent = 0
        if game.state.is_frozen:
            percent = 1 - clamp(game.events.frozen.time/6)

        self.effect.percent_full = percent

        charge = math.floor(game.state.charge)
        self.charge.set_text('0 ' * clamp(charge, 0, 3))


TUTORIAL = '''
Use as {key}setas{end} do teclado para se movimentar.
Use {key}ESC{end} pausar/despausar.

Impeça que a infecção se propague comendo as células {inf}.

Você pode acumular até 3 {cargas}.
Pressione {key}ESPAÇO{end} para usar uma carga,
invocando células {imunes} na sua posição.

Depois de {tempo}5 segundos{end} as células {imunes} se tornarão células saudáveis.

A cada {tempo}10 segundos{end} as frutas irão respawnar.

Coma uma {apple} para crescer de tamanho.

Coma um {lemon} para gerar células imunes.

Coma uma {amora} para parar parar o tempo por {tempo}6 segundos{end}.'''.format(
    end    = '</font>',
    key    = '<font color="#22c55e">',
    tempo  = f'<font color="#6366f1">',
    inf    = f'<font color="{hex(colors.INFECTED)}">infectadas</font>',
    cargas = f'<font color="{hex(colors.LEMON)}">cargas</font>',
    imunes = f'<font color="{hex(colors.LEMON)}">imunes</font>',
    apple  = f'<font color="{hex(colors.APPLE)}">maçã</font>',
    lemon  = f'<font color="{hex(colors.LEMON)}">limão</font>',
    amora  = f'<font color="{hex(colors.AMORA)}">amora</font>',
)

TUTORIAL = f'<font face="silkscreen" pixel_size="14">{TUTORIAL.strip()}</font>'

class GuidInterface:
    panel   : UIPanel
    title   : UILabel
    textbox : UITextBox
    close   : UIButton

    def __init__(self, manager: UIManager) -> None:
        self.panel = UIPanel(
            manager=manager,
            relative_rect=Rect(0, 0, 520, 600),
            visible=False,
            anchors={'center':'center'},
            object_id=ID("#guide-panel"))

        self.title = UILabel(
            text='Tutorial',
            manager=manager,
            container=self.panel,
            relative_rect=Rect(16, 10, -1, -1),
            object_id=ID("#guide-title", "@text"))

        self.textbox = UITextBox(
            html_text=TUTORIAL,
            manager=manager,
            relative_rect=Rect(0, 50, 520, 580),
            container=self.panel,
            object_id=ID("#guide-text"))

        rect = Rect(0, 0, 26, 26)
        rect.topright = (-5, 5)
        self.close = UIButton(
            text='X',
            manager=manager,
            relative_rect=rect,
            container=self.panel,
            anchors={'top': 'top', 'right': 'right'},
            object_id=ID('#guide-close'))

        self.panel.change_layer(3)
        self.textbox.change_layer(4)
        self.close.change_layer(5)
        self.title.change_layer(6)
        self.panel.rebuild()
