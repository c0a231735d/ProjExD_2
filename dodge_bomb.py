import sys
import pygame as pg
import random
import os
import time
import math

# 画面の幅と高さを設定
WIDTH, HEIGHT = 1100, 650
# 現在のファイルのディレクトリに移動
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rect):
    """
    rectが画面内か画面外かを判定する関数
    引数:rect - こうかとんRect or 爆弾Rect
    戻り値:横方向・縦方向の真理値タプル（True:画面内/False:画面外）
    """
    x, y = True, True
    # 左端が0未満または右端が画面幅を超える場合、xをFalseに設定
    if rect.left < 0 or rect.right > WIDTH:
        x = False
    # 上端が0未満または下端が画面高さを超える場合、yをFalseに設定
    if rect.top < 0 or rect.bottom > HEIGHT:
        y = False
    return (x, y)

def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー時に、半透明の黒い画面上に「Game Over」と表示し、
    泣いているこうかとん画像を貼り付ける関数
    """
    # 半透明の黒い画面を描画
    blackout = pg.Surface((WIDTH, HEIGHT))
    blackout.set_alpha(128)  # 透明度を設定
    blackout.fill((0, 0, 0))  # 黒色で塗りつぶす
    screen.blit(blackout, (0, 0))  # 画面に描画

    # "Game Over"の文字列を描画
    font = pg.font.Font(None, 80)
    txt = font.render("Game Over", True, (255, 255, 255))  # 白色で文字を描画
    txt_rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # 画面中央に配置
    screen.blit(txt, txt_rect.topleft)  # 画面に描画

    # 泣いているこうかとん画像を描画（左側）
    crying_kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    crying_kk_rct = crying_kk_img.get_rect()
    crying_kk_rct.center = (txt_rect.left - crying_kk_rct.width // 2, HEIGHT // 2)
    screen.blit(crying_kk_img, crying_kk_rct)  # 画面に描画

    # 泣いているこうかとん画像を描画（右側）
    crying_kk_rct.center = (txt_rect.right + crying_kk_rct.width // 2, HEIGHT // 2)
    screen.blit(crying_kk_img, crying_kk_rct)  # 画面に描画

    pg.display.update()  # 画面を更新
    time.sleep(5)  # 5秒間表示

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

def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    orgから見て、dstがどこにあるかを計算し、方向ベクトルをタプルで返す関数
    """
    dx, dy = dst.centerx - org.centerx, dst.centery - org.centery  # 目的地までの差分を計算
    distance = math.hypot(dx, dy)  # 距離を計算
    if distance <= 300:  # 距離が300未満の場合、慣性として前の方向に移動
        norm = math.sqrt(50)
        vx, vy = dx / distance * norm, dy / distance * norm
    else:    
        return current_xy
      # 速度ベクトルのノルムを√50に正規化
    vx, vy = dx / distance * norm, dy / distance * norm

    return [vx, vy]

def main():
    pg.display.set_caption("逃げろ！こうかとん")  # ウィンドウのタイトルを設定
    screen = pg.display.set_mode((WIDTH, HEIGHT))  # 画面を設定
    bg_img = pg.image.load("fig/pg_bg.jpg")  # 背景画像を読み込む
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)  # こうかとんの画像を読み込む
    kk_rct = kk_img.get_rect()  # こうかとんのRectを取得
    kk_rct.center = 300, 200  # こうかとんの初期位置を設定
    clock = pg.time.Clock()  # クロックオブジェクトを作成
    tmr = 0  # タイマーを初期化

    DELTA = {
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, 5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (5, 0)
    }

    bb_imgs, bb_accs = init_bb_imgs()  # 爆弾の画像と加速度のリストを初期化
    bb_rct = bb_imgs[0].get_rect()  # 爆弾の初期位置を設定
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)  # 爆弾の初期位置をランダムに設定
    vx, vy = 5, 5  # 爆弾の初期速度

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0])  # 背景画像を描画

        key_lst = pg.key.get_pressed()  # 押されているキーを取得
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
        screen.blit(kk_img, kk_rct)  # こうかとんを描画

        idx = min(tmr // 500, 9)  # 時間に応じて爆弾のサイズと速度を変更
        avx, avy = calc_orientation(bb_rct, kk_rct, (vx * bb_accs[idx], vy * bb_accs[idx]))  # 追従型爆弾の方向を計算
        bb_rct.move_ip(avx, avy)  # 爆弾を移動
        x_bound, y_bound = check_bound(bb_rct)
        if not x_bound:
            vx = -vx
        if not y_bound:
            vy = -vy
        screen.blit(bb_imgs[idx], bb_rct)  # 爆弾を描画

        if kk_rct.colliderect(bb_rct):  # こうかとんが爆弾に衝突した場合
            gameover(screen)  # ゲームオーバー画面を表示
            return

        pg.display.update()  # 画面を更新
        clock.tick(60)  # フレームレートを設定
        tmr += 1  # タイマーを更新

if __name__ == "__main__":
    pg.init()  # Pygameを初期化
    main()  # メイン関数を実行
    pg.quit()  # Pygameを終了
    sys.exit()  # プログラムを終了