cmake_minimum_required(VERSION 3.21)
project(moko LANGUAGES C ASM)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

psn00bsdk_add_executable(moko GPREL src/main.c src/moko_sprite.c src/gameplay.c src/audio.c src/finale.c)
target_include_directories(moko PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/src")

set(MOKO_ASSET_DIR "${CMAKE_CURRENT_SOURCE_DIR}/assets")
set(MOKO_TEXTURE_DIR "${MOKO_ASSET_DIR}/textures")
set(MOKO_AUDIO_DIR "${MOKO_ASSET_DIR}/audio")

set(MOKO_GENERATED_DIR "${PROJECT_BINARY_DIR}/generated")
set(MOKO_TIM "${MOKO_GENERATED_DIR}/moko.tim")
add_custom_command(
    OUTPUT "${MOKO_TIM}"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${MOKO_GENERATED_DIR}"
    COMMAND ${Python3_EXECUTABLE} "${PROJECT_SOURCE_DIR}/tools/generate_moko_tim.py" "${MOKO_TIM}"
    DEPENDS "${PROJECT_SOURCE_DIR}/tools/generate_moko_tim.py"
    VERBATIM
)
add_custom_target(moko_assets DEPENDS "${MOKO_TIM}")
add_dependencies(moko moko_assets)
psn00bsdk_target_incbin(moko PRIVATE moko_tim "${MOKO_TIM}")

psn00bsdk_add_cd_image(moko_cd MOKO iso.xml DEPENDS moko)
