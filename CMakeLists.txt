cmake_minimum_required(VERSION 3.21)
project(moko LANGUAGES C ASM)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

# CLEAN TEXTURED VERTICAL SLICE BUILD
# ----------------------------------
# Authoring assets remain external OBJ files. They are converted at build time
# into compact PS1 position/UV/triangle tables and consumed by one explicit
# runtime. The old injection chain remains out of the active build.

set(MOKO_GENERATED_DIR "${PROJECT_BINARY_DIR}/generated")
set(MOKO_OBJ_CONVERTER "${PROJECT_SOURCE_DIR}/tools/obj_to_header.py")
set(MOKO_MODEL_H "${MOKO_GENERATED_DIR}/moko_generated.h")
set(MOKO_VILLAGE_H "${MOKO_GENERATED_DIR}/village_model.h")
set(MOKO_CLOCKMAKER_H "${MOKO_GENERATED_DIR}/clockmaker_model.h")
set(MOKO_BOAR_H "${MOKO_GENERATED_DIR}/boar_model.h")

add_custom_command(
    OUTPUT "${MOKO_MODEL_H}"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${MOKO_GENERATED_DIR}"
    COMMAND ${Python3_EXECUTABLE} "${MOKO_OBJ_CONVERTER}"
            "${PROJECT_SOURCE_DIR}/assets/models/moko_lowpoly.obj"
            "${MOKO_MODEL_H}" moko
    DEPENDS "${MOKO_OBJ_CONVERTER}" "${PROJECT_SOURCE_DIR}/assets/models/moko_lowpoly.obj"
    VERBATIM
)
add_custom_command(
    OUTPUT "${MOKO_VILLAGE_H}"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${MOKO_GENERATED_DIR}"
    COMMAND ${Python3_EXECUTABLE} "${MOKO_OBJ_CONVERTER}"
            "${PROJECT_SOURCE_DIR}/assets/models/village_dawn_slice.obj"
            "${MOKO_VILLAGE_H}" village
    DEPENDS "${MOKO_OBJ_CONVERTER}" "${PROJECT_SOURCE_DIR}/assets/models/village_dawn_slice.obj"
    VERBATIM
)
add_custom_command(
    OUTPUT "${MOKO_CLOCKMAKER_H}"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${MOKO_GENERATED_DIR}"
    COMMAND ${Python3_EXECUTABLE} "${MOKO_OBJ_CONVERTER}"
            "${PROJECT_SOURCE_DIR}/assets/models/clockmaker.obj"
            "${MOKO_CLOCKMAKER_H}" clockmaker
    DEPENDS "${MOKO_OBJ_CONVERTER}" "${PROJECT_SOURCE_DIR}/assets/models/clockmaker.obj"
    VERBATIM
)
add_custom_command(
    OUTPUT "${MOKO_BOAR_H}"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${MOKO_GENERATED_DIR}"
    COMMAND ${Python3_EXECUTABLE} "${MOKO_OBJ_CONVERTER}"
            "${PROJECT_SOURCE_DIR}/assets/models/shadow_boar.obj"
            "${MOKO_BOAR_H}" boar
    DEPENDS "${MOKO_OBJ_CONVERTER}" "${PROJECT_SOURCE_DIR}/assets/models/shadow_boar.obj"
    VERBATIM
)

add_custom_target(moko_models DEPENDS
    "${MOKO_MODEL_H}" "${MOKO_VILLAGE_H}" "${MOKO_CLOCKMAKER_H}" "${MOKO_BOAR_H}")

psn00bsdk_add_executable(moko GPREL src/clean_vertical_slice_textured_fix.c)
target_include_directories(moko PRIVATE "${MOKO_GENERATED_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}/src")
add_dependencies(moko moko_models)
psn00bsdk_add_cd_image(moko_cd MOKO iso.xml DEPENDS moko)
