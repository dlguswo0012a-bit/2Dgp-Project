from pico2d import *
import game_framework
import game_world
from state_machine import StateMachine

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
GRAVITY = 9.8

# ===== 입력 이벤트 =====
def d_down(e): return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d
def d_up(e):   return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYUP and e[1].key == SDLK_d
def a_down(e): return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def a_up(e):   return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a
def e_down(e): return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_e
def q_down(e): return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_q
def q_up(e):   return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYUP and e[1].key == SDLK_q

def l_down(e): return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_l
def l_up(e):   return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYUP and e[1].key == SDLK_l
def j_down(e): return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_j
def j_up(e):   return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYUP and e[1].key == SDLK_j
def u_down(e): return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_u
def o_down(e): return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_o
def o_up(e):   return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYUP and e[1].key == SDLK_o

# ====================== 상태들 ============================
class Stand:
    def __init__(self, hk): self.hk = hk
    def enter(self, e): self.hk.dir = 0
    def exit(self, e): pass
    def do(self):
        frames = self.hk.frames['stand']
        n = len(frames)
        self.hk.frame = (self.hk.frame + n * ACTION_PER_TIME * game_framework.frame_time) % n
    def draw(self):
        img, x, y, w, h = self.hk.get_current_frame('stand')
        self.hk.draw_frame(img, x, y, w, h)


class Walk:
    def __init__(self, hk): self.hk = hk
    def enter(self, e):
        player = e[0]
        if player == 'INPUT_P1':
            if d_down(e) or a_up(e):
                self.hk.dir = 1
                self.hk.face = 1
            elif a_down(e) or d_up(e):
                self.hk.dir = -1
                self.hk.face = -1
        elif player == 'INPUT_P2':
            if l_down(e) or j_up(e):
                self.hk.dir = 1
                self.hk.face = 1
            elif j_down(e) or l_up(e):
                self.hk.dir = -1
                self.hk.face = -1
    def exit(self, e): pass
    def do(self):
        frames = self.hk.frames['walk']
        n = len(frames)
        self.hk.frame = (self.hk.frame + n * ACTION_PER_TIME * game_framework.frame_time) % n
        self.hk.x += self.hk.dir * 200 * game_framework.frame_time
    def draw(self):
        img, x, y, w, h = self.hk.get_current_frame('walk')
        self.hk.draw_frame(img, x, y, w, h)


class Attack:
    def __init__(self, hk): self.hk = hk
    def enter(self, e):
        self.hk.frame = 0
        self.hk.attack_box = None

        if e[0] == 'INPUT_P1':
            ev = e[1]
            if ev.type == SDL_KEYDOWN:
                if ev.key == SDLK_q:
                    self.hk.current_attack = 'attack_q1'
                elif ev.key == SDLK_e:
                    self.hk.current_attack = 'attack_e'
            elif ev.type == SDL_KEYUP:
                if ev.key == SDLK_q:
                    self.hk.current_attack = 'attack_q2'
        elif e[0] == 'INPUT_P2':
            ev = e[1]
            if ev.type == SDL_KEYDOWN:
                if ev.key == SDLK_o:
                    self.hk.current_attack = 'attack_q1'
                elif ev.key == SDLK_u:
                    self.hk.current_attack = 'attack_e'
            elif ev.type == SDL_KEYUP:
                if ev.key == SDLK_o:
                    self.hk.current_attack = 'attack_q2'
    def exit(self, e):
        if self.hk.attack_box:
            game_world.remove_object(self.hk.attack_box)
            self.hk.attack_box = None
    def do(self):
        action = self.hk.current_attack
        frames = self.hk.frames[action]
        n = len(frames)

        self.hk.frame += n * ACTION_PER_TIME * game_framework.frame_time
        idx = int(self.hk.frame)
        if action =="attack_q1":
           if idx == 1 or idx == 2:
               if self.hk.attack_box:
                     game_world.remove_object(self.hk.attack_box)
               self.hk.spawn_attack_box()
           self.hk.x += self.hk.dir * 200 * game_framework.frame_time

        elif action =="attack_q2":
            if self.hk.frame >= n:
                self.hk.state_machine.handle_state_event(('ATTACK_DONE', None))

        elif action =="attack_e":
            if idx == 3:
                if self.hk.attack_box is None:
                    self.hk.spawn_attack_box()
            if self.hk.frame >=n:
                self.hk.state_machine.handle_state_event(('ATTACK_DONE', None))


    def draw(self):
        action = self.hk.current_attack
        img, x, y, w, h = self.hk.get_current_frame(action)
        self.hk.draw_frame(img, x, y, w, h)


class Hit:
    def __init__(self, hk): self.hk = hk
    def enter(self, e): self.hk.frame = 0
    def exit(self, e): pass
    def do(self):
        frames = self.hk.frames['hit']
        n = len(frames)
        self.hk.frame += n * ACTION_PER_TIME * game_framework.frame_time
        if self.hk.frame >= n:
            self.hk.state_machine.handle_state_event(('HIT_DONE', None))
    def draw(self):
        img, x, y, w, h = self.hk.get_current_frame('hit')
        self.hk.draw_frame(img, x, y, w, h)
class Jump:
    pass

class Attack_Box:
    def __init__(self, x, y, w, h, owner):
        self.x, self.y = x + 50, y
        self.w, self.h = w, h
        self.owner = owner

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
        if other ==self.owner:
            return
        other.state_machine.handle_state_event(('HIT', None))

# ==================== 본체 ========================
class Hammer_Kirby:
    def __init__(self):
        self.x, self.y = 500, 150
        self.frame = 0
        self.face = 1
        self.dir = 0

        self.target = None
        self.attack_box = None

        self.yv = 0.0
        self.on_floor = False

        self.images = {
            'stand': load_image('Hammer_Kirby_stand.png'),
            'walk': load_image('Hammer_Kirby_walk.png'),
            'hit': load_image('Hammer_Kirby_hit.png'),
            'attack_e': load_image('Hammer_Kirby_attack_e.png'),
            'attack_q1': load_image('Hammer_Kirby_attack_q1.png'),
            'attack_q2': load_image('Hammer_Kirby_attack_q2.png'),
            'jump_start': load_image('Hammer_Kirby_jump_start.png'),
            'jumping': load_image('Hammer_Kirby_jumping.png'),
            'jumping_tired': load_image('Hammer_Kirby_jumping_tired.png'),
            'jump_finish': load_image('Hammer_Kirby_jump_finish.png'),
        }

        self.frames = {
            'stand': [
                ('stand', 3, 2, 37, 46),
                ('stand', 44, 2, 37, 46),
                ('stand', 85, 2, 37, 46),

            ],
            'walk': [
                ('walk', 11, 2, 27, 48),
                ('walk', 42, 2, 31, 48),
                ('walk', 77, 2, 32, 48),
                ('walk', 113, 2, 34, 48),
                ('walk', 151, 2, 36, 48),
                ('walk', 191, 2, 37, 48),
                ('walk', 232, 2, 36, 48),
                ('walk', 272, 2, 34, 48),
                ('walk', 310, 2, 31, 48),
                ('walk', 345, 2, 29, 48),
            ],
            'attack_e': [
                ('attack_e', 138, 2, 49, 53),
                ('attack_e', 101, 4, 33, 48),
                ('attack_e', 56, 6, 41, 46),
                ('attack_e', 8, 11, 44, 41),
            ],
            'attack_q1': [
                ('attack_q1', 6, 4, 29, 26),
                ('attack_q1', 39, 6, 40, 24),
                ('attack_q1', 83, 7, 45, 23),
                ('attack_q1', 132, 5, 34, 25),
                ('attack_q1', 170, 4, 29, 26),
                ('attack_q1', 203, 5, 39, 25),
                ('attack_q1', 247, 5, 46, 25),
                ('attack_q1', 297, 5, 34, 25),
            ],
            'attack_q2': [
                ('attack_q2', 2, 11, 28, 26),
                ('attack_q2', 34, 11, 26, 26),
                ('attack_q2', 64, 12, 25, 24),
                ('attack_q2', 93, 3, 33, 33),
                ('attack_q2', 130, 0, 37, 36),
            ],
            'jump_start': [
                ('jump_start', 9, 6, 35, 45),
                ('jump_start', 48, 10, 31, 41),
                ('jump_start', 83, 4, 36, 47),
                ('jump_start', 123, 4, 38, 47),
                ('jump_start', 165, 4, 43, 47),
                ('jump_start', 216, 1, 40, 50),
            ],
            'jumping': [
                ('jumping', 2, 3, 40, 54),
                ('jumping', 46, 3, 40, 54),
                ('jumping', 90, 3, 40, 54),
                ('jumping', 134, 3, 40, 54),
                ('jumping', 178, 3, 41, 54),
                ('jumping', 223, 3, 41, 54),
            ],
            'jump_tired': [
                ('jump_tired', 3, 3, 36, 56),
                ('jump_tired', 42, 3, 37, 56),
                ('jump_tired', 82, 3, 38, 56),
                ('jump_tired', 123, 3, 40, 56),
                ('jump_tired', 166, 3, 39, 56),
            ],
            'jump_finish': [
                ('jump_finish', 2, 3, 42, 48),
                ('jump_finish', 48, 5, 41, 46),
                ('jump_finish', 93, 4, 38, 47),
                ('jump_finish', 135, 3, 37, 48),
            ],
            'hit': [
                ('hit', 3, 4, 45, 34),
            ]
        }

        self.STAND = Stand(self)
        self.WALK = Walk(self)
        self.ATTACK = Attack(self)
        self.JUMP = Jump()
        self.HIT = Hit(self)

        self.cur_state = 'attack_e'

        self.state_machine = StateMachine(
            self.STAND,
            {
                self.STAND: {d_down: self.WALK, a_down: self.WALK, e_down: self.ATTACK,q_down: self.ATTACK,
                             j_down: self.WALK, l_down: self.WALK, u_down: self.ATTACK,o_down: self.ATTACK,
                             lambda e: e[0] == 'HIT': self.HIT},
                self.WALK: {d_up: self.STAND, a_up: self.STAND, e_down: self.ATTACK,q_down: self.ATTACK,
                            j_up: self.STAND, l_up: self.STAND, u_down: self.ATTACK,o_down: self.ATTACK,
                            lambda e: e[0] == 'HIT': self.HIT},
                self.ATTACK: {lambda e: e[0] == 'ATTACK_DONE': self.STAND, q_up: self.STAND, o_up: self.STAND,
                              lambda e: e[0] == 'HIT': self.HIT},
                self.HIT:    {lambda e: e[0] == 'HIT_DONE': self.STAND},
            }
        )

    def get_current_frame(self, action):
        frames = self.frames[action]
        idx = int(self.frame) % len(frames)
        return frames[idx]

    def draw_frame(self, key, x, y, w, h):
        img = self.images[key]

        if self.face == 1:
            img.clip_draw(x, y, w, h, self.x, self.y)
        else:
            img.clip_composite_draw(x, y, w, h, 0, 'h', self.x, self.y, w, h)

    def update(self):
        self.state_machine.update()
        if not self.on_floor:
            self.gravity()
        if self.on_floor:
            self.yv = 0.0

    def handle_event_p1(self, event):
        if event.type ==SDL_KEYDOWN:
            if event.key == SDLK_d:
                self.dir = 1
                self.face = 1
            elif event.key == SDLK_a:
                self.dir = -1
                self.face = -1
        elif event.type ==SDL_KEYUP:
            if event.key == SDLK_d or event.key == SDLK_a:
                self.dir = 0
        self.state_machine.handle_state_event(('INPUT_P1', event))

    def handle_event_p2(self, event):
        if event.type ==SDL_KEYDOWN:
            if event.key == SDLK_l:
                self.dir = 1
                self.face = 1
            elif event.key == SDLK_j:
                self.dir = -1
                self.face = -1
        elif event.type ==SDL_KEYUP:
            if event.key == SDLK_l or event.key == SDLK_j:
                self.dir = 0
        self.state_machine.handle_state_event(('INPUT_P2', event))

    def draw(self):
        self.state_machine.draw()
        self.draw_bb()

    def get_bb(self):
        w = 30
        h = 40
        return self.x - w // 2, self.y - h // 2, self.x + w // 2, self.y + h // 2

    def draw_bb(self):
        draw_rectangle(*self.get_bb())

    def handle_collision(self, group, other):
        if group == 'attack:body':
           print('충돌')
           self.state_machine.handle_state_event(('HIT', None))
        if group =='body:floor':
            self.on_floor = True
            self.yv = 0.0

    def spawn_attack_box(self):
        if self.target is None:
            return

        box_x = self.x + 40 if self.face == 1 else self.x - 40
        box_y = self.y

        self.attack_box = Attack_Box(box_x, box_y, 30, 20, self)
        game_world.add_object(self.attack_box, 1)
        game_world.add_collision_pair('attack:body', self.attack_box, self.target)
    def gravity(self):
        self.yv -= GRAVITY * game_framework.frame_time
        self.y += self.yv* game_framework.frame_time*ACTION_PER_TIME
