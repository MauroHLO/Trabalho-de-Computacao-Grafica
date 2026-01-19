from typing import Optional, Tuple, List

def plataforma_bounds(p) -> Tuple[float, float, float, float]:
    x_min = min(p.x - p.w / 2.0, p.x + p.w / 2.0)
    x_max = max(p.x - p.w / 2.0, p.x + p.w / 2.0)

    z_min = min(p.z - p.d / 1.75, p.z + p.d / 1.75)
    z_max = max(p.z - p.d / 1.75, p.z + p.d / 1.75)
    return x_min, x_max, z_min, z_max


def achar_plataforma_embaixo(x: float, z: float, plataformas: List) -> Optional[object]:
    """
    Retorna a plataforma MAIS ALTA que contém (x,z). Se não tiver, retorna None.
    Usado para: spawn e "camada" (alto vs chão).
    """
    melhor = None
    melhor_h = float("-inf")
    for p in plataformas:
        if p.contencao(x, z) and p.h > melhor_h:
            melhor_h = p.h
            melhor = p
    return melhor


def clamp_dentro_plataforma(x: float, z: float, p, margem: float = 0.35) -> Tuple[float, float]:
    """
    "Puxa" o ponto pra dentro do retângulo da plataforma, para evitar ficar na borda.
    """
    x_min, x_max, z_min, z_max = plataforma_bounds(p)
    x_min += margem
    x_max -= margem
    z_min += margem
    z_max -= margem

    if x < x_min: x = x_min
    if x > x_max: x = x_max
    if z < z_min: z = z_min
    if z > z_max: z = z_max
    return x, z

