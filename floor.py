from pico2d import *

class Floor:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.image = load_image('grass.png')

        self.w, self.h = self.image.w, self.image.h-15


    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x, self.y)
        self.draw_bb()

    def get_bb(self):
        return self.x - self.w // 2, self.y - self.h // 2, self.x + self.w // 2, self.y + self.h // 2

    def draw_bb(self):
        draw_rectangle(*self.get_bb())

    def handle_collision(self, group, other):
        pass