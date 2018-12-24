#!/bin/bash
# Himawari-8 gridded format sample script. v1.00 201605
# fortran compiler and GMT plot tool is required.
#(Download, count2tbb  and image converting )

# Himawari Gridded data path
FTP="ftp://hmwr829gr.cr.chiba-u.ac.jp/gridded/FD/V20151105"

# Count to tbb (albedo) program name
# 2km: main20 1km: main10 0.5km: main05
src="main20.f90"
exefile="tir.x"
#ifort ${src} -assume byterecl -o ${exefile}
gfortran ${src} -o ${exefile}

src="main10.f90"
exefile="vis.x"
#ifort ${src} -assume byterecl -o ${exefile}
gfortran ${src} -o ${exefile}

src="main05.f90"
exefile="ext.x"
#ifort ${src} -assume byterecl -o ${exefile}
gfortran ${src} -o ${exefile}

# 
if [ ! -f tir.x ] || [ ! -f vis.x ] || [ ! -f ext.x ];then
   echo "fortran program is not ready"
   exit
fi


# Set DATE
for YYYY in 2016 ; do      # Year (from 2015)
  for MM in 05 ; do        # Month
    for DD in 08 ; do      # Day
      for HH in 02  ; do   # Hour
      for MN in 30  ;do    # 00 10 20 30 40 50 # Minute
# Set band type
      for CHN in TIR ;do  #VIS TIR SIR EXT;do
      for NUM in 1;do  #2 3 4 5 6 7 8 9 10 ;do #band number
# -------------------------------------------------------
# Quick reference list (Released gridded data and Himawari8 band)
# [EXT] 01:Band03 
# [VIS] 01:Band01 02:Band02 03:Band04
# [SIR] 01:Band05 02:Band06
# [TIR] 01:Band13 02:Band14 03:Band15 04:Band16 05:Band07
#       06:Band08 07:Band09 08:Band10 09:Band11 10:Band12
# -------------------------------------------------------

      if [ ${CHN} = "VIS" ] && [ ${NUM} -gt 3 ];then
         break
      elif [ ${CHN} = "SIR" ] && [ ${NUM} -gt 2 ]; then
         break
      elif [ ${CHN} = "EXT" ] && [ ${NUM} -gt 1 ]; then
         break
      fi
      if [ ${NUM} -lt 10 ];then
         NUM=0${NUM}
      fi

      echo "Download file"
      echo "${YYYY}${MM}${DD}${HH}${MN}.${CHN,,}.${NUM}.fld.geoss.bz2"
      wget ${FTP}/${YYYY}${MM}/${CHN}/${YYYY}${MM}${DD}${HH}${MN}.${CHN,,}.${NUM}.fld.geoss.bz2

      if [ ! \( -e ${YYYY}${MM}${DD}${HH}${MN}.${CHN,,}.${NUM}.fld.geoss.bz2 \) ] ; then
         echo "${YYYY}${MM}${DD}${HH}" >> nofiles.txt
      else
         echo "Extract file"
         bunzip2 ${YYYY}${MM}${DD}${HH}${MN}.${CHN,,}.${NUM}.fld.geoss.bz2
         echo "Convert byte order"
         dd if=${YYYY}${MM}${DD}${HH}${MN}.${CHN,,}.${NUM}.fld.geoss of=little.geoss conv=swab
         para=`echo ${YYYY}${MM}${DD}${HH}${MN}.${CHN,,}.${NUM}.fld.geoss | cut -c 14-19`
         echo "Convert count to tbb(albedo)"
         if [ ${CHN} = "TIR" -o ${CHN} = "SIR" ];then
            ./tir.x little.geoss ${para}
            resolution="0.02"
         elif [ ${CHN} = "VIS" ];then
            ./vis.x little.geoss ${para}
            resolution="0.01"
         elif [ ${CHN} = "EXT" ];then
            dd if=little.geoss of=01.geoss bs=576000000 count=1
            ./ext.x 01.geoss ${para} && mv grid05.dat grid05_1.dat
            dd if=little.geoss of=02.geoss bs=576000000 skip=1
            ./ext.x 02.geoss ${para} && mv grid05.dat grid05_2.dat
            cat grid05_1.dat grid05_2.dat > grid05.dat 
            resolution="0.005"
         fi
         rm *.geoss

# mv grid??.dat ${YYYY}${MM}${DD}${HH}${MN}.${CHN,,}.${NUM}.fld.dat
# For GrADS user, comment out below GMT part and just open "grid??.dat" data.


# create image by GMT ------------------------------------------
echo "converting image(GMT) ..."
gmtset BASEMAP_TYPE PLAIN
if [ ${CHN} = "VIS" ] || [ ${CHN} = "EXT" ] || [ ${CHN} = "SIR" ];then
   makecpt -Cgray -T0/110/10 -Z > count.cpt
   unit="(%)"
elif [ ${CHN} = "TIR" ];then
   makecpt -Cgray -T200/300/10 -I -Z > count.cpt
   unit="(K)"
fi
imgfn=${YYYY}${MM}${DD}${HH}${MN}.${CHN,,}.${NUM}.fld
xyz2grd grid??.dat -Glittle_endian.gmt -I${resolution}/${resolution} -R85/205/-60/60 -F -N-999. -ZTLf
grdimage little_endian.gmt -JQ140/15 -Ccount.cpt -K -P -R85/205/-60/60 > ${imgfn}.eps
pscoast -Ba20g20/a15g15eWSn -J -R -Dh -K -N1/2t7.5_7.5:0/0/255/0 -W1/0/255/0 -O >> ${imgfn}.eps
echo "140 62 18 0 0 CB Himawari-8 (${para}) ${YYYY}${MM}${DD} ${HH}${MN}UTC" | pstext -R -J -G0/0/0 -O -K -N >> ${imgfn}.eps
psscale -D7.5/-1/12/0.5h -Ccount.cpt -B10/:"${unit}": -O >> ${imgfn}.eps
ps2raster ${imgfn}.eps  -P -A -E300 -Qt -Qg -Tg #&& eog ${imgfn}.png
# --------------------------------------------------------------


# delete downloaded file
rm  *.gmt *.dat *.eps   #(Modify setting if user leaving .dat data)

         fi #file exist
      done
      done
      done
      done
    done
  done
done
