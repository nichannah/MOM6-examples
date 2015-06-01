cmake_minimum_required(VERSION 2.8 FATAL_ERROR)
project(MOM6_model)
enable_language(Fortran)
enable_language(C)

find_package(MPI REQUIRED)

set (NETCDF_F90 "YES")
find_package (NetCDF REQUIRED)

add_definitions(-Duse_netCDF)
include_directories(${MPI_F90_INCLUDE_PATH} /usr/include MOM6/config_src/dynamic MOM6/src/framework ${CMAKE_BINARY_DIR}/FMS ${CMAKE_BINARY_DIR}/MOM6)

# make sure that the default is a RELEASE
if (NOT CMAKE_BUILD_TYPE)
  set (CMAKE_BUILD_TYPE RELEASE CACHE STRING
      "Choose the type of build, options are: Repro Debug Release."
       FORCE)
endif (NOT CMAKE_BUILD_TYPE)

get_filename_component(Fortran_COMPILER_NAME  ${CMAKE_Fortran_COMPILER} NAME)
if (Fortran_COMPILER_NAME MATCHES "gfortran")
  set (GFORTAN_FLAGS "-fcray-pointer -fdefault-real-8 -fdefault-double-8 -Waliasing -ffree-line-length-none -fno-range-check")
  set (CMAKE_Fortran_FLAGS_RELEASE "${GFORTAN_FLAGS} -O2 -fno-expensive-optimizations")
  set (CMAKE_Fortran_FLAGS_DEBUG "${GFORTAN_FLAGS} -O0 -g -W -fbounds-check -fbacktrace -fcheck-array-temporaries")
endif (Fortran_COMPILER_NAME MATCHES "gfortran")

add_subdirectory(FMS)
add_subdirectory(MOM6)
add_subdirectory(SIS2)
