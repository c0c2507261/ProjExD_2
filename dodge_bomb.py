import math
import os
import random
import sys
import time

import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def gameover(screen: pg.Surface) -> None:
    """
    こうかとんが爆弾に衝突したときのゲームオーバー画面を表示する
    画面をブラックアウトし、泣いているこうかとんと「Game Over」を5秒間表示する
    引数：スクリーンSurface
    """
    blackout = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(blackout, (0, 0, 0), pg.Rect(0, 0, WIDTH, HEIGHT))
    blackout.set_alpha(200)

    cry_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    cry_rct = cry_img.get_rect()

    fonto = pg.font.Font(None, 80)
    txt = fonto.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect()

    blackout.blit(txt, [WIDTH / 2 - txt_rct.width / 2,
                        HEIGHT / 2 - txt_rct.height / 2])
    blackout.blit(cry_img, [WIDTH / 2 - txt_rct.width / 2 - cry_rct.width,
                            HEIGHT / 2 - cry_rct.height / 2])
    blackout.blit(cry_img, [WIDTH / 2 + txt_rct.width / 2,
                            HEIGHT / 2 - cry_rct.height / 2])

    screen.blit(blackout, [0, 0])
    pg.display.update()
    time.sleep(5)


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    押下キーに対する移動量タプルをキー、向きに応じたこうかとんSurfaceを値とする辞書を返す
    戻り値：{(vx, vy): こうかとんSurface}
    """
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_img_flip = pg.transform.flip(kk_img, True, False)
    return {
        (0, 0): kk_img_flip,
        (-5, 0): kk_img,
        (-5, -5): pg.transform.rotozoom(kk_img, -45, 1.0),
        (0, -5): pg.transform.rotozoom(kk_img, -90, 1.0),
        (+5, -5): pg.transform.rotozoom(kk_img_flip, 45, 1.0),
        (+5, 0): kk_img_flip,
        (+5, +5): pg.transform.rotozoom(kk_img_flip, -45, 1.0),
        (0, +5): pg.transform.rotozoom(kk_img, 90, 1.0),
        (-5, +5): pg.transform.rotozoom(kk_img, 45, 1.0),
    }


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    時間経過に応じた爆弾Surfaceリストと加速度リストを生成する
    戻り値：（爆弾Surfaceリスト, 加速度リスト）
    """
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r))
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs


def calc_orientation(org: pg.Rect, dst: pg.Rect,
                     current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    爆弾から見て、こうかとんRectがある方向を計算し、正規化したベクトルを返す
    引数1 org：爆弾Rect（始点）
    引数2 dst：こうかとんRect（終点）
    引数3 current_xy：計算前の方向ベクトル
    戻り値：正規化された方向ベクトル（vx, vy）／距離が近い場合はcurrent_xy
    """
    x_diff = dst.centerx - org.centerx
    y_diff = dst.centery - org.centery
    norm = math.sqrt(x_diff ** 2 + y_diff ** 2)
    if norm < 300:
        return current_xy
    return x_diff / norm * math.sqrt(50), y_diff / norm * math.sqrt(50)


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRectか爆弾Rect
    戻り値：タプル（横方向判定結果, 縦方向判定結果）
    画面内ならTrue, 画面外ならFalse
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(-5, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        screen.blit(bg_img, [0, 0])

        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        if tuple(sum_mv) in kk_imgs and sum_mv != [0, 0]:
            kk_img = kk_imgs[tuple(sum_mv)]
        screen.blit(kk_img, kk_rct)

        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        idx = min(tmr // 500, 9)
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_img = bb_imgs[idx]
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height

        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
        screen.blit(bb_img, bb_rct)

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
