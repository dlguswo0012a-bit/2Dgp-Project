from pico2d import *
import game_framework
import game_world
import play_mode
from state_machine import StateMachine

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
GRAVITY = 9.8 * 2
import time

# ===== 입력 이벤트 =====
def d_down(e): return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d
def d_up(e):   return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYUP and e[1].key == SDLK_d
def a_down(e): return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def a_up(e):   return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a
def e_down(e): return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_e
def w_down(e): return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_w
def w_up(e):   return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYUP and e[1].key == SDLK_w
def q_down(e): return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_q
def q_up(e):   return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYUP and e[1].key == SDLK_q


def l_down(e): return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_l
def l_up(e):   return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYUP and e[1].key == SDLK_l
def j_down(e): return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_j
def j_up(e):   return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYUP and e[1].key == SDLK_j
def u_down(e): return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_u
def i_down(e): return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_i
def i_up(e):   return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYUP and e[1].key == SDLK_i
def o_down(e): return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_o
def o_up(e):   return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYUP and e[1].key == SDLK_o

# ====================== 상태들 ============================
class Stand:
    def __init__(self, D): self.D = D
    def enter(self, e): self.D.dir = 0
    def exit(self, e): pass
    def do(self):
        frames = self.D.frames['stand']
        n = len(frames)
        self.D.frame = (self.D.frame + n * ACTION_PER_TIME * game_framework.frame_time) % n
    def draw(self):
        img, x, y, w, h = self.D.get_current_frame('stand')
        self.D.draw_frame(img, x, y, w, h)



class Walk:
    def __init__(self, D): self.D = D
    def enter(self, e):
        player = e[0]
        if player == 'INPUT_P1':
            if d_down(e) or a_up(e):
                self.D.dir = 1
                self.D.face = 1
            elif a_down(e) or d_up(e):
                self.D.dir = -1
                self.D.face = -1
        elif player == 'INPUT_P2':
            if l_down(e) or j_up(e):
                self.D.dir = 1
                self.D.face = 1
            elif j_down(e) or l_up(e):
                self.D.dir = -1
                self.D.face = -1
    def exit(self, e): pass
    def do(self):
        frames = self.D.frames['walk']
        n = len(frames)
        self.D.frame = (self.D.frame + n * ACTION_PER_TIME * game_framework.frame_time) % n
        self.D.x += self.D.dir * 200 * game_framework.frame_time
    def draw(self):
        img, x, y, w, h = self.D.get_current_frame('walk')
        self.D.draw_frame(img, x, y, w, h)


class Attack:
    def __init__(self, D):
        self.D = D
        self.attack_spawn = False
    def enter(self, e):
        self.D.frame = 0
        self.attack_spawn = False
        if self.D.attack_box:
            game_world.remove_object(self.D.attack_box)
            self.D.attack_box = None
    def exit(self, e):
        if self.D.attack_box:
            game_world.remove_object(self.D.attack_box)
            self.D.attack_box = None
        self.attack_spawn = False
    def do(self):
        frames = self.D.frames['attack']
        n = len(frames)
        self.D.frame += n * ACTION_PER_TIME * game_framework.frame_time
        idx = int(self.D.frame)
        if idx == 3 and not self.attack_spawn:
            self.attack_spawn = True
            if self.D.attack_box is None:
                self.D.spawn_attack_box(damage = 20)
        if self.D.frame >= n:
            self.D.state_machine.handle_state_event(('ATTACK_DONE', None))
    def draw(self):
        img, x, y, w, h = self.D.get_current_frame('attack')
        self.D.draw_frame(img, x, y, w, h)


class Hit:
    def __init__(self, D): self.D = D
    def enter(self, e): self.D.frame = 0
    def exit(self, e): pass
    def do(self):
        frames = self.D.frames['hit']
        n = len(frames)
        self.D.frame += n * ACTION_PER_TIME * game_framework.frame_time
        if self.D.frame >= n:
            self.D.state_machine.handle_state_event(('HIT_DONE', None))
    def draw(self):
        img, x, y, w, h = self.D.get_current_frame('hit')
        self.D.draw_frame(img, x, y, w, h)

class Jump:
    def __init__(self, D):
        self.D = D
    def enter(self, e):
        player = e[0]
        if player == 'INPUT_P1':
            if d_down(e) or a_up(e):
                self.D.dir = 1
                self.D.face = 1
            elif a_down(e) or d_up(e):
                self.D.dir = -1
                self.D.face = -1
        elif player == 'INPUT_P2':
            if l_down(e) or j_up(e):
                self.D.dir = 1
                self.D.face = 1
            elif j_down(e) or l_up(e):
                self.D.dir = -1
                self.D.face = -1

        if self.D.on_floor:
            self.D.frame = 0
            self.D.yv = 70.0
            self.D.on_floor = False
            self.D.count_jump =1
            self.D.jump_delay = 0.1
    def exit(self, e): pass

    def do(self):
        self.D.y += self.D.yv * game_framework.frame_time *5.0
        self.D.yv -= GRAVITY * game_framework.frame_time*5.0

        if self.D.yv > 0.0:
            self.D.frame = 0
            self.D.x += self.D.dir * 150 * game_framework.frame_time
        elif not self.D.on_floor:
            self.D.frame = 1
            self.D.x += self.D.dir * 150 * game_framework.frame_time
    def draw(self):
        img, x, y, w, h = self.D.frames['jump'][self.D.frame]
        self.D.draw_frame(img, x, y, w, h)

class LAND:
    def __init__(self, D):
        self.D = D
    def enter(self, e):
        self.D.frame = 2
        self.D.on_floor = True
        self.delay = get_time()
    def exit(self, e): pass
    def do(self):
        if get_time() - self.delay > 0.3:
            print("LAND")
            self.D.state_machine.handle_state_event(('JUMP_DONE', None))
    def draw(self):
        img, x, y, w, h = self.D.frames['jump'][2]
        self.D.draw_frame(img, x, y, w, h)

class Attack_Box:
    def __init__(self, x, y, w, h, owner, damage):
        self.x, self.y = x+50, y
        self.w, self.h = w, h
        self.owner = owner
        self.hit = False
        self.damage = damage

    def update(self):
        if self.owner.face == 1:
            self.x = self.owner.x + 40
        else:
            self.x = self.owner.x - 40
        self.y = self.owner.y
    def draw(self):
        draw_rectangle(*self.get_bb())
    def get_bb(self):
        return self.x - self.w // 2, self.y - self.h // 2, self.x + self.w // 2, self.y + self.h // 2
    def handle_collision(self, group, other):
        if other.no_damage:
            print('무적')
            return
        if self.hit:
            return
        if other == self.owner:
            return
        other.state_machine.handle_state_event(('HIT', None))

        print('충돌')

        if other is play_mode.p1:
            play_mode.p1_hp[0] -= self.damage
            print(f"P1 HP = {play_mode.p1_hp[0]}")
            if play_mode.p1_hp[0] <= 0:
                other.dead = True
        else:
            play_mode.p2_hp[0] -= self.damage
            print(f"P2 HP = {play_mode.p2_hp[0]}")
            if play_mode.p2_hp[0] <= 0:
                other.dead = True

        self.hit = True

        game_world.remove_object(self)
        self.owner.attack_box = None

class Counter:
    def __init__(self, D):
        self.D = D
        self.attack_spawn = False
        self.counter_start_time = 0.0
    def enter(self, e):
        self.D.frame = 0
        self.D.no_damage = True
        self.attack_spawn = False
        self.counter_start_time = get_time()
        if self.D.attack_box:
            game_world.remove_object(self.D.attack_box)
            self.D.attack_box = None
    def exit(self, e):
        if self.D.attack_box:
            game_world.remove_object(self.D.attack_box)
            self.D.attack_box = None
        self.attack_spawn = False
        self.D.no_damage = False
    def do(self):
        frames = self.D.frames['attack']
        n = len(frames)
        self.D.frame += n * ACTION_PER_TIME * game_framework.frame_time
        idx = int(self.D.frame)
        if idx == 3 and not self.attack_spawn:
            self.attack_spawn = True
            if self.D.attack_box is None:
                self.D.spawn_attack_box(damage = 30)
        if get_time() - self.counter_start_time > 3.0:
            self.D.no_damage = False
        if self.D.frame >= n:
            self.D.state_machine.handle_state_event(('ATTACK_DONE', None))
    def draw(self):
        img, x, y, w, h = self.D.get_current_frame('attack')
        self.D.draw_frame(img, x, y, w, h)


# ==================== 본체 ========================
class King_DDD:
    def __init__(self):
        self.x = 150
        self.y = 600
        self.frame = 0
        self.face = 1
        self.dir = 0

        self.attack_box = None
        self.target = None

        self.yv = 0.0

        self.on_floor = False
        self.delay = 0.0
        self.jump_delay = 0.0

        self.width = 60
        self.height = 40

        self.dead = False
        self.swap = False
        self.no_damage = False

        self.images = {
            'stand': load_image('king_dedede_stand.png'),
            'walk': load_image('king_dedede_walk.png'),
            'hit': load_image('king_dedede_hit.png'),
            'attack': load_image('king_dedede_attack.png'),
            'jump': load_image('king_dedede_jump.png')
        }

        self.frames = {
            'stand': [
                ('stand', 3, 3, 59, 59),
                ('stand', 66, 3, 61, 57),
                ('stand', 131, 3, 61, 56),
                ('stand', 196, 3, 59, 58),

            ],
            'walk': [
                ('walk', 4, 2, 60, 68),
                ('walk', 68, 2, 61, 68),
                ('walk', 133, 2, 64, 68),
                ('walk', 201, 2, 62, 68),
            ],
            'attack': [
                ('attack', 222, 7, 62, 76),
                ('attack', 151, 7, 67, 78),
                ('attack', 288, 7, 88, 97),
                ('attack', 69, 7, 78, 103),
                ('attack', 0, 7, 65, 95),
                ('attack', 380, 7, 88, 70),
            ],
            'jump': [
                ('jump', 13, 9, 59, 69),
                ('jump', 77, 9, 63, 69),
                ('jump', 144, 9, 65, 57),
            ],
            'hit': [
                ('hit', 9, 4, 63, 69)
            ]
        }

        self.STAND = Stand(self)
        self.WALK = Walk(self)
        self.ATTACK = Attack(self)
        self.JUMP = Jump(self)
        self.HIT = Hit(self)
        self.LAND = LAND(self)
        self.COUNTER = Counter(self)

        self.state_machine = StateMachine(
            self.STAND,
            {
                self.STAND: {d_down: self.WALK, a_down: self.WALK, e_down: self.ATTACK,
                             j_down: self.WALK, l_down: self.WALK, u_down: self.ATTACK,
                             w_down: self.JUMP, i_down: self.JUMP,  # lambda e: e[0] == 'LANDING': self.LANDING,
                             lambda e: e[0] == 'HIT': self.HIT},
                self.WALK: {d_up: self.STAND, a_up: self.STAND, e_down: self.ATTACK,
                            j_up: self.STAND, l_up: self.STAND, u_down: self.ATTACK,
                            w_down: self.JUMP, i_down: self.JUMP,  # lambda e: e[0] == 'LANDING': self.LANDING,
                            lambda e: e[0] == 'HIT': self.HIT},
                self.ATTACK: {lambda e: e[0] == 'ATTACK_DONE': self.STAND, lambda e: e[0] == 'HIT': self.HIT},
                self.HIT: {lambda e: e[0] == 'HIT_DONE': self.STAND},
                self.JUMP: {d_down: self.JUMP, a_down: self.JUMP, j_down: self.JUMP, l_down: self.JUMP,lambda e: e[0] == 'HIT': self.HIT,
                            lambda e: e[0] == 'LAND': self.LAND},
                self.LAND: {lambda e: e[0] == 'JUMP_DONE': self.STAND,lambda e: e[0] == 'HIT': self.HIT},
                self.COUNTER: {lambda e: e[0] == 'ATTACK_DONE': self.STAND},

            }
        )

    def get_current_frame(self, action):
        frames = self.frames[action]
        idx = int(self.frame) % len(frames)
        return frames[idx]

    def draw_frame(self, key, x, y, w, h):
        img = self.images[key]
        draw_y = self.y + (h // 2) - 20
        if self.face == 1:

            img.clip_draw(x, y, w, h, self.x, draw_y)
        else:
            img.clip_composite_draw(x, y, w, h, 0, 'h', self.x, draw_y, w, h)

    def update(self):
        self.state_machine.update()

        if self.jump_delay > 0:
            self.jump_delay -= game_framework.frame_time
        if not self.on_floor:
            self.gravity()
            # self.state_machine.handle_state_event(('LANDING', None))

        if self.on_floor:
            self.yv = 0.0

    def handle_event_p1(self, event):
        if event.type ==SDL_KEYDOWN and event.key == SDLK_q:
            self.swap = True
        self.state_machine.handle_state_event(('INPUT_P1', event))

    def handle_event_p2(self, event):
        if event.type ==SDL_KEYDOWN and event.key == SDLK_o:
            self.swap = True
        self.state_machine.handle_state_event(('INPUT_P2', event))

    def draw(self):
        self.state_machine.draw()
        self.draw_bb()

    def get_bb(self):
        w = 60
        h = 60
        return self.x - w // 2, self.y - h // 2+10, self.x + w // 2, self.y + h // 2+10

    def draw_bb(self):
        draw_rectangle(*self.get_bb())

    def handle_collision(self, group, other):
        if group == 'body:floor':
            if self.jump_delay > 0:
                return

            if not self.on_floor:
                self.on_floor = True
                self.yv = 0.0
                self.state_machine.handle_state_event(('LAND', None))

    def spawn_attack_box(self, damage):
        if self.target is None:
            return

        box_x = self.x + 40 if self.face == 1 else self.x - 40
        box_y = self.y

        self.attack_box = Attack_Box(box_x, box_y, 30, 20,self, damage)
        game_world.add_object(self.attack_box, 1)

        game_world.add_collision_pair('attack:body', self.attack_box, self.target)

    def gravity(self):
        self.yv -= GRAVITY * game_framework.frame_time
        self.y += self.yv* game_framework.frame_time*ACTION_PER_TIME



