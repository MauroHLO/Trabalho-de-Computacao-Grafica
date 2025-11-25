import glfw
from OpenGL.GL import *
import numpy as np
import math
import ctypes
import time

# === Engine ===
from engine.transformacoes import perspectiva, translacao, escala, rotacaoX, look_at
from engine.geometrias import criarCubo, criarPlataforma, criarVAO
from engine.colisao import colisaoINI

# === Game ===
from game.jogador import Player
from game.inimigo import Inimigo
from game.plataforma import Plataforma
from game.rampa import Rampa

# === Core ===
from core.renderizador import desenhar
from core.shaders import criarPrograma

# === Carregar shaders dos arquivos ===
with open("src/assets/shaders/basic.vert") as f:
    VERT = f.read()
with open("src/assets/shaders/basic.frag") as f:
    FRAG = f.read()


def main():
    if not glfw.init(): return
    w,h=1600,900
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR,3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR,3)
    glfw.window_hint(glfw.OPENGL_PROFILE,glfw.OPENGL_CORE_PROFILE)
    win=glfw.create_window(w,h,"zelda_proto",None,None)
    glfw.make_context_current(win)

    glEnable(GL_DEPTH_TEST)
    programa = criarPrograma(VERT,FRAG)
    glUseProgram(programa)

    # CORES SUAVES ESTILO ZELDA
    ground_cor = [0.33, 0.60, 0.28]
    plat1_cor = [0.58, 0.42, 0.20]    
    plat2_cor = [0.70, 0.55, 0.30]    
    ramp_cor = [0.64, 0.48, 0.24]
    link_cor = [0.10, 0.45, 0.15]    
    Inimigo1_cor = [0.75, 0.20, 0.20]
    Inimigo2_cor = [0.15, 0.25, 0.60]
    espada_cor = [0.8, 0.8, 0.8]

    # Meshes
    cubo_link = criarVAO(*criarCubo(link_cor))
    cubo_Inimigo1 = criarVAO(*criarCubo(Inimigo1_cor))
    cubo_Inimigo2 = criarVAO(*criarCubo(Inimigo2_cor))
    cubo_ground = criarVAO(*criarCubo(ground_cor))
    cubo_plat1 = criarVAO(*criarCubo(plat1_cor))
    cubo_plat2 = criarVAO(*criarCubo(plat2_cor))
    plane_ramp = criarVAO(*criarPlataforma(ramp_cor))
    cubo_espada = criarVAO(*criarCubo(espada_cor))

    # Cenário
    plataformas = [
        Plataforma(0,0,20,-20,0, plat1_cor),
        Plataforma(0,-15,10,-10,4, plat2_cor)
    ]

    # aqui d = -8 (negativo) é aceito agora
    ramp = Rampa(0, -7.5, 8, -8, 0, 4, ramp_cor)

    player = Player()
    inimigos = [
        Inimigo(3,2, Inimigo1_cor, "melee"),
        Inimigo(-6,-6,Inimigo2_cor,"ranged")
    ]

    # Input
    keys={}
    def key_cb(win,k,s,a,m):
        if a==glfw.PRESS: keys[k]=True
        if a==glfw.RELEASE: keys[k]=False
        if k==glfw.KEY_SPACE and a==glfw.PRESS:
            player.ataque=True
            player.temp=0
    glfw.set_key_callback(win,key_cb)

    proj = perspectiva(math.radians(60), w/h, 0.1,200)
    last=glfw.get_time()

    # ---------------------------
    # LOOP DO JOGO
    # ---------------------------
    while not glfw.window_should_close(win):
        now=glfw.get_time()
        dt=now-last
        last=now

        glfw.poll_events()

        player.update(dt,keys,plataformas,ramp)
        for e in inimigos:
            e.update(dt,player)

        atk = player.espada_box()
        if atk:
            for e in inimigos:
                if e.vivo and colisaoINI(atk,e.aabb()):
                    e.vivo=False

        glClearColor(0.52,0.80,0.98,1)  # céu suave azul claro
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        cam_eye = np.array([player.x+0, player.y+7, player.z+14], dtype=np.float32)
        cam_tgt = np.array([player.x, player.y, player.z], dtype=np.float32)
        view = look_at(cam_eye, cam_tgt, np.array([0,1,0],dtype=np.float32))
        vp = proj @ view

        # chão (um cubo largo achato)
        model = translacao(0,-0.51,0) @ escala(40,1,40)
        desenhar(cubo_ground,model,vp,programa)

        # plataformas
        for p in plataformas:
            model = translacao(p.x,p.h-0.5,p.z) @ escala(p.w,1,p.d)
            desenhar(cubo_plat1 if p.h==0 else cubo_plat2, model, vp, programa)

        # rampa
        # calcula o ângulo sem deformar quando d é negativo
        ang = math.atan2((ramp.y1 - ramp.y0), abs(ramp.d))

        # se d for negativo, inverter inclinação
        if ramp.d < 0:
            ang = -ang

        mid_y = (ramp.y0 + ramp.y1) / 2

        model = translacao(ramp.x, mid_y, ramp.z) @ rotacaoX(-ang) @ escala(ramp.w, 0.1, abs(ramp.d))

        desenhar(plane_ramp, model, vp, programa)


        # jogador
        model = translacao(player.x, player.y, player.z) @ escala(1,1,1)
        desenhar(cubo_link,model,vp,programa)

        # espada
        if player.ataque:
            dx=math.sin(player.face)
            dz=math.cos(player.face)
            sx=player.x+dx
            sz=player.z+dz
            model = translacao(sx,player.y,sz) @ escala(0.5,0.15,0.15)
            desenhar(cubo_espada,model,vp,programa)

        # inimigos
        for e in inimigos:
            if not e.vivo: continue
            model = translacao(e.x,e.y,e.z) @ escala(1,1,1)
            desenhar(cubo_Inimigo1 if e.tipo=="melee" else cubo_Inimigo2, model, vp, programa)

        glfw.swap_buffers(win)

    glfw.terminate()

if __name__ == "__main__":
    main()
