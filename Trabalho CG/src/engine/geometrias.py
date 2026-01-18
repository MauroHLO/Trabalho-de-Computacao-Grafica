import numpy as np
from OpenGL.GL import *

import numpy as np

def criarCubo(cor=(1.0, 1.0, 1.0)):
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


def criarPlataforma(cor=(1,1,1)):
    c = cor
    verts = np.array([
        -0.5,0, -0.5, *c,
         0.5,0, -0.5, *c,
         0.5,0,  0.5, *c,
        -0.5,0,  0.5, *c
    ], dtype=np.float32)

    idx = np.array([0,1,2, 2,3,0], dtype=np.uint32)
    return verts, idx, cor

def criarVAO(verts, idx, cor=(1.0, 1.0, 1.0)):
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)

    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, idx.nbytes, idx, GL_STATIC_DRAW)

    stride = (3 + 3) * 4  # pos + normal

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))

    glBindVertexArray(0)

    # 👇 agora devolve o tint junto no tuple
    return vao, vbo, ebo, idx.size, cor


