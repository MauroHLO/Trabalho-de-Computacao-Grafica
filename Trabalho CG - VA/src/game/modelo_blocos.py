# src/game/modelo_blocos.py
import math
from engine.transformacoes import translacao, escala, rotacaoY, rotacaoX


class ModeloBlocos:
    def __init__(self, vao_pele, vao_roupa, vao_bota, vao_detalhe, vao_metal, vao_madeira):
        self.vao_pele = vao_pele
        self.vao_roupa = vao_roupa
        self.vao_bota = vao_bota
        self.vao_detalhe = vao_detalhe
        self.vao_metal = vao_metal
        self.vao_madeira = vao_madeira

    def draw_link(self, desenhar_fn, prog, vp, x, y, z, face, t, andando=False, atacando=False):
        base = translacao(x, y, z) @ rotacaoY(face)

        swing = 0.0
        if andando:
            swing = math.sin(t * 10.0) * 0.6

        # Ataque: agora é um "corte de cima pra baixo"
        # (antes estava levantando/indo no sentido errado)
        atk = +1.1 if atacando else 0.0

        # === TRONCO (um pouco maior) ===
        tronco = base @ translacao(0.0, 1.10, 0.0) @ escala(0.95, 1.05, 0.60)
        desenhar_fn(self.vao_roupa, tronco, vp, prog)

        # === CABEÇA (mais baixa e perto) ===
        cabeca = base @ translacao(0.0, 2.05, 0.0) @ escala(0.70, 0.70, 0.70)
        desenhar_fn(self.vao_pele, cabeca, vp, prog)

        # === BRAÇO ESQ (mais perto do corpo) ===
        braco_e = (
            base
            @ translacao(-0.60, 1.30, 0.0)
            @ rotacaoX(+swing)
            @ escala(0.25, 0.85, 0.25)
        )
        desenhar_fn(self.vao_roupa, braco_e, vp, prog)

        # === BRAÇO DIR (mais perto + ataque) ===
        braco_d_base = base @ translacao(+0.60, 1.30, 0.0) @ rotacaoX(-swing + atk)
        braco_d = braco_d_base @ escala(0.25, 0.85, 0.25)
        desenhar_fn(self.vao_roupa, braco_d, vp, prog)

        # === PERNAS (mais perto do centro) ===
        perna_e = base @ translacao(-0.22, 0.32, 0.0) @ rotacaoX(-swing) @ escala(0.30, 0.90, 0.30)
        perna_d = base @ translacao(+0.22, 0.32, 0.0) @ rotacaoX(+swing) @ escala(0.30, 0.90, 0.30)
        desenhar_fn(self.vao_bota, perna_e, vp, prog)
        desenhar_fn(self.vao_bota, perna_d, vp, prog)

        # === CINTO ===
        cinto = base @ translacao(0.0, 0.92, 0.0) @ escala(1.00, 0.15, 0.62)
        desenhar_fn(self.vao_detalhe, cinto, vp, prog)

        # ======================
        # ESPADA (presa na mão direita)
        # Agora ela fica "pra frente" e não colada no braço
        # ======================

        # Estocada: empurra pra frente (sem swing vertical estranho)
        atk = 0.0  # sem rotação extra
        estocada = 0.35 if atacando else 0.0  # empurra a arma pra frente

        braco_d_base = base @ translacao(+0.60, 1.30, 0.0) @ rotacaoX(-swing + atk)

        # mão: empurra pra frente quando ataca
        mao = braco_d_base @ translacao(0.0, -0.40, 0.40 - estocada)


        # Cabo (madeira) - apontando para frente (Z)
        cabo = mao @ translacao(0.0, 0.00, 0.10) @ escala(0.10, 0.10, 0.40)
        desenhar_fn(self.vao_madeira, cabo, vp, prog)

        # Guarda (metal)
        guarda = mao @ translacao(0.0, 0.00, 0.30) @ escala(0.35, 0.10, 0.10)
        desenhar_fn(self.vao_metal, guarda, vp, prog)

        # Lâmina (metal) - longa no eixo Z (pra frente)
        lamina = mao @ translacao(0.0, 0.05, 0.95) @ escala(0.12, 0.08, 1.25)
        desenhar_fn(self.vao_metal, lamina, vp, prog)

        # Ponta
        ponta = mao @ translacao(0.0, 0.05, 1.65) @ escala(0.08, 0.06, 0.18)
        desenhar_fn(self.vao_metal, ponta, vp, prog)
