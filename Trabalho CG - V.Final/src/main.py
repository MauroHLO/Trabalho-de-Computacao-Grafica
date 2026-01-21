import glfw
from OpenGL.GL import *
import numpy as np
import math
from pathlib import Path

# === Engine ===
from engine.transformacoes import ortho, perspectiva, translacao, escala, look_at
from engine.geometrias import criarCubo, criarPlataforma, criarRampaSolida, criarVAO
from engine.colisao import colisaoINI
from engine.texturas import Texture2D

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
with open("src/assets/shaders/basic.vert", "r", encoding="utf-8") as f:
    VERT = f.read()

with open("src/assets/shaders/basic.frag", "r", encoding="utf-8") as f:
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
    
    # <----------------------------->
    # TEXTURAS (ATLAS)
    # <----------------------------->
    atlas_pedra_grama = Texture2D.from_file(
        "src/textures/atlas_pedra_grama.png",
        flip_y=True,
        generate_mipmaps=False,
        min_filter=GL_NEAREST,
        mag_filter=GL_NEAREST,
        wrap_s=GL_REPEAT,
        wrap_t=GL_REPEAT,
    )
    
    atlas_parede_gelo = Texture2D.from_file(
        "src/textures/atlas_parede_gelo.png",
        flip_y=True,
        generate_mipmaps=False,
        min_filter=GL_NEAREST,
        mag_filter=GL_NEAREST,
        wrap_s=GL_REPEAT,
        wrap_t=GL_REPEAT,
    )
    
    atlas_parede_under = Texture2D.from_file(
        "src/textures/atlas_parede_under.png",
        flip_y=True,
        generate_mipmaps=False,
        min_filter=GL_NEAREST,
        mag_filter=GL_NEAREST,
        wrap_s=GL_REPEAT,
        wrap_t=GL_REPEAT,
    )
    
    # === Texturas ===   
    #Overworld   
    text_over = Texture2D.from_file("src/textures/Chao_Grama.png")     
    atlas_over = atlas_pedra_grama
    rampa_over = Texture2D.from_file("src/textures/Chao_Caverna.png")

    # Eter (gelo)
    text_eter = Texture2D.from_file("src/textures/Chao_Gelo.png")
    atlas_eter = atlas_parede_gelo    
    rampa_eter = Texture2D.from_file("src/textures/rampa_gelo.png")

    # Under (caverna)
    text_under = Texture2D.from_file("src/textures/Chao_Under.png")
    atlas_under= atlas_parede_under 
    rampa_under = Texture2D.from_file("src/textures/Chao_Under.png") 

    TEX_MUNDO = {
        WORLD_OVER: {
            "chao":  text_over,   
            "parede": atlas_over,  
            "rampa": rampa_over,  
        },
        WORLD_ETER: {
            "chao":  text_eter,      
            "parede": atlas_eter,    
            "rampa": rampa_eter,     
        },
        WORLD_UNDER: {
            "chao":  text_under,    
            "parede": atlas_under,   
            "rampa": rampa_under,    
        },
    }

    text_chao  = TEX_MUNDO[WORLD_OVER]["chao"]
    text_parede = TEX_MUNDO[WORLD_OVER]["parede"]
    text_rampa = TEX_MUNDO[WORLD_OVER]["rampa"]


    # <----------------------------->
    # CORES / MATERIAIS
    # <----------------------------->
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
    cor_dummy   = (0.0, 0.0, 0.0)

    # <----------------------------->
    # VAOs (pos + normal + tint)
    # <----------------------------->

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


    # <----------------------------->
    # MODELOS
    # <----------------------------->
    modelo_player  = ModeloBlocos(vao_pele, vao_roupa, vao_bota, vao_det, vao_metal, vao_madeira)
    modelo_inimigos = ModeloInimigos(vao_inim_corpo, vao_inim_cabeca, vao_metal, vao_madeira, vao_corda)

    # <----------------------------->
    # CENÁRIO 
    # <----------------------------->
    def criar_mapa(plat1_cor, plat2_cor, ramp_cor):

        plataformas = [
            # chão base (grande)
            Plataforma(0, 0,  42, -42, 0, plat1_cor),

            # PAREDES FINAS DA BORDA (INVISÍVEIS)
            # esquerda
            Plataforma(-22, 0, 1.0, -42.0, 10.0, cor_dummy, visivel=False),
            # direita
            Plataforma(22, 0, 1.0, -42.0, 10.0, cor_dummy, visivel=False),
            # cima
            Plataforma(0, 22, 42.0, -1.0, 10.0, cor_dummy, visivel=False),
            # baixo
            Plataforma(0, -22, 42.0, -1.0, 10.0, cor_dummy, visivel=False),
]


        Z_WALL = 16.5
        D_WALL = -9.0  
        H_WALL = 7.0

        plataformas += [
            Plataforma(-15.0,  Z_WALL, 14.0, D_WALL, H_WALL, plat2_cor),
            Plataforma(  0.0,  Z_WALL, 16.0, D_WALL, H_WALL, plat2_cor),
            Plataforma( 15.0,  Z_WALL, 14.0, D_WALL, H_WALL, plat2_cor),
        ]

        plataformas += [
            Plataforma(-15.0, -Z_WALL, 14.0, D_WALL, H_WALL, plat2_cor),
            Plataforma(  0.0, -Z_WALL, 16.0, D_WALL, H_WALL, plat2_cor),
            Plataforma( 15.0, -Z_WALL, 14.0, D_WALL, H_WALL, plat2_cor),
        ]

        plataformas += [
            Plataforma(-7,  9,  8.0, -6.0, H_WALL, plat2_cor),
            Plataforma( 17.5, -10.0,  8.5, -5.0, H_WALL, plat2_cor),
            Plataforma(17.5,  9.0,  9, -6.0, H_WALL, plat2_cor),
        ]

        # TERRENO ALTO (ranged em cima)
        plat1 = Plataforma(-3.5,  7.5,  6.5, -5.5, 3.5, plat2_cor)
        plataformas += [plat1]

        plat2 = Plataforma(11.5, -9.8,  7.0, -6.0, 4.0, plat2_cor)
        plataformas += [plat2]

        rampas = [
            Rampa(-3.5,  3.0,  5.0,  5.5, 0.0, 3.5, ramp_cor),   
            Rampa(11.5, -3.8,  5.5, -6.0, 0.0, 4.0, ramp_cor),   
        ]

        return plataformas, rampas


    plataformas, rampas = criar_mapa(plat1_cor, plat2_cor, ramp_cor)


    # <----------------------------->
    # ESTADO DO JOGO
    # <----------------------------->
    player = Player()

    X_START = -18.0
    X_END   =  18.0

    ALTAR_X, ALTAR_Z = 17.0, 0.0
    ALTAR_RAIO = 1.2

    player.x = X_START + 1.0
    player.z = 0.0
    
    # <----------------------------->
    # BAU (tutorial + endgame)
    # <----------------------------->
    BAU_RAIO_INTERACAO = 1.6

    bau_x = player.x
    bau_z = player.z - 2.0
    bau_y = 0.0

    tutorial_estado = 0

    endgame_ativo = False

    def dist_xz(ax, az, bx, bz):
        return math.hypot(ax - bx, az - bz)

    def bau_perto_do_player():
        return dist_xz(player.x, player.z, bau_x, bau_z) <= BAU_RAIO_INTERACAO

    def tem_todos_fragmentos():
        return bool(ecos[WORLD_OVER] and ecos[WORLD_ETER] and ecos[WORLD_UNDER])

    mundo_atual = WORLD_OVER
    cfg_mundo = WORLD_CFG[mundo_atual]
    set_uTint(programa, cfg_mundo["tint"])

    ecos = {WORLD_OVER: False, WORLD_ETER: False, WORLD_UNDER: False}

    # <----------------------------->
    # TRECHOS
    # <----------------------------->
    ZMIN, ZMAX = -8.5, 8.5
    trechos = [
        Trecho(0, "Entrada", (X_START, -13.0, ZMIN, ZMAX), {
            WORLD_OVER: [],
            WORLD_ETER: [],
            WORLD_UNDER: [],
        }, chave=False),

        Trecho(1, "Encontro 1", (-13.0, -7.5, ZMIN, ZMAX), {
            WORLD_OVER:  [SpawnInfo("melee", -11.0,  1.0), SpawnInfo("melee", -9.5, -1.0)],
            WORLD_ETER:  [SpawnInfo("ranged", -11.0,  2.5), SpawnInfo("melee", -9.8, -1.5)],
            WORLD_UNDER: [SpawnInfo("melee", -11.2, -2.0), SpawnInfo("melee", -9.2,  2.0)],
        }, chave=True),

        Trecho(2, "Subida Platô 1", (-7.5, -1.0, ZMIN, ZMAX), {
            WORLD_OVER:  [SpawnInfo("melee", -6.2,  -0.5), SpawnInfo("ranged", -6.8,  1.8)],
            # Mundo 2: ranged no topo do 1
            WORLD_ETER:  [SpawnInfo("ranged", -5.0,  7.0), SpawnInfo("ranged", -2.0,  6.0)],
            WORLD_UNDER: [SpawnInfo("melee", -5.5, -1.5), SpawnInfo("ranged", -3.0,  7.0)],
        }, chave=True),

        Trecho(3, "Corredor Central", (-1.0, 6.0, ZMIN, ZMAX), {
            WORLD_OVER:  [SpawnInfo("melee",  1.0,  1.5), SpawnInfo("melee",  3.0, -1.5)],
            WORLD_ETER:  [SpawnInfo("ranged", 2.0,  2.5), SpawnInfo("ranged", 4.0, -2.5)],
            WORLD_UNDER: [SpawnInfo("melee",  1.5,  2.0), SpawnInfo("melee",  4.0,  0.0)],
        }, chave=True),

        Trecho(4, "Subida Platô 2", (6.0, 12.5, ZMIN, ZMAX), {
            WORLD_OVER:  [SpawnInfo("ranged",  8.8, -1.8), SpawnInfo("melee",  8.0,  1.2)],
            # Mundo 2: ranged no 2
            WORLD_ETER:  [SpawnInfo("ranged", 11.0, -7.0), SpawnInfo("ranged", 17.0, -6.0)],
            WORLD_UNDER: [SpawnInfo("melee",   8.5,  0.5), SpawnInfo("ranged", 11.0, -7.0)],
        }, chave=True),

        Trecho(5, "Pré-Altar", (12.5, 15.5, ZMIN, ZMAX), {
            WORLD_OVER:  [SpawnInfo("melee",  13.5,  1.0)],
            WORLD_ETER:  [SpawnInfo("ranged", 13.7, -2.0), SpawnInfo("melee", 13.0,  2.0)],
            WORLD_UNDER: [SpawnInfo("melee",  13.2, -1.0), SpawnInfo("melee", 14.2,  2.0)],
        }, chave=True),

        Trecho(6, "Altar", (15.5, X_END, ZMIN, ZMAX), {
            WORLD_OVER: [],
            WORLD_ETER: [],
            WORLD_UNDER: [],
        }, chave=False),
    ]


    fase = Fase(trechos, leash_radius=7.0)

    # <----------------------------->
    # Movimentação
    # <----------------------------->
    keys = {}

    def trocar_mundo(novo_mundo: int):
        nonlocal mundo_atual, cfg_mundo, text_chao, text_parede, text_rampa

        mundo_atual = novo_mundo
        cfg_mundo = WORLD_CFG[mundo_atual]
        set_uTint(programa, cfg_mundo["tint"])

        text_chao   = TEX_MUNDO[mundo_atual]["chao"]
        text_parede = TEX_MUNDO[mundo_atual]["parede"]
        text_rampa  = TEX_MUNDO[mundo_atual]["rampa"]

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
            player.update(dt, keys, plataformas, rampas)

        fase.update(player, mundo_atual, cfg_mundo, plataformas, rampas, cor_inim=inim_corpo)
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
            e.update(dt, player, plataformas, rampas)

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

        # <----------------------------->
        # INTERAÇÃO COM BAÚ (prioridade sobre portal)
        # <----------------------------->
        if e_press and (mundo_atual == WORLD_OVER):
            if endgame_ativo:
                pass
            else:
                # 1) abre tutorial
                if tutorial_estado == 0 and bau_perto_do_player():
                    tutorial_estado = 1
                    e_press = False

                # 2) fecha tutorial
                elif tutorial_estado == 1:
                    tutorial_estado = 2
                    e_press = False

                # 3) endgame (só com 3 fragmentos)
                elif tutorial_estado == 2 and bau_perto_do_player() and tem_todos_fragmentos():
                    endgame_ativo = True
                    e_press = False

        # <----------------------------->
        # PORTAL (só se não consumiu E no baú)
        # <----------------------------->
        if portal_ativo and dist_altar < ALTAR_RAIO and e_press and (not endgame_ativo) and (tutorial_estado != 1):
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


        # <----------------------------->
        # RENDER
        # <----------------------------->
        sky = cfg_mundo["sky"]
        glClearColor(float(sky[0]), float(sky[1]), float(sky[2]), 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        cam_eye = np.array([player.x - 18, player.y + 24, player.z], dtype=np.float32)
        cam_tgt = np.array([player.x, player.y, player.z], dtype=np.float32)
        view = look_at(cam_eye, cam_tgt, np.array([0, 1, 0], dtype=np.float32))
        vp = proj @ view


        # <----------------------------->
        # ILUMINAÇÃO
        # <----------------------------->
        if mundo_atual == WORLD_OVER:
            dir_dir = (0.25, -1.0, 0.20)
            dir_color = (1.00, 0.98, 0.92)   # sol
            dir_int = 1.15
            amb = 0.22

            p_col = [(1.0, 0.95, 0.85)] * 4  # tochas
        elif mundo_atual == WORLD_ETER:
            dir_dir = (0.10, -1.0, -0.15)
            dir_color = (0.70, 0.85, 1.10)   # sol frio
            dir_int = 1.05
            amb = 0.18

            p_col = [(0.65, 0.85, 1.25)] * 4 # cristais brilhantes
        else:  
            dir_dir = (-0.10, -1.0, 0.05)
            dir_color = (1.10, 0.55, 0.40)   # Sol mais forte
            dir_int = 0.85
            amb = 0.12

            p_col = [(1.25, 0.55, 0.35)] * 4 # fogo/lava

        p_pos = [
            (-12.0, 2.0,  0.0),          
            (-3.5,  3.2,  7.5),           
            (11.5,  3.5, -7.8),           
            (ALTAR_X, 3.0, ALTAR_Z),      
        ]

        p_int = [1.2, 1.0, 1.0, 1.6]
        p_rng = [12.0, 10.0, 10.0, 14.0]

        cam_pos = (float(cam_eye[0]), float(cam_eye[1]), float(cam_eye[2]))

        desenhar(
            cubo_ground, translacao(0, -0.51, 0) @ escala(40, 1, 40), vp, programa, view_pos=cam_pos, 
            dir_dir=dir_dir, dir_color=dir_color, dir_intensity=dir_int, ambient_strength=amb,
            point_pos=p_pos, point_color=p_col, point_intensity=p_int, point_range=p_rng, tex=text_chao, use_tex=True
            )

        for p in plataformas:
            
            if not getattr(p, "visivel", True):
                continue
            
            vao = cubo_plat1 if p.h == 0 else cubo_plat2

            if p.h == 0:
                desenhar(
                    vao,
                    translacao(p.x, -0.5, p.z) @ escala(p.w, 1, p.d),
                    vp, programa, view_pos=cam_pos, 
                    dir_dir=dir_dir, dir_color=dir_color, dir_intensity=dir_int, ambient_strength=amb,
                    point_pos=p_pos, point_color=p_col, point_intensity=p_int, point_range=p_rng, tex=text_parede, use_tex=True
                )
            else:
                altura = float(p.h)
                desenhar(
                    vao,
                    translacao(p.x, altura / 2.0, p.z) @ escala(p.w, altura, p.d),
                    vp, programa, view_pos=cam_pos, 
                    dir_dir=dir_dir, dir_color=dir_color, dir_intensity=dir_int, ambient_strength=amb,
                    point_pos=p_pos, point_color=p_col, point_intensity=p_int, point_range=p_rng, tex=text_parede, use_tex=True
                )

        for r in rampas:
            sz = abs(r.d)
            sz_draw = -sz if r.d < 0 else sz

            desenhar(
                vao_rampa_solida,
                translacao(r.x, r.y0 + 0.001, r.z)
                @ escala(r.w, (r.y1 - r.y0), sz_draw),
                vp, programa, view_pos=cam_pos, 
                dir_dir=dir_dir, dir_color=dir_color, dir_intensity=dir_int, ambient_strength=amb,
                point_pos=p_pos, point_color=p_col, point_intensity=p_int, point_range=p_rng, tex=text_rampa, use_tex=True
            )


        # <----------------------------->
        # DESENHA BAÚ
        # <----------------------------->
        if mundo_atual == WORLD_OVER:
            desenhar(
                vao_madeira,
                translacao(bau_x, 0.35, bau_z) @ escala(1.2, 0.7, 0.9),
                vp, programa, view_pos=cam_pos, 
                dir_dir=dir_dir, dir_color=dir_color, dir_intensity=dir_int, ambient_strength=amb,
                point_pos=p_pos, point_color=p_col, point_intensity=p_int, point_range=p_rng
                )
            desenhar(
                vao_madeira,
                translacao(bau_x, 0.75, bau_z) @ escala(1.25, 0.25, 0.95),
                vp, programa, view_pos=cam_pos, 
                dir_dir=dir_dir, dir_color=dir_color, dir_intensity=dir_int, ambient_strength=amb,
                point_pos=p_pos, point_color=p_col, point_intensity=p_int, point_range=p_rng
                )
            desenhar(
                vao_metal,
                translacao(bau_x, 0.55, bau_z + 0.48) @ escala(0.25, 0.25, 0.10),
                vp, programa, view_pos=cam_pos, 
                dir_dir=dir_dir, dir_color=dir_color, dir_intensity=dir_int, ambient_strength=amb,
                point_pos=p_pos, point_color=p_col, point_intensity=p_int, point_range=p_rng
                )


        model = translacao(ALTAR_X, 0.0, ALTAR_Z) @ escala(2.0, 0.6, 2.0)
        desenhar(vao_altar, model, vp, programa, view_pos=cam_pos, 
            dir_dir=dir_dir, dir_color=dir_color, dir_intensity=dir_int, ambient_strength=amb,
            point_pos=p_pos, point_color=p_col, point_intensity=p_int, point_range=p_rng
            )

        if eco_coletavel:
            model = translacao(ALTAR_X, 1.3, ALTAR_Z) @ escala(0.6, 0.6, 0.6)
            desenhar(vao_eco, model, vp, programa, view_pos=cam_pos, 
            dir_dir=dir_dir, dir_color=dir_color, dir_intensity=dir_int, ambient_strength=amb,
            point_pos=p_pos, point_color=p_col, point_intensity=p_int, point_range=p_rng
            )

        if portal_ativo:
            model = translacao(ALTAR_X, 1.4, ALTAR_Z) @ escala(1.2, 2.2, 0.4)
            desenhar(vao_portal, model, vp, programa, view_pos=cam_pos, 
            dir_dir=dir_dir, dir_color=dir_color, dir_intensity=dir_int, ambient_strength=amb,
            point_pos=p_pos, point_color=p_col, point_intensity=p_int, point_range=p_rng)

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

        # <----------------------------->
        # HUD VIDA
        # <----------------------------->
        frac = 0.0
        if player.vida_max > 0:
            frac = max(0.0, min(1.0, player.vida / player.vida_max))

        vp_hud = ortho(-1, 1, -1, 1)

        glDisable(GL_DEPTH_TEST)

        HUD_X = -0.78
        HUD_Y =  0.82

        HUD_W = 0.55
        HUD_H = 0.06

        # Fundo (barra vazia)
        model_bg = translacao(HUD_X, HUD_Y, 0.0) @ escala(HUD_W, HUD_H, 1.0)
        desenhar(hud_bg, model_bg, vp_hud, programa, unlit=True)

        fill_w = HUD_W * frac
        shift = (HUD_W - fill_w) * 0.5

        model_hp = translacao(HUD_X - shift, HUD_Y, 0.0) @ escala(fill_w, HUD_H * 0.75, 1.0)
        desenhar(hud_hp, model_hp, vp_hud, programa, unlit=True)
        
        # <----------------------------->
        # HUD FRAGMENTOS (3 mundos)
        # <----------------------------->
        FR_X0 = -0.10
        FR_Y  =  0.82
        FR_S  =  0.07
        FR_GAP = 0.09

        # fundo "vazio"
        for i in range(3):
            x = FR_X0 + i * FR_GAP
            desenhar(hud_bg, translacao(x, FR_Y, 0.0) @ escala(FR_S, FR_S, 1.0), vp_hud, programa, unlit=True)

        if ecos[WORLD_OVER]:
            desenhar(vao_ecoV, translacao(FR_X0 + 0 * FR_GAP, FR_Y, 0.0) @ escala(FR_S * 0.85, FR_S * 0.85, 1.0), vp_hud, programa, unlit=True)
        if ecos[WORLD_ETER]:
            desenhar(vao_ecoA, translacao(FR_X0 + 1 * FR_GAP, FR_Y, 0.0) @ escala(FR_S * 0.85, FR_S * 0.85, 1.0), vp_hud, programa, unlit=True)
        if ecos[WORLD_UNDER]:
            desenhar(vao_ecoR, translacao(FR_X0 + 2 * FR_GAP, FR_Y, 0.0) @ escala(FR_S * 0.85, FR_S * 0.85, 1.0), vp_hud, programa, unlit=True)

        # <----------------------------->
        # OVERLAYS 
        # <----------------------------->

        # tutorial painel
        if tutorial_estado == 1:
            desenhar(hud_bg, translacao(0.0, 0.0, 0.0) @ escala(1.6, 0.75, 1.0), vp_hud, programa, unlit=True)
            desenhar(hud_hp, translacao(0.0, 0.18, 0.0) @ escala(1.45, 0.08, 1.0), vp_hud, programa, unlit=True)
            desenhar(hud_hp, translacao(0.0, 0.05, 0.0) @ escala(1.25, 0.05, 1.0), vp_hud, programa, unlit=True)
            desenhar(hud_hp, translacao(0.0, -0.05, 0.0) @ escala(1.35, 0.05, 1.0), vp_hud, programa, unlit=True)
            desenhar(hud_hp, translacao(0.0, -0.20, 0.0) @ escala(0.95, 0.04, 1.0), vp_hud, programa, unlit=True)

        # endgame painel
        if endgame_ativo:
            desenhar(hud_bg, translacao(0.0, 0.0, 0.0) @ escala(1.8, 0.9, 1.0), vp_hud, programa, unlit=True)
            desenhar(hud_hp, translacao(0.0, 0.22, 0.0) @ escala(1.3, 0.10, 1.0), vp_hud, programa, unlit=True)
            desenhar(hud_hp, translacao(0.0, 0.02, 0.0) @ escala(1.0, 0.07, 1.0), vp_hud, programa, unlit=True)

        glEnable(GL_DEPTH_TEST)

        glfw.swap_buffers(win)

    glfw.terminate()

if __name__ == "__main__":
    main()
