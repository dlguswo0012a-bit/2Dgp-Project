from pico2d import *
import game_framework
import play_mode

character_select = None

def init():
    global character_select
    character_select = load_image('character_select.png')

def update():
    pass

def draw():
    clear_canvas()
    character_select.draw(600, 300, 1200, 600)
    update_canvas()

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            else:
                game_framework.change_mode(play_mode)

def finish():
    pass
def pause():
    pass
def resume():
    pass