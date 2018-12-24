
*******************************************************************************

CEReS Chiba University
Himawari-8/9 : Gridded Data Sample Code Information [10 May 2016]

*******************************************************************************
This code is ready for reading "HIMAWARI 8" gridded data full-disk (FD) observation mode.

# 1.Files   ##

- count2tbb.sh
 main shell script. 

- main05.f90, main10.f90, main20.f90
Fortran script of converting count to tbb (albedo).
main05.f90 is for ext.01 band (0.5km Resolution)
main10.f90 is for vis.01-03 band (1km Resolution)
main20.f90 is for sir01-02/tir.01-10 band (2km Resolution)

- count2tbb05.c, count2tbb10.c, count2tbb20.c
C source code of converting count to tbb (albedo).
The two digits number of code name is same rule as fortran code.

- grads05.ctl, grads10.ctl, grads20.ctl
GrADS control file. (This file is ready for GrADS users)
grads05.f90 is for ext.01 band (0.5km Resolution)
grads10.f90 is for vis.01-03 band (1km Resolution)
grads20.f90 is for sir01-02/tir.01-10 band (2km Resolution)

- ext.01, vis.[01-03], sir[01-02]/tir.[01-10]
Count to tbb (albedo) look up table of individual band data. 

- mktable.sh (supplemental file)
Code of converting look up tabe form. Original table is in ./LUT_H08/ directory.

# 2.Preparations  ##
For running this scripts, following tools are required.

For Fortran users: gfortran, or Intel fortran compiler
For C users: gcc

Viewing the data as a image file.
GMT plot tool (https://www.soest.hawaii.edu/gmt/)
GrADS (http://cola.gmu.edu/grads/downloads.php)


# 3.Usage  ##
Edit "count2tbb.sh" file
Confirm Himawari8 Gridded data path.
example:
(ftp://hmwr829gr.cr.chiba-u.ac.jp/gridded/FD/V20151105)

Set appropriate compiler (gfortran, ifort or gcc).

Set appropriate date (Year Month Day Hour Min).

***Select appropriate band (VIS TIR SIR EXT) and the number.
Released gridded data has different band naming rule with JMA official Himawari 8/9 bands names.***
[IMPORTANT] If user try to download ALL BANDS DATA, users storage would be required at least 3 TB! (even though compressed files!). 
# -------------------------------------------------------
# Quick reference list (Released gridded data and Himawari8 band)
# [EXT] 01:Band03 
# [VIS] 01:Band01 02:Band02 03:Band04
# [SIR] 01:Band05 02:Band06
# [TIR] 01:Band13 02:Band14 03:Band15 04:Band16 05:Band07
#       06:Band08 07:Band09 08:Band10 09:Band11 10:Band12
# -------------------------------------------------------


Type below command.
$ sh count2tbb.sh

Output file is PNG format image. 
(Converted tbb data (grid??.dat) will be deleted in initial setting. If users want to use this data, change the setting.)

This script works 1) Compile f90 program 2)Download the Gridded Himawari8 products 3)Extract 4)convert byte order 5)Convert count to tbb(albedo) 6)convert into image (.png)


