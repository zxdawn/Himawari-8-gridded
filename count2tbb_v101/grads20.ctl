dset grid20.dat
title HIMAWARI-8
options yrev little_endian
undef -999.0
xdef 6000 linear 85.01  0.02
ydef 6000 linear -59.99 0.02
zdef 1 linear 1 1
tdef 1 linear 01JUN05 1hr
vars 1
tbb 0 99 brightness temperature [K] 
endvars
