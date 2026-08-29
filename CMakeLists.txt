cmake_minimum_required(VERSION 3.21)
project(moko C)

# Native PS1 executable. Game code currently keeps its procedural fallback
# renderer while the asset pipeline is introduced incrementally.
psn00bsdk_add_executable(moko GPREL src/main.c)

# PSn00bSDK can embed binary assets (TIM/VAG) into the executable through
# objcopy-generated objects. Keep the source list centralized here so real
# MOKO textures/audio can be added without changing the disc layout.
set(MOKO_ASSET_DIR "${CMAKE_CURRENT_SOURCE_DIR}/assets")
set(MOKO_TEXTURE_DIR "${MOKO_ASSET_DIR}/textures")
set(MOKO_AUDIO_DIR "${MOKO_ASSET_DIR}/audio")

# Final PlayStation BIN/CUE image.
psn00bsdk_add_cd_image(moko_cd MOKO iso.xml DEPENDS moko)
