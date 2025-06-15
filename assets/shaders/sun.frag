#version 330 core

out vec4 FragColor;

// Inputs from the vertex shader and engine
in vec2 v_TexCoord;
uniform float u_time; // Time passed since engine start

void main()
{
    // Define two colors for our fire effect
    vec3 color1 = vec3(1.0, 0.8, 0.0); // Bright Yellow
    vec3 color2 = vec3(1.0, 0.2, 0.0); // Deep Orange/Red

    // Create a shimmering, time-animated pattern using sine waves
    // based on the texture coordinate and time. This creates horizontal bands that move.
    float mix_value = (sin(v_TexCoord.y * 30.0 + u_time * 5.0) + 1.0) / 2.0;
    
    // Mix the two colors based on the pattern
    vec3 final_color = mix(color1, color2, mix_value);
    
    // Add some brighter "hotspots"
    float hotspot = pow(sin(v_TexCoord.y * 10.0 - u_time * 7.0) * 0.5 + 0.5, 16.0);
    final_color += vec3(1.0, 0.6, 0.2) * hotspot;

    FragColor = vec4(final_color, 1.0);
}