#version 330 core

layout (location = 0) out vec4 fragColor;

// This input variable now correctly matches the vertex shader's output
in vec3 texCoord;

uniform samplerCube skybox;

void main()
{
    // Sample the cubemap texture using the direction vector from the vertex shader
    fragColor = texture(skybox, texCoord);
}