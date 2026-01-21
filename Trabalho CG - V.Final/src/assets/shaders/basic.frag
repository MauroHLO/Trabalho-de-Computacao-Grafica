#version 330 core

in vec3 vNormal;
in vec3 vFragPos;
in vec2 vUV;

out vec4 fragCor;

uniform vec3 uTint;

// textura
uniform sampler2D uTex0;
uniform bool uUseTex;

// camera
uniform vec3 viewPos;

// HUD/Unlit
uniform bool uUnlit;

// =========================
// Luz Direcional
// =========================
uniform vec3 uDirLightDir;
uniform vec3 uDirLightColor;
uniform float uDirLightIntensity;

// ambiente
uniform float uAmbientStrength;

// =========================
// Luzes Pontuais (4)
// =========================
#define NUM_POINT_LIGHTS 4

uniform vec3  uPointPos[NUM_POINT_LIGHTS];
uniform vec3  uPointColor[NUM_POINT_LIGHTS];
uniform float uPointIntensity[NUM_POINT_LIGHTS];
uniform float uPointRange[NUM_POINT_LIGHTS];

// -------------------------
// Funções auxiliares
// -------------------------
float pointAttenuation(float dist, float range) {
    float x = clamp(dist / max(range, 0.0001), 0.0, 1.0);
    float smoothFactor = 1.0 - (x * x * (3.0 - 2.0 * x));
    float inv = 1.0 / (1.0 + dist * dist * 0.08);
    return smoothFactor * inv;
}


void main() {

    // Cor base
    vec3 albedo = uTint;

    if (uUseTex) {
        vec4 tex = texture(uTex0, vUV);
        albedo *= tex.rgb;
    }

    // HUD/objetos sem luz
    if (uUnlit) {
        fragCor = vec4(albedo, 1.0);
        return;
    }

    vec3 N = normalize(vNormal);
    vec3 V = normalize(viewPos - vFragPos);

    // =========================
    // AMBIENTE
    // =========================
    vec3 ambient = uAmbientStrength * albedo;

    // =========================
    // DIRECIONAL (Phong simples)
    // =========================
    vec3 Ld = normalize(-uDirLightDir);
    float diffD = max(dot(N, Ld), 0.0);

    vec3 Rd = reflect(-Ld, N);
    float specD = pow(max(dot(V, Rd), 0.0), 32.0);

    vec3 dirLight = (diffD * albedo + 0.35 * specD * vec3(1.0))
                    * uDirLightColor * uDirLightIntensity;

    // =========================
    // PONTUAIS (4)
    // =========================
    vec3 pointSum = vec3(0.0);

    for (int i = 0; i < NUM_POINT_LIGHTS; i++) {
        vec3 LpVec = uPointPos[i] - vFragPos;
        float dist = length(LpVec);
        vec3 Lp = LpVec / max(dist, 0.0001);

        float att = pointAttenuation(dist, uPointRange[i]) * uPointIntensity[i];

        float diffP = max(dot(N, Lp), 0.0);

        vec3 Rp = reflect(-Lp, N);
        float specP = pow(max(dot(V, Rp), 0.0), 32.0);

        vec3 lightP = (diffP * albedo + 0.35 * specP * vec3(1.0))
                      * uPointColor[i] * att;

        pointSum += lightP;
    }

    vec3 color = ambient + dirLight + pointSum;
    fragCor = vec4(color, 1.0);

}
