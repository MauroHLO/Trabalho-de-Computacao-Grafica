#version 330 core

in vec3 vNormal;
in vec3 vFragPos;

out vec4 fragCor;

uniform vec3 uTint;

uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 lightColor;
uniform bool uUnlit;


void main() {

    // ✅ HUD/objetos "unlit": cor fixa, sem influência de luz
    if (uUnlit) {
        fragCor = vec4(uTint, 1.0);
        return;
    }

    vec3 N = normalize(vNormal);
    vec3 L = normalize(lightPos - vFragPos);

    // Ambiente
    vec3 ambient = 0.15 * lightColor;

    // Difusa (Lambert)
    float diff = max(dot(N, L), 0.0);
    vec3 diffuse = diff * lightColor;

    // Especular (Phong)
    vec3 V = normalize(viewPos - vFragPos);
    vec3 R = reflect(-L, N);
    float spec = pow(max(dot(V, R), 0.0), 32.0);
    vec3 specular = 0.5 * spec * lightColor;

    vec3 color = (ambient + diffuse + specular) * uTint;
    fragCor = vec4(color, 1.0);
}

