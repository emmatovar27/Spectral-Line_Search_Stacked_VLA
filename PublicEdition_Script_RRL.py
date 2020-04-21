import numpy as np
import glob
import os
import csv
import imp
import sys
sys.path.append(os.getcwd())
import  stacking_module


mylines = []                            
with open ('requirements.txt', 'rt') as myfile: .
    for myline in myfile:               
        mylines.append(myline.rstrip('\n').split('='))         
#print(mylines[0][1],mylines[1][1])                          


band=mylines[0][1]#'K_band/'
path=mylines[1][1]+band #'/data/esanchez/RRL_in_Ionized_Jets_from_Rosero2016_Emmanuel_Sanchez/Rosero_2016_all_data/TAR/'+band
path_analysis=os.getcwd()+'/'
out_path=path_analysis+'/Output/'+band
species_path=path_analysis+'/Species'
sources= []


try:
    os.mkdir(out_path)
except OSError:
    print ("\nCreation of the directory %s failed is already created" %out_path )
else:  
    print ("\nSuccessfully created the directory %s " %out_path)  

try:
    os.mkdir(species_path)
    os.system("mv Halpha.tsv "+species_path)
except OSError:
    print ("\nCreation of the directory %s failed is already created" %species_path )
else:  
    print ("\nSuccessfully created the directory %s " % species_path)

folders=os.listdir(path)
folders=sorted(folders)
print "\nSelect the source or sources: \n"
print folders

while True:
    input_ms=raw_input("\nSelect the source: ")
    if input_ms=="":
        break
    sources.append(input_ms)
print("\n Total # of sources is {}".format(len(sources)))
print(sources)

#Generate listobs for the data using CASA

def list():
    default(listobs)
    global vis ,verbose,overwrite,listfile
    vis=path+mySDM
    verbose=False
    listfile=new_path+'log.txt'
    overwrite=True
    inp(listobs)
    go(listobs)


#Creating the SPW's array
def lines():
    with open(new_path+"log.txt",'r') as log_file:
        line=log_file.readline()
        cnt=1
        while line:
            #print("Line {}: {}".format(cnt, line.strip()))
            if 'SpwID' in line: 
                spw_line=cnt
            if 'Antennas:' in line:
                anten=cnt
            if 'Fields' in line:
                field=cnt+1
            if 'Spectral Windows' in line:
                spw=cnt
                print spw
            line = log_file.readline()
            cnt += 1
        foot2=cnt-spw
        footer=cnt-anten        
        return spw_line,footer,field,foot2

def ploting(fields):
    #Create the plotms and move to the Output folder
    global vis
    global xaxis
    global yaxis
    global field
    global spw
    global avgtime
    global avgbaseline
    global plotfile
    global expformat
    global overwrite
    global showgui
    for i in range(len(temp)):
        default(plotms)
        vis=path+mySDM
        xaxis = 'freq'       
        yaxis ='amp'       
        field =fields
        spw =str(i)
        avgtime ='1.0e10'        #  Average over time (blank = False, otherwise value in
        avgbaseline = True        #  Average over all baselines (mutually exclusive with
        plotfile=new_path+'spw'+ str(i) +'.txt'
        expformat='txt'
        overwrite=True
        showgui=False
        inp(plotms)
        go(plotms)
        #os.system("mv -u " + plotfile +' '+ new_path)


def select_file():
    os.chdir(new_path)
    files = glob.glob("*.txt")
    os.chdir(path_analysis+'Species/')
    species=glob.glob("*")
    if len(species)==0:
        return
        print("You need a file from Splatalogue DataBase")
    for i in species:
        print i
    os.chdir(path_analysis)
    Select=raw_input("\nWrite the name of the Species file to review: ") 
    return Select

def create_freq(sel_mole):
    spw_found=[]
    os.chdir(new_path)
    files = glob.glob("*.txt")
    os.chdir(path_analysis)
    Select=sel_mole
    for spw in files:  # Extract the frequencies
         if os.stat(new_path+'/'+spw).st_size > 100:
             i=np.genfromtxt(new_path+'/'+spw,comments='#',usecols=(0))
             min=np.amin(i)
             max=np.amax(i)
             with open(path_analysis+'Species/'+Select) as Species_file:
                 Reader=csv.reader(Species_file,delimiter='\t')
                 next(Reader)#Skip the Blank line
                 next(Reader)#Skip the Header
                 for row in Reader:
                     rest_freq= float(row[2].split(',')[0])
                     specie=row[0]
                     quatum_trans=row[3]
                     energy=float(row[7])
                     if min <= rest_freq <= max and energy<500.0:
                         print("SPW {} Quatum {} Rest_freq: {} GHz Energy {} K".format(spw,quatum_trans,rest_freq,energy))
                         spw_found.append([spw,min,max,1,specie,quatum_trans,rest_freq])
                         spw_n=spw[3:-4]
                         print("&{0:s}&\t&{1:s}\t &{2:2.6f}&\t {3:3.3f}".format(specie,spw_n,rest_freq,energy))
         else:
             pass
    
    os.chdir(path_analysis)
    return spw_found

def create_img(spws,fields,mySDM):
    #Global Variables
    images_array=[]
    global vis
    global imagename
    global datacolumn
    global field
    global spw
    global specmode
    #global width 
    global restfreq
    #global start 
    global outframe 
    global nchan 
    global threshold  
    global imsize
    global cell
    global niter  
    global deconvolver
    global weighting 
    global robust
    global pbcor  
    global pblimit 
    global restoringbeam 
    global chanchunks  
    global gridder  
    global interactive
    global phasecenter
    for i in range(len(spws)):
        spw_to_do= str(spws[i][0])[:-4] +'-' +spws[i][4]+'-'+spws[i][5]
        spw_to_do=spw_to_do.replace('&','')
        spw_to_do=spw_to_do.replace(';','')
        spw_to_do=spw_to_do.replace('=','')
        spw_to_do=spw_to_do.replace(',','_')
        spw_to_do=spw_to_do.replace('/','_')
        spw_number=str(spws[i][0])[3:-4]
        spw_rest_freq=str( spws[i][6])+ ' GHz' 
        images_array.append(spw_to_do + '.image') # Create the array with the SPW to stacking
        default(tclean)
        vis=path+mySDM
        imagename=new_path+spw_to_do
        datacolumn='corrected'
        if band=="C_band/":
            spw=spw_number #+':5~50'
        else:
            spw=spw_number#+ ':5~60'
        field=fields
        specmode='cube'  
        #width='30km/s' 
        restfreq = spw_rest_freq
        #start='550km/s' 
        #outframe='LSRK' 
        threshold='0.5mJy' # 0.4 '0.05mJy'  
        imsize=[1000] 
        cell=['0.035arcsec']  
        niter= 10000 
        deconvolver='hogbom'  
        weighting= 'briggs' 
        robust=0.5 
        pbcor=True  
        pblimit=0.2  
        restoringbeam='common'         
        interactive=False
        #phasecenter ='J2000 19:28:55.58 17.52.03.11'
        #'J2000 19:29:33.52 18.00.54.20'
        #'J2000 18h21m09s -14d31m48s'
        #'J2000 19h29m33s +18d00m54s'
        #'J2000 19h29m33s +18d00m54s'
        # 19282 'J2000 19h30m23s +18d20m26.0s'
        go_img= 'N'#raw_input("Create image Y/N: ")
        if not os.path.exists(new_path+spw_to_do+'.residual'): #or go_img.upper()=='Y':
            print("Did not Found -> Start Image")
            inp(tclean)
            go(tclean)
            max_min(imagename+'.image')
        else:
            max_min(imagename+'.image')
            print "Exist"

    return images_array
   
def max_min(image):
    global imagename
    global moments
    global outfile
    if not os.path.exists(image+".moments.maximum"):
        default(immoments)
        imagename=image
        moments=[8,10]
        outfile=image+'.moments'
        inp(immoments)
        go(immoments)
        print "Min and Max done"
    else:
        print("Min and Max done")
    



    
##########################################

# Execute_Script
def main():
    for i in sources:
        mySDM = i
        mySDM_Folder=str(mySDM[0:-3])+ band 

        #Create Folder for the plotms Outputs
        try:  
            new_path=path_analysis+'Output/'+band+mySDM_Folder
            os.mkdir(new_path)
        except OSError:  
            print ("Creation of the directory %s failed is already created" % new_path)
        else:  
            print ("Successfully created the directory %s " % new_path)

        #Creation of the listobs
        if not os.path.exists(new_path+'log.txt'):
            list()
    
        header,foot,f_header,f_foot=lines()
        
        temp=np.genfromtxt(new_path+"log.txt",skip_header=header,skip_footer=foot,usecols=(0))
        fields=np.genfromtxt(new_path+"log.txt",skip_header=f_header,skip_footer=f_foot,usecols=(0))
        fields_n=np.genfromtxt(new_path+"log.txt",skip_header=f_header,skip_footer=f_foot, dtype=None,usecols=(2))
        f='0'
        try:
            len_field=len(fields)
            print "Source\t | Source Name"
            for j in range(len(fields)):
                print("{}\t | {} ".format(fields[j], fields_n[j]))

            f=str(raw_input("Select the number of the source: "))
        except TypeError:
            print('Only one source in ms')
        print('Spectral Windows in the Source: ')

        print temp

        #plots of freq vs amp in txt files
        plots=glob.glob(new_path+'*.txt*')
        if len(plots)<2:
            ploting(f)

        #Function to find acording to the species

        sel_file= select_file() #'CH3OH.tsv'#'OH.tsv'# 'OH.tsv' 
        array_spws=create_freq(sel_file)
        if array_spws==[]:
            next
        global new_path
        try:  
            new_path=path_analysis+'Output/'+band+mySDM_Folder+sel_file[:-4]+'/'
            os.mkdir(new_path)
        except OSError:
            print ("Creation of the directory %s failed is already created" % new_path)
        else:  
            print ("Successfully created the directory %s " % new_path)
        #Create images of the previous findings 
        images_cube=create_img(array_spws,f,mySDM)
        if sel_file=='HalphaRRL.tsv':
            temp=[]
            temp2=[]
            for cube in images_cube:
                 temp.append(int(cube[cube.find('(')+1:cube.find(')')]))
            temp.sort(reverse=True)
            temp=[str(x) for x in temp]
            for n in temp:
                for name in images_cube:
                    if n in name:
                        temp2.append(name)
            images_cube=temp2
            print images_cube
            images_cube.append(new_path)
            #Stacking Cubes
            execfile("stacking_module.py",globals())
            stack(images_cube)


if __name__ == '__main__':
    main()
