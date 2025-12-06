from pico2d import *
import game_framework
import game_world
from state_machine import StateMachine

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
GRAVITY = 9.8*2
HEIGHT = 40

# ===== 입력 이벤트 =====
def d_down(e): return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d
def d_up(e):   return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYUP and e[1].key == SDLK_d
def a_down(e): return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def a_up(e):   return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a
def e_down(e): return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_e
def w_down(e): return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_w
def w_up(e):   return e[0] == 'INPUT_P1' and e[1].type == SDL_KEYUP and e[1].key == SDLK_w



def l_down(e): return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_l
def l_up(e):   return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYUP and e[1].key == SDLK_l
def j_down(e): return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_j
def j_up(e):   return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYUP and e[1].key == SDLK_j
def u_down(e): return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_u
def i_down(e): return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_i
def i_up(e):   return e[0] == 'INPUT_P2' and e[1].type == SDL_KEYUP and e[1].key == SDLK_i



# ====================== 상태들 ============================
class Stand:
    def __init__(self, mk): self.mk = mk
    def enter(self, e): self.mk.dir = 0
    def exit(self, e): pass
    def do(self):
        frames = self.mk.frames['stand']
        n = len(frames)
        self.mk.frame = (self.mk.frame + n * ACTION_PER_TIME * game_framework.frame_time) % n
    def draw(self):
        img, x, y, w, h = self.mk.get_current_frame('stand')
        self.mk.draw_frame(img, x, y, w, h)


class Walk:
    def __init__(self, mk): self.mk = mk
    def enter(self, e):
        player = e[0]
        if player == 'INPUT_P1':
            if d_down(e) or a_up(e):
                self.mk.dir = 1
                self.mk.face = 1
            elif a_down(e) or d_up(e):
                self.mk.dir = -1
                self.mk.face = -1
        elif player == 'INPUT_P2':
            if l_down(e) or j_up(e):
                self.mk.dir = 1
                self.mk.face = 1
            elif j_down(e) or l_up(e):
                self.mk.dir = -1
                self.mk.face = -1
    def exit(self, e): pass
    def do(self):
        frames = self.mk.frames['walk']
        n = len(frames)
        self.mk.frame = (self.mk.frame + n * ACTION_PER_TIME * game_framework.frame_time) % n
        self.mk.x += self.mk.dir * 200 * game_framework.frame_time
    def draw(self):
        img, x, y, w, h = self.mk.get_current_frame('walk')
        self.mk.draw_frame(img, x, y, w, h)


class Attack:
    def __init__(self, mk): self.mk = mk
    def enter(self, e):
        self.mk.frame = 0
        self.mk.attack_box = None

        self.mk.attack_x = self.mk.x + (10*self.mk.face)
        self.mk.attack_y = self.mk.y+((HEIGHT+5)//2)

        self.mk.impact_x = self.mk.attack_x
        self.mk.impact_y = self.mk.attack_y

    def exit(self, e):
        if self.mk.attack_box:
            game_world.remove_object(self.mk.attack_box)
            self.mk.attack_box = None
    def do(self):
        frames = self.mk.frames['attack']
        n = len(frames)
        self.mk.frame += n * ACTION_PER_TIME * game_framework.frame_time
        idx = int(self.mk.frame)
        if idx == 2:
            if self.mk.attack_box is None:
                self.mk.spawn_attack_box()

        if self.mk.frame >= n:
            self.mk.state_machine.handle_state_event(('ATTACK_DONE', None))
    def draw(self):
        img, ax, ay, aw, ah = self.mk.get_current_frame('attack')
        self.mk.draw_frame('attack', ax, ay, aw, ah)
        frame = int(self.mk.frame)

        img,ix, iy, iw, ih = self.mk.frames['impact'][frame]
        effect_img = self.mk.images['impact']

        offset_x = 20
        effect_x = self.mk.x + (offset_x if self.mk.face == 1 else -offset_x)
        effect_y = self.mk.y + (ih * self.mk.scale) / 2  # 발 기준 y 고정


        if self.mk.face == 1:
            effect_img.clip_draw(ix, iy, iw, ih,effect_x, effect_y,iw * self.mk.scale,ih * self.mk.scale)
        else:
            effect_img.clip_composite_draw(ix, iy, iw, ih, 0, 'h',effect_x, effect_y,iw * self.mk.scale,ih * self.mk.scale)


class Hit:
    def __init__(self, mk): self.mk = mk
    def enter(self, e): self.mk.frame = 0
    def exit(self, e): pass
    def do(self):
        frames = self.mk.frames['hit']
        n = len(frames)
        self.mk.frame += n * ACTION_PER_TIME * game_framework.frame_time
        if self.mk.frame >= n:
            self.mk.state_machine.handle_state_event(('HIT_DONE', None))
    def draw(self):
        img, x, y, w, h = self.mk.get_current_frame('hit')
        self.mk.draw_frame(img, x, y, w, h)
class Jump:
    def __init__(self, mk):
        self.mk = mk

    def enter(self, e):
        player = e[0]

        if player == 'INPUT_P1':
            if d_down(e) or a_up(e):
                self.mk.dir = 1
                self.mk.face = 1
            elif a_down(e) or d_up(e):
                self.mk.dir = -1
                self.mk.face = -1
        elif player == 'INPUT_P2':
            if l_down(e) or j_up(e):
                self.mk.dir = 1
                self.mk.face = 1
            elif j_down(e) or l_up(e):
                self.mk.dir = -1
                self.mk.face = -1

        if self.mk.on_floor:
            self.mk.frame = 0
            self.mk.yv = 70.0
            self.mk.on_floor = False
            self.mk.jump_delay = 0.1
    def exit(self, e): pass

    def do(self):
        self.mk.y += self.mk.yv * game_framework.frame_time *5.0
        self.mk.yv -= GRAVITY * game_framework.frame_time*5.0

        if self.mk.yv > 0.0:
            self.mk.frame = 0
            self.mk.x += self.mk.dir * 150 * game_framework.frame_time
        elif not self.mk.on_floor:
            self.mk.frame = 1
            self.mk.x += self.mk.dir * 150 * game_framework.frame_time
    def draw(self):
        img, x, y, w, h = self.mk.frames['jump'][self.mk.frame]
        self.mk.draw_frame(img, x, y, w, h)

class LAND:
    def __init__(self, mk):
        self.mk = mk
    def enter(self, e):
        self.mk.frame = 2
        self.mk.on_floor = True
        self.delay = 0.0
    def exit(self, e): pass
    def do(self):
        if self.mk.frame == 2:
            self.mk.frame = 3
            self.delay = get_time()
            return
        if self.mk.frame == 3:
            if get_time() - self.delay > 0.3:
                self.mk.state_machine.handle_state_event(('JUMP_DONE', None))
    def draw(self):
        img, x, y, w, h = self.mk.frames['jump'][self.mk.frame]
        self.mk.draw_frame(img, x, y, w, h)

class Attack_Box:
    def __init__(self, x, y, w, h, owner):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.owner = owner
        self.hit = False

    def update(self):
        if self.owner.face == 1:
            self.x = self.owner.x + 40
        else:
            self.x = self.owner.x - 40
        self.y = self.owner.y
    def draw(self):
        draw_rectangle(*self.get_bb())
    def get_bb(self):
        return (self.x - self.w // 2)-10, self.y , (self.x + self.w // 2)+5, self.y + self.h*2.5
    def handle_collision(self, group, other):
        if self.hit:
            return
        if other == self.owner:
            return
        other.state_machine.handle_state_event(('HIT', None))

        print('충돌')
        other.hp -= 50
        print(f'HP: {other.hp}')

        if other.hp <= 50:
            other.swap = True
        if other.hp <= 0:
            print("죽음")
            other.dead = True
            other.hp = 100
            self.owner.hp = 100
        self.hit = True

        game_world.remove_object(self)
        self.owner.attack_box = None

# ==================== 본체 ========================
class Meta_knight:
    def __init__(self):
        self.x, self.y = 400, 150
        self.frame = 0
        self.face = 1
        self.dir = 0

        self.target = None
        self.attack_box = None

        self.on_floor = False
        self.delay = 0.0
        self.jump_delay = 0.0
        self.yv = 0.0

        self.hp = 100
        self.dead = False
        self.swap = False

        self.scale = 2

        self.images = {
            'stand': load_image('meta_night_stand.png'),
            'walk': load_image('meta_night_walk.png'),
            'hit': load_image('meta_night_hit.png'),
            'attack': load_image('meta_night_attack_remove_impact.png'),
            'attack_done': load_image('meta_night_attack_remove_impact.png'),
            'impact': load_image('meta_night_attack_impact.png'),
            'jump': load_image('meta_knight_jump.png'),

        }

        self.frames = {
            'stand': [
                ('stand',0, 0, 29, 25)

            ],
            'walk': [
                ('walk', 3, 1, 27, 22),
                ('walk', 32, 1, 25, 22),
                ('walk', 59, 1, 28, 22),
                ('walk', 89, 1, 27, 22),
                ('walk', 118, 1, 27, 22),
                ('walk', 147, 1, 30, 22),
                ('walk', 180, 1, 30, 22),
                ('walk', 212, 1, 27, 22),
            ],
            'attack': [
                ('attack',2, 9, 28, 26),
                ('attack',53, 11, 33, 24),
                ('attack',128, 10, 34, 25),
                ('attack',207, 10, 34, 25),

            ],
            'attack_done':[
                ('attack', 251, 8, 39, 37),
                ('attack', 294, 8, 33, 37),
            ],
            'impact':[
                ('impact',2, 0, 40, 45),
                ('impact',53, 0, 65, 45),
                ('impact',128, 0, 65, 45),
                ('impact',207, 10, 42, 35),
            ],
            'hit': [
                ('hit', 254, 0, 32, 50)
            ],
            'jump': [
                ('jump',17, 1, 33, 46),
                ('jump',63, 6, 38, 41),
                ('jump',117, 13, 38, 34),
                ('jump',170, 11, 34, 36),

            ]
        }

        self.STAND = Stand(self)
        self.WALK = Walk(self)
        self.ATTACK = Attack(self)
        self.HIT = Hit(self)
        self.JUMP = Jump(self)
        self.LAND = LAND(self)

        self.state_machine = StateMachine(
            self.STAND,
            {
                self.STAND: {d_down: self.WALK, a_down: self.WALK, e_down: self.ATTACK,
                             j_down: self.WALK, l_down: self.WALK, u_down: self.ATTACK,
                             w_down: self.JUMP, i_down: self.JUMP,#lambda e: e[0] == 'LANDING': self.LANDING,
                             lambda e: e[0] == 'HIT': self.HIT},
                self.WALK: {d_up: self.STAND, a_up: self.STAND, e_down: self.ATTACK,
                            j_up: self.STAND, l_up: self.STAND, u_down: self.ATTACK,
                            w_down: self.JUMP, i_down: self.JUMP, #lambda e: e[0] == 'LANDING': self.LANDING,
                            lambda e: e[0] == 'HIT': self.HIT},
                self.ATTACK: {lambda e: e[0] == 'ATTACK_DONE': self.STAND, lambda e: e[0] == 'HIT': self.HIT},
                self.HIT: {lambda e: e[0] == 'HIT_DONE': self.STAND},
                self.JUMP: {d_down: self.JUMP, a_down: self.JUMP, j_down: self.JUMP, l_down: self.JUMP,
                            lambda e: e[0] == 'LAND': self.LAND},
                self.LAND: {lambda e: e[0] == 'JUMP_DONE': self.STAND},
                #self.LANDING: {lambda e: e[0] == 'LAND': self.LAND}

            }
        )

    def get_current_frame(self, action):
        frames = self.frames[action]
        idx = int(self.frame) % len(frames)
        return frames[idx]

    def draw_frame(self, key, x, y, w, h):
        img = self.images[key]

        scaled_h = h * self.scale
        if key == 'attack' or key == 'jump':
            self.scale = 1.5
            scaled_h = h * self.scale
        else:
            self.scale = 2

        draw_y = self.y + scaled_h / 2

        if self.face == 1:
            img.clip_draw(x, y, w, h, self.x, draw_y, w*self.scale, scaled_h)
        else:
            img.clip_composite_draw(x, y, w, h, 0, 'h', self.x, draw_y, w*self.scale, scaled_h)

    def update(self):
        self.state_machine.update()
        if self.jump_delay > 0:
            self.jump_delay -= game_framework.frame_time
        if not self.on_floor:
            self.gravity()
            #self.state_machine.handle_state_event(('LANDING', None))

        if self.on_floor:
            self.yv = 0.0

    def handle_event_p1(self, event):
        self.state_machine.handle_state_event(('INPUT_P1', event))

    def handle_event_p2(self, event):
        self.state_machine.handle_state_event(('INPUT_P2', event))

    def draw(self):
        self.state_machine.draw()
        self.draw_bb()

    def get_bb(self):
        w = 50
        h = HEIGHT+2
        return self.x - w // 2, self.y, self.x + w // 2, self.y+h

    def handle_collision(self, group, other):
        if group == 'attack:body':
            if hasattr(other, 'owner'):
                if other.owner == self:
                    return
            self.state_machine.handle_state_event(('HIT', None))
        if group == 'body:floor':
            if self.jump_delay > 0:
                return
            if isinstance(self.state_machine.cur_state, Jump):
                self.on_floor = True
                self.yv = 0.0
                self.state_machine.handle_state_event(('LAND', None))
            else:
                self.on_floor = True
                self.yv = 0.0

    def draw_bb(self):
        draw_rectangle(*self.get_bb())

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
        self.y += self.yv * game_framework.frame_time * ACTION_PER_TIME

