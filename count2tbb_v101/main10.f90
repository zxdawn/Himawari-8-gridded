program main
! count to albedo v1.00
implicit none
character*29::arg
character*8::filelist
integer :: status, system
real*4,dimension(5000)::tbb
integer*2,dimension(5000)::cnt
integer*2:: i, j, k, io,NoF,N
integer*2,parameter::pix=12000
integer*2,dimension(pix,pix)::data_all
real,dimension(pix,pix)::data_tbb

call getarg( 1, arg ) 
call getarg( 2, filelist)

! Open and Read data
Open(21,file=arg,access='direct',status='old',iostat=io, recl=12000*12000*2)
if(status==0)then
read(21,rec=1)((data_all(i,j),i=1,pix),j=1,pix);close (21)
end if

! Read Tbb table file
NoF=5000
Open ( Unit=20, FILE=filelist,&
   STATUS='OLD',ACCESS='SEQUENTIAL',FORM='FORMATTED')
do N=1,NoF
READ (20, *, IOSTAT = io ) cnt(N),tbb(N)
if (io .ne. 0)exit
end do

! convert CTT to TBB
do i=1,pix
   do j=1,pix
      data_tbb(i,j)=real(tbb(data_all(i,j)+1))
   end do
end do


Open ( Unit=10, File="grid10.dat", access='DIRECT',recl=12000*12000*4)
   Write ( 10,rec=1 )((data_tbb(i,j),i=1,12000),j=1,12000)
close(10)
end program
