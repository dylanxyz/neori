import pygame

from math import inf
from typing import Tuple
from dataclasses import dataclass

Vec2i = Tuple[int, int]

def clamp(value, vmin=0, vmax=1):
    return max(vmin, min(vmax, value))

def hex(color: pygame.Color):
    return '#%02x%02x%02x' % (color.r, color.g, color.b)

@dataclass
class Timer:
    time    : float = 0.0
    paused  : bool  = False
    interval: float = inf

    def update(self, dt):
        if not self.paused:
            self.time += dt
            if self.time > self.interval:
                self.reset()

    def elapsed(self, seconds) -> bool:
        return self.time > seconds

    def reset(self):
        self.time = 0.0

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.pause()
        self.reset()
