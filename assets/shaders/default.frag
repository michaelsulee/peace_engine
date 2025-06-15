#version 330 core
out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoords;
in vec4 FragPosLightSpace; // Received from vertex shader

uniform sampler2D shadowMap; // The depth texture from the first pass

uniform vec3 u_viewPos;
uniform vec3 u_lightPos;

uniform bool u_is_ghost;
uniform bool u_is_selected;
uniform bool u_textured;
uniform bool u_is_unlit;

// Calculates the shadow factor (0.0 for in shadow, 1.0 for lit)
float CalculateShadow(vec4 fragPosLightSpace) {
    // Perform perspective divide to get normalized device coordinates
    vec3 projCoords = fragPosLightSpace.xyz / fragPosLightSpace.w;
    // Transform to [0,1] range for texture sampling
    projCoords = projCoords * 0.5 + 0.5;

    // Return 1.0 (fully lit) if outside the shadow map
    if (projCoords.z > 1.0) {
        return 1.0;
    }

    // Get depth of current fragment from light's perspective
    float currentDepth = projCoords.z;
    // Set a bias to prevent "shadow acne" artifact
    float bias = max(0.005 * (1.0 - dot(normalize(Normal), normalize(u_lightPos - FragPos))), 0.0005);
    
    // PCF (Percentage-Closer Filtering) for soft shadows
    float shadow = 0.0;
    vec2 texelSize = 1.0 / textureSize(shadowMap, 0);
    for(int x = -1; x <= 1; ++x) {
        for(int y = -1; y <= 1; ++y) {
            float pcfDepth = texture(shadowMap, projCoords.xy + vec2(x, y) * texelSize).r; 
            if(currentDepth - bias > pcfDepth) {
                shadow += 1.0;
            }
        }    
    }
    shadow /= 9.0;

    return 1.0 - shadow;
}

void main() {
    if (u_is_unlit) {
        FragColor = vec4(1.0, 1.0, 0.9, 1.0);
        return;
    }

    float ambientStrength = 0.2;
    vec3 lightColor = vec3(1.0, 1.0, 1.0);
    vec3 objectColor = vec3(0.75, 0.75, 0.75);

    vec3 ambient = ambientStrength * lightColor;

    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(u_lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    
    float specularStrength = 0.5;
    vec3 viewDir = normalize(u_viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = specularStrength * spec * lightColor;
    
    // Calculate shadow factor
    float shadow = CalculateShadow(FragPosLightSpace);
    
    // Apply shadow to diffuse and specular components only
    vec3 lighting = (ambient + shadow * (diffuse + specular));
    vec3 result = lighting * objectColor;
    FragColor = vec4(result, 1.0);

    if (u_is_selected) {
        FragColor.rgb += vec3(0.15, 0.15, 0.15); 
    }
    if (u_is_ghost) {
        FragColor = vec4(0.0, 1.0, 0.0, 0.4);
    }
}