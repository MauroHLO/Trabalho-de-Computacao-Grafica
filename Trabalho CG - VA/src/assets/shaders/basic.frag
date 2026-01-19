#version 330 core

in vec3 vNormal;
in vec3 vFragPos;
in vec2 vUV;

out vec4 fragCor;

uniform vec3 uTint;

uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 lightColor;

uniform bool uUnlit;

// textura
uniform sampler2D uTex0;
uniform bool uUseTex;

void main() {

    // Albedo base: cor do material (com ou sem textura)
    vec3 albedo = uTint;

    if (uUseTex) {
        vec4 tex = texture(uTex0, vUV);
        albedo *= tex.rgb;

        // opcional: respeitar alpha da textura
        // se tu for usar transparência em sprites/HUD, tu pode:
        // if (tex.a < 0.1) discard;
    }

    // ✅ HUD/objetos "unlit": cor fixa, sem luz
    if (uUnlit) {
        fragCor = vec4(albedo, 1.0);
        return;
    }

    vec3 N = normalize(vNormal);
    vec3 L = normalize(lightPos - vFragPos);

    // Ambiente
    vec3 ambient = 0.75 * lightColor;

    // Difusa
    float diff = max(dot(N, L), 0.5);
    vec3 diffuse = diff * lightColor;

    // Especular (Phong)
    vec3 V = normalize(viewPos - vFragPos);
    vec3 R = reflect(-L, N);
    float spec = pow(max(dot(V, R), 0.0), 32.0);
    vec3 specular = 0.5 * spec * lightColor;

    vec3 color = (ambient + diffuse + specular) * albedo;
    fragCor = vec4(color, 1.0);
}
