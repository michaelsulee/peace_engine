// assets/shaders/ui.frag
#version 330 core
out vec4 FragColor;
in vec2 v_TexCoord;
uniform sampler2D UIsampler;
uniform vec4 color;
void main() {
    FragColor = texture(UIsampler, v_TexCoord) * color;
}