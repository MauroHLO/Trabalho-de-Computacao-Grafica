def criarCubo(cor=[0.7,0.7,0.7]):
    # cubo com cor aplicada a todos os vértices
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
