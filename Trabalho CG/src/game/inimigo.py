import math
import numpy as np
from engine.colisao import liang_barsky_3d

class Inimigo:
    def __init__(self, x, z, cor, tipoINI="melee"):
        self.x, self.z = x, z
        self.y = 1.0
        self.cor = cor
        self.tipo = tipoINI
        self.tam = 1.0
        self.vivo = True
        self.behavior = "chase" if tipoINI=="melee" else "kite"
        self.burst = 1
        self.burst_left = 0
        self.burst_gap = 0.12
        self.burst_timer = 0.0
        self.can_shoot = True  # controlado pela main (opportunist)
        # --- Trechos / leash (Zelda feel)
        self.home_x = self.x
        self.home_z = self.z
        self.leash_radius = 7.0
        self.trecho_id = -1
        self.ativo_no_trecho = True  # será controlado pela Fase



        # ---- VIDA (se quiser já começar a usar por mundo)
        self.hp_max = 3 if tipoINI == "melee" else 2
        self.hp = self.hp_max

        # ---- MOVIMENTO
        self.veloc = 3.0 if tipoINI == "melee" else 2.0

        # ---- MELEE
        self.alcance_atk = 1.2
        self.dano = 1
        self.cooldown_atk = 0.8
        self.atk_timer = 0.0

        # ---- RANGED (projéteis)
        self.dano_range = 1
        self.cooldown_atk_range = 2.0
        self.atk_timer_range = 0.0
        self.flechas_ativas = []
        self.flecha_speed = 11.0
        self.flecha_ttl = 2.0

    def tomar_dano(self, dano):
        if not self.vivo:
            return
        self.hp -= dano
        if self.hp <= 0:
            self.hp = 0
            self.vivo = False
            self.flechas_ativas = []

    def atacar_melee(self, player, dt):
        if self.atk_timer > 0:
            self.atk_timer -= dt
            return

        dx = player.x - self.x
        dz = player.z - self.z
        d = math.hypot(dx, dz)

        if d <= self.alcance_atk:
            player.tomar_dano(self.dano)
            self.atk_timer = self.cooldown_atk

    def atacar_ranged(self, player, dt):
        if not self.can_shoot:
            return
        
        # controla intervalo entre tiros dentro do burst
        if self.burst_timer > 0:
            self.burst_timer -= dt
            return

        # cooldown geral entre bursts
        if self.atk_timer_range > 0 and self.burst_left == 0:
            self.atk_timer_range -= dt
            return

        # trava de segurança pra não virar metralhadora em nenhum mundo
        self.cooldown_atk_range = max(self.cooldown_atk_range, 1.6)
        
        # se não está em burst, inicia um novo
        if self.burst_left == 0:
            self.burst_left = max(1, int(self.burst))

        if self.atk_timer_range > 0:
            self.atk_timer_range -= dt
            return

        origem = (self.x, self.y, self.z)
        alvo = (player.x, player.y, player.z)

        # linha de tiro: segmento inimigo->player cruza AABB do player
        if liang_barsky_3d(origem, alvo, player.aabb()):
            vx = alvo[0] - origem[0]
            vz = alvo[2] - origem[2]
            L = math.hypot(vx, vz)
            if L < 1e-6:
                return

            vx /= L
            vz /= L

            nova_flecha = {
                "pos": np.array([self.x, self.y, self.z], dtype=np.float32),
                "vel": np.array([vx * self.flecha_speed, 0.0, vz * self.flecha_speed], dtype=np.float32),
                "tempo_vida": float(self.flecha_ttl),
            }
            self.flechas_ativas.append(nova_flecha)
            self.burst_left -= 1

            if self.burst_left > 0:
                # próximo tiro rápido
                self.burst_timer = self.burst_gap
            else:
                # terminou o burst -> entra no cooldown "grande"
                self.atk_timer_range = self.cooldown_atk_range

    def update(self, dt, player):
        if (not self.vivo) or (not player.vivo):
            self.flechas_ativas = []
            return
        
        # Se ainda não "acordou" no trecho, não faz nada (fica parado)
        if not getattr(self, "ativo_no_trecho", True):
            return

        # Leash: se saiu muito do território, volta pro ponto inicial
        hx = getattr(self, "home_x", self.x)
        hz = getattr(self, "home_z", self.z)
        leash = float(getattr(self, "leash_radius", 7.0))

        if math.hypot(self.x - hx, self.z - hz) > leash:
            self.x = hx
            self.z = hz
            self.flechas_ativas = []
            # pequeno atraso para não voltar atirando instant
            self.atk_timer = 0.2
            self.atk_timer_range = 0.2
            return

        dx = player.x - self.x
        dz = player.z - self.z
        d = math.hypot(dx, dz)
        if d < 1e-6:
            return

        # =========================
        # MOVIMENTO + ATAQUE
        # =========================
        if self.tipo == "melee":
            # persegue se longe
            if d > self.alcance_atk:
                nx, nz = dx / d, dz / d
                self.x += nx * self.veloc * dt
                self.z += nz * self.veloc * dt
            self.atacar_melee(player, dt)

        else:  # ranged
            # kiting: manter entre 6 e 10
            if d > 9.0:
                nx, nz = dx / d, dz / d
                self.x += nx * self.veloc * dt
                self.z += nz * self.veloc * dt
            elif d < 5.0:
                nx, nz = -dx / d, -dz / d
                self.x += nx * self.veloc * dt
                self.z += nz * self.veloc * dt
            else:
                pass    

            self.atacar_ranged(player, dt)

        self.y = 0.5 + self.tam / 2

        # =========================
        # ATUALIZA FLECHAS
        # =========================
        sobreviventes = []
        for f in self.flechas_ativas:
            f["pos"] += f["vel"] * dt
            f["tempo_vida"] -= dt

            # colisão simples com player (mais estável que AABB vs AABB)
            dist_xz = math.hypot(float(f["pos"][0] - player.x), float(f["pos"][2] - player.z))
            dist_y = abs(float(f["pos"][1] - player.y))
            colidiu = (dist_xz < 0.8) and (dist_y < 1.0)

            if colidiu:
                player.tomar_dano(self.dano_range)
                continue

            if f["tempo_vida"] > 0:
                sobreviventes.append(f)

        self.flechas_ativas = sobreviventes

    def aabb(self):
        half = 0.5
        return (self.x-half, self.y-half, self.z-half,
                self.x+half, self.y+half, self.z+half)
