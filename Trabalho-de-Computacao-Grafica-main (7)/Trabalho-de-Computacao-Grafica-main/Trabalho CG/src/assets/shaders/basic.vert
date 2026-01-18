#version 330 core

layout(location = 0) in vec3 pos;
layout(location = 1) in vec3 normal;

uniform mat4 mvp;
uniform mat4 model;

out vec3 vNormal;
out vec3 vFragPos;

void main() {
    gl_Position = mvp * vec4(pos, 1.0);

    vec4 worldPos = model * vec4(pos, 1.0);
    vFragPos = worldPos.xyz;

    mat3 normalMat = transpose(inverse(mat3(model)));
    vNormal = normalize(normalMat * normal);
}
