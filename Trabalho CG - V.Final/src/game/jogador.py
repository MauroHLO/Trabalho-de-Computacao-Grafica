import glfw
import math
from engine.colisao import colisaoINI

class Player:
    def __init__(self):
        self.x = 0
        self.z = 3
        self.y = 1
        self.face = 0
        self.tam = 1
        self.veloc = 6
        self.ataque = False
        self.temp = 0

        # === VIDA / MORTE ===
        self.vida_max = 10
        self.vida = self.vida_max
        self.vivo = True
        self.inv_timer = 0.0

    def tomar_dano(self, dano):
        if not self.vivo:
            return
        if self.inv_timer > 0:
            return

        self.vida -= dano
        if self.vida <= 0:
            self.vida = 0
            self.vivo = False

        self.inv_timer = 1000  # debug (invencível)

    def update(self, dt, keys, plats, rampas):
        if not self.vivo:
            return

        if self.inv_timer > 0:
            self.inv_timer -= dt
        # =========================
        # MOVIMENTO
        # =========================
        dx = dz = 0
        if keys.get(glfw.KEY_W): dx += 1
        if keys.get(glfw.KEY_S): dx -= 1
        if keys.get(glfw.KEY_A): dz -= 1
        if keys.get(glfw.KEY_D): dz += 1

        old_x, old_z = self.x, self.z  # ✅ para poder reverter se bater

        if dx or dz:
            L = math.hypot(dx, dz)
            dx /= L
            dz /= L
            self.x += dx * self.veloc * dt
            self.z += dz * self.veloc * dt
            self.face = math.atan2(dx, dz)

        half = self.tam / 2.0

        # =========================
        # PAREDES LATERAIS INVISÍVEIS DA RAMPA
        # (impede subir/entrar pela lateral, estilo "parede do bloco")
        # =========================
        if rampas:
            aabb_player = self.aabb()
            for r in rampas:
                if r is None or not hasattr(r, "paredes_laterais"):
                    continue
                for parede in r.paredes_laterais(espessura=0.18):
                    if colisaoINI(aabb_player, parede):
                        self.x, self.z = old_x, old_z
                        break


        # =========================
        # ALTURA (rampa + plataformas)
        # =========================
        novo_Y = 0.0

        # rampa (só aplica se estiver dentro e passando pela frente, se existir _pela_frente)
        if rampas:
            for r in rampas:
                if r is None:
                    continue
                if r.contencao(self.x, self.z):
                    if (not hasattr(r, "_pela_frente")) or r._pela_frente(self.z):
                        novo_Y = max(novo_Y, float(r.altura(self.x, self.z)))


        # plataformas (pega maior)
        for p in plats:
            if p.contencao(self.x, self.z):
                novo_Y = max(novo_Y, float(p.h))

        # não deixa abaixo do chão
        if novo_Y < 0.0:
            novo_Y = 0.0

        self.y = novo_Y + half

        # =========================
        # COLISÃO LATERAL COM PLATAFORMAS ALTAS (BLOCO)
        # - impede entrar no bloco
        # - mas NÃO bloqueia quando você já está quase no topo (pra conseguir subir)
        # =========================
        margem_subida = 0.15  # quanto perto do topo libera entrar

        for p in plats:
            if p.h <= 0:
                continue

            x_min = p.x - abs(p.w) / 2.0
            x_max = p.x + abs(p.w) / 2.0
            z_min = p.z - abs(p.d) / 2.0
            z_max = p.z + abs(p.d) / 2.0
            y_top = float(p.h)

            # só bloqueia lateral se o player estiver abaixo do topo - margem
            if (self.y - half) < (y_top - margem_subida):
                if (x_min - half <= self.x <= x_max + half) and (z_min - half <= self.z <= z_max + half):
                    # empurra para fora pela menor penetração
                    pen_left  = abs(self.x - (x_min - half))
                    pen_right = abs((x_max + half) - self.x)
                    pen_front = abs(self.z - (z_min - half))
                    pen_back  = abs((z_max + half) - self.z)

                    m = min(pen_left, pen_right, pen_front, pen_back)

                    if m == pen_left:
                        self.x = x_min - half
                    elif m == pen_right:
                        self.x = x_max + half
                    elif m == pen_front:
                        self.z = z_min - half
                    else:
                        self.z = z_max + half

        # =========================
        # ATAQUE
        # =========================
        if self.ataque:
            self.temp += dt
            if self.temp > 0.25:
                self.ataque = False

    def espada_box(self):
        if not self.ataque or not self.vivo:
            return None
        dx = math.sin(self.face)
        dz = math.cos(self.face)
        sx = self.x + dx
        sz = self.z + dz
        sy = self.y
        return (sx-0.3, sy-0.2, sz-0.3, sx+0.3, sy+0.2, sz+0.3)

    def aabb(self):
        half = 0.5
        return (self.x-half, self.y-half, self.z-half,
                self.x+half, self.y+half, self.z+half)
