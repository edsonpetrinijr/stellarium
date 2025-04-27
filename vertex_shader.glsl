// vertex_shader.glsl
#version 120
void main() {
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    gl_PointSize = gl_Vertex.w;  
    // ou passe o tamanho por atributo/uniform, se preferir
}

// fragment_shader.glsl
#version 120
uniform vec4 uColor;
void main() {
    // gl_PointCoord vai de (0,0) a (1,1) dentro do sprite
    float d = distance(gl_PointCoord, vec2(0.5));
    if (d > 0.5) {
        discard;            // fora do círculo
    }
    gl_FragColor = uColor;
}
