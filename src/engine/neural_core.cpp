#include <emscripten/emscripten.h>
#include <cmath>

extern "C" {
    // Ye function JavaScript se 10x fast calculate karega neural paths
    EMSCRIPTEN_KEEPALIVE
    float calculate_pull_force(float x, float y, float targetX, float targetY) {
        float dx = targetX - x;
        float dy = targetY - y;
        return sqrt(dx*dx + dy*dy) / 100.0; // Optimized math
    }
}
