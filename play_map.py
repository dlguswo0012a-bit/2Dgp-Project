from pico2d import *
import game_world
import play_mode
import random
from floor import Floor

class PlayMap:
    def __init__(self):
        self.background = load_image('Background.png')
        self.floor1 = Floor(300, 130,300, 90)
        game_world.add_object(self.floor1,0)
        self.floor2 = Floor(900,130, 300,90)
        game_world.add_object(self.floor2,0)
        self.floor3 = Floor(100, 250, 300, 90)
        game_world.add_object(self.floor3, 0)
        self.floor4 = Floor(1100, 250, 300, 90)
        game_world.add_object(self.floor4, 0)
        self.floor5 = Floor(600, 260, 200, 90)
        game_world.add_object(self.floor5, 0)



    def handle_collision(self, p1, p2):
        game_world.clear_collision_group('body:floor')

        game_world.add_collision_pair('body:floor', p1, self.floor1)
        game_world.add_collision_pair('body:floor', p1, self.floor2)
        game_world.add_collision_pair('body:floor', p1, self.floor3)
        game_world.add_collision_pair('body:floor', p1, self.floor4)
        game_world.add_collision_pair('body:floor', p1, self.floor5)

        game_world.add_collision_pair('body:floor', p2, self.floor1)
        game_world.add_collision_pair('body:floor', p2, self.floor2)
        game_world.add_collision_pair('body:floor', p2, self.floor3)
        game_world.add_collision_pair('body:floor', p2, self.floor4)
        game_world.add_collision_pair('body:floor', p2, self.floor5)
    def update(self):
        pass

    def draw(self):
        self.background.draw(600, 300, 1200, 600)
