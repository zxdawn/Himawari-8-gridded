# HIMAWARI-8-gridded
## What is it?

Scripts of downloading Gridded-processed data of Himawari 8 geostationary meteorological satellite (H8).

The sample programs (F90 and C) and calibration tables provided by [CEReS](http://www.cr.chiba-u.jp/databases/GEO/H8_9/FD/index.html) are in `count2tbb_v101` directory.

Since downloading multiple files needs many modifications, I write them in python to make this easy to get **TBB files in nc format**.

## Requirements

- [NetCDF Operators (NCO)](http://nco.sourceforge.net/)
- [Climate Data Operators (CDO)](https://code.mpimet.mpg.de/projects/cdo/wiki/Cdo)
- [ftplib](https://docs.python.org/3/library/ftplib.html)
- [xarray](https://github.com/pydata/xarray)
- [tqdm](https://github.com/tqdm/tqdm)

## Usage

Download or clone the repository first

```
git clone git@github.com:zxdawn/Himawari-8-gridded.git
```

Check the help information

```
python count2tbb.py --help
```

```
Usage: count2tbb.py [OPTIONS]

  Himawari-8 gridded format shell script. v1.00 (201605)
      Converted to .py and modified by [Xin Zhang] (20181225)
  Fuctions:
      Download, count2tbb, convert and merge to daily nc files
  Contact:
      xinzhang1215@gmail.com

Options:
  -r, --req_path TEXT   Directory where you put count2tbb_v101.  [default:
                        ./count2tbb_v101]
  -s, --save_path TEXT  Directory where you want to save files.  [default:
                        ./data]
  -sd, --sdate TEXT     Beginning date of downloaded files
                          YYYY-MM-DD-hh:mm
  -ed, --edate TEXT     Ending date of downloaded files
                          YYYY-MM-DD-hh:mm
  -ts, --tstep INTEGER  Time step (min) between files  [default: 720]
  -c, --chn TEXT        Channel name in Capital.
                          EXT, VIS ,SIR or TIR
                        [default: TIR]
  -n, --num TEXT        Band number according to channel
                        -----------------------------------
                        Reference:
                        -----------------------------------
                        [EXT] 01:Band03
                        -----------------------------------
                        [VIS] 01:Band01
                        02:Band02 03:Band04
                        -----------------------------------
                        [SIR] 01:Band05
                        02:Band06
                        -----------------------------------
                        [TIR]
                        01:Band13 02:Band14 03:Band15 04:Band16 05:Band07
                        06:Band08 07:Band09 08:Band10 09:Band11 10:Band12
                        -----------------------------------  [default: 2]
  -d, --debug INTEGER   Debug level  [default: 0]
  --help                Show this message and exit.
```

## Brief example

 Test if it works:

```
python count2tbb.py -sd <starting_date> -ed <ending_date>
```

![example_1](https://github.com/zxdawn/Himawari-8-gridded/raw/master/example/tbb_1.gif)

If there're any errors, please increase the debug level to check it:

```
python count2tbb.py -d 1 -sd <starting_date> -ed <ending_date>
```

![example_2](https://github.com/zxdawn/Himawari-8-gridded/raw/master/example/tbb_2.gif)

If it works, the structure of files is like this:

```
├── data
│   ├── YYYY
│   │   └── MM
│           └── ....
│   │   └── MM
│           └── ....
│   └── YYYY
│       └── MM
│           └── ....
│   │   └── MM
│           └── ....
```

## Support, Issues, Bugs, ...

Please use the github page to report issues/bugs/features: https://github.com/zxdawn/Himawari-8-gridded.