import glfw
from OpenGL.GL import *
import numpy as np
import math

# === Engine ===
from engine.transformacoes import perspectiva, translacao, escala, rotacaoX, look_at
from engine.geometrias import criarCubo, criarPlataforma, criarVAO
from engine.colisao import colisaoINI

# === Game ===
from game.jogador import Player
from game.inimigo import Inimigo
from game.plataforma import Plataforma
from game.rampa import Rampa
from game.modelo_blocos import ModeloBlocos
from game.modelo_inimigos import ModeloInimigos

# === Core ===
from core.renderizador import desenhar
from core.shaders import criarPrograma

# === Shaders ===
with open("src/assets/shaders/basic.vert") as f:
    VERT = f.read()
with open("src/assets/shaders/basic.frag") as f:
    FRAG = f.read()


def inimigo_face_para_player(inimigo, player):
    """Face (rot Y) para o inimigo olhar na direção do player."""
    dx = player.x - inimigo.x
    dz = player.z - inimigo.z
    if abs(dx) < 1e-6 and abs(dz) < 1e-6:
        return 0.0
    return math.atan2(dx, dz)


def player_esta_andando(keys):
    return bool(keys.get(glfw.KEY_W) or keys.get(glfw.KEY_A) or keys.get(glfw.KEY_S) or keys.get(glfw.KEY_D))


def main():
    if not glfw.init():
        return

    w, h = 1600, 900
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    win = glfw.create_window(w, h, "Echoes of Dimensions", None, None)
    glfw.make_context_current(win)

    glEnable(GL_DEPTH_TEST)

    programa = criarPrograma(VERT, FRAG)
    glUseProgram(programa)

    # =========================
    # CORES BASE (mundo base)
    # =========================
    pele = (0.90, 0.75, 0.60)
    roupa = (0.15, 0.65, 0.25)
    bota = (0.20, 0.12, 0.06)
    det = (0.55, 0.35, 0.10)

    inim_corpo = (0.55, 0.20, 0.20)
    inim_cabeca = (0.75, 0.75, 0.75)
    inim_arma = (0.85, 0.85, 0.85)

    metal  = (0.85, 0.85, 0.90)
    madeira = (0.45, 0.28, 0.12)
    corda  = (0.95, 0.95, 0.95)

    ground_cor = (0.33, 0.60, 0.28)
    plat1_cor = (0.58, 0.42, 0.20)
    plat2_cor = (0.70, 0.55, 0.30)
    ramp_cor = (0.64, 0.48, 0.24)

    hud_bg_cor = (0.15, 0.15, 0.15)
    hud_hp_cor = (0.85, 0.15, 0.15)

    # =========================
    # VAOs
    # =========================
    vao_pele = criarVAO(*criarCubo(pele))
    vao_roupa = criarVAO(*criarCubo(roupa))
    vao_bota = criarVAO(*criarCubo(bota))
    vao_det = criarVAO(*criarCubo(det))

    vao_inim_corpo = criarVAO(*criarCubo(inim_corpo))
    vao_inim_cabeca = criarVAO(*criarCubo(inim_cabeca))
    vao_inim_arma = criarVAO(*criarCubo(inim_arma))

    cubo_ground = criarVAO(*criarCubo(ground_cor))
    cubo_plat1 = criarVAO(*criarCubo(plat1_cor))
    cubo_plat2 = criarVAO(*criarCubo(plat2_cor))
    plane_ramp = criarVAO(*criarPlataforma(ramp_cor))

    hud_bg = criarVAO(*criarCubo(hud_bg_cor))
    hud_hp = criarVAO(*criarCubo(hud_hp_cor))

    vao_metal   = criarVAO(*criarCubo(metal))
    vao_madeira = criarVAO(*criarCubo(madeira))
    vao_corda   = criarVAO(*criarCubo(corda))


    # =========================
    # MODELOS
    # =========================
    modelo_player = ModeloBlocos(vao_pele, vao_roupa, vao_bota, vao_det, vao_metal, vao_madeira)
    modelo_inimigos = ModeloInimigos(vao_inim_corpo, vao_inim_cabeca, vao_metal, vao_madeira, vao_corda)


    # =========================
    # CENÁRIO
    # =========================
    plataformas = [
        Plataforma(0, 0, 20, -20, 0, plat1_cor),
        Plataforma(0, -15, 10, -10, 4, plat2_cor),
    ]
    ramp = Rampa(0, -7.5, 8, -8, 0, 4, ramp_cor)

    player = Player()
    inimigos = [
        Inimigo(3, 2, inim_corpo, "melee"),
        Inimigo(-6, -6, inim_corpo, "ranged"),
    ]

    # =========================
    # INPUT
    # =========================
    keys = {}

    def key_cb(win, k, s, a, m):
        if a == glfw.PRESS:
            keys[k] = True
        if a == glfw.RELEASE:
            keys[k] = False
        if k == glfw.KEY_SPACE and a == glfw.PRESS and player.vivo:
            player.ataque = True
            player.temp = 0

    glfw.set_key_callback(win, key_cb)

    proj = perspectiva(math.radians(60), w / h, 0.1, 200)
    last = glfw.get_time()

    # =========================
    # LOOP
    # =========================
    while not glfw.window_should_close(win):
        now = glfw.get_time()
        dt = now - last
        last = now

        glfw.poll_events()

        if player.vivo:
            player.update(dt, keys, plataformas, ramp)

        for e in inimigos:
            e.update(dt, player)

        atk = player.espada_box() if player.vivo else None
        if atk:
            for e in inimigos:
                if e.vivo and colisaoINI(atk, e.aabb()):
                    e.vivo = False

        glClearColor(0.52, 0.80, 0.98, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        cam_eye = np.array([player.x, player.y + 7, player.z + 14], dtype=np.float32)
        cam_tgt = np.array([player.x, player.y, player.z], dtype=np.float32)
        view = look_at(cam_eye, cam_tgt, np.array([0, 1, 0], dtype=np.float32))
        vp = proj @ view

        # Chão
        desenhar(cubo_ground, translacao(0, -0.51, 0) @ escala(40, 1, 40), vp, programa)

        # Plataformas
        for p in plataformas:
            vao = cubo_plat1 if p.h == 0 else cubo_plat2
            desenhar(vao, translacao(p.x, p.h - 0.5, p.z) @ escala(p.w, 1, p.d), vp, programa)

        # Rampa
        ang = math.atan2((ramp.y1 - ramp.y0), abs(ramp.d))
        if ramp.d < 0:
            ang = -ang
        mid_y = (ramp.y0 + ramp.y1) / 2
        desenhar(
            plane_ramp,
            translacao(ramp.x, mid_y, ramp.z) @ rotacaoX(-ang) @ escala(ramp.w, 0.1, abs(ramp.d)),
            vp, programa
        )

        # Player (modelo em blocos)
        modelo_player.draw_link(
            desenhar, programa, vp,
            player.x, player.y, player.z,
            player.face, now,
            andando=player_esta_andando(keys),
            atacando=player.ataque
        )

        # Inimigos (modelos em blocos)
        for e in inimigos:
            if not e.vivo:
                continue

            face = inimigo_face_para_player(e, player)

            if e.tipo == "melee":
                modelo_inimigos.draw_melee(desenhar, programa, vp, e.x, e.y, e.z, face)
            else:
                modelo_inimigos.draw_ranged(desenhar, programa, vp, e.x, e.y, e.z, face)

        # HUD VIDA
        frac = 0.0
        if player.vida_max > 0:
            frac = max(0.0, min(1.0, player.vida / player.vida_max))

        hud_x = cam_eye[0] - 6.5
        hud_y = cam_eye[1] + 3.5
        hud_z = cam_eye[2] - 10.0

        desenhar(hud_bg, translacao(hud_x, hud_y, hud_z) @ escala(4.0, 0.3, 0.2), vp, programa)
        desenhar(
            hud_hp,
            translacao(hud_x - (2.0 * (1 - frac)), hud_y, hud_z) @ escala(4.0 * frac, 0.25, 0.18),
            vp, programa
        )

        glfw.swap_buffers(win)

    glfw.terminate()


if __name__ == "__main__":
    main()
