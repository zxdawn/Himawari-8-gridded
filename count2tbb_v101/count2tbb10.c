#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define N150 150

#define NX 12000
#define NY 12000

int main(int argc, char *argv[]){
  FILE	*fp;
  char outputfilename[N150];
  int	i, j, tmp_cn, cn;
  float	 tmp_tbb, tbb[5000];
  unsigned short *data_all;
  float *dt;

/* alert */
  if(argc!=3){
     fprintf(stderr,"Usage: count2tbb.c inputfilename converttable\n");
     exit(1);
  }

   data_all=(unsigned short*)malloc(2*NX*NY);
   dt=(float*)malloc(4*NX*NY);

/* open data file */
  if((fp=fopen(argv[1],"r"))==NULL){
     fprintf(stderr,"*** inputfile (%s) cannot open ***\n",argv[1]);
     exit(1);
  }
  fread(data_all,sizeof(unsigned short),NX*NY,fp);
  fclose(fp);

/* open TBB table */
  if((fp=fopen(argv[2],"r"))==NULL){
     fprintf(stderr,"*** convert file (%s) cannot open ***\n",argv[2]);
     exit(1);
  }
  for(i=0;i<5000;i++){
   fscanf(fp,"%d  %f",&tmp_cn, &tmp_tbb);
     tbb[i]=tmp_tbb;
  }
  fclose(fp);

/* Convert CNT to TBB */
  for(i=0;i<NY;i++){
  for(j=0;j<NX;j++){
     cn=(int)data_all[NX*i+j];
     dt[NX*i+j]=tbb[cn];
//      printf("%d\t%f\n",cn,tbb[cn]);
  }}

/* Output data */
  sprintf(outputfilename,"grid10.dat",argv[1]);
  fp=fopen(outputfilename,"w");
  fwrite(dt,sizeof(float),NX*NY,fp);
  fclose(fp);

  free(dt);  free(data_all);
  return 0;
}
