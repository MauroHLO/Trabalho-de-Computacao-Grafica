import math

class Inimigo:
    def __init__(self, x, z, cor, tipoINI="melee"):
        self.x, self.z = x, z
        self.y = 1
        self.cor = cor
        self.tipo = tipoINI
        self.tam = 1.0
        self.veloc = 3 if tipoINI == "melee" else 2
        self.vivo = True

        self.alcance_atk = 1.2
        self.dano = 1
        self.cooldown_atk = 0.8
        self.atk_timer = 0.0

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
            print("Inimigo melee acertou! Vida do player:", player.vida)

    def update(self, dt, player):
        if not self.vivo or not player.vivo:
            return

        dx = player.x - self.x
        dz = player.z - self.z
        d = math.hypot(dx, dz)
        if d < 0.001:
            return

        if self.tipo == "melee":
            if d <= self.alcance_atk:
                self.atacar_melee(player, dt)
            else:
                nx, nz = dx / d, dz / d
                self.x += nx * self.veloc * dt
                self.z += nz * self.veloc * dt
        else:
            if d > 7:
                nx, nz = dx / d, dz / d
                self.x += nx * self.veloc * dt
                self.z += nz * self.veloc * dt
            else:
                nx, nz = -dx / d, -dz / d
                self.x += nx * self.veloc * dt
                self.z += nz * self.veloc * dt

        self.y = 0.5 + self.tam / 2

    def aabb(self):
        return (self.x-0.5,self.y-0.5,self.z-0.5, self.x+0.5,self.y+0.5,self.z+0.5)