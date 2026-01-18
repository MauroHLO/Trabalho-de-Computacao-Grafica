class Rampa:
    def __init__(self, x, z, w, d, y0, y1, cor):
        self.x, self.z, self.w, self.d = x, z, w, d
        self.y0, self.y1 = y0, y1
        self.cor = cor

    def _bounds(self):
        x_min = min(self.x - self.w/2, self.x + self.w/2)
        x_max = max(self.x - self.w/2, self.x + self.w/2)
        z_min = min(self.z - self.d/2.3, self.z + self.d/2.3)
        z_max = max(self.z - self.d/2.3, self.z + self.d/2.3)
        return x_min, x_max, z_min, z_max

    def contencao(self, px, pz):
        x_min, x_max, z_min, z_max = self._bounds()
        return (x_min <= px <= x_max) and (z_min <= pz <= z_max)

    def paredes_laterais(self, espessura=0.15):
        """
        Retorna duas AABBs (esquerda e direita) que funcionam como
        paredes invisíveis da rampa.

        >>> ESSENCIAL: usar os mesmos bounds (x_min/x_max/z_min/z_max) do contencao,
        senão o inimigo pode "vazar" pela diferença de d/2 vs d/1.2.
        """
        x_min, x_max, z_min, z_max = self._bounds()

        y_min = self.y0
        y_max = self.y1

        parede_esq = (
            x_min - espessura, y_min, z_min,
            x_min + espessura, y_max, z_max
        )

        parede_dir = (
            x_max - espessura, y_min, z_min,
            x_max + espessura, y_max, z_max
        )

        return parede_esq, parede_dir

    def _pela_frente(self, pz, margem=0.15):
        """
        Só deixa subir pela parte frontal (lado da base y0).
        - d > 0: sobe indo pro +Z, topo no z_max => bloqueia perto do topo
        - d < 0: sobe indo pro -Z, topo no z_min => bloqueia perto do topo
        """
        _, _, z_min, z_max = self._bounds()
        if self.d > 0:
            return pz <= (z_max - margem)
        else:
            return pz >= (z_min + margem)

    def altura(self, px, pz):
        if not self.contencao(px, pz):
            return self.y0

        # bloqueia subida pela traseira/topo
        if not self._pela_frente(pz, margem=0.5):
            return self.y0

        z0 = self.z - self.d/2.0
        z1 = self.z + self.d/1.2
        comprimento = (z1 - z0)

        if abs(comprimento) < 1e-6:
            return self.y0

        t = (pz - z0) / comprimento
        t = max(0.0, min(1.0, t))

        return (1.0 - t) * self.y0 + t * self.y1
