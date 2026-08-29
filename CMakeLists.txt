cmake_minimum_required(VERSION 3.20)
project(moko C)

psn00bsdk_add_executable(moko GPREL src/main.c)
psn00bsdk_add_cd_image(moko_cd MOKO iso.xml DEPENDS moko)
