#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoords;

out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoords;
out vec4 FragPosLightSpace; // For shadow mapping

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform mat4 u_lightSpaceMatrix; // Matrix to transform to light's perspective

void main() {
    FragPos = vec3(u_model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(u_model))) * aNormal;
    TexCoords = aTexCoords;
    
    // Transform vertex position to light space for shadow calculation
    FragPosLightSpace = u_lightSpaceMatrix * vec4(FragPos, 1.0);

    gl_Position = u_projection * u_view * vec4(FragPos, 1.0);
}