from OpenGL.GL import *

def desenhar(vao_tuple, model, vp, prog,
             light_pos=(2.0, 3.0, 4.0),
             view_pos=(0.0, 0.0, 5.0),
             light_color=(1.0, 1.0, 1.0),
             tint=None,
             unlit=False,
             tex=None,          # <- Texture2D (engine/texturas.py)
             use_tex=False):    # <- liga/desliga no shader

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

    # cor do material (vira multiplicador do albedo)
    glUniform3f(glGetUniformLocation(prog, "uTint"), *tint)

    loc_unlit = glGetUniformLocation(prog, "uUnlit")
    if loc_unlit != -1:
        glUniform1i(loc_unlit, 1 if unlit else 0)

    # -------- TEXTURA (opcional) --------
    loc_use = glGetUniformLocation(prog, "uUseTex")
    if loc_use != -1:
        glUniform1i(loc_use, 1 if (use_tex and tex is not None) else 0)

    if use_tex and tex is not None:
        # bind na unit 0
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex.id)  # se teu Texture2D tiver .id

        loc_tex = glGetUniformLocation(prog, "uTex0")
        if loc_tex != -1:
            glUniform1i(loc_tex, 0)

    glBindVertexArray(vao)
    glDrawElements(GL_TRIANGLES, count, GL_UNSIGNED_INT, None)
    glBindVertexArray(0)
