cmake_minimum_required(VERSION 3.21)
project(moko LANGUAGES C ASM)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

# CLEAN VERTICAL SLICE BUILD
# --------------------------
# The previous build generated the runtime by applying a long sequence of text
# injection scripts to src/main.c/world3d_v2.c. That made visual changes fragile
# and kept legacy primitive presentation alive. The clean slice instead compiles
# one explicit runtime and generates compact PS1 mesh tables directly from OBJ
# authoring assets. This follows the asset/runtime separation used by practical
# PS1 projects while keeping every MOKO model and level original.

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
    "${MOKO_MODEL_H}"
    "${MOKO_VILLAGE_H}"
    "${MOKO_CLOCKMAKER_H}"
    "${MOKO_BOAR_H}"
)

psn00bsdk_add_executable(moko GPREL src/clean_vertical_slice.c)
target_include_directories(moko PRIVATE
    "${MOKO_GENERATED_DIR}"
    "${CMAKE_CURRENT_SOURCE_DIR}/src"
)
add_dependencies(moko moko_models)

psn00bsdk_add_cd_image(moko_cd MOKO iso.xml DEPENDS moko)
