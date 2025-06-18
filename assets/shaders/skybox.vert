#version 330 core

// Declare all attributes that the Mesh class provides to prevent mismatch
layout (location = 0) in vec3 a_position;
layout (location = 1) in vec3 a_normal;
layout (location = 2) in vec2 a_texcoord;
layout (location = 3) in vec3 a_tangent;
layout (location = 4) in vec3 a_bitangent;

out vec3 texCoord;

uniform mat4 view;
uniform mat4 projection;

void main()
{
    // We only use the position for the texture coordinate and final position
    texCoord = a_position;
    
    // Use the .xyww trick for robust depth rendering
    vec4 pos = projection * view * vec4(a_position, 1.0);
    gl_Position = pos.xyww;
}