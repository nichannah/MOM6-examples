cmake_minimum_required(VERSION 2.8 FATAL_ERROR)
project(MOM6)
enable_language(Fortran)
enable_language(C)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/../tools/cmake/Modules/")

find_package(MPI REQUIRED)
set (NETCDF_F90 "YES")
find_package (NetCDF REQUIRED)

add_definitions(-Duse_netCDF)
include_directories(${MPI_F90_INCLUDE_PATH} /usr/include MOM6/config_src/dynamic
                    MOM6/src/framework ${CMAKE_BINARY_DIR}/FMS SIS2 FMS/include)

# Make sure that the default is a RELEASE
if (NOT CMAKE_BUILD_TYPE)
  set (CMAKE_BUILD_TYPE RELEASE CACHE STRING
      "Choose the type of build, options are: Repro Debug Release."
       FORCE)
endif (NOT CMAKE_BUILD_TYPE)

# Set up compiler flags
get_filename_component(Fortran_COMPILER_NAME  ${CMAKE_Fortran_COMPILER} NAME)
if (Fortran_COMPILER_NAME MATCHES "gfortran")
  set (GFORTAN_FLAGS "-fcray-pointer -fdefault-real-8 -fdefault-double-8 -Waliasing -ffree-line-length-none -fno-range-check")
  set (CMAKE_Fortran_FLAGS_RELEASE "${GFORTAN_FLAGS} -O2 -fno-expensive-optimizations")
  set (CMAKE_Fortran_FLAGS_DEBUG "${GFORTAN_FLAGS} -O0 -g -W -fbounds-check -fbacktrace -fcheck-array-temporaries")
endif (Fortran_COMPILER_NAME MATCHES "gfortran")

file(GLOB_RECURSE MOM_SRC FOLLOW_SYMLINKS MOM6/src/*.F90  MOM6/src/*.c)
file(GLOB SOLO_DRIVER_SRC MOM6/config_src/solo_driver/*.F90)
file(GLOB SIS2_SRC SIS2/*.F90)
file(GLOB_RECURSE ATMOS_NULL_SRC atmos_null/*.F90)
file(GLOB LAND_NULL_SRC land_null/*.F90)
file(GLOB COUPLER_SRC coupler/*.F90 FMS/coupler/*.F90 MOM6/config_src/coupled_driver/*.F90)
file(GLOB ICE_PARAM_SRC ice_param/*.F90)

option(ice_ocean_SIS2 "Build MOM6 ocean and SIS2 ice")
if (ice_ocean_SIS2)
  add_executable(MOM6 ${MOM_SRC} ${SIS2_SRC} ${ATMOS_NULL_SRC} ${LAND_NULL_SRC} ${COUPLER_SRC} ${ICE_PARAM_SRC})
else (ice_ocean_SIS2)
  add_executable(MOM6 ${MOM_SRC} ${SOLO_DRIVER_SRC})
endif (ice_ocean_SIS2)

add_subdirectory(FMS)
target_link_libraries(MOM6 fms ${NETCDF_F90_LIBRARIES})
