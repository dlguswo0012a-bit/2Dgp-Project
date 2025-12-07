from pico2d import *
import game_framework
import game_world
import play_mode
from state_machine import StateMachine

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
GRAVITY = 9.8 *2

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
    def __init__(self, hk):
        self.hk = hk
        self.attack_spawn = False
        self.counter_start_time = 0.0

        self.impact_img = load_image('attack_star_impact.png')
        self.impact_start_time = 0.0
        self.impact_duration = 0.2

    def enter(self, e):
        self.hk.frame = 0
        self.attack_spawn = False

        if self.hk.attack_box:
            game_world.remove_object(self.hk.attack_box)
            self.hk.attack_box = None

    def exit(self, e):
        if self.hk.attack_box:
            game_world.remove_object(self.hk.attack_box)
            self.hk.attack_box = None

        self.attack_spawn = False

    def do(self):
        frames = self.hk.frames['attack']
        n = len(frames)

        self.hk.frame += n * ACTION_PER_TIME * game_framework.frame_time
        idx = int(self.hk.frame)

        if idx == 1 and not self.attack_spawn:
            self.attack_spawn = True
            self.impact_start_time = get_time()
            if self.hk.attack_box is None:
                self.hk.spawn_attack_box(damage = 20)

        if self.hk.frame >= n:
            self.hk.state_machine.handle_state_event(('ATTACK_DONE', None))

    def draw(self):
        img, x, y, w, h = self.hk.get_current_frame('attack')
        self.hk.draw_frame(img, x, y, w, h)
        now = get_time()
        if now - self.impact_start_time < self.impact_duration:
            offset_x = 60
            if self.hk.face == 1:
                fx = self.hk.x + offset_x
            else:
                fx = self.hk.x - offset_x
            fx = self.hk.x + 40 if self.hk.face == 1 else self.hk.x - 40
            if self.hk.face == 1:
                self.impact_img.draw(fx, self.hk.y, 60, 60)
            else:
                self.impact_img.composite_draw(fx, 'h', self.hk.x-60, self.hk.y, 60, 60)

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
    def __init__(self,  hk): self.hk = hk

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

        if self.hk.on_floor:
            self.hk.frame = 0
            self.hk.yv = 70.0
            self.hk.on_floor = False
            self.hk.jump_delay = 0.1
    def exit(self, e): pass

    def do(self):
        self.hk.y += self.hk.yv * game_framework.frame_time *5.0
        self.hk.yv -= GRAVITY * game_framework.frame_time*5.0

        if self.hk.yv > 0.0:
            self.hk.frame = 0
            self.hk.x += self.hk.dir * 150 * game_framework.frame_time
        elif not self.hk.on_floor:
            self.hk.frame = 1
            self.hk.x += self.hk.dir * 150 * game_framework.frame_time
    def draw(self):
        img, x, y, w, h = self.hk.frames['jump'][self.hk.frame]
        self.hk.draw_frame(img, x, y, w, h)

class LAND:
    def __init__(self, hk):
        self.hk = hk
    def enter(self, e):
        self.hk.frame = 2
        self.hk.on_floor = True
        self.delay = 0.0
    def exit(self, e): pass
    def do(self):
        if self.hk.frame == 2:
            self.hk.frame = 3
            self.delay = get_time()
            return
        if self.hk.frame == 3:
            if get_time() - self.delay > 0.3:
                self.hk.state_machine.handle_state_event(('JUMP_DONE', None))
    def draw(self):
        img, x, y, w, h = self.hk.frames['jump'][self.hk.frame]
        self.hk.draw_frame(img, x, y, w, h)


class Attack_Box:
    def __init__(self, x, y, w, h, owner,damage):
        self.x, self.y = x + 50, y
        self.w, self.h = w, h
        self.owner = owner
        self.hit = False
        self.damage = damage

    def update(self):
        if self.owner.face == 1:
            self.x = self.owner.x + 40
        else:
            self.x = self.owner.x - 65
        self.y = self.owner.y

    def draw(self):
        #draw_rectangle(*self.get_bb())
        pass
    def get_bb(self):
        return (self.x - self.w // 2), self.y -  self.h*1.5, (self.x + self.w // 2)+10, self.y + self.h*1.5
    def handle_collision(self, group, other):
        if other.no_damage:
            return
        if self.hit:
            return
        if other == self.owner:
            return
        print('충돌')
        other.state_machine.handle_state_event(('HIT', None))

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
    def __init__(self, hk):
        self.hk = hk
        self.attack_spawn = False
        self.counter_start_time = 0.0
        self.counter_start_time = 0.0

        self.impact_img = load_image('attack_star_impact.png')
        self.impact_start_time = 0.0
        self.impact_duration = 0.2

    def enter(self, e):
        self.hk.frame = 0
        self.attack_spawn = False
        self.hk.no_damage = True
        self.counter_start_time = get_time()

        if self.hk.attack_box:
            game_world.remove_object(self.hk.attack_box)
            self.hk.attack_box = None

    def exit(self, e):
        if self.hk.attack_box:
            game_world.remove_object(self.hk.attack_box)
            self.hk.attack_box = None

        self.attack_spawn = False
        self.hk.no_damage = False
    def do(self):
        frames = self.hk.frames['attack']
        n = len(frames)

        self.hk.frame += n * ACTION_PER_TIME * game_framework.frame_time
        idx = int(self.hk.frame)

        if idx == 1 and not self.attack_spawn:
            self.impact_start_time = get_time()
            self.attack_spawn = True
            if self.hk.attack_box is None:
                self.hk.spawn_attack_box(damage = 30)

        if get_time() - self.counter_start_time > 3.0:
            self.hk.no_damage = False

        if self.hk.frame >= n:
            self.hk.state_machine.handle_state_event(('ATTACK_DONE', None))

    def draw(self):
        img, x, y, w, h = self.hk.get_current_frame('attack')
        self.hk.draw_frame(img, x, y, w, h)
        now = get_time()
        if now - self.impact_start_time < self.impact_duration:
            offset_x = 60
            if self.hk.face == 1:
                fx = self.hk.x + offset_x
            else:
                fx = self.hk.x - offset_x
            fx = self.hk.x + 40 if self.hk.face == 1 else self.hk.x - 40
            if self.hk.face == 1:
                self.impact_img.draw(fx, self.hk.y, 60, 60)
            else:
                self.impact_img.composite_draw(fx, 'h', self.hk.x-60, self.hk.y, 60, 60)


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
        self.delay = 0.0
        self.jump_delay = 0.0


        self.dead = False
        self.swap = False
        self.no_damage = False

        self.knockback_power = 0.0
        self.knockback_dir = 0
        self.knockback_timer = 0.0

        self.knockback_count = 0
        self.power_knockback = 3

        self.player = None
        self.impact_time = 0.0
        self.impact_start = 0.2

        self.images = {
            'stand': load_image('Hammer_Kirby_stand.png'),
            'walk': load_image('Hammer_Kirby_walk.png'),
            'hit': load_image('Hammer_Kirby_hit.png'),
            'attack': load_image('Hammer_Kirby_attack_e.png'),
            'jump': load_image('Hammer_Kirby_jump.png'),
            'impact': load_image('attack_star_impact.png'),

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
            'attack': [
                ('attack', 138, 2, 49, 53),
                ('attack', 101, 4, 33, 48),
                ('attack', 56, 6, 41, 46),
                ('attack', 8, 11, 44, 41),
            ],

            'jump': [
                ('jump', 5, 0, 38, 70),
                ('jump',56, 0, 35, 70),
                ('jump',104, 0, 37, 70),
                ('jump',158, 0, 34, 70)
            ],
            'hit': [
                ('hit', 3, 4, 45, 34),
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
                self.JUMP: {d_down: self.JUMP, a_down: self.JUMP, j_down: self.JUMP, l_down: self.JUMP,
                            lambda e: e[0] == 'HIT': self.HIT,
                            lambda e: e[0] == 'LAND': self.LAND},
                self.LAND: {lambda e: e[0] == 'JUMP_DONE': self.STAND, lambda e: e[0] == 'HIT': self.HIT},
                self.COUNTER: {lambda e: e[0] == 'ATTACK_DONE': self.STAND},

            }
        )

    def get_current_frame(self, action):
        frames = self.frames[action]
        idx = int(self.frame) % len(frames)
        return frames[idx]

    def draw_frame(self, key, x, y, w, h):
        img = self.images[key]

        if self.face == 1:
            img.clip_draw(x, y, w, h, self.x, self.y, w*1.2, h*1.2)
        else:
            img.clip_composite_draw(x, y, w, h, 0, 'h', self.x, self.y, w*1.2, h*1.2)

    def update(self):
        self.state_machine.update()
        if self.jump_delay > 0:
            self.jump_delay -= game_framework.frame_time
        if not self.on_floor:
            self.gravity()

        if self.on_floor:
            self.yv = 0.0
        if self.knockback_timer > 0.0:
            self.x += self.knockback_dir * self.knockback_power * game_framework.frame_time
            self.knockback_timer -= game_framework.frame_time

        if self.y < 50:
            self.y = 300
            self.x = 600
        self.x = clamp(50, self.x, 1150)



    def handle_event_p1(self, event):
        if event.type ==SDL_KEYDOWN:
            if event.key == SDLK_d:
                self.dir = 1
                self.face = 1
            elif event.key == SDLK_a:
                self.dir = -1
                self.face = -1
            elif event.key == SDLK_q:
                self.swap = True

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
            elif event.key == SDLK_o:
                self.swap = True
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_l or event.key == SDLK_j:
                self.dir = 0
        self.state_machine.handle_state_event(('INPUT_P2', event))

    def draw(self):
        self.state_machine.draw()
        self.draw_bb()


    def get_bb(self):
        w = 60
        h = 40
        return self.x - w // 2, self.y - h // 2-10, self.x + w // 2 - 10, self.y + h // 2-10

    def draw_bb(self):
        #draw_rectangle(*self.get_bb())
        pass
    def handle_collision(self, group, other):
        if group == 'attack:body':
            if hasattr(other, 'owner'):
                if other.owner == self:
                    return
            if not self.no_damage and self.knockback_count < self.power_knockback:
                self.knockback_power = 100.0
                self.knockback_count += 1
                if other.x > self.x:
                    self.knockback_dir = -1
                else:
                    self.knockback_dir = 1
                self.knockback_timer = 0.2
            elif not self.no_damage and self.knockback_count == self.power_knockback:
                self.knockback_power = 300.0
                self.knockback_count = 0
                if other.x > self.x:
                    self.knockback_dir = -1
                else:
                    self.knockback_dir = 1
                self.knockback_timer = 0.2

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

        self.attack_box = Attack_Box(box_x, box_y, 30, 20, self, damage)
        game_world.add_object(self.attack_box, 1)
        game_world.add_collision_pair('attack:body', self.attack_box, self.target)

    def gravity(self):
        self.yv -= GRAVITY * game_framework.frame_time
        self.y += self.yv* game_framework.frame_time*ACTION_PER_TIME
