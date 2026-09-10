cmake_minimum_required(VERSION 3.21)
project(moko LANGUAGES C ASM)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(MOKO_GENERATED_DIR "${PROJECT_BINARY_DIR}/generated")
set(MOKO_GENERATED_VISUAL_BASE "${MOKO_GENERATED_DIR}/main_visual_base.c")
set(MOKO_GENERATED_ENEMY_BASE "${MOKO_GENERATED_DIR}/main_enemy_base.c")
set(MOKO_GENERATED_SAVE_BASE "${MOKO_GENERATED_DIR}/main_save_base.c")
set(MOKO_GENERATED_MISSION_BASE "${MOKO_GENERATED_DIR}/main_mission_base.c")
set(MOKO_GENERATED_DELIVERY_BASE "${MOKO_GENERATED_DIR}/main_delivery_base.c")
set(MOKO_GENERATED_COMBAT_BASE "${MOKO_GENERATED_DIR}/main_combat_base.c")
set(MOKO_GENERATED_ENCOUNTER_BASE "${MOKO_GENERATED_DIR}/main_encounter_base.c")
set(MOKO_GENERATED_GUARD_BASE "${MOKO_GENERATED_DIR}/main_guard_base.c")
set(MOKO_GENERATED_MAIN "${MOKO_GENERATED_DIR}/main_visual.c")
add_custom_command(
    OUTPUT "${MOKO_GENERATED_MAIN}"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${MOKO_GENERATED_DIR}"
    COMMAND ${Python3_EXECUTABLE} "${PROJECT_SOURCE_DIR}/tools/inject_station_visuals.py" "${PROJECT_SOURCE_DIR}/src/main.c" "${MOKO_GENERATED_VISUAL_BASE}"
    COMMAND ${Python3_EXECUTABLE} "${PROJECT_SOURCE_DIR}/tools/inject_enemy_visuals.py" "${MOKO_GENERATED_VISUAL_BASE}" "${MOKO_GENERATED_ENEMY_BASE}"
    COMMAND ${Python3_EXECUTABLE} "${PROJECT_SOURCE_DIR}/tools/inject_save_continue.py" "${MOKO_GENERATED_ENEMY_BASE}" "${MOKO_GENERATED_SAVE_BASE}"
    COMMAND ${Python3_EXECUTABLE} "${PROJECT_SOURCE_DIR}/tools/inject_mission_polish.py" "${MOKO_GENERATED_SAVE_BASE}" "${MOKO_GENERATED_MISSION_BASE}"
    COMMAND ${Python3_EXECUTABLE} "${PROJECT_SOURCE_DIR}/tools/inject_delivery_polish.py" "${MOKO_GENERATED_MISSION_BASE}" "${MOKO_GENERATED_DELIVERY_BASE}"
    COMMAND ${Python3_EXECUTABLE} "${PROJECT_SOURCE_DIR}/tools/inject_combat_polish.py" "${MOKO_GENERATED_DELIVERY_BASE}" "${MOKO_GENERATED_COMBAT_BASE}"
    COMMAND ${Python3_EXECUTABLE} "${PROJECT_SOURCE_DIR}/tools/inject_encounter_polish.py" "${MOKO_GENERATED_COMBAT_BASE}" "${MOKO_GENERATED_ENCOUNTER_BASE}"
    COMMAND ${Python3_EXECUTABLE} "${PROJECT_SOURCE_DIR}/tools/inject_clock_guard.py" "${MOKO_GENERATED_ENCOUNTER_BASE}" "${MOKO_GENERATED_GUARD_BASE}"
    COMMAND ${Python3_EXECUTABLE} "${PROJECT_SOURCE_DIR}/tools/inject_memory_clocks.py" "${MOKO_GENERATED_GUARD_BASE}" "${MOKO_GENERATED_MAIN}"
    DEPENDS "${PROJECT_SOURCE_DIR}/src/main.c" "${PROJECT_SOURCE_DIR}/tools/inject_station_visuals.py" "${PROJECT_SOURCE_DIR}/tools/inject_enemy_visuals.py" "${PROJECT_SOURCE_DIR}/tools/inject_save_continue.py" "${PROJECT_SOURCE_DIR}/tools/inject_mission_polish.py" "${PROJECT_SOURCE_DIR}/tools/inject_delivery_polish.py" "${PROJECT_SOURCE_DIR}/tools/inject_combat_polish.py" "${PROJECT_SOURCE_DIR}/tools/inject_encounter_polish.py" "${PROJECT_SOURCE_DIR}/tools/inject_clock_guard.py" "${PROJECT_SOURCE_DIR}/tools/inject_memory_clocks.py" "${PROJECT_SOURCE_DIR}/src/world3d.h" "${PROJECT_SOURCE_DIR}/src/save.h"
    VERBATIM
)

psn00bsdk_add_executable(moko GPREL "${MOKO_GENERATED_MAIN}" src/moko_sprite.c src/gameplay.c src/audio.c src/finale.c src/save.c src/memcard.c src/quests.c src/world_events.c src/adventure.c src/level_data.c src/items.c src/journal.c src/ambient.c src/npc.c src/enemies.c src/world_runtime.c src/intro.c src/station_visuals.c)
target_include_directories(moko PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/src")

set(MOKO_ASSET_DIR "${CMAKE_CURRENT_SOURCE_DIR}/assets")
set(MOKO_TEXTURE_DIR "${MOKO_ASSET_DIR}/textures")
set(MOKO_AUDIO_DIR "${MOKO_ASSET_DIR}/audio")

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
