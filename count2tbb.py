from __future__ import print_function
import numpy as np
import xarray as xr
import ftplib, click
from tqdm import tqdm
from shutil import move
from subprocess import call
from datetime import date, timedelta, datetime
import os, sys, pathlib, ntpath, glob, subprocess

# -------------------------------------------------------

def check(chn, num):
    error_message = 'Check the reference list! There is a mismatch between chn and num'
    for n in num:
        if (chn == "VIS" and n > 3) | (chn == "SIR" and n > 2) \
                | (chn == "EXT" and n > 1) | (chn == "EXT" and n > 1) \
                | (chn == "TIR" and n > 10):
            print (error_message)
            sys.exit()

def fortran_compile(compiler, req_path):
    # Count to tbb (albedo) program name
    # 2km: main20 1km: main10 0.5km: main05
    src     = req_path+'main20.f90'
    exefile = req_path+'tir.x'
    if compiler == 'gfortran':
        call (['gfortran', src, '-o', exefile])
    else:
        call(['ifort', src, '-assume', 'byterecl', '-o', exefile])

    src     = req_path+'main10.f90'
    exefile = req_path+'vis.x'
    if compiler == 'gfortran':
        call (['gfortran', src, '-o', exefile])
    else:
        call(['ifort', src, '-assume', 'byterecl', '-o', exefile])

    src     = req_path+'main05.f90'
    exefile = req_path+'ext.x'
    if compiler == 'gfortran':
        call (['gfortran', src, '-o', exefile])
    else:
        call(['ifort', src, '-assume', 'byterecl', '-o', exefile])

    fortran_programs = ['tir.x', 'vis.x', 'ext.x']

    if not all([os.path.isfile(f) for f in [req_path + x for x in fortran_programs]]):
        print ("fortran program is not ready")
        sys.exit()

def cdir(save_path, year, month):
    destination = save_path+str(year)+'/'+str(month).zfill(2)
    pathlib.Path(destination).mkdir(parents=True, exist_ok=True)

def cdirs(dir_list, save_path):
    # Create monthly directories: YYYY/MM/
    syear  = dir_list[0].year
    eyear  = dir_list[-1].year
    smonth = dir_list[0].month
    emonth = dir_list[-1].month

    # If just one year, create directories by month;
    # Otherwise, iterate year to create these.
    if syear == eyear:
        for m in np.arange(smonth,emonth+1,1):
            cdir (save_path, syear, m)
    else:
        for y in np.arange(syear,eyear+1,1):
            if y == syear:
                for m in np.arange(smonth,13,1):
                    cdir (save_path, y, m)
            elif y == eyear:
                for m in np.arange(1,emonth+1,1):
                    cdir (save_path, y, m)
            else:
                for m in np.arange(1,13,1):
                    cdir (save_path, y, m)

def files_list(d1, d2, tstep, chn, num):
    # generate time array by time step
    # https://stackoverflow.com/questions/
    #   39298054/generating-15-minute-time-interval-array-in-python
    files   = []
    step    = timedelta(minutes=tstep)
    seconds = (d2- d1).total_seconds()

    for i in range(0, int(seconds), int(step.total_seconds())):
        files.append(d1 + timedelta(seconds=i))

    # get all files from sdate to edate by tstep
    files = [date.strftime('%Y%m/')+chn+date.strftime('/%Y%m%d%H%M.')+chn.lower()+'.'\
                    +str(n).zfill(2)+'.fld.geoss.bz2' for date in files for n in num]

    return files

def downloadFiles(ftp, source, file, destination, debug):
    try:
        ftp.cwd(os.path.dirname(source + file))
    except OSError:
        pass
    except ftplib.error_perm:
        print ('Error: could not change to ' + os.path.dirname(source + file))
        return 0

    filename = ntpath.basename(file)

    try:
        ftp.sendcmd('TYPE I') 
        filesize = ftp.size(filename)
        with open(destination, 'wb') as f:
            # set progress bar
            with tqdm(total=filesize, unit_scale=True, desc=filename, miniters=1, 
                file=sys.stdout, leave=False) as pbar:
                def file_write(data):
                    pbar.update(len(data))
                    f.write(data)
                ftp.retrbinary('RETR ' + filename, file_write)

            if debug > 0:
                print ('    Downloaded')
    except:
        print ('Error: File could not be downloaded ' + filename)
        return 0

    return 1

def convert_tbb(chn, req_path, desdir, para):
    if chn in ['TIR', 'SIR']:
        call ([req_path+'tir.x', desdir+'little.geoss', para])
        move ('grid20.dat', desdir+'grid20.dat')

    elif chn == 'VIS':
        call ([req_path+'vis.x', desdir+'little.geoss', para])
        move ('grid10.dat', desdir+'grid10.dat')

    elif chn == 'EXT':
        call (['dd', 'if='+desdir+'little.geoss', 'of='+desdir+'01.geoss', 'bs=576000000', 'count=1'])
        call ([req_path+'ext.x', desdir+'01.geoss', para])
        move ('grid05.dat', desdir+'grid05_1.dat')
        call (['dd', 'if='+desdir+'little.geoss', 'of='+desdir+'02.geoss', 'bs=576000000', 'skip=1'])
        call ([req_path+'ext.x', desdir+'02.geoss', para])
        move ('grid05.dat', desdir+'grid05_2.dat')

        dats = [desdir+'grid05_1.dat', desdir+'grid05_2.dat']
        with open(desdir+grid05.dat, 'w') as outfile:
            for dat in dats:
                with open(dat) as infile:
                    for line in infile:
                        outfile.write(line)

def rm_tmp(file_pattern):
    # remove tmp files
    for f in glob.glob(file_pattern):
        os.remove(f)

def concatenate(chn, filename, files, tmp_check, desdir, debug):
    # get the date of file: YYYYMMDD
    prefix_file = filename[0:8]

    # concatenate minutely files to a daily file
    #   and aviod concatenating daily file
    if prefix_file != tmp_check:

        if debug > 0:
            print ('Concatenate '+tmp_check+' files')

        minutely_pattern = tmp_check+'????.'+chn.lower()+'.??.nc'
        ds = xr.open_mfdataset(minutely_pattern, combine='nested', concat_dim='time', parallel=True)
        comp = dict(zlib=True, complevel=5)
        encoding = {var: comp for var in ds.data_vars}
        ds.to_netcdf(path=desdir+tmp_check+'.nc', encoding=encoding)

        # avoid deleting concatenated file
        rm_tmp(desdir+minutely_pattern)
        tmp_check = prefix_file

    # concatenate the rest files
    if filename == ntpath.basename(files[-1]):
        # check whether daily file exists
        if not os.path.isfile(desdir+prefix_file+'.nc'):

            if debug > 0:
                print ('Concatenate '+prefix_file+' files')

            ds = xr.open_mfdataset(desdir+prefix_file+'*.nc', combine='nested', concat_dim='time',decode_times=False,parallel=True)
            ds.time.attrs['units'] = 'hours since 2015-01-01 00:00'
            ds.to_netcdf(desdir+prefix_file+'.nc')

        # deleting minutely files
        rm_tmp(desdir+tmp_check+'????.'+chn.lower()+'.??.nc')

# -------------------------------------------------------
@click.command()
@click.option(
    '--req_path',
    '-r',
    default = './count2tbb_v101',
    help='Directory where you put count2tbb_v101.',
    show_default=True
)

@click.option(
    '--save_path',
    '-s',
    default = './data',
    help='Directory where you want to save files.',
    show_default=True
)

@click.option(
    '--sdate',
    '-sd',
    help=
    '''
    Beginning date of downloaded files
      YYYY-MM-DD-hh:mm
    '''
)

@click.option(
    '--edate',
    '-ed',
    help=
    '''
    Ending date of downloaded files
      YYYY-MM-DD-hh:mm
    '''
)

@click.option(
    '--tstep',
    '-ts',
    default = 720,
    help='Time step (min) between files',
    show_default=True
)

@click.option(
    '--chn',
    '-c',
    default = 'TIR',
    help=
    '''
    Channel name in Capital.
      EXT, VIS ,SIR or TIR
    ''',
    show_default=True,
)

@click.option(
    '--num',
    '-n',
    is_flag=False,
    default = ','.join(['2']),
    type=click.STRING,
    help='Band number according to channel'
    '''
    -----------------------------------
    Reference:
    -----------------------------------
    [EXT] 01:Band03
    -----------------------------------
    [VIS] 01:Band01 02:Band02 03:Band04
    -----------------------------------
    [SIR] 01:Band05 02:Band06
    -----------------------------------
    [TIR] 01:Band13 02:Band14 03:Band15 04:Band16 05:Band07
    06:Band08 07:Band09 08:Band10 09:Band11 10:Band12
    -----------------------------------
    ''',
    show_default=True
)

@click.option(
    '--compiler',
    '-c',
    default = 'gfortran',
    help='Compiler: gfortran, ifort',
    show_default=True
)

@click.option(
    '--debug',
    '-d',
    default = 0,
    help='Debug level',
    show_default=True
)

# -------------------------------------------------------

def main(req_path,save_path,sdate,edate,tstep,chn,num,compiler,debug):
    '''
    \b
    Himawari-8 gridded format shell script. v1.00 (201605)
        Converted to .py and modified by [Xin Zhang] (20181225)
    Fuctions:
        Download, count2tbb, convert and merge to daily nc files
    Contact:
        xinzhang1215@gmail.com
    '''

    server    = 'hmwr829gr.cr.chiba-u.ac.jp'  # Himawari Gridded data server
    source    = '/gridded/FD/V20190123/'  # old data path: V20151105
    req_path  = os.path.join(req_path, "")
    save_path = os.path.join(save_path, "")

    # check input channel name
    if chn in ['TIR', 'SIR']:
        ctl  = 'grads20.ctl'
    elif chn == 'VIS':
        ctl  = 'grads10.ctl'
    elif chn == 'EXT':
        ctl  = 'grads05.ctl'

    # get the list of datetime from sdate to edate by day
    d1       = datetime.strptime(sdate, '%Y-%m-%d-%H:%M')
    d2       = datetime.strptime(edate, '%Y-%m-%d-%H:%M')
    delta    = d2 - d1
    dir_list = [d1 + timedelta(i) for i in range(delta.days + 1)]
    # get time array by time step
    num   = [c.strip() for c in num.split(',')]
    num   = list(map(int, num))
    files = files_list(d1, d2, tstep, chn, num)

    # check the input
    check (chn,num)
    # compile fortran code
    fortran_compile(compiler,req_path)
    # Create monthly directories: YYYY/MM/
    cdirs(dir_list, save_path)

    user     = "anonymous"
    password = "anonymous"
    ftp      = ftplib.FTP(server)
    ftp.login(user, password)

    # check data day by day
    tmp_check = ntpath.basename(files[0])[0:8]

    for file in tqdm(files, desc='total progress'):
        # download compressed file
        filename    = ntpath.basename(file)
        destination = os.path.join(save_path+file[0:4]+'/'+file[4:6], filename)
        desdir      = os.path.dirname(destination)+'/'

        if debug > 0:
            print ('Downloading '+ filename +' ...')

        file_exist = downloadFiles(ftp, source, file, destination, debug)
        # skip following steps if file isn't found
        if not file_exist:
            continue

        if debug > 0:
            print ('    Extract file')

        call (['bunzip2', destination])

        if debug > 0:
            print ('    Convert byte order')

        call (['dd', 'if='+destination[:-4], 'of='+desdir+'little.geoss', 'conv=swab'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        if debug > 0:
            print ('    Convert count to tbb(albedo)')
        
        para = req_path+filename.split('.',1)[1].rsplit('.',3)[0]
        convert_tbb(chn, req_path, desdir, para)

        # remove temporary .geoss files
        rm_tmp(desdir+'*.geoss')

        # set path of .ctl and savename
        ctl_file = req_path+ctl
        nc_file  = filename.rsplit('.',3)[0]+'.nc'

        # correct the path of .dat file in .ctl
        with open(ctl_file) as f:
            lines = f.readlines()
            lines[0] = 'dset '+desdir+ctl[:-4].replace('s', '').replace('a', 'i')+'.dat\n'
        with open(ctl_file, "w") as f:
            f.writelines(lines)

        # convert .dat to .nc
        if debug > 0:
            print ('    Convert to '+nc_file)

        command = 'cdo -f nc4c -z zip_6 import_binary '+ctl_file+' '+desdir+nc_file
        call (command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)

        # remove temporary .dat files
        rm_tmp(desdir+'*.dat')

        # set right datetime and lon (-180 ~ 180)
        with xr.open_dataset(desdir+nc_file) as ds:
            # calculate diff between 2015-01-01 and this date
            const_date = '201501010000'
            now_date   = nc_file.split('.',1)[0]
            str_format = '%Y%m%d%H%M'
            diff       = datetime.strptime(now_date, str_format) \
                        - datetime.strptime(const_date, str_format)

            # assign value and attributes
            ds.coords['time']       = [diff.total_seconds()/3600]
            ds.coords['time'].attrs = {'units': 'hours since 2015-01-01'}

            # save file
            ds.to_netcdf(desdir+nc_file+'tmp')

        # rename file
        move(desdir+nc_file+'tmp', desdir+nc_file)

        # concatenate minutely files to a daily file
        concatenate(chn, filename, files, tmp_check, desdir, debug)


if __name__ == '__main__':
    main()
