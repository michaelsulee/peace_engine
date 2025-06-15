#version 330 core
layout (location = 0) in vec3 aPos;

out vec3 TexCoords;

uniform mat4 projection;
uniform mat4 view; // This should be the view matrix without translation

void main() {
    TexCoords = aPos;
    // Remove the need for depth modifications in the main loop
    // by setting z and w to the same value. This forces the depth to be 1.0 after perspective divide.
    vec4 pos = projection * view * vec4(aPos, 1.0);
    gl_Position = pos.xyww; 
}