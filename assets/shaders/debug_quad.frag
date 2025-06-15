#version 330 core

out vec4 FragColor;
in vec2 v_TexCoord;

uniform sampler2D debugTexture;

void main()
{
    // Sample the texture (our shadow map) and display its single
    // red component as a grayscale color.
    float depthValue = texture(debugTexture, v_TexCoord).r;
    FragColor = vec4(vec3(depthValue), 1.0);
}