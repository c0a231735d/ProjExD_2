import os
import sys
import pygame as pg
import random
import os

WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rect):
    """
    rectが画面内か画面外かを判定する関数
    引数:rect - こうかとんRect or 爆弾Rect
    戻り値:横方向・縦方向の真理値タプル（True:画面内/False:画面外）
    """
    x, y = True, True
    if rect.left < 0 or rect.right > WIDTH:
        x = False
    if rect.top < 0 or rect.bottom > HEIGHT:
        y = False
    return x, y

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    clock = pg.time.Clock()
    tmr = 0

    DELTA = {
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, 5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (5, 0)
    }

    bb_img = pg.Surface((20, 20))
    bb_img.set_colorkey((0, 0, 0))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    vx, vy = 5, 5

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, delta in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += delta[0]
                sum_mv[1] += delta[1]

        kk_rct.move_ip(sum_mv)
        if not check_bound(kk_rct)[0]:
            kk_rct.move_ip(-sum_mv[0], 0)
        if not check_bound(kk_rct)[1]:
            kk_rct.move_ip(0, -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        bb_rct.move_ip(vx, vy)
        x_bound, y_bound = check_bound(bb_rct)
        if not x_bound:
            vx = -vx
        if not y_bound:
            vy = -vy
        screen.blit(bb_img, bb_rct)

        if kk_rct.colliderect(bb_rct):
            return

        pg.display.update()
        clock.tick(60)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()