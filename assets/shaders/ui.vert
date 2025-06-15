// assets/shaders/ui.vert
#version 330 core
layout (location = 0) in vec3 a_Position;
layout (location = 2) in vec2 a_TexCoord;
out vec2 v_TexCoord;
uniform mat4 projection;
uniform mat4 model;
void main() {
    gl_Position = projection * model * vec4(a_Position.xy, 0.0, 1.0);
    v_TexCoord = a_TexCoord;
}