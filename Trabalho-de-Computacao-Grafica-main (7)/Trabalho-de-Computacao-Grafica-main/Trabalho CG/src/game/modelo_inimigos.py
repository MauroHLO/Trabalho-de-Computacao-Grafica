import math
from engine.transformacoes import translacao, escala, rotacaoY

class ModeloInimigos:
    def __init__(self, vao_corpo, vao_cabeca, vao_metal, vao_madeira, vao_corda):
        self.vao_corpo = vao_corpo
        self.vao_cabeca = vao_cabeca
        self.vao_metal = vao_metal
        self.vao_madeira = vao_madeira
        self.vao_corda = vao_corda

    # =========================
    # INIMIGO MELEE (faca)
    # =========================
    def draw_melee(self, desenhar_fn, prog, vp, x, y, z, face):
        base = translacao(x, y, z) @ rotacaoY(face)

        corpo = base @ translacao(0.0, 0.9, 0.0) @ escala(0.9, 1.0, 0.6)
        desenhar_fn(self.vao_corpo, corpo, vp, prog)

        cabeca = base @ translacao(0.0, 1.70, 0.0) @ escala(0.6, 0.6, 0.6)
        desenhar_fn(self.vao_cabeca, cabeca, vp, prog)

        # “mão” na frente direita
        mao = base @ translacao(0.65, 1.05, 0.45)

        # cabo (madeira) - horizontal (Z)
        cabo = mao @ translacao(0.0, 0.0, 0.10) @ escala(0.10, 0.10, 0.35)
        desenhar_fn(self.vao_madeira, cabo, vp, prog)

        # lâmina (metal) - horizontal (Z) apontando pra frente
        lamina = mao @ translacao(0.0, 0.02, 0.55) @ escala(0.08, 0.06, 0.85)
        desenhar_fn(self.vao_metal, lamina, vp, prog)

        # ponta
        ponta = mao @ translacao(0.0, 0.02, 1.05) @ escala(0.06, 0.05, 0.15)
        desenhar_fn(self.vao_metal, ponta, vp, prog)


    # =========================
    # INIMIGO RANGED (arco)
    # =========================
    def draw_ranged(self, desenhar_fn, prog, vp, x, y, z, face):
        base = translacao(x, y, z) @ rotacaoY(face)

        corpo = base @ translacao(0.0, 1.0, 0.0) @ escala(0.6, 1.2, 0.5)
        desenhar_fn(self.vao_corpo, corpo, vp, prog)

        cabeca = base @ translacao(0.0, 1.9, 0.0) @ escala(0.6, 0.6, 0.6)
        desenhar_fn(self.vao_cabeca, cabeca, vp, prog)

        # arco na frente do inimigo
        arco_base = base @ translacao(0.65, 1.15, 0.40) @ rotacaoY(math.pi)

        # “curva fake”: 3 segmentos madeira (topo, meio, baixo)
        topo = arco_base @ translacao(0.0, 0.45, 0.0) @ escala(0.12, 0.45, 0.12)
        meio = arco_base @ translacao(0.0, 0.00, 0.0) @ escala(0.10, 0.55, 0.10)
        baixo = arco_base @ translacao(0.0, -0.45, 0.0) @ escala(0.12, 0.45, 0.12)
        desenhar_fn(self.vao_madeira, topo, vp, prog)
        desenhar_fn(self.vao_madeira, meio, vp, prog)
        desenhar_fn(self.vao_madeira, baixo, vp, prog)

        # “pontas” do arco (um pouco pra frente)
        # pontas mais alongadas (Y maior) e um pouco mais "pra frente" (Z)
        ponta_cima  = arco_base @ translacao(0.0, 0.92, 0.08) @ escala(0.10, 0.26, 0.12)
        ponta_baixo = arco_base @ translacao(0.0, -0.92, 0.08) @ escala(0.10, 0.26, 0.12)

        desenhar_fn(self.vao_madeira, ponta_cima, vp, prog)
        desenhar_fn(self.vao_madeira, ponta_baixo, vp, prog)

        # corda (clara) – bem fininha
        corda = arco_base @ translacao(0.0, 0.0, 0.10) @ escala(0.02, 1.65, 0.02)
        desenhar_fn(self.vao_corda, corda, vp, prog)
