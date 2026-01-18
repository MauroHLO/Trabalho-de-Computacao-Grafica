from OpenGL.GL import *
from engine.transformacoes import escala
from engine.transformacoes import rotacaoY, translacao
def desenhar(vao_tuple,model,vp,prog):
    vao,vbo,ebo,count = vao_tuple
    mvp = vp @ model
    glUseProgram(prog)
    loc = glGetUniformLocation(prog,"mvp")
    glUniformMatrix4fv(loc,1,GL_FALSE,mvp.T)
    glBindVertexArray(vao)
    glDrawElements(GL_TRIANGLES,count,GL_UNSIGNED_INT,None)
    glBindVertexArray(0)

