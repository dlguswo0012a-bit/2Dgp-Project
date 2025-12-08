from pico2d import *

class Floor:
    def __init__(self, x, y, width, height):
        self.x, self.y = x, y
        self.w=width
        self.image = load_image('grass.png')


        self.h = self.image.h-15


    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x, self.y,self.w, self.h)
        self.draw_bb()

    def get_bb(self):
        return self.x - self.w // 2, self.y - self.h // 2, self.x + self.w // 2, self.y + self.h // 2 -10

    def draw_bb(self):
        #draw_rectangle(*self.get_bb())
        pass

    def handle_collision(self, group, other):
        pass