#version 330 core
in vec3 vCor;
out vec4 fragCor;
void main(){
    fragCor = vec4(vCor, 1.0);
}