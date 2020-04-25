

# Installation and Configuration 

Extract the files in the path. 

Before running the python program we need to define two variables inside the python script. 
Open the **requirements.txt** and edit the band and path variables. Change the values of band and path for strings with the band of your observations and the path where you store your calibrate data.
 

* band = ' '
* path = ' '

Example: 

* band='K_band/'
* path='/data/esanchez/Rosero_2016_all_data/TAR/'

# Splatalogue - Files
[Splatalogue](https://www.cv.nrao.edu/php/splat/index.php)

After the initial variables you must download the files from Splatalogue and saved it in the 'Species' folder. The file must be download in '.tsv' format following the this two parameters. Field Separator: Tab
Range: All Records

# Execution

The next step will be run the main script from casa interface using the command
```
execfile('PublicEdition_Script_RRL.py')
```
## Source Selection

The Script will ask for which sources or source do you want to run through. You have to enter the name of the source.

## Fields Selection

If the source has more than one field you can selected base on the number of the field.  

## Frequency Selection

### If you have multiples files in the **Species** folder:
 
You must selected the file with the frequencies of interested. You must type name of the file.

### Imaging generation

The program will use the default  settings for each source that you selected. The output of the images will be located at /Output/'band'/'Source Name'

