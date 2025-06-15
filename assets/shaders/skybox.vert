#version 330 core

layout (location = 0) in vec3 a_Position;

out vec3 TexCoords;

uniform mat4 projection;
uniform mat4 view;

void main()
{
    TexCoords = a_Position;
    
    // Remove the translation part of the view matrix so the skybox doesn't move
    mat4 view_no_translation = mat4(mat3(view));
    
    // Project the vertex
    vec4 pos = projection * view_no_translation * vec4(a_Position, 1.0);
    
    // Set the z component of the final position to w. This forces the depth value
    // to be 1.0, the maximum depth, ensuring it's always drawn in the background.
    gl_Position = pos.xyww;
}