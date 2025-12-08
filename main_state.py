from pico2d import *
import game_framework

import title_mode as start_mode

open_canvas(1200, 600)
bgm = load_music('sound/bgm.mp3')
bgm.set_volume(30)
bgm.repeat_play()
game_framework.run(start_mode)
close_canvas()
