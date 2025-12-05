from pico2d import *
import game_framework
import play_mode

character_select = None
hammer_img = None
king_img = None
meta_img = None
p1_choices = []
p2_choices = []
def init():
    global character_select, hammer_img, king_img, meta_img
    character_select = load_image('character_select.png')
    hammer_img = load_image('Hammer_Kirby_select.png')
    king_img = load_image('King_DDD_select.png')
    meta_img = load_image('meta_knight_select.png')
def update():
    pass
def draw_face(name, x, y, w=120, h=120):
    if name == 'kirby':
        hammer_img.draw(x, y, w, h)
    elif name == 'ddd':
        king_img.draw(x, y, w, h)
    elif name == 'meta':
        meta_img.draw(x, y, w, h)
def draw():
    clear_canvas()
    character_select.draw(600, 300, 1200, 600)

    if len(p1_choices) > 0:
        draw_face(p1_choices[0], 440, 310)
    if len(p1_choices) > 1:
        draw_face(p1_choices[1], 195, 310)

    if len(p2_choices) > 0:
        draw_face(p2_choices[0], 760, 310)
    if len(p2_choices) > 1:
        draw_face(p2_choices[1], 1006, 310)
    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            # P1 키
            elif event.key == SDLK_1 and len(p1_choices) < 2:
                p1_choices.append('meta')
            elif event.key == SDLK_2 and len(p1_choices) < 2:
                p1_choices.append('ddd')
            elif event.key == SDLK_3 and len(p1_choices) < 2:
                p1_choices.append('kirby')

            # P2 키
            elif event.key == SDLK_z and len(p2_choices) < 2:
                p2_choices.append('meta')
            elif event.key == SDLK_x and len(p2_choices) < 2:
                p2_choices.append('ddd')
            elif event.key == SDLK_c and len(p2_choices) < 2:
                p2_choices.append('kirby')
            else:
                game_framework.change_mode(play_mode)



def finish():
    pass
def pause():
    pass
def resume():
    pass
