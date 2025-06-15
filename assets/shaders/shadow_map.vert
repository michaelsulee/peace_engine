#version 330 core

layout (location = 0) in vec3 a_Position;

uniform mat4 lightSpaceMatrix;
uniform mat4 model;

void main()
{
    // This shader's only job is to transform vertices into the light's
    // coordinate space for the depth pass.
    gl_Position = lightSpaceMatrix * model * vec4(a_Position, 1.0);
}