import random
from pico2d import *

import game_framework
import game_world
import character_select

from floor import Floor
from meta_knight import Meta_knight
from king_DDD import King_DDD
from hammer_kriby import Hammer_Kirby


background = None
p1 = None
p2 = None
arrow_p1 = None
arrow_p2 = None


selected_p1 = []
selected_p2 = []

selected_p1_org = []
selected_p2_org = []

p1_win = 0
p2_win = 0
max_wins = 2
game_over = False

p1_hp = [100]
p2_hp = [100]

hp_bar = None

swap_count_p1 = 0
swap_count_p2 = 0

round_time = 60
timer = round_time


def draw_win_icon(x1, y1, win_count, icon_img):
    icon_size = 20
    spacing = 10

    for i in range(win_count):
        icon_x = x1 + i * (icon_size + spacing) + icon_size // 2
        icon_y = y1 + icon_size // 2
        icon_img.draw(icon_x, icon_y, icon_size, icon_size)

def draw_hp_bar(x, y, hp, img):
    block_size = 50
    max_blocks = 10
    filled_blocks = hp // 10

    for i in range(filled_blocks):
        bx = x + i * block_size
        img.draw(bx + 25, y + 25, block_size, block_size)


    draw_rectangle(x, y, x + block_size * max_blocks, y + block_size)



def set_selected_characters(p1_list, p2_list):
    global selected_p1, selected_p2, selected_p1_org, selected_p2_org
    selected_p1 = p1_list[:]
    selected_p2 = p2_list[:]

    selected_p1_org = p1_list[:]
    selected_p2_org = p2_list[:]


def create_character(name):
    if name == 'kirby':
        return Hammer_Kirby()
    elif name == 'ddd':
        return King_DDD()
    elif name == 'meta':
        return Meta_knight()
    else:
        return Hammer_Kirby()


def choice_character(char,p):
    global p1, p2, floor1, floor2,floor3,floor4,floor5
    game_world.clear_collision_group('attack:body')

    if p is p1:
        old = p1
        old_x, old_y, old_face = old.x, old.y, old.face
        # 기존 공격 박스가 있으면 제거
        if old.attack_box:
            game_world.remove_object(old.attack_box)
            old.attack_box = None
        # 기존 객체 제거 및 새 객체 추가
        game_world.remove_object(old)
        p1 = char
        p1.x, p1.y = old_x, old_y
        p1.face = old_face
        p1.hp = p1_hp
        p1.player = 'p1'
        game_world.add_object(p1, 1)

    elif p is p2:
        old = p2
        old_x, old_y, old_face = old.x, old.y, old.face
        if old.attack_box:
            game_world.remove_object(old.attack_box)
            old.attack_box = None
        game_world.remove_object(old)
        p2 = char
        p2.x, p2.y = old_x, old_y
        p2.face = old_face
        p2.hp = p2_hp
        p2.player = 'p2'
        game_world.add_object(p2, 1)

    p1.target=p2
    p2.target=p1

    if p1.attack_box is not None:
        game_world.add_collision_pair('attack:body', p1.attack_box, p2)
    if p2.attack_box is not None:
        game_world.add_collision_pair('attack:body', p2.attack_box, p1)


    game_world.add_collision_pair('attack:body', p1.attack_box, p2)
    game_world.add_collision_pair('attack:body', p2.attack_box, p1)

    game_world.add_collision_pair('body:floor', p1, floor1)
    game_world.add_collision_pair('body:floor', p1, floor2)
    game_world.add_collision_pair('body:floor', p1, floor3)
    game_world.add_collision_pair('body:floor', p1, floor4)
    game_world.add_collision_pair('body:floor', p1, floor5)

    game_world.add_collision_pair('body:floor', p2, floor1)
    game_world.add_collision_pair('body:floor', p2, floor2)
    game_world.add_collision_pair('body:floor', p2, floor3)
    game_world.add_collision_pair('body:floor', p2, floor4)
    game_world.add_collision_pair('body:floor', p2, floor5)



    char.frame = 0
    char.state_machine.cur_state = char.STAND

def reset_game():
    global selected_p1, selected_p2, selected_p1_org, selected_p2_org, p1_win, p2_win, game_over, swap_count_p1, swap_count_p2
    selected_p1 = []
    selected_p2 = []
    selected_p1_org = []
    selected_p2_org = []
    p1_win = 0
    p2_win = 0
    swap_count_p2 = 0
    swap_count_p1 = 0

    game_over = False
    character_select.p1_choices.clear()
    character_select.p2_choices.clear()
    game_world.clear()

def reset_round():
    global selected_p1, selected_p2, p1_win, p2_win, swap_count_p1, swap_count_p2, timer
    swap_count_p1 = 0
    swap_count_p2 = 0
    selected_p1 = selected_p1_org[:]
    selected_p2 = selected_p2_org[:]

    timer = round_time

    game_world.clear()
    init()

def final_round():
    global game_over
    if p1_win >= max_wins:
        print("P1 최종 승리!")
        game_over = True
    elif p2_win >= max_wins:
        print("P2 최종 승리!")
        game_over = True
    else:
        print("다음 라운드 시작!")
        game_over = False
        p1_hp[0] = 100
        p2_hp[0] = 100
        reset_round()

def handle_events():
    global p1,p2

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_SPACE and game_over:
            reset_game()
            game_framework.change_mode(character_select)
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

        if event.key in (SDLK_w,SDLK_a,SDLK_s,SDLK_d,SDLK_f,SDLK_g) and event.type in (SDL_KEYDOWN, SDL_KEYUP):
            p1.handle_event_p1(event)
        elif event.key in (SDLK_i, SDLK_j, SDLK_k, SDLK_l, SDLK_KP_7, SDLK_KP_8) and event.type in (SDL_KEYDOWN, SDL_KEYUP):
            p2.handle_event_p2(event)

def init():
    global p1, p2, floor1, floor2, background, hp_bar, selected_p1, selected_p2, timer,floor3, floor4, floor5, arrow_p1, arrow_p2

    background = load_image('Background.png')
    hp_bar = load_image('hp.png')
    arrow_p1 = load_image('p1.png')
    arrow_p2 = load_image('p2.png')
    bgm = load_music('bgm.mp3')
    bgm.set_volume(64)
    bgm.repeat_play()

    p1 = create_character(selected_p1[0])
    p2 = create_character(selected_p2[0])

    p1.x = 400
    p1.y = 250

    p2.x = 800
    p2.y = 250
    p2.face = -1

    game_world.add_object(p1,1)
    game_world.add_object(p2,1)

    p1.target=p2
    p2.target=p1

    timer = round_time

    game_world.add_collision_pair('attack:body', p1.attack_box, p2)
    game_world.add_collision_pair('attack:body', p2.attack_box, p1)

    floor1 = Floor(300, 130,300, 90)
    game_world.add_object(floor1,0)
    floor2 = Floor(900,130, 300,90)
    game_world.add_object(floor2,0)
    floor3 = Floor(100, 250, 300, 90)
    game_world.add_object(floor3, 0)
    floor4 = Floor(1100, 250, 300, 90)
    game_world.add_object(floor4, 0)
    floor5 = Floor(600, 260, 200, 90)
    game_world.add_object(floor5, 0)

    game_world.add_collision_pair('body:floor', p1, floor1)
    game_world.add_collision_pair('body:floor', p1, floor2)
    game_world.add_collision_pair('body:floor', p1, floor3)
    game_world.add_collision_pair('body:floor', p1, floor4)
    game_world.add_collision_pair('body:floor', p1, floor5)

    game_world.add_collision_pair('body:floor', p2, floor1)
    game_world.add_collision_pair('body:floor', p2, floor2)
    game_world.add_collision_pair('body:floor', p2, floor3)
    game_world.add_collision_pair('body:floor', p2, floor4)
    game_world.add_collision_pair('body:floor', p2, floor5)
p1_swap = False
p2_swap = False

def update():
    global p1, p2, selected_p1, selected_p2, game_over, p1_win, p2_win
    global p1_swap, p2_swap, swap_count_p1, swap_count_p2, timer
    if game_over:
        return


    timer -=game_framework.frame_time
    if timer <= 0:
        print("타임아웃!")
        if p1_hp[0] > p2_hp[0]:
            p1_win += 1
            print("P1 타임아웃 승리!")
            final_round()
            return
        elif p2_hp[0] > p1_hp[0]:
            p2_win += 1
            print("P2 타임아웃 승리!")
            final_round()
            return
        else:
            print("무승부 (타임아웃)")
            final_round()
            return



    p1.on_floor = False
    p2.on_floor = False
    if p1_hp[0] == 0 and p2_hp[0] == 0:
        print("무승부")
        final_round()
        return
    if p1_hp[0] <= 0:
        print("P1 모든 캐릭터 사망")
        p2_win += 1
        final_round()
        return
    if p2_hp[0] <= 0:
        print("P2 모든 캐릭터 사망")
        p1_win += 1
        final_round()
        return
    if p1.swap and not p1_swap:
        swap_count_p1 += 1
        if len(selected_p1) > 1 and swap_count_p1 <= 5:
            selected_p1.append(selected_p1[0])
            selected_p1.pop(0)
            next_char = create_character(selected_p1[0])
            choice_character(next_char, p1)
            p1.attack_box = None
            p1.swap = False
            p1.state_machine.change_state(p1.COUNTER)



    if p2.swap and not p2_swap:
        swap_count_p2 += 1
        if len(selected_p2) > 1 and swap_count_p2 <=5:
            selected_p2.append(selected_p2[0])
            selected_p2.pop(0)
            print(selected_p2)
            next_char = create_character(selected_p2[0])
            choice_character(next_char, p2)
            p2.attack_box = None
            p2.swap = False
            p2_swap = True
            p2.state_machine.change_state(p2.COUNTER)

    p1_swap = False
    p2_swap = False


    game_world.update()
    game_world.handle_collisions()



def draw():
    clear_canvas()
    background.draw(600, 300, 1200, 600)
    draw_hp_bar(50, 530, p1_hp[0], hp_bar)  # Player 1
    draw_hp_bar(650, 530, p2_hp[0], hp_bar)  # Player 2

    draw_win_icon(50, 510, p1_win, hp_bar)  # P1
    draw_win_icon(650, 510, p2_win, hp_bar)  # P2

    timer_font = load_font('ENCR10B.TTF', 60)
    timer_font.draw(570, 550, f"{int(timer)}", (255, 255, 0))

    if hasattr(p1, 'x') and hasattr(p1, 'y') :
        arrow_p1.draw(p1.x, p1.y + 80, 30, 30)
    if hasattr(p2, 'x') and hasattr(p2, 'y') :
        arrow_p2.draw(p2.x, p2.y + 80, 30, 30)

    game_world.render()
    update_canvas()


def finish():
    game_world.clear()

def pause(): pass
def resume(): pass

