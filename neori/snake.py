from typing import List
from neori.utils import Vec2i

class Snake:
    dir  : Vec2i
    body : List[Vec2i]

    def __init__(self, x: int, y: int):
        self.dir = (0, 0)
        self.body = [(x, y)]
        self.grow()
        self.grow()
        self.grow()
        self.grow()

    @property
    def head(self):
        return self.body[-1]

    def update(self):
        head = self.head
        self.body.pop(0)
        self.body.append((head[0] + self.dir[0], head[1] + self.dir[1]))

    def grow(self):
        self.body.append(self.head)

    def drop(self):
        return self.body.pop(0)

    def collides(self, cell: Vec2i):
        return cell in self.body

    def change_dir(self, new_dir: Vec2i):
        dx, dy = self.dir
        if new_dir != (-dx, -dy):
            self.dir = new_dir
