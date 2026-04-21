import math
import os
import random
import sys

import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
    pg.K_w: (0, -5),
    pg.K_s: (0, +5),
    pg.K_a: (-5, 0),
    pg.K_d: (+5, 0),
}
DIFFICULTY = {
    "Easy":   {"acc_step": 800, "min_dist": 250, "max_idx": 7, "init_speed": 4,
               "spawn_step": 25 * 50, "item_step": (8 * 50, 14 * 50)},
    "Normal": {"acc_step": 500, "min_dist": 300, "max_idx": 9, "init_speed": 5,
               "spawn_step": 15 * 50, "item_step": (8 * 50, 14 * 50)},
    "Hard":   {"acc_step": 300, "min_dist": 350, "max_idx": 9, "init_speed": 6,
               "spawn_step": 10 * 50, "item_step": (6 * 50, 12 * 50)},
}
ITEM_COLORS = {
    "shield": (80, 180, 255),
    "clear":  (255, 80, 80),
    "boost":  (255, 200, 50),
}
ITEM_LABELS = {"shield": "S", "clear": "C", "boost": "B"}
PICKUP_BONUS = 200
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def jp_font(size: int) -> pg.font.Font:
    """
    日本語表示が可能なシステムフォントを取得する
    引数：フォントサイズ
    戻り値：pg.font.Font オブジェクト
    """
    return pg.font.SysFont("yugothic,msgothic,meiryo,ipagothic", size)


def title_screen(screen: pg.Surface,
                 hi_scores: dict[str, int]) -> str | None:
    """
    タイトル画面を表示し、難易度選択 or 終了入力を待つ
    引数1 screen：スクリーンSurface
    引数2 hi_scores：難易度ごとのハイスコア辞書
    戻り値：選択された難易度名（"Easy"/"Normal"/"Hard"）／終了の場合はNone
    """
    title_font = jp_font(90)
    menu_font = jp_font(48)
    score_font = jp_font(28)
    desc_font = jp_font(28)

    title = title_font.render("逃げろ！こうかとん", True, (255, 255, 255))
    menu_items = [
        (pg.K_1, "[1] Easy",   "Easy"),
        (pg.K_2, "[2] Normal", "Normal"),
        (pg.K_3, "[3] Hard",   "Hard"),
    ]
    quit_text = desc_font.render("[ESC] 終了", True, (200, 200, 200))
    hint = desc_font.render("矢印キー / WASD で移動 / 爆弾から逃げ続けろ！", True, (180, 180, 220))

    clock = pg.time.Clock()
    pg.event.clear()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return None
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return None
                for key, _, name in menu_items:
                    if event.key == key:
                        return name

        screen.fill((25, 30, 55))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 130)))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 210)))

        for i, (_, label, name) in enumerate(menu_items):
            txt = menu_font.render(label, True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(midright=(WIDTH // 2 + 20, 320 + i * 70)))
            best = hi_scores.get(name, 0)
            best_txt = score_font.render(f"Best: {best}", True, (255, 220, 100))
            screen.blit(best_txt, best_txt.get_rect(midleft=(WIDTH // 2 + 50, 320 + i * 70)))

        screen.blit(quit_text, quit_text.get_rect(center=(WIDTH // 2, HEIGHT - 70)))
        pg.display.update()
        clock.tick(50)


def gameover_screen(screen: pg.Surface, score: int,
                    best: int, is_new_record: bool) -> str | None:
    """
    ゲームオーバー画面を表示し、リスタート/タイトル/終了の入力を待つ
    引数1 screen：スクリーンSurface
    引数2 score：今回の最終スコア
    引数3 best：当該難易度のベストスコア
    引数4 is_new_record：今回のスコアがベスト更新かどうか
    戻り値："restart"（再挑戦）/ "title"（タイトルへ）/ None（終了）
    """
    blackout = pg.Surface((WIDTH, HEIGHT))
    blackout.fill((0, 0, 0))
    blackout.set_alpha(210)

    cry_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    big_font = jp_font(90)
    mid_font = jp_font(40)
    small_font = jp_font(32)

    title_txt = big_font.render("Game Over", True, (255, 255, 255))
    title_rct = title_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))

    score_color = (255, 100, 100) if is_new_record else (255, 255, 100)
    score_label = "NEW RECORD!  " if is_new_record else ""
    score_txt = mid_font.render(
        f"{score_label}Score: {score}   Best: {best}",
        True, score_color)
    score_rct = score_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))

    menu_txt = small_font.render(
        "[R] もう一度   [T] タイトル   [ESC] 終了",
        True, (220, 220, 220))
    menu_rct = menu_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

    cry_left = cry_img.get_rect(midright=(title_rct.left - 30, title_rct.centery))
    cry_right = cry_img.get_rect(midleft=(title_rct.right + 30, title_rct.centery))

    blackout.blit(cry_img, cry_left)
    blackout.blit(cry_img, cry_right)
    blackout.blit(title_txt, title_rct)
    blackout.blit(score_txt, score_rct)
    blackout.blit(menu_txt, menu_rct)

    screen.blit(blackout, (0, 0))
    pg.display.update()

    pg.time.delay(500)
    pg.event.clear()
    clock = pg.time.Clock()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return None
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    return "restart"
                if event.key == pg.K_t:
                    return "title"
                if event.key == pg.K_ESCAPE:
                    return None
        clock.tick(50)


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
                     current_xy: tuple[float, float],
                     min_dist: int) -> tuple[float, float]:
    """
    爆弾から見て、こうかとんRectがある方向を計算し、正規化したベクトルを返す
    引数1 org：爆弾Rect（始点）
    引数2 dst：こうかとんRect（終点）
    引数3 current_xy：計算前の方向ベクトル
    引数4 min_dist：これ以下の距離なら追従せず慣性で動く閾値
    戻り値：正規化された方向ベクトル（vx, vy）／距離が近い場合はcurrent_xy
    """
    x_diff = dst.centerx - org.centerx
    y_diff = dst.centery - org.centery
    norm = math.sqrt(x_diff ** 2 + y_diff ** 2)
    if norm < min_dist:
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


def make_bomb(bomb_type: str, tmr: int, kk_rct: pg.Rect,
              init_speed: float) -> dict:
    """
    新しい爆弾の状態dictを生成する。プレイヤーから300px以上離れた位置に出現させる
    引数1 bomb_type："chase"（追従型）または "bounce"（直進バウンド型）
    引数2 tmr：現在のフレーム時刻（chase の段階計算に使う）
    引数3 kk_rct：こうかとんRect
    引数4 init_speed：chase 型の初速
    戻り値：爆弾dict（type/x/y/vx/vy/spawn_tmr/img/rct）
    """
    while True:
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        if math.hypot(x - kk_rct.centerx, y - kk_rct.centery) > 300:
            break
    if bomb_type == "chase":
        vx, vy = float(init_speed), float(init_speed)
    else:
        angle = random.uniform(0, 2 * math.pi)
        speed = 9.0
        vx = speed * math.cos(angle)
        vy = speed * math.sin(angle)
    return {
        "type": bomb_type,
        "x": float(x), "y": float(y),
        "vx": vx, "vy": vy,
        "spawn_tmr": tmr,
        "img": None,
        "rct": pg.Rect(0, 0, 20, 20),
    }


def update_bomb(bomb: dict, bb_imgs: list[pg.Surface], bb_accs: list[int],
                cfg: dict, tmr: int, kk_rct: pg.Rect) -> None:
    """
    1個の爆弾の位置・速度・画像・Rectを次フレーム分更新する（壁での跳ね返り含む）
    引数1 bomb：爆弾dict（in-place 更新）
    引数2 bb_imgs：爆弾画像リスト
    引数3 bb_accs：加速度リスト
    引数4 cfg：難易度設定
    引数5 tmr：現在のフレーム時刻
    引数6 kk_rct：こうかとんRect（chase の追従先）
    """
    if bomb["type"] == "chase":
        idx = min((tmr - bomb["spawn_tmr"]) // cfg["acc_step"], cfg["max_idx"])
        org = pg.Rect(0, 0, 1, 1)
        org.center = (int(bomb["x"]), int(bomb["y"]))
        bomb["vx"], bomb["vy"] = calc_orientation(
            org, kk_rct, (bomb["vx"], bomb["vy"]), cfg["min_dist"])
        bb_img = bb_imgs[idx]
        avx = bomb["vx"] * bb_accs[idx]
        avy = bomb["vy"] * bb_accs[idx]
    else:
        bb_img = bb_imgs[2]
        avx = bomb["vx"]
        avy = bomb["vy"]

    bomb["x"] += avx
    bomb["y"] += avy

    hw = bb_img.get_width() / 2
    hh = bb_img.get_height() / 2
    if bomb["x"] < hw:
        bomb["x"] = hw
        bomb["vx"] = abs(bomb["vx"])
    elif bomb["x"] > WIDTH - hw:
        bomb["x"] = WIDTH - hw
        bomb["vx"] = -abs(bomb["vx"])
    if bomb["y"] < hh:
        bomb["y"] = hh
        bomb["vy"] = abs(bomb["vy"])
    elif bomb["y"] > HEIGHT - hh:
        bomb["y"] = HEIGHT - hh
        bomb["vy"] = -abs(bomb["vy"])

    bomb["img"] = bb_img
    bomb["rct"] = bb_img.get_rect(center=(int(bomb["x"]), int(bomb["y"])))


def make_item(kk_rct: pg.Rect) -> dict:
    """
    新しいアイテムの状態dictを生成する。プレイヤーから150px以上離れた位置に出現させる
    引数 kk_rct：こうかとんRect
    戻り値：アイテムdict（type/rct）
    """
    item_type = random.choice(["shield", "clear", "boost"])
    while True:
        x = random.randint(40, WIDTH - 40)
        y = random.randint(40, HEIGHT - 40)
        if math.hypot(x - kk_rct.centerx, y - kk_rct.centery) > 150:
            break
    return {
        "type": item_type,
        "rct": pg.Rect(x - 20, y - 20, 40, 40),
    }


def play(screen: pg.Surface, difficulty: str) -> int:
    """
    1ゲーム分のメインループを実行し、最終スコアを返す
    複数爆弾（追従型/直進バウンド型）とアイテム（シールド/クリア/ブースト）を管理する
    引数1 screen：スクリーンSurface
    引数2 difficulty：難易度名（DIFFICULTYのキー）
    戻り値：最終スコア（int）／pg.QUITで終了した場合は -1
    """
    cfg = DIFFICULTY[difficulty]
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bb_imgs, bb_accs = init_bb_imgs()

    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(-5, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bombs = [make_bomb("chase", 0, kk_rct, cfg["init_speed"])]
    items: list[dict] = []
    spawn_alternate = 0  # 0:bounce, 1:chase で交互に出現
    next_spawn_tmr = cfg["spawn_step"]
    next_item_tmr = random.randint(*cfg["item_step"])

    shield_timer = 0
    boost_timer = 0
    score = 0

    score_font = jp_font(36)
    item_font = jp_font(28)
    diff_label = score_font.render(f"[{difficulty}]", True, (255, 200, 100))

    pg.event.clear()
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return -1
        screen.blit(bg_img, [0, 0])

        # 新しい爆弾を一定間隔で追加（直進と追従を交互に）
        if tmr >= next_spawn_tmr:
            new_type = "bounce" if spawn_alternate == 0 else "chase"
            bombs.append(make_bomb(new_type, tmr, kk_rct, cfg["init_speed"]))
            spawn_alternate = 1 - spawn_alternate
            next_spawn_tmr = tmr + cfg["spawn_step"]

        # アイテムをランダム間隔で出現
        if tmr >= next_item_tmr:
            items.append(make_item(kk_rct))
            next_item_tmr = tmr + random.randint(*cfg["item_step"])

        # こうかとん移動
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        sum_mv[0] = max(-5, min(5, sum_mv[0]))
        sum_mv[1] = max(-5, min(5, sum_mv[1]))
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        if tuple(sum_mv) in kk_imgs and sum_mv != [0, 0]:
            kk_img = kk_imgs[tuple(sum_mv)]

        # 爆弾更新
        for bomb in bombs:
            update_bomb(bomb, bb_imgs, bb_accs, cfg, tmr, kk_rct)

        # アイテム取得判定
        remaining_items = []
        for item in items:
            if kk_rct.colliderect(item["rct"]):
                if item["type"] == "shield":
                    shield_timer = 3 * 50
                elif item["type"] == "clear":
                    # 全爆弾を遠方へ再配置（追従型は段階もリセット）
                    for b in bombs:
                        nb = make_bomb(b["type"], tmr, kk_rct, cfg["init_speed"])
                        b["x"], b["y"] = nb["x"], nb["y"]
                        b["vx"], b["vy"] = nb["vx"], nb["vy"]
                        b["spawn_tmr"] = tmr
                elif item["type"] == "boost":
                    boost_timer = 5 * 50
                score += PICKUP_BONUS
                continue
            remaining_items.append(item)
        items = remaining_items

        # 衝突判定（シールド中は無敵）
        if shield_timer == 0:
            for bomb in bombs:
                if kk_rct.colliderect(bomb["rct"]):
                    return score

        # スコア加算
        multiplier = 2 if boost_timer > 0 else 1
        score += multiplier

        # タイマー減衰
        if shield_timer > 0:
            shield_timer -= 1
        if boost_timer > 0:
            boost_timer -= 1

        # === 描画 ===
        for item in items:
            color = ITEM_COLORS[item["type"]]
            pg.draw.rect(screen, color, item["rct"], border_radius=8)
            pg.draw.rect(screen, (255, 255, 255), item["rct"], width=3, border_radius=8)
            label = item_font.render(ITEM_LABELS[item["type"]], True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=item["rct"].center))

        if shield_timer > 0:
            radius = max(kk_rct.width, kk_rct.height) // 2 + 8
            pulse = (shield_timer // 5) % 2
            ring_color = (100, 200, 255) if pulse else (200, 240, 255)
            pg.draw.circle(screen, ring_color, kk_rct.center, radius, 3)
        screen.blit(kk_img, kk_rct)

        for bomb in bombs:
            screen.blit(bomb["img"], bomb["rct"])

        score_color = (255, 200, 80) if boost_timer > 0 else (255, 255, 255)
        score_txt = score_font.render(f"Score: {score}", True, score_color)
        screen.blit(score_txt, (20, 20))
        screen.blit(diff_label, (20, 60))

        y_offset = 100
        if shield_timer > 0:
            txt = item_font.render(
                f"SHIELD {shield_timer / 50:.1f}s", True, ITEM_COLORS["shield"])
            screen.blit(txt, (20, y_offset))
            y_offset += 30
        if boost_timer > 0:
            txt = item_font.render(
                f"BOOST x2  {boost_timer / 50:.1f}s", True, ITEM_COLORS["boost"])
            screen.blit(txt, (20, y_offset))

        pg.display.update()
        tmr += 1
        clock.tick(50)


def main():
    """
    「逃げろ！こうかとん」のメイン関数
    タイトル → プレイ → ゲームオーバーのループを管理し、
    難易度選択・リスタート・難易度別ハイスコア（セッション内）を扱う
    """
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    hi_scores: dict[str, int] = {"Easy": 0, "Normal": 0, "Hard": 0}

    while True:
        difficulty = title_screen(screen, hi_scores)
        if difficulty is None:
            return

        while True:
            score = play(screen, difficulty)
            if score < 0:
                return
            is_new = score > hi_scores[difficulty]
            if is_new:
                hi_scores[difficulty] = score

            choice = gameover_screen(screen, score, hi_scores[difficulty], is_new)
            if choice is None:
                return
            if choice == "title":
                break


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
