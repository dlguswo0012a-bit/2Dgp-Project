import random
from pico2d import *

import game_framework
import game_world

from floor import Floor
from meta_knight import Meta_knight
from king_DDD import King_DDD
from hammer_kriby import Hammer_Kirby



p1 = None
p2 = None




def choice_character(char,p):
    global p1, p2

    if p == p1:
        x,y = p1.x, p1.y
        game_world.remove_object(p1)
        p1 = char
        p1.x, p1.y = x,y
        game_world.add_object(p1,1)
    if p == p2:
        x,y = p2.x, p2.y
        face = p2.face
        game_world.remove_object(p2)
        p2 = char
        p2.x, p2.y = x,y
        p2.face = face
        game_world.add_object(p2,1)

    p1.target=p2
    p2.target=p1

    game_world.add_collision_pair('attack:body', p1.attack_box, p2)
    game_world.add_collision_pair('attack:body', p2.attack_box, p1)

    game_world.add_collision_pair('body:floor', p1, floor1)
    game_world.add_collision_pair('body:floor', p1, floor2)
    game_world.add_collision_pair('body:floor', p2, floor1)
    game_world.add_collision_pair('body:floor', p2, floor2)




def handle_events():
    global p1,p2

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.key == SDLK_1 and event.type == SDL_KEYDOWN:
            choice_character(Meta_knight(),p1)
            print("p1 : meta knight")
        elif event.key == SDLK_2 and event.type == SDL_KEYDOWN:
            choice_character(King_DDD(),p1)
            print("p1 : king DDD")
        elif event.key == SDLK_3 and event.type == SDL_KEYDOWN:
            choice_character(Hammer_Kirby(),p1)
            print("p1 : hammer kriby")

        elif event.key == SDLK_z and event.type == SDL_KEYDOWN:
            choice_character(Meta_knight(),p2)
            print("p2 : meta knight")
        elif event.key == SDLK_x and event.type == SDL_KEYDOWN:
            choice_character(King_DDD(),p2)
            print("p2 : king DDD")
        elif event.key == SDLK_c and event.type == SDL_KEYDOWN:
            choice_character(Hammer_Kirby(),p2)
            print("p2 : hammer kriby")

        if event.key in (SDLK_w,SDLK_a,SDLK_s,SDLK_d,SDLK_e,SDLK_q) and event.type in (SDL_KEYDOWN, SDL_KEYUP):
            p1.handle_event_p1(event)
        elif event.key in (SDLK_i, SDLK_j, SDLK_k, SDLK_l, SDLK_u, SDLK_o) and event.type in (SDL_KEYDOWN, SDL_KEYUP):
            p2.handle_event_p2(event)

def init():
    global p1, p2, floor1, floor2

    p1 = Hammer_Kirby()
    p2 = Meta_knight()

    p1.x = 400
    p1.y = 150

    p2.x = 1200
    p2.y = 300
    p2.face = -1

    game_world.add_object(p1,1)
    game_world.add_object(p2,1)

    p1.target=p2
    p2.target=p1

    game_world.add_collision_pair('attack:body', p1.attack_box, p2)
    game_world.add_collision_pair('attack:body', p2.attack_box, p1)

    floor1 = Floor(400,30)
    game_world.add_object(floor1,0)
    floor2 = Floor(1200,200)
    game_world.add_object(floor2,0)

    game_world.add_collision_pair('body:floor', p1, floor1)
    game_world.add_collision_pair('body:floor', p1, floor2)

    game_world.add_collision_pair('body:floor', p2, floor1)
    game_world.add_collision_pair('body:floor', p2, floor2)
def update():
    global p1, p2

    p1.on_floor = False
    p2.on_floor = False

    game_world.update()
    game_world.handle_collisions()



def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def finish():
    game_world.clear()

def pause(): pass
def resume(): pass

