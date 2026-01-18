class Plataforma:
    def __init__(self, x, z, w, d, h, cor, visivel=True):
        self.x, self.z, self.w, self.d, self.h = x, z, w, d, h
        self.cor = cor
        self.visivel = visivel

    def contencao(self, px, pz):
        x_min = min(self.x - self.w/2.0, self.x + self.w/2.0)
        x_max = max(self.x - self.w/2.0, self.x + self.w/2.0)
        z_min = min(self.z - self.d/1.7, self.z + self.d/1.7)
        z_max = max(self.z - self.d/1.7, self.z + self.d/1.7)
        return (x_min <= px <= x_max) and (z_min <= pz <= z_max)
