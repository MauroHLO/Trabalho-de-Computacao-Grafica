class Inimigo:
    def __init__(self,x,z,cor,tipoINI="melee"):
        self.x,self.z=x,z
        self.y=1
        self.cor=cor
        self.tipo=tipoINI
        self.tam=1.0
        self.veloc = 3 if tipoINI=="melee" else 2
        self.vivo=True

    def update(self,dt,player):
        if not self.vivo: return
        dx = player.x-self.x
        dz = player.z-self.z
        d = math.hypot(dx,dz)
        if d<0.001: return

        if self.tipo=="melee":
            nx, nz = dx/d, dz/d
            self.x += nx*self.veloc*dt
            self.z += nz*self.veloc*dt
        else:
            # ranged: foge
            if d<7:
                nx, nz = -dx/d, -dz/d
                self.x += nx*self.veloc*dt
                self.z += nz*self.veloc*dt

        self.y = 0.5 + self.tam/2

    def aabb(self):
        return (self.x-0.5,self.y-0.5,self.z-0.5, self.x+0.5,self.y+0.5,self.z+0.5)
