class Rampa:
    def __init__(self,x,z,w,d,y0,y1,cor):
        # x,z centro; w largura (x), d profundidade (local z, pode ser negativo)
        # y0 = base, y1 = topo
        self.x,self.z,self.w,self.d = x,z,w,d
        self.y0,self.y1 = y0,y1
        self.cor = cor

    def contencao(self,px,pz):
        x_min = min(self.x - self.w/2.0, self.x + self.w/2.0)
        x_max = max(self.x - self.w/2.0, self.x + self.w/2.0)
        z_min = min(self.z - self.d/2.0, self.z + self.d/2.0)
        z_max = max(self.z - self.d/2.0, self.z + self.d/2.0)
        return (x_min <= px <= x_max) and (z_min <= pz <= z_max)

    def altura(self,px,pz):
        """
        Calcula a altura y na posição (px,pz) projetada ao longo do eixo Z local da rampa.
        Suporta d negativo. A rampa é considerada alinhada com o eixo Z global.
        """
        # define z0 (início) e z1 (fim) como os extremos na ordem natural
        z0 = self.z - self.d/2.0
        z1 = self.z + self.d/2.0
        comprimento = (z1 - z0)
        if abs(comprimento) < 1e-6:
            return self.y0  # rampa sem comprimento

        # t normalizado ao longo do comprimento da rampa (0..1)
        t = (pz - z0) / comprimento
        t = max(0.0, min(1.0, t))

        # interpolação linear entre y0 e y1
        y = (1.0 - t) * self.y0 + t * self.y1
        return y