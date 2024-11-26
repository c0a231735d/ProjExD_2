import sys
import pygame as pg
import random
import os
import time

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

def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー時に、半透明の黒い画面上に「Game Over」と表示し、
    泣いているこうかとん画像を貼り付ける関数
    """
    # 半透明の黒い画面を描画
    blackout = pg.Surface((WIDTH, HEIGHT))
    blackout.set_alpha(128)  # 透明度を設定
    blackout.fill((0, 0, 0))
    screen.blit(blackout, (0, 0))

    # "Game Over"の文字列を描画
    font = pg.font.Font(None, 80)
    txt = font.render("Game Over", True, (255, 255, 255))
    txt_rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(txt, txt_rect.topleft)

    # 泣いているこうかとん画像を描画（左側）
    crying_kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    crying_kk_rct = crying_kk_img.get_rect()
    crying_kk_rct.center = (txt_rect.left - crying_kk_rct.width // 2, HEIGHT // 2)
    screen.blit(crying_kk_img, crying_kk_rct)

    # 泣いているこうかとん画像を描画（右側）
    crying_kk_rct.center = (txt_rect.right + crying_kk_rct.width // 2, HEIGHT // 2)
    screen.blit(crying_kk_img, crying_kk_rct)

    pg.display.update()
    time.sleep(5)

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    サイズの異なる爆弾Surfaceを要素としたリストと加速度リストを返す関数
    """
    bb_imgs = []  # 爆弾の画像リスト
    bb_accs = [a for a in range(1, 11)]  # 加速度のリスト
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))  # 爆弾のサイズを変更
        bb_img.set_colorkey((0, 0, 0))  # 黒色を透明に設定
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)  # 赤い円を描画
        bb_imgs.append(bb_img)  # リストに追加
    return bb_imgs, bb_accs

def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:
    """
    移動量の合計値タプルに対応する向きの画像Surfaceを返す関数
    """
    kk_imgs = {
        (-5, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9),  # 左向き
        (-5, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), -45, 0.9),  # 左上向き
        (-5, 5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 45, 0.9),  # 左下向き
        (0, 5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 90, 0.9),  # 下向き
        (0, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), -90, 0.9),  # 上向き
        (5, -5): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), 135, 0.9), False, True),  # 右下向き
        (5, 5): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), -135, 0.9), False, True),  # 右上向き
        (5, 0): pg.transform.flip(pg.image.load("fig/3.png"), True, False),  # 右向き
    }
    return kk_imgs.get(sum_mv, pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9))  # デフォルトは正面向き

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

    bb_imgs, bb_accs = init_bb_imgs()  # 爆弾の画像と加速度のリストを初期化
    bb_rct = bb_imgs[0].get_rect()  # 爆弾の初期位置を設定
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    vx, vy = 5, 5  # 爆弾の初期速度

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

        kk_img = get_kk_img(tuple(sum_mv))  # 移動方向に応じてこうかとんの画像を取得
        kk_rct.move_ip(sum_mv)  # こうかとんを移動
        if not check_bound(kk_rct)[0]:
            kk_rct.move_ip(-sum_mv[0], 0)
        if not check_bound(kk_rct)[1]:
            kk_rct.move_ip(0, -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        idx = min(tmr // 500, 9)  # 時間に応じて爆弾のサイズと速度を変更
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_rct.move_ip(avx, avy)
        x_bound, y_bound = check_bound(bb_rct)
        if not x_bound:
            vx = -vx
        if not y_bound:
            vy = -vy
        screen.blit(bb_imgs[idx], bb_rct)

        if kk_rct.colliderect(bb_rct):  # こうかとんが爆弾に衝突した場合
            gameover(screen)  # ゲームオーバー画面を表示
            return

        pg.display.update()
        clock.tick(60)
        tmr += 1

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()