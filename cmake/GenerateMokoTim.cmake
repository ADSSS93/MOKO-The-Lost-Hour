# Generate a tiny valid 16-bit PlayStation TIM texture at build time.
# The image is 16x24 pixels and is intentionally simple: it proves the native
# TIM -> incbin -> VRAM path without requiring a binary file in the repository.
if(NOT DEFINED OUTPUT_FILE)
  message(FATAL_ERROR "OUTPUT_FILE is required")
endif()

# TIM header: magic 0x10, flags 0x02 (16-bit direct color).
set(hex "1000000002000000")
# Image block: 12-byte header + 16*24*2 bytes = 780 (0x30c).
string(APPEND hex "0c030000c001000010001800")

# 384 little-endian BGR555 pixels. Transparent-looking dark border plus a
# warm face/body silhouette, teal coat and bright eye/highlight pixels.
foreach(y RANGE 0 23)
  foreach(x RANGE 0 15)
    set(px "0000")
    if(y GREATER_EQUAL 2 AND y LESS_EQUAL 9 AND x GREATER_EQUAL 4 AND x LESS_EQUAL 11)
      set(px "7f5e")
    endif()
    if(y GREATER_EQUAL 9 AND y LESS_EQUAL 19 AND x GREATER_EQUAL 2 AND x LESS_EQUAL 13)
      set(px "4a29")
    endif()
    if(y GREATER_EQUAL 19 AND y LESS_EQUAL 22 AND ((x GREATER_EQUAL 3 AND x LESS_EQUAL 6) OR (x GREATER_EQUAL 9 AND x LESS_EQUAL 12)))
      set(px "2925")
    endif()
    if(y GREATER_EQUAL 4 AND y LESS_EQUAL 6 AND x EQUAL 9)
      set(px "ffff")
    endif()
    string(APPEND hex "${px}")
  endforeach()
endforeach()

file(WRITE "${OUTPUT_FILE}" "")
# Convert hexadecimal pairs to raw bytes using a generated shell-independent
# helper script consumed by CMake itself.
string(LENGTH "${hex}" hex_len)
math(EXPR last "${hex_len} - 2")
foreach(i RANGE 0 ${last} 2)
  string(SUBSTRING "${hex}" ${i} 2 byte_hex)
  math(EXPR byte_dec "0x${byte_hex}")
  string(ASCII ${byte_dec} byte_char)
  file(APPEND "${OUTPUT_FILE}" "${byte_char}")
endforeach()
