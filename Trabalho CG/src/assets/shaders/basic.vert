#version 330 core
layout(location = 0) in vec3 pos;
layout(location = 1) in vec3 cor;
uniform mat4 mvp;
out vec3 vCor;
void main(){
    gl_Position = mvp * vec4(pos, 1.0);
    vCor = cor;
}