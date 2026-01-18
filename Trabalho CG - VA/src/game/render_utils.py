import math
from engine.transformacoes import translacao, escala, rotacaoY

def desenhar_flecha(desenhar_fn, prog, vp, x, y, z, yaw, vao_madeira, vao_metal, vao_pena):
    base = translacao(x, y, z) @ rotacaoY(yaw)

    # haste
    haste = base @ translacao(0.0, 0.0, 0.35) @ escala(0.05, 0.05, 0.70)
    desenhar_fn(vao_madeira, haste, vp, prog)

    # ponta
    ponta = base @ translacao(0.0, 0.0, 0.78) @ escala(0.07, 0.07, 0.12)
    desenhar_fn(vao_metal, ponta, vp, prog)

    # penas
    pena1 = base @ translacao(0.03, 0.02, -0.02) @ escala(0.02, 0.08, 0.18)
    pena2 = base @ translacao(-0.03, 0.02, -0.02) @ escala(0.02, 0.08, 0.18)
    desenhar_fn(vao_pena, pena1, vp, prog)
    desenhar_fn(vao_pena, pena2, vp, prog)
