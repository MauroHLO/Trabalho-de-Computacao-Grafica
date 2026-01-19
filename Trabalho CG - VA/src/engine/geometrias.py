import numpy as np
import ctypes
from OpenGL.GL import *

# ============================================================
# GEOMETRIAS
# ============================================================

def _normal_tri(a, b, c):
    import numpy as np

    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    c = np.array(c, dtype=np.float32)

    n = np.cross(b - a, c - a)
    norm = np.linalg.norm(n)
    if norm < 1e-9:
        return (0.0, 1.0, 0.0)

    n /= norm
    return (float(n[0]), float(n[1]), float(n[2]))

def criarCubo(cor=(1.0, 1.0, 1.0), com_normais=True):
    """
    Se com_normais=True:
        layout [pos(3) + normal(3) + uv(2)] com UV por face para atlas.
    Se com_normais=False:
        layout [pos(3) + cor(3)].
    """
    if com_normais:
        data = []

        def uvs_rect(u0, v0, u1, v1):
            # 4 vértices do quad: (0,0) (1,0) (1,1) (0,1)
            return [
                (u0, v0),
                (u1, v0),
                (u1, v1),
                (u0, v1),
            ]

        # ====== ATLAS UVs ======
        # Exemplo atlas 2 colunas:
        # [ SIDES | TOP ]
        UV_SIDES  = (0.0, 0.0, 0.5, 1.0)
        UV_TOP    = (0.5, 0.0, 1.0, 1.0)
        UV_BOTTOM = UV_SIDES  # ou cria outra região se quiser

        def add_face(v0, v1, v2, v3, n, uv_rect):
            vs = [v0, v1, v2, v3]
            uvs = uvs_rect(*uv_rect)
            for (x, y, z), (u, v) in zip(vs, uvs):
                data.extend([x, y, z, n[0], n[1], n[2], u, v])

        # FRENTE (Z+) -> LADO
        add_face(
            (-0.5, -0.5,  0.5),
            ( 0.5, -0.5,  0.5),
            ( 0.5,  0.5,  0.5),
            (-0.5,  0.5,  0.5),
            (0, 0, 1),
            UV_SIDES
        )

        # TRAS (Z-) -> LADO
        add_face(
            ( 0.5, -0.5, -0.5),
            (-0.5, -0.5, -0.5),
            (-0.5,  0.5, -0.5),
            ( 0.5,  0.5, -0.5),
            (0, 0, -1),
            UV_SIDES
        )

        # ESQUERDA (X-) -> LADO
        add_face(
            (-0.5, -0.5, -0.5),
            (-0.5, -0.5,  0.5),
            (-0.5,  0.5,  0.5),
            (-0.5,  0.5, -0.5),
            (-1, 0, 0),
            UV_SIDES
        )

        # DIREITA (X+) -> LADO
        add_face(
            ( 0.5, -0.5,  0.5),
            ( 0.5, -0.5, -0.5),
            ( 0.5,  0.5, -0.5),
            ( 0.5,  0.5,  0.5),
            (1, 0, 0),
            UV_SIDES
        )

        # CIMA (Y+) -> TOPO
        add_face(
            (-0.5,  0.5,  0.5),
            ( 0.5,  0.5,  0.5),
            ( 0.5,  0.5, -0.5),
            (-0.5,  0.5, -0.5),
            (0, 1, 0),
            UV_TOP
        )

        # BAIXO (Y-) -> (lados, ou outra textura)
        add_face(
            (-0.5, -0.5, -0.5),
            ( 0.5, -0.5, -0.5),
            ( 0.5, -0.5,  0.5),
            (-0.5, -0.5,  0.5),
            (0, -1, 0),
            UV_BOTTOM
        )

        verts = np.array(data, dtype=np.float32)

        idx = np.array([
             0, 1, 2,  2, 3, 0,
             4, 5, 6,  6, 7, 4,
             8, 9,10, 10,11, 8,
            12,13,14, 14,15,12,
            16,17,18, 18,19,16,
            20,21,22, 22,23,20,
        ], dtype=np.uint32)

        return verts, idx, cor

    # ---- versão simples (pos + cor) ----
    ...

    # ---- versão simples (pos + cor) ----
    c = cor
    verts = np.array([
        -0.5,-0.5,-0.5, *c,
         0.5,-0.5,-0.5, *c,
         0.5, 0.5,-0.5, *c,
        -0.5, 0.5,-0.5, *c,
        -0.5,-0.5, 0.5, *c,
         0.5,-0.5, 0.5, *c,
         0.5, 0.5, 0.5, *c,
        -0.5, 0.5, 0.5, *c
    ], dtype=np.float32)

    idx = np.array([
        0,1,2, 2,3,0,
        4,5,6, 6,7,4,
        4,5,1, 1,0,4,
        7,6,2, 2,3,7,
        5,6,2, 2,1,5,
        4,7,3, 3,0,4
    ], dtype=np.uint32)

    return verts, idx, cor


def criarPlataforma(cor=(0.4, 0.8, 0.4), tile=1.0):
    """
    Plataforma simples em y=0.
    Layout: [pos(3) + normal(3) + uv(2)]
    tile: fator de repetição da textura (1.0 = uma vez)
    """
    n = (0.0, 1.0, 0.0)

    verts = np.array([
        # x,    y,    z,    nx, ny, nz,   u,           v
        -0.5,  0.0, -0.5,  *n,  0.0,       0.0,
         0.5,  0.0, -0.5,  *n,  tile,      0.0,
         0.5,  0.0,  0.5,  *n,  tile,      tile,
        -0.5,  0.0,  0.5,  *n,  0.0,       tile,
    ], dtype=np.float32)

    idx = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

    return verts, idx, cor



def criarRampaSolida(cor=(0.64, 0.48, 0.24), tile=1.0):
    """
    Rampa sólida (wedge) FECHADA.
    Layout: [pos(3) + normal(3) + uv(2)]
    Normais por face (vértices duplicados por triângulo), igual o cubo com luz.

    tile: repetição da textura (1.0 = uma vez)
    """

    # pontos
    A = (-0.5, 0.0, -0.5)
    B = ( 0.5, 0.0, -0.5)
    C = ( 0.5, 0.0,  0.5)
    D = (-0.5, 0.0,  0.5)
    E = (-0.5, 1.0,  0.5)
    F = ( 0.5, 1.0,  0.5)

    verts = []
    idx = []

    def uv_for(p, mode: str):
        x, y, z = p
        # mapeia [-0.5, 0.5] -> [0, 1]
        def map01(v): 
            return (v + 0.5) * tile

        if mode == "xz":   # chão/base
            return (map01(x), map01(z))
        if mode == "zy":   # paredes laterais
            # z em [-0.5,0.5] => [0,1], y em [0,1] => [0,1]
            return (map01(z), y * tile)
        if mode == "xy":   # topo inclinado
            return (map01(x), y * tile)

        # fallback
        return (0.0, 0.0)

    def add_tri(p1, p2, p3, uv_mode: str):
        n = _normal_tri(p1, p2, p3)
        base = len(verts) // 8

        u1, v1 = uv_for(p1, uv_mode)
        u2, v2 = uv_for(p2, uv_mode)
        u3, v3 = uv_for(p3, uv_mode)

        verts.extend([
            *p1, *n, u1, v1,
            *p2, *n, u2, v2,
            *p3, *n, u3, v3,
        ])
        idx.extend([base, base + 1, base + 2])

    # ===== Faces (fechadas) =====
    # Base (baixo) -> winding invertido p/ normal pra baixo
    add_tri(A, C, B, "xz")
    add_tri(A, D, C, "xz")

    # Topo inclinado
    add_tri(C, D, E, "xy")
    add_tri(C, E, F, "xy")

    # Lateral esquerda (triângulo)
    add_tri(A, D, E, "zy")

    # Lateral direita (triângulo)
    add_tri(B, F, C, "zy")

    # Converter
    verts = np.array(verts, dtype=np.float32)
    idx = np.array(idx, dtype=np.uint32)
    return verts, idx, cor


# ============================================================
# VAO / VBO / EBO
# ============================================================

def criarVAO(verts, idx, tint=(1.0, 1.0, 1.0)):
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)

    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, idx.nbytes, idx, GL_STATIC_DRAW)

    # agora: pos(3) + normal(3) + uv(2) = 8 floats
    stride = 8 * 4

    # location 0: pos (vec3)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

    # location 1: normal (vec3)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))

    # location 2: uv (vec2)
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))

    glBindVertexArray(0)

    return vao, vbo, ebo, idx.size, tint
