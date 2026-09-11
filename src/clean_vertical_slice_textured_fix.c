#include <psxgpu.h>

/* Compatibility shim for PSn00bSDK v0.24: the textured vertical slice stores
   a precomputed tpage value, while setTPage() in this SDK expects texture mode,
   blend mode and VRAM coordinates. Keep the renderer source clean and assign
   the already computed tpage directly. */
#undef setTPage
#define setTPage(p,tp) ((p)->tpage=(tp))
#define SetShadeTex setShadeTex

#include "clean_vertical_slice_textured.c"
