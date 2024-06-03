import random
import numpy as np

from enum import IntEnum
from neori.utils import Vec2i, clamp

class Cell(IntEnum):
    Dead = 0
    Healthy = 1
    Infected = 2
    Immune = 3
    SpawnInfected = 4
    SpawnImmune = 5

class WorldGrid:
    res  : int
    cols : int
    rows : int
    curr : np.ndarray
    next : np.ndarray

    @property
    def size(self) -> Vec2i:
        return self.cols, self.rows

    @property
    def iterator(self):
        return np.ndenumerate(self.curr)

    @property
    def infections(self) -> int:
        return self.cell_count[Cell.Infected.value]

    @property
    def cell_count(self):
        return np.bincount(self.curr.flatten(), minlength=6)

    def __init__(self, width, height, res) -> None:
        self.res  = res
        self.cols = width // self.res
        self.rows = height // self.res
        self.curr = np.random.randint(2, size=self.size)
        self.next = np.zeros((self.cols, self.rows), dtype=np.int64)

    def update_at(self, i: int, j: int):
        cell = self.curr[i, j]
        cells = self.curr[max(0, i-1) : i+2, max(0, j-1) : j+2].flatten()
        mutation = Cell.Healthy
        count = np.bincount(cells, minlength=6)

        # quantas celulas de cada tipo
        healthy = count[Cell.Healthy]
        immune = count[Cell.Immune]
        infected = count[Cell.Infected]
        neighbors = np.count_nonzero(cells) - clamp(cell)

        neighbors -= count[Cell.SpawnImmune]
        neighbors -= count[Cell.SpawnInfected]

        # infecta a célula se ela estiver próxima à uma célula infectada
        if infected > 0:
            mutation = Cell.Infected

        if immune > 0 and healthy == 0:
            mutation = Cell.Immune

        if cell == Cell.SpawnImmune:
            pass

        elif cell == Cell.SpawnInfected and infected > 0:
            self.next[i, j] = mutation

        # se a célula estiver morta e tiver mais de 3 células
        # vizinhas viva ela renascerá com a mutação adequada
        elif cell == Cell.Dead and neighbors == 3:
            self.next[i, j] = mutation

        # se a célula estiver viva e tiver menos de 2 ou mais de 3
        # células vizinhas vivas ela morrerá
        elif cell > 0 and (neighbors < 2 or neighbors > 3):
            self.next[i, j] = Cell.Dead

        # caso contrário, a célula continuará como está
        else:
            self.next[i, j] = self.curr[i, j]

    def update(self):
        self.curr = self.next.copy()

    def rand_cell(self) -> Vec2i:
        i = random.randint(0, self.cols-1)
        j = random.randint(0, self.rows-1)
        return i, j

    def set_cell(self, i: int, j: int, kind: Cell):
            self.curr[i, j] = kind
            self.next[i, j] = kind

    def set_square_region(self, i: int, j: int, kind: Cell, size=2):
        for n in self.slice_col(i, size):
            for m in self.slice_row(j, size):
                self.set_cell(n, m, kind)

    def set_circular_region(self, i: int, j: int, kind: Cell, size=2):
        r = size*size
        for n in self.slice_col(i, size):
            di = n - i
            for m in self.slice_row(j, size):
                dj = m - j
                if di*di + dj*dj <= r:
                    self.set_cell(n, m, kind)

    def set_circular_ring(self, i: int, j: int, kind: Cell, size=2, th=1):
        r, k = size**2, (size-th)**2
        for n in self.slice_col(i, size):
            di = n - i
            for m in self.slice_row(j, size):
                dj = m - j
                if k <= di*di + dj*dj <= r:
                    self.set_cell(n, m, kind)

    def slice_row(self, i: int, size: int = 2):
        return range(max(0, i-size), min(i+size+1, self.rows))

    def slice_col(self, j: int, size: int = 2):
        return range(max(0, j-size), min(j+size+1, self.cols))

    def infect(self, i = -1, j = -1):
        i = i if i > -1 else random.randint(4, self.cols-3)
        j = j if j > -1 else random.randint(4, self.rows-3)
        self.set_circular_ring(i, j, Cell.Infected, size=8, th=2)
