import numpy as np
import ctypes
from OpenGL.GL import *

def criarCubo(cor=[0.7,0.7,0.7]):
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
    return verts, idx

def criarPlataforma(cor=[0.4,0.8,0.4]):
    c = cor
    verts = np.array([
        -0.5,0, -0.5, *c,
         0.5,0, -0.5, *c,
         0.5,0,  0.5, *c,
        -0.5,0,  0.5, *c
    ], dtype=np.float32)

    idx = np.array([0,1,2, 2,3,0], dtype=np.uint32)
    return verts, idx

def criarRampaSolida(cor=[0.64, 0.48, 0.24]):
    """
    Rampa sólida (prisma triangular), totalmente fechada.
    A face inclinada está com winding CORRETO (CCW),
    então NÃO fica transparente com GL_CULL_FACE ligado.
    """
    c = cor

    # Vértices
    # base (y = 0)
    # topo sobe até y = 1 no final (z = +0.5)
    verts = np.array([
        # base
        -0.5, 0.0, -0.5, *c,  # 0
         0.5, 0.0, -0.5, *c,  # 1
         0.5, 0.0,  0.5, *c,  # 2
        -0.5, 0.0,  0.5, *c,  # 3

        # topo inclinado (final da rampa)
        -0.5, 1.0,  0.5, *c,  # 4
         0.5, 1.0,  0.5, *c,  # 5
    ], dtype=np.float32)

    # Índices (triângulos)
    idx = np.array([
        # base (embaixo)
        0, 2, 1,
        0, 3, 2,

        # topo inclinado (CORRIGIDO – CCW)
        2, 3, 4,
        2, 4, 5,

        # lateral esquerda
        0, 3, 4,
        0, 4, 0,  # degenerate evitado depois

        # lateral direita
        1, 5, 2,
        1, 1, 5,  # degenerate evitado depois
    ], dtype=np.uint32)

    # === versão FINAL (sem triângulos degenerados, totalmente fechada) ===
    verts = np.array([
        # base
        -0.5, 0.0, -0.5, *c,  # 0
         0.5, 0.0, -0.5, *c,  # 1
         0.5, 0.0,  0.5, *c,  # 2
        -0.5, 0.0,  0.5, *c,  # 3

        # topo inclinado
        -0.5, 1.0,  0.5, *c,  # 4
         0.5, 1.0,  0.5, *c,  # 5

        # duplicados para fechar traseira corretamente
        -0.5, 0.0, -0.5, *c,  # 6
         0.5, 0.0, -0.5, *c,  # 7
    ], dtype=np.float32)

    idx = np.array([
        # base
        0, 2, 1,
        0, 3, 2,

        # topo inclinado (CORRETO)
        2, 3, 4,
        2, 4, 5,

        # lateral esquerda
        0, 3, 4,
        0, 4, 6,

        # lateral direita
        1, 7, 5,
        1, 5, 2,

        # traseira
        0, 6, 7,
        0, 7, 1,
    ], dtype=np.uint32)

    return verts, idx

def criarVAO(verts, idx):
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)

    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, idx.nbytes, idx, GL_STATIC_DRAW)

    stride = (3+3)*4
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,stride,ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,stride,ctypes.c_void_p(12))

    glBindVertexArray(0)
    return vao, vbo, ebo, idx.size
