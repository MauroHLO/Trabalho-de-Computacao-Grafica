import math
import numpy as np
def perspectiva(fov, aspecto, perto, longe):
    f = 1.0 / math.tan(fov/2)
    M = np.zeros((4,4), dtype=np.float32)
    M[0,0] = f/aspecto
    M[1,1] = f
    M[2,2] = (longe+perto)/(perto-longe)
    M[2,3] = (2*longe*perto)/(perto-longe)
    M[3,2] = -1
    return M

def translacao(x,y,z):
    M = np.eye(4, dtype=np.float32)
    M[0,3], M[1,3], M[2,3] = x,y,z
    return M

def escala(sx,sy,sz):
    M = np.eye(4, dtype=np.float32)
    M[0,0], M[1,1], M[2,2] = sx,sy,sz
    return M

def rotacaoX(a):
    c, s = math.cos(a), math.sin(a)
    M = np.eye(4, dtype=np.float32)
    M[1,1], M[1,2] = c, -s
    M[2,1], M[2,2] = s, c
    return M

def rotacaoY(a):
    c, s = math.cos(a), math.sin(a)
    M = np.eye(4, dtype=np.float32)
    M[0,0], M[0,2] = c, s
    M[2,0], M[2,2] = -s, c
    return M

def look_at(visao, alvo, up):
    f = alvo - visao
    f = f / np.linalg.norm(f)
    u = up / np.linalg.norm(up)
    s = np.cross(f,u)
    s = s / np.linalg.norm(s)
    u = np.cross(s,f)
    M = np.eye(4, dtype=np.float32)
    M[0,0:3] = s
    M[1,0:3] = u
    M[2,0:3] = -f
    T = translacao(-visao[0], -visao[1], -visao[2])
    return M @ T
