from OpenGL.GL import *

NUM_POINT_LIGHTS = 4

def _u3(prog, name, v):
    loc = glGetUniformLocation(prog, name)
    if loc != -1:
        glUniform3f(loc, float(v[0]), float(v[1]), float(v[2]))

def _u1f(prog, name, x):
    loc = glGetUniformLocation(prog, name)
    if loc != -1:
        glUniform1f(loc, float(x))

def _u1i(prog, name, x):
    loc = glGetUniformLocation(prog, name)
    if loc != -1:
        glUniform1i(loc, int(x))

def desenhar(vao_tuple, model, vp, prog,
             # camera
             view_pos=(0.0, 0.0, 5.0),

             # direcional
             dir_dir=(0.3, -1.0, 0.2),
             dir_color=(1.0, 1.0, 1.0),
             dir_intensity=1.0,
             ambient_strength=0.18,

             # 4 point lights
             point_pos=None,
             point_color=None,
             point_intensity=None,
             point_range=None,

             # material
             tint=None,
             unlit=False,

             # textura
             tex=None,
             use_tex=False):

    if len(vao_tuple) == 5:
        vao, vbo, ebo, count, vao_tint = vao_tuple
    else:
        vao, vbo, ebo, count = vao_tuple
        vao_tint = (1.0, 1.0, 1.0)

    if tint is None:
        tint = vao_tint

    # defaults para 4 luzes
    if point_pos is None:
        point_pos = [(0.0, 2.0, 0.0)] * NUM_POINT_LIGHTS
    if point_color is None:
        point_color = [(1.0, 1.0, 1.0)] * NUM_POINT_LIGHTS
    if point_intensity is None:
        point_intensity = [0.0] * NUM_POINT_LIGHTS
    if point_range is None:
        point_range = [10.0] * NUM_POINT_LIGHTS

    mvp = vp @ model

    glUseProgram(prog)

    glUniformMatrix4fv(glGetUniformLocation(prog, "mvp"), 1, GL_FALSE, mvp.T)
    glUniformMatrix4fv(glGetUniformLocation(prog, "model"), 1, GL_FALSE, model.T)

    # material tint
    _u3(prog, "uTint", tint)

    # camera
    _u3(prog, "viewPos", view_pos)

    # unlit
    _u1i(prog, "uUnlit", 1 if unlit else 0)

    # direcional
    _u3(prog, "uDirLightDir", dir_dir)
    _u3(prog, "uDirLightColor", dir_color)
    _u1f(prog, "uDirLightIntensity", dir_intensity)
    _u1f(prog, "uAmbientStrength", ambient_strength)

    # 4 point lights (arrays)
    for i in range(NUM_POINT_LIGHTS):
        _u3(prog, f"uPointPos[{i}]", point_pos[i])
        _u3(prog, f"uPointColor[{i}]", point_color[i])
        _u1f(prog, f"uPointIntensity[{i}]", point_intensity[i])
        _u1f(prog, f"uPointRange[{i}]", point_range[i])

    # -------- TEXTURA (opcional) --------
    _u1i(prog, "uUseTex", 1 if (use_tex and tex is not None) else 0)

    if use_tex and tex is not None:
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex.id)

        loc_tex = glGetUniformLocation(prog, "uTex0")
        if loc_tex != -1:
            glUniform1i(loc_tex, 0)

    glBindVertexArray(vao)
    glDrawElements(GL_TRIANGLES, count, GL_UNSIGNED_INT, None)
    glBindVertexArray(0)