import numpy as np
import ctypes
from OpenGL.GL import *

# ============================================================
# GEOMETRIAS
# ============================================================

def criarCubo(cor=(1.0, 1.0, 1.0), com_normais=True):
    """
    Se com_normais=True:
        retorna cubo com 24 vertices (4 por face) em layout [pos(3) + normal(3)].
    Se com_normais=False:
        retorna cubo com 8 vertices em layout [pos(3) + cor(3)].
    """
    if com_normais:
        verts = np.array([
            # FRENTE (Z+)
            -0.5,-0.5, 0.5,   0,0,1,
             0.5,-0.5, 0.5,   0,0,1,
             0.5, 0.5, 0.5,   0,0,1,
            -0.5, 0.5, 0.5,   0,0,1,

            # TRAS (Z-)
             0.5,-0.5,-0.5,   0,0,-1,
            -0.5,-0.5,-0.5,   0,0,-1,
            -0.5, 0.5,-0.5,   0,0,-1,
             0.5, 0.5,-0.5,   0,0,-1,

            # ESQUERDA (X-)
            -0.5,-0.5,-0.5,  -1,0,0,
            -0.5,-0.5, 0.5,  -1,0,0,
            -0.5, 0.5, 0.5,  -1,0,0,
            -0.5, 0.5,-0.5,  -1,0,0,

            # DIREITA (X+)
             0.5,-0.5, 0.5,   1,0,0,
             0.5,-0.5,-0.5,   1,0,0,
             0.5, 0.5,-0.5,   1,0,0,
             0.5, 0.5, 0.5,   1,0,0,

            # CIMA (Y+)
            -0.5, 0.5, 0.5,   0,1,0,
             0.5, 0.5, 0.5,   0,1,0,
             0.5, 0.5,-0.5,   0,1,0,
            -0.5, 0.5,-0.5,   0,1,0,

            # BAIXO (Y-)
            -0.5,-0.5,-0.5,   0,-1,0,
             0.5,-0.5,-0.5,   0,-1,0,
             0.5,-0.5, 0.5,   0,-1,0,
            -0.5,-0.5, 0.5,   0,-1,0,
        ], dtype=np.float32)

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


def criarPlataforma(cor=(0.4, 0.8, 0.4)):
    """
    Plataforma simples em y=0.
    AGORA: Layout [pos(3) + normal(3)] (normal fixa pra cima)
    A cor continua retornando no 3º retorno, para você usar no uTint.
    """
    n = (0.0, 1.0, 0.0)
    verts = np.array([
        -0.5, 0.0, -0.5, *n,
         0.5, 0.0, -0.5, *n,
         0.5, 0.0,  0.5, *n,
        -0.5, 0.0,  0.5, *n,
    ], dtype=np.float32)

    idx = np.array([0,1,2, 2,3,0], dtype=np.uint32)
    return verts, idx, cor


def _normal_tri(a, b, c):
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    c = np.array(c, dtype=np.float32)
    n = np.cross(b - a, c - a)
    norm = np.linalg.norm(n)
    if norm < 1e-9:
        return (0.0, 1.0, 0.0)
    n = n / norm
    return (float(n[0]), float(n[1]), float(n[2]))


def criarRampaSolida(cor=(0.64, 0.48, 0.24)):
    """
    Rampa sólida (wedge) FECHADA.
    AGORA: Layout [pos(3) + normal(3)].
    Normais por face (vértices duplicados por triângulo), igual o cubo com luz.
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

    def add_tri(p1, p2, p3):
        n = _normal_tri(p1, p2, p3)
        base = len(verts) // 6
        verts.extend([*p1, *n, *p2, *n, *p3, *n])
        idx.extend([base, base+1, base+2])

    # ===== Faces (todas fechadas) =====
    # Base (baixo) -> queremos normal pra baixo (0,-1,0), então winding invertido olhando de cima:
    add_tri(A, C, B)
    add_tri(A, D, C)

    # Topo inclinado
    add_tri(C, D, E)
    add_tri(C, E, F)

    # Lateral esquerda (triângulo)
    add_tri(A, D, E)

    # Lateral direita (triângulo)
    add_tri(B, F, C)

    # Traseira (retângulo em z=-0.5)
    add_tri(A, B, F)  # parte “superior” é degenerada em altura? aqui fecha como parede inclinada? não:
    # Para traseira correta no wedge, a traseira real é o retângulo A-B (em baixo) + “ponto” nenhum em cima.
    # Então a rampa wedge fechada NÃO tem parede traseira alta — mas pra evitar buraco visual,
    # fechamos com dois triângulos até a linha superior (E/F ficam em z=+0.5, então não servem).
    # Melhor: NÃO criar traseira extra. Se você quer parede traseira, o shape muda.
    # -> removemos esta tentativa (não adiciona nada útil).

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

    stride = 6 * 4  # pos(3) + normal(3)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))

    glBindVertexArray(0)

    return vao, vbo, ebo, idx.size, tint