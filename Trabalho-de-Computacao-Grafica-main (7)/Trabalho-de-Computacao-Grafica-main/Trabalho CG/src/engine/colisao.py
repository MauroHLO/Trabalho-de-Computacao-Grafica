def colisaoINI(a,b):
    return not (a[3]<b[0] or a[0]>b[3] or
                a[4]<b[1] or a[1]>b[4] or
                a[5]<b[2] or a[2]>b[5])

def liang_barsky_3d(p0, p1, aabb):
    """
    p0: origem (inimigo), p1: destino (player)
    aabb: (xmin, ymin, zmin, xmax, ymax, zmax) do player
    Retorna True se o raio intercepta a caixa.
    """
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    xmin, ymin, zmin, xmax, ymax, zmax = aabb

    t_min = 0.0
    t_max = 1.0

    dx = x1 - x0
    dy = y1 - y0
    dz = z1 - z0

    def test(p, q):
        nonlocal t_min, t_max
        if p == 0:
            return q >= 0
        t = q / p
        if p < 0:
            if t > t_max: return False
            if t > t_min: t_min = t
        else:
            if t < t_min: return False
            if t < t_max: t_max = t
        return True

    # Testa as 6 faces do volume 3D
    if not test(-dx, x0 - xmin): return False
    if not test(dx, xmax - x0): return False
    if not test(-dy, y0 - ymin): return False
    if not test(dy, ymax - y0): return False
    if not test(-dz, z0 - zmin): return False
    if not test(dz, zmax - z0): return False

    return t_min <= t_max
