import random

from enum import IntEnum
from pygame import Color
from neori import colors
from neori.utils import Vec2i

class Fruit(IntEnum):
    Apple = 5 # 50%
    Lemon = 3 # 30%
    Amora = 2 # 20%

Fruits  = [Fruit[k] for k in Fruit.__members__]
Weights = [float(fruit.value)/10 for fruit in Fruits]
Distrib = random.choices(Fruits, weights=Weights, k=10)

FruitColor = {
    Fruit.Apple: colors.APPLE,
    Fruit.Lemon: colors.LEMON,
    Fruit.Amora: colors.AMORA,
}

class Food:
    col   : int
    row   : int
    type  : Fruit
    color : Color

    def __init__(self, col: int, row: int, type: Fruit = None):
        self.type = random.choice(Distrib) if type == None else type
        self.row, self.col = row, col
        self.color = FruitColor[self.type]

    @property
    def pos(self) -> Vec2i:
        return (self.col, self.row)
