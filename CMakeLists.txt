cmake_minimum_required(VERSION 3.16)
project(geant4_cerenkov_new)

set(CMAKE_CXX_STANDARD 17)

# --- Geant4 Paketini Bul ---
find_package(Geant4 REQUIRED ui_all vis_all)
include(${Geant4_USE_FILE})

# --- Include Dizinleri (çok önemli) ---
include_directories(
    ${PROJECT_SOURCE_DIR}/include
)

# --- Kaynak Dosyalar ---
file(GLOB SOURCES ${PROJECT_SOURCE_DIR}/src/*.cc)

# --- main.cc kök dizindeyse (seninki öyle) ---
add_executable(main ${PROJECT_SOURCE_DIR}/main.cc ${SOURCES})

# --- Kütüphaneler ---
target_link_libraries(main ${Geant4_LIBRARIES})

# --- Makro klasörünü build dizinine kopyala (isteğe bağlı) ---
file(COPY ${PROJECT_SOURCE_DIR}/macros DESTINATION ${CMAKE_BINARY_DIR})
