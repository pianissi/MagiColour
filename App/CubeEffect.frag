#version 440
layout(location = 0) in vec2 coord;
layout(location = 0) out vec4 fragColor;

layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
		float hueOffset;
};
// layout(binding = 1) uniform sampler2D src;
// uniform float hueOffset;

vec3 hue2rgb(float hue) {
		hue = fract(hue); //only use fractional part of hue, making it loop,
		float r = abs(hue * 6 - 3) - 1; //red,
		float g = 2 - abs(hue * 6 - 2); //green,
		float b = 2 - abs(hue * 6 - 4); //blue,
		vec3 rgb = vec3(r,g,b); //combine components,
		rgb = clamp(rgb, 0.0, 1.0); //clamp between 0 and 1,
		return rgb;
}
vec3 hsv2rgb(vec3 hsv) {
		vec3 rgb = hue2rgb(hsv.x); //apply hue,
		rgb = mix(vec3(1), rgb, hsv.y); //apply saturation,
		rgb = rgb * hsv.z; //apply value,
		return rgb;
}

void main() {
    // vec4 tex = texture(src, coord);
    // fragColor = vec4(vec3(dot(tex.rgb, vec3(0.344, 0.5, 0.156))), tex.a) * qt_Opacity;

		// vec2 uv = coord / iResolution.xy;
		vec2 uv = coord;
		vec3 hsv = vec3(hueOffset, uv.x, uv.y * -1 + 1);
		fragColor = vec4(hsv2rgb(hsv), 1.0);
}