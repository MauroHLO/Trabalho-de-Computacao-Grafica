class Plataforma:
    def __init__(self, x,z,w,d,h,cor):
        # x,z centro; w largura (x), d profundidade (z), h altura (y) do topo
        self.x,self.z,self.w,self.d,self.h = x,z,w,d,h
        self.cor = cor

    def contencao(self,px,pz):
        # suporta w ou d negativos usando min/max
        x_min = min(self.x - self.w/2.0, self.x + self.w/2.0)
        x_max = max(self.x - self.w/2.0, self.x + self.w/2.0)
        z_min = min(self.z - self.d/1.75, self.z + self.d/1.75)
        z_max = max(self.z - self.d/1.75, self.z + self.d/1.75)
        return (x_min <= px <= x_max) and (z_min <= pz <= z_max)