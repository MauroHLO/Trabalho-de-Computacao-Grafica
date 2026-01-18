#version 330 core
in vec3 vCor;
out vec4 fragCor;

uniform vec3 uTint;

void main(){
    vec3 c = vCor * uTint;
    fragCor = vec4(c, 1.0);
}
