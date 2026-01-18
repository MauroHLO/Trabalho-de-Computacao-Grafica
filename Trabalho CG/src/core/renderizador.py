from OpenGL.GL import *

def desenhar(vao_tuple, model, vp, prog,
             light_pos=(2.0, 3.0, 4.0),
             view_pos=(0.0, 0.0, 5.0),
             light_color=(1.0, 1.0, 1.0),
             tint=None):

    if len(vao_tuple) == 5:
        vao, vbo, ebo, count, vao_tint = vao_tuple
    else:
        vao, vbo, ebo, count = vao_tuple
        vao_tint = (1.0, 1.0, 1.0)

    if tint is None:
        tint = vao_tint

    mvp = vp @ model

    glUseProgram(prog)
    glUniformMatrix4fv(glGetUniformLocation(prog, "mvp"), 1, GL_FALSE, mvp.T)
    glUniformMatrix4fv(glGetUniformLocation(prog, "model"), 1, GL_FALSE, model.T)

    glUniform3f(glGetUniformLocation(prog, "lightPos"), *light_pos)
    glUniform3f(glGetUniformLocation(prog, "viewPos"), *view_pos)
    glUniform3f(glGetUniformLocation(prog, "lightColor"), *light_color)

    # aqui: cor do material
    glUniform3f(glGetUniformLocation(prog, "uTint"), *tint)

    glBindVertexArray(vao)
    glDrawElements(GL_TRIANGLES, count, GL_UNSIGNED_INT, None)
    glBindVertexArray(0)

