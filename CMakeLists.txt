cmake_minimum_required(VERSION 3.21)
project(moko LANGUAGES C ASM)

# Native PS1 executable. Game code currently keeps its procedural fallback
# renderer while the asset pipeline is introduced incrementally.
psn00bsdk_add_executable(moko GPREL src/main.c)

# Native asset roots. Binary TIM/VAG files can be embedded directly into the
# executable with psn00bsdk_target_incbin() as they are introduced.
set(MOKO_ASSET_DIR "${CMAKE_CURRENT_SOURCE_DIR}/assets")
set(MOKO_TEXTURE_DIR "${MOKO_ASSET_DIR}/textures")
set(MOKO_AUDIO_DIR "${MOKO_ASSET_DIR}/audio")

# psn00bsdk_target_incbin() requires ASM support (enabled above). Example for
# the first real texture once assets/textures/moko.tim is committed:
# psn00bsdk_target_incbin(moko PRIVATE moko_tim assets/textures/moko.tim)

# Final PlayStation BIN/CUE image.
psn00bsdk_add_cd_image(moko_cd MOKO iso.xml DEPENDS moko)
