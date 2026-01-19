import math
import numpy as np
from engine.terreno import clamp_dentro_plataforma
from engine.colisao import liang_barsky_3d, colisaoINI

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
        self.can_shoot = True  # oportunista

        # --- Trechos
        self.home_x = self.x
        self.home_z = self.z
        self.leash_radius = 7.0
        self.trecho_id = -1
        self.ativo_no_trecho = True

        # ---- VIDA
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

        # Camada do terreno:
        # "chao"  -> não sobe em plataforma
        # "plat"  -> não desce; preso na plataforma
        self.terrain_layer = "chao"
        self.plat_ref = None


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

        if self.burst_timer > 0:
            self.burst_timer -= dt
            return

        if self.atk_timer_range > 0 and self.burst_left == 0:
            self.atk_timer_range -= dt
            return

        self.cooldown_atk_range = max(self.cooldown_atk_range, 1.6)

        if self.burst_left == 0:
            self.burst_left = max(1, int(self.burst))

        if self.atk_timer_range > 0:
            self.atk_timer_range -= dt
            return

        origem = (self.x, self.y, self.z)
        alvo = (player.x, player.y, player.z)

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
                self.burst_timer = self.burst_gap
            else:
                self.atk_timer_range = self.cooldown_atk_range

    def _empurrar_fora_aabb(self, obst_aabb):
        """
        Resolve colisão AABB vs AABB empurrando o inimigo para fora
        pela menor penetração (só X/Z, mantém Y).
        """
        a = self.aabb()
        b = obst_aabb

        if not colisaoINI(a, b):
            return False

        # penetrações em X
        pen_left  = abs(a[3] - b[0])  # a.right - b.left
        pen_right = abs(b[3] - a[0])  # b.right - a.left

        # penetrações em Z
        pen_front = abs(a[5] - b[2])  # a.back  - b.front
        pen_back  = abs(b[5] - a[2])  # b.back  - a.front

        m = min(pen_left, pen_right, pen_front, pen_back)

        if m == pen_left:
            self.x -= pen_left
        elif m == pen_right:
            self.x += pen_right
        elif m == pen_front:
            self.z -= pen_front
        else:
            self.z += pen_back

        return True

    def update(self, dt, player, plataformas=None, rampas=None):
        if (not self.vivo) or (not player.vivo):
            self.flechas_ativas = []
            return

        if not getattr(self, "ativo_no_trecho", True):
            return

        hx = getattr(self, "home_x", self.x)
        hz = getattr(self, "home_z", self.z)
        leash = float(getattr(self, "leash_radius", 7.0))

        if math.hypot(self.x - hx, self.z - hz) > leash:
            self.x = hx
            self.z = hz
            self.flechas_ativas = []
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
        old_x, old_z = self.x, self.z

        if self.tipo == "melee":
            if d > self.alcance_atk:
                nx, nz = dx / d, dz / d
                self.x += nx * self.veloc * dt
                self.z += nz * self.veloc * dt
            self.atacar_melee(player, dt)
        else:
            if d > 9.0:
                nx, nz = dx / d, dz / d
                self.x += nx * self.veloc * dt
                self.z += nz * self.veloc * dt
            elif d < 5.0:
                nx, nz = -dx / d, -dz / d
                self.x += nx * self.veloc * dt
                self.z += nz * self.veloc * dt

            self.atacar_ranged(player, dt)

        # =========================
        # TRAVA DE CAMADA (alto vs chão)
        # =========================
        if self.terrain_layer == "plat" and self.plat_ref is not None:
            if not self.plat_ref.contencao(self.x, self.z):
                self.x, self.z = old_x, old_z

            self.x, self.z = clamp_dentro_plataforma(self.x, self.z, self.plat_ref, margem=0.35)
            self.y = float(self.plat_ref.h) + 0.5

        else:
            # inimigo do chão: não entra em plataforma alta
            if plataformas:
                entrou_em_plat = False
                for p in plataformas:
                    if p.h > 0.0 and p.contencao(self.x, self.z):
                        entrou_em_plat = True
                        break
                if entrou_em_plat:
                    self.x, self.z = old_x, old_z

            self.y = 0.5  # centro no chão

            # =========================
            # COLISÃO CONTRA RAMPAS
            # =========================
            if rampas:
                entrou_em_rampa = False
                for r in rampas:
                    if r.contencao(self.x, self.z):
                        entrou_em_rampa = True

                        p_esq, p_dir = r.paredes_laterais(espessura=0.20)
                        self._empurrar_fora_aabb(p_esq)
                        self._empurrar_fora_aabb(p_dir)

                        if r.contencao(self.x, self.z):
                            self.x, self.z = old_x, old_z

                        break

        # =========================
        # ATUALIZA FLECHAS
        # =========================
        sobreviventes = []
        for f in self.flechas_ativas:
            f["pos"] += f["vel"] * dt
            f["tempo_vida"] -= dt

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

