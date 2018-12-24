#!/bin/bash
# Modify LUT v1.00

HD=`pwd`
tablepath=${HD}/"LUT_H08"

cd ${tablepath}

for file in `ls -1 *.txt `;do
   echo $file
if [ $file = "HS01.txt" ];then
   ext="vis.01"
elif [ $file = "HS02.txt" ];then
   ext="vis.02"
elif [ $file = "HS03.txt" ];then
   ext="ext.01"
elif [ $file = "HS04.txt" ];then
   ext="vis.03"
elif [ $file = "HS05.txt" ];then
   ext="sir.01"
elif [ $file = "HS06.txt" ];then
   ext="sir.02"
elif [ $file = "HS07.txt" ];then
   ext="tir.05"
elif [ $file = "HS08.txt" ];then
   ext="tir.06"
elif [ $file = "HS09.txt" ];then
   ext="tir.07"
elif [ $file = "HS10.txt" ];then
   ext="tir.08"
elif [ $file = "HS11.txt" ];then
   ext="tir.09"
elif [ $file = "HS12.txt" ];then
   ext="tir.10"
elif [ $file = "HS13.txt" ];then
   ext="tir.01"
elif [ $file = "HS14.txt" ];then
   ext="tir.02"
elif [ $file = "HS15.txt" ];then
   ext="tir.03"
elif [ $file = "HS16.txt" ];then
   ext="tir.04"
fi
   cat $file  |sed -e 's/=/ /g' |gawk '{printf "%d %f \n",$8,$9}' > ${HD}/${ext}
done
