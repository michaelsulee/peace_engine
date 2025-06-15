#version 330 core

// This shader is intentionally empty. For the depth pass, we don't need to
// output any color. The depth buffer is populated automatically by OpenGL
// based on the positions calculated in the vertex shader.
void main()
{
}