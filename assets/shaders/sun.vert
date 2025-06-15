#version 330 core

layout (location = 0) in vec3 a_Position;
layout (location = 1) in vec3 a_Normal;
layout (location = 2) in vec2 a_TexCoord;

// Pass texture coordinates to the fragment shader
out vec2 v_TexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    v_TexCoord = a_TexCoord;
    gl_Position = projection * view * model * vec4(a_Position, 1.0);
}