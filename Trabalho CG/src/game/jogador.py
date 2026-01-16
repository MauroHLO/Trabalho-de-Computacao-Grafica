import glfw
import math

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

        self.inv_timer = 0.35  # invencibilidade curta

    def update(self, dt, keys, plats, ramp):
        if not self.vivo:
            return

        if self.inv_timer > 0:
            self.inv_timer -= dt

        dx = dz = 0
        if keys.get(glfw.KEY_W): dz -= 1
        if keys.get(glfw.KEY_S): dz += 1
        if keys.get(glfw.KEY_A): dx -= 1
        if keys.get(glfw.KEY_D): dx += 1

        if dx or dz:
            L = math.hypot(dx, dz)
            dx /= L; dz /= L
            self.x += dx * self.veloc * dt
            self.z += dz * self.veloc * dt
            self.face = math.atan2(dx, dz)

        novo_Y = 0
        if ramp is not None and ramp.contencao(self.x, self.z):	
            novo_Y = ramp.altura(self.x, self.z)
        else:
            for p in plats:
                if p.contencao(self.x, self.z):
                    novo_Y = max(novo_Y, p.h)

        self.y = novo_Y + self.tam / 2

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