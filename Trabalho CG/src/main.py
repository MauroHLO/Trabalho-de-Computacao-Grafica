import glfw
from OpenGL.GL import *
import numpy as np
import math

# === Engine ===
from engine.transformacoes import perspectiva, translacao, escala, look_at
from engine.geometrias import criarCubo, criarPlataforma, criarRampaSolida, criarVAO
from engine.colisao import colisaoINI

# === Game ===
from game.jogador import Player
from game.plataforma import Plataforma
from game.rampa import Rampa
from game.modelo_blocos import ModeloBlocos
from game.modelo_inimigos import ModeloInimigos
from game.render_utils import desenhar_flecha
from game.fase import Fase, Trecho, SpawnInfo

# === Core ===
from core.renderizador import desenhar
from core.shaders import criarPrograma

# === Shaders ===
with open("src/assets/shaders/basic.vert") as f:
    VERT = f.read()
with open("src/assets/shaders/basic.frag") as f:
    FRAG = f.read()

WORLD_OVER = 0
WORLD_ETER = 1
WORLD_UNDER = 2

WORLD_CFG = {
    WORLD_OVER: {
        "name": "Overworld",
        "sky": (0.52, 0.80, 0.98),
        "tint": (1.0, 1.0, 1.0),
        "melee":  {"hp": 3, "speed": 2.0, "behavior": "chase"},
        "ranged": {"hp": 2, "speed": 1.5, "behavior": "kite", "fire_cd": 2.2, "burst": 1},
    },
    WORLD_ETER: {
        "name": "Eter",
        "sky": (0.20, 0.10, 0.35),
        "tint": (0.75, 0.85, 1.15),
        "melee":  {"hp": 2, "speed": 3.2, "behavior": "backstab"},
        "ranged": {"hp": 3, "speed": 2.0, "behavior": "kite_burst", "fire_cd": 1.8, "burst": 2},
    },
    WORLD_UNDER: {
        "name": "Underground",
        "sky": (0.18, 0.03, 0.03),
        "tint": (1.15, 0.70, 0.70),
        "melee":  {"hp": 4, "speed": 1.9, "behavior": "pack_chase"},
        "ranged": {"hp": 1, "speed": 2.2, "behavior": "opportunist", "fire_cd": 2.5, "burst": 1},
    },
}

def set_uTint(programa, tint):
    loc = glGetUniformLocation(programa, "uTint")
    glUseProgram(programa)
    if loc != -1:
        glUniform3f(loc, float(tint[0]), float(tint[1]), float(tint[2]))

def inimigo_face_para_player(inimigo, player):
    dx = player.x - inimigo.x
    dz = player.z - inimigo.z
    if abs(dx) < 1e-6 and abs(dz) < 1e-6:
        return 0.0
    return math.atan2(dx, dz)

def player_esta_andando(keys):
    return bool(keys.get(glfw.KEY_W) or keys.get(glfw.KEY_A) or keys.get(glfw.KEY_S) or keys.get(glfw.KEY_D))

def proximo_mundo(m):
    if m == WORLD_OVER:
        return WORLD_ETER
    if m == WORLD_ETER:
        return WORLD_UNDER
    return WORLD_OVER

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
    # CORES / MATERIAIS
    # =========================
    pele = (0.90, 0.75, 0.60)
    roupa = (0.15, 0.65, 0.25)
    bota = (0.20, 0.12, 0.06)
    det  = (0.55, 0.35, 0.10)

    inim_corpo  = (0.55, 0.20, 0.20)
    inim_cabeca = (0.75, 0.75, 0.75)

    metal   = (0.85, 0.85, 0.90)
    madeira = (0.45, 0.28, 0.12)
    corda   = (0.95, 0.95, 0.95)
    pena_cor = (0.95, 0.95, 0.95)

    ground_cor = (0.33, 0.60, 0.28)
    plat1_cor  = (0.58, 0.42, 0.20)
    plat2_cor  = (0.70, 0.55, 0.30)
    ramp_cor   = (0.64, 0.48, 0.24)

    hud_bg_cor = (0.15, 0.15, 0.15)
    hud_hp_cor = (0.85, 0.15, 0.15)

    altar_cor = (0.85, 0.85, 0.85)
    eco_verde = (0.20, 0.95, 0.20)
    eco_azul  = (0.25, 0.55, 1.00)
    eco_verm  = (1.00, 0.25, 0.25)

    portal_azul = (0.25, 0.65, 1.00)
    portal_verm = (1.00, 0.25, 0.25)
    portal_verd = (0.20, 0.95, 0.20)

    # =========================
    # VAOs (pos + normal + tint)
    # =========================

    def mk_cubo(cor):
        v, i, c = criarCubo(cor, com_normais=True)
        return criarVAO(v, i, c)

    vao_pele  = mk_cubo(pele)
    vao_roupa = mk_cubo(roupa)
    vao_bota  = mk_cubo(bota)
    vao_det   = mk_cubo(det)

    vao_inim_corpo  = mk_cubo(inim_corpo)
    vao_inim_cabeca = mk_cubo(inim_cabeca)

    cubo_ground = mk_cubo(ground_cor)
    cubo_plat1  = mk_cubo(plat1_cor)
    cubo_plat2  = mk_cubo(plat2_cor)

    # rampa sólida
    v, i, c = criarRampaSolida(ramp_cor)
    vao_rampa_solida = criarVAO(v, i, c)

    hud_bg = mk_cubo(hud_bg_cor)
    hud_hp = mk_cubo(hud_hp_cor)

    vao_metal   = mk_cubo(metal)
    vao_madeira = mk_cubo(madeira)
    vao_corda   = mk_cubo(corda)
    vao_pena    = mk_cubo(pena_cor)

    vao_altar = mk_cubo(altar_cor)
    vao_ecoV  = mk_cubo(eco_verde)
    vao_ecoA  = mk_cubo(eco_azul)
    vao_ecoR  = mk_cubo(eco_verm)

    vao_portalA = mk_cubo(portal_azul)
    vao_portalR = mk_cubo(portal_verm)
    vao_portalV = mk_cubo(portal_verd)


    # =========================
    # MODELOS
    # =========================
    modelo_player  = ModeloBlocos(vao_pele, vao_roupa, vao_bota, vao_det, vao_metal, vao_madeira)
    modelo_inimigos = ModeloInimigos(vao_inim_corpo, vao_inim_cabeca, vao_metal, vao_madeira, vao_corda)

    # =========================
    # CENÁRIO
    # =========================
    plataformas = [
        Plataforma(0, 0,   20, -20, 0, plat1_cor),
        Plataforma(0, -15, 10, -10, 4, plat2_cor),
    ]
    ramp = Rampa(0, -7.5, 8, -8, 0, 4, ramp_cor)

    # =========================
    # ESTADO DO JOGO
    # =========================
    player = Player()

    X_START = -18.0
    X_END   =  18.0

    ALTAR_X, ALTAR_Z = 17.0, 0.0
    ALTAR_RAIO = 1.2

    player.x = X_START + 1.0
    player.z = 0.0

    mundo_atual = WORLD_OVER
    cfg_mundo = WORLD_CFG[mundo_atual]
    set_uTint(programa, cfg_mundo["tint"])

    ecos = {WORLD_OVER: False, WORLD_ETER: False, WORLD_UNDER: False}

    # =========================
    # TRECHOS (T0..T6)
    # =========================
    ZMIN, ZMAX = -10.0, 10.0
    trechos = [
        Trecho(0, "Templo", (X_START, -12.0, ZMIN, ZMAX), {
            WORLD_OVER: [],
            WORLD_ETER: [],
            WORLD_UNDER: [],
        }, chave=False),

        Trecho(1, "Tutorial", (-12.0, -6.0, ZMIN, ZMAX), {
            WORLD_OVER: [SpawnInfo("melee", -9.0,  0.0)],
            WORLD_ETER: [SpawnInfo("ranged", -9.0, 3.0)],
            WORLD_UNDER:[SpawnInfo("melee", -10.0, -2.0), SpawnInfo("melee", -8.0, 2.0)],
        }, chave=False),

        Trecho(2, "Guarda do Plato", (-6.0, 0.0, ZMIN, ZMAX), {
            WORLD_OVER: [SpawnInfo("ranged", -2.0, 5.0), SpawnInfo("melee", -3.0, 0.0)],
            WORLD_ETER: [SpawnInfo("ranged", -2.0, 5.0), SpawnInfo("ranged", -4.0, 4.0)],
            WORLD_UNDER:[SpawnInfo("melee", -4.0, 0.0), SpawnInfo("melee", -1.0, -2.0), SpawnInfo("ranged", -5.0, 6.0)],
        }, chave=True),

        Trecho(3, "Travessia", (0.0, 6.0, ZMIN, ZMAX), {
            WORLD_OVER: [SpawnInfo("melee", 2.0, -2.0), SpawnInfo("ranged", 4.0, 5.0)],
            WORLD_ETER: [SpawnInfo("ranged", 2.0, 5.0), SpawnInfo("ranged", 5.0, 4.0)],
            WORLD_UNDER:[SpawnInfo("melee", 2.0, -2.0), SpawnInfo("melee", 4.0, 0.0), SpawnInfo("melee", 5.0, 2.0)],
        }, chave=True),

        Trecho(4, "Pressao", (6.0, 12.0, ZMIN, ZMAX), {
            WORLD_OVER: [SpawnInfo("melee", 8.0, -2.0), SpawnInfo("melee", 10.0, 2.0), SpawnInfo("ranged", 11.0, 5.0)],
            WORLD_ETER: [SpawnInfo("ranged", 8.0, 5.0), SpawnInfo("ranged", 10.0, 4.0), SpawnInfo("ranged", 11.0, 3.0), SpawnInfo("melee", 9.0, -1.0)],
            WORLD_UNDER:[SpawnInfo("melee", 8.0, -2.0), SpawnInfo("melee", 10.0, 0.0), SpawnInfo("melee", 11.0, 2.0), SpawnInfo("ranged", 12.0, 5.0)],
        }, chave=True),

        Trecho(5, "Pre-final", (12.0, 16.0, ZMIN, ZMAX), {
            WORLD_OVER: [SpawnInfo("melee", 13.0, 0.0), SpawnInfo("ranged", 15.0, 5.0)],
            WORLD_ETER: [SpawnInfo("ranged", 13.0, 5.0), SpawnInfo("ranged", 15.0, 4.0), SpawnInfo("melee", 14.0, -1.0)],
            WORLD_UNDER:[SpawnInfo("melee", 13.0, 0.0), SpawnInfo("melee", 14.0, -2.0), SpawnInfo("melee", 15.0, 2.0), SpawnInfo("melee", 15.5, 0.0)],
        }, chave=True),

        Trecho(6, "Eco", (16.0, X_END, ZMIN, ZMAX), {
            WORLD_OVER: [],
            WORLD_ETER: [],
            WORLD_UNDER: [],
        }, chave=False),
    ]

    fase = Fase(trechos, leash_radius=7.0)

    # =========================
    # INPUT
    # =========================
    keys = {}

    def trocar_mundo(novo_mundo: int):
        nonlocal mundo_atual, cfg_mundo
        mundo_atual = novo_mundo
        cfg_mundo = WORLD_CFG[mundo_atual]
        set_uTint(programa, cfg_mundo["tint"])
        fase.reset_mundo()

        player.x = X_START + 1.0
        player.z = 0.0
        player.y = 1.0

    def key_cb(win, k, s, a, m):
        if a == glfw.PRESS:
            keys[k] = True
        elif a == glfw.RELEASE:
            keys[k] = False

        if k == glfw.KEY_SPACE and a == glfw.PRESS and player.vivo:
            player.ataque = True
            player.temp = 0

        if k == glfw.KEY_E and a == glfw.PRESS:
            keys["E_PRESS"] = True

        if a == glfw.PRESS and k in (glfw.KEY_1, glfw.KEY_2, glfw.KEY_3):
            if k == glfw.KEY_1:
                trocar_mundo(WORLD_OVER)
            elif k == glfw.KEY_2:
                trocar_mundo(WORLD_ETER)
            elif k == glfw.KEY_3:
                trocar_mundo(WORLD_UNDER)

    glfw.set_key_callback(win, key_cb)

    proj = perspectiva(math.radians(60), w / h, 0.1, 200)
    last = glfw.get_time()

    dbg_t = 0.0

    while not glfw.window_should_close(win):
        now = glfw.get_time()
        dt = now - last
        last = now

        glfw.poll_events()

        if player.vivo:
            player.update(dt, keys, plataformas, ramp)

        fase.update(player, mundo_atual, cfg_mundo, cor_inim=inim_corpo)
        inimigos = fase.inimigos_todos()

        if mundo_atual == WORLD_UNDER:
            melee_perto = False
            for m in inimigos:
                if m.vivo and m.tipo == "melee":
                    d = math.hypot(m.x - player.x, m.z - player.z)
                    if d < 2.5:
                        melee_perto = True
                        break
            for e in inimigos:
                if e.tipo == "ranged":
                    e.can_shoot = melee_perto
        else:
            for e in inimigos:
                if e.tipo == "ranged":
                    e.can_shoot = True

        for e in inimigos:
            e.update(dt, player)

        atk = player.espada_box() if player.vivo else None
        if atk:
            for e in inimigos:
                if e.vivo and colisaoINI(atk, e.aabb()):
                    e.tomar_dano(1)

        dist_altar = math.hypot(player.x - ALTAR_X, player.z - ALTAR_Z)

        mundo_ok = fase.mundo_completo()
        eco_coletavel = (not ecos[mundo_atual]) and mundo_ok

        acabou_de_coletar = False
        if eco_coletavel and dist_altar < ALTAR_RAIO:
            ecos[mundo_atual] = True
            acabou_de_coletar = True

        portal_ativo = ecos[mundo_atual] or acabou_de_coletar
        e_press = keys.pop("E_PRESS", False)
        if portal_ativo and dist_altar < ALTAR_RAIO and e_press:
            trocar_mundo(proximo_mundo(mundo_atual))

        dbg_t += dt
        if dbg_t > 1.0:
            dbg_t = 0.0
            print("DBG mundo:", cfg_mundo["name"],
                  "trecho:", fase.trecho_atual_id,
                  "mundo_ok:", mundo_ok,
                  "eco_já:", ecos[mundo_atual],
                  "dist_altar:", round(dist_altar, 2),
                  "playerX:", round(player.x, 2))

        if mundo_atual == WORLD_OVER:
            vao_eco = vao_ecoV
            vao_portal = vao_portalA
        elif mundo_atual == WORLD_ETER:
            vao_eco = vao_ecoA
            vao_portal = vao_portalR
        else:
            vao_eco = vao_ecoR
            vao_portal = vao_portalV

        # =========================
        # RENDER
        # =========================
        sky = cfg_mundo["sky"]
        glClearColor(float(sky[0]), float(sky[1]), float(sky[2]), 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        cam_eye = np.array([player.x, player.y + 7, player.z + 14], dtype=np.float32)
        cam_tgt = np.array([player.x, player.y, player.z], dtype=np.float32)
        view = look_at(cam_eye, cam_tgt, np.array([0, 1, 0], dtype=np.float32))
        vp = proj @ view

        desenhar(cubo_ground, translacao(0, -0.51, 0) @ escala(40, 1, 40), vp, programa)

        for p in plataformas:
            vao = cubo_plat1 if p.h == 0 else cubo_plat2

            # plataforma do chão (fininha, só “superfície”)
            if p.h == 0:
                desenhar(
                    vao,
                    translacao(p.x, -0.5, p.z) @ escala(p.w, 1, p.d),
                    vp, programa
                )
            else:
                # plataforma alta vira um BLOCO que encosta no chão (base em y=0)
                altura = float(p.h)
                desenhar(
                    vao,
                    translacao(p.x, altura / 2.0, p.z) @ escala(p.w, altura, p.d),
                    vp, programa
                )


        # ✅ RAMPA SÓLIDA (prisma) - substitui a “folha” diagonal
        sz = abs(ramp.d)
        sz_draw = -sz if ramp.d < 0 else sz
        desenhar(
            vao_rampa_solida,
            translacao(ramp.x, ramp.y0 + 0.001, ramp.z) @ escala(ramp.w, (ramp.y1 - ramp.y0), sz_draw),
            vp, programa
        )

        model = translacao(ALTAR_X, 0.0, ALTAR_Z) @ escala(2.0, 0.6, 2.0)
        desenhar(vao_altar, model, vp, programa)

        if eco_coletavel:
            model = translacao(ALTAR_X, 1.3, ALTAR_Z) @ escala(0.6, 0.6, 0.6)
            desenhar(vao_eco, model, vp, programa)

        if portal_ativo:
            model = translacao(ALTAR_X, 1.4, ALTAR_Z) @ escala(1.2, 2.2, 0.4)
            desenhar(vao_portal, model, vp, programa)

        if player.vivo:
            modelo_player.draw_link(
                desenhar, programa, vp,
                player.x, player.y, player.z,
                player.face, now,
                andando=player_esta_andando(keys),
                atacando=player.ataque
            )

        for e in inimigos:
            if not e.vivo:
                continue

            face = inimigo_face_para_player(e, player)

            if e.tipo == "melee":
                modelo_inimigos.draw_melee(desenhar, programa, vp, e.x, e.y, e.z, face)
            else:
                modelo_inimigos.draw_ranged(desenhar, programa, vp, e.x, e.y, e.z, face)

            for f in e.flechas_ativas:
                px, py, pz = float(f["pos"][0]), float(f["pos"][1]), float(f["pos"][2])
                vx, vz = float(f["vel"][0]), float(f["vel"][2])
                yaw = math.atan2(vx, vz)
                desenhar_flecha(desenhar, programa, vp, px, py, pz, yaw, vao_madeira, vao_metal, vao_pena)

        # HUD VIDA
        frac = 0.0
        if player.vida_max > 0:
            frac = max(0.0, min(1.0, player.vida / player.vida_max))

        forward = cam_tgt - cam_eye
        norm = np.linalg.norm(forward)
        if norm < 1e-6:
            forward = np.array([0, 0, -1], dtype=np.float32)
        else:
            forward = forward / norm

        up = np.array([0, 1, 0], dtype=np.float32)
        right = np.cross(forward, up)
        rnorm = np.linalg.norm(right)
        if rnorm < 1e-6:
            right = np.array([1, 0, 0], dtype=np.float32)
        else:
            right = right / rnorm

        hud_pos = cam_eye + forward * 6.0 + right * (-3.4) + up * (2.70)

        glDisable(GL_DEPTH_TEST)

        model = translacao(float(hud_pos[0]), float(hud_pos[1]), float(hud_pos[2])) @ escala(2.8, 0.18, 0.12)
        desenhar(hud_bg, model, vp, programa)

        hp_pos = hud_pos + right * (-(1.4) * (1 - frac))
        model = translacao(float(hp_pos[0]), float(hp_pos[1]), float(hp_pos[2])) @ escala(2.8 * frac, 0.14, 0.10)
        desenhar(hud_hp, model, vp, programa)

        glEnable(GL_DEPTH_TEST)

        glfw.swap_buffers(win)

    glfw.terminate()

if __name__ == "__main__":
    main()
