cmake_minimum_required(VERSION 3.21)
project(moko LANGUAGES C ASM)

psn00bsdk_add_executable(moko GPREL src/main.c)

set(MOKO_ASSET_DIR "${CMAKE_CURRENT_SOURCE_DIR}/assets")
set(MOKO_TEXTURE_DIR "${MOKO_ASSET_DIR}/textures")
set(MOKO_AUDIO_DIR "${MOKO_ASSET_DIR}/audio")

# Build the first native PS1 TIM asset from a text generator so the repository
# stays editable through GitHub while the resulting game still embeds a real
# binary TIM texture.
set(MOKO_GENERATED_DIR "${PROJECT_BINARY_DIR}/generated")
set(MOKO_TIM "${MOKO_GENERATED_DIR}/moko.tim")
add_custom_command(
    OUTPUT "${MOKO_TIM}"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${MOKO_GENERATED_DIR}"
    COMMAND ${CMAKE_COMMAND} -DOUTPUT_FILE="${MOKO_TIM}" -P "${PROJECT_SOURCE_DIR}/cmake/GenerateMokoTim.cmake"
    DEPENDS "${PROJECT_SOURCE_DIR}/cmake/GenerateMokoTim.cmake"
    VERBATIM
)
add_custom_target(moko_assets DEPENDS "${MOKO_TIM}")
add_dependencies(moko moko_assets)
psn00bsdk_target_incbin(moko PRIVATE moko_tim "${MOKO_TIM}")

psn00bsdk_add_cd_image(moko_cd MOKO iso.xml DEPENDS moko)
