import os
import glob
import numpy as np
import csv
#cube=[]
#path_analysis='/data/esanchez/RRL_in_Ionized_Jets_from_Rosero2016_Emmanuel_Sanchez/ANALYSIS'
#out_path='/data/esanchez/RRL_in_Ionized_Jets_from_Rosero2016_Emmanuel_Sanchez/ANALYSIS/Output/K_band'
#out_path='/data/esanchez/RRL_in_Ionized_Jets_from_Rosero2016_Emmanuel_Sanchez/ANALYSIS/Output/C_band'

#new_path=out_path+'/g53.11_mm2K_band/'

def chans_rm_continuum(cube_input):
    global imstat,default
    new_path=cube_input[-1]
    del(cube_input[-1])
    #Stats for each cube
    channels_use=[]
    chans=0
    last=''
    for cube in cube_input:
        array_channel=[]
        print new_path+cube
        stats=imstat(imagename=new_path+cube,  box='50,50,300,300', axes=[0,1])
        a =np.array(stats['rms'])
        b =np.array(stats['flux'])
        c=np.array(stats['mean'])
        rms_mean=a.mean()
        rms_std=a.std()
        flux_mean=b.mean()
        flux_std= 3 * a.mean()
        lower_lim=flux_mean-flux_std
        upper_lim=flux_mean+flux_std
        print cube
        print("RMS Cube:{0:3.3e} ".format(6*a.mean()))
        print("RMS Cube:{0:3.3e} ".format(b.std()))
        print "Mean {0:2.3e} Std {1:2.3e} Lower limit {2:2.3e} Upper Limit {3:2.3e} rms {4:2.3e}".format(flux_mean,flux_std,lower_lim,upper_lim,rms_mean)
        channel_conti=''
        num=len(stats['rms']-5)# Number of channels
        channel_join = ''
        for i in range(num):
            chan_stats=imstat(imagename=new_path+cube,  box='50,50,300,300',axes=[0,1] ,chans=str(i))
            if len(chan_stats['rms'])==0:
                pass
                chans=i+1
                print("Empty {}".format(i))
            else:
                #print "Flux {0:3.3e}".format(chan_stats['flux'][0])
                #print "Lower Lim {0:2.3e} , Upper Lim {1:2.3e} RMS {2:2.3e}".format(lower_lim,upper_lim,chan_stats['rms'][0])
                #print("RMS {0:3.3e} Channel {1:1d}".format(chan_stats['rms'][0],i))
                if chan_stats['flux'][0]>lower_lim and chan_stats['flux'][0]<upper_lim:
                    pass
                else:
                    channs_end=i-1
                    if chans<channs_end:
                        channel_conti =str(chans)+'~'+str(channs_end)
                        print channel_conti
                        #print str(i)+" Out limits" 
                        chans=i+1
                        array_channel.append(channel_conti)
                        channel_join=','.join(array_channel)
                        last=str(chans)+'~'+str(num-1)
        channels_use.append(channel_join)       
        print(last)
    #channels_use.append(channel_join)
    #print channels_use
    return channels_use
    #print ("Lower Limit % {0:2f} Upper limit % {1:2f}".format(chan_stats['flux'][0]/lower_lim , chan_stats['flux'][0]/upper_lim))
    #print  "Channel {0:1d} RMS {1:3.3e} Flux {2:3.3e} ".format(i, chan_stats['rms'][0], chan_stats['flux'][0])



def stack(cube_input):
    new_path=cube_input[-1]
    channels=chans_rm_continuum(cube_input)
    del(cube_input[-1])
    global default
    global imagename
    global linefile
    global contfile
    global chans
    global output
    global template
    global asvelocity
    global overwrite
    global mode
    global expr
    global outfile
    global fitorder
    global axes
    ## Remove continuum: this is better if done in the UV plane before tclean
    cube =[]
    for i in range(len(cube_input)):
        spw_to=cube_input[i]
        if not os.path.exists(new_path+spw_to+'.NC'):
            default(imcontsub)
            imagename = new_path+cube_input[i]
            linefile = new_path +cube_input[i]+'.NC'
            contfile = new_path+cube_input[i]+'.C'            
            chans = channels[i] #this is cube dependent
            #fitorder=1
            inp(imcontsub)
            imcontsub()
            cube.append(linefile)
        else:
            linefile = new_path+cube_input[i]+'.NC' 
            cube.append(linefile) 

    #regrid spectrum, to be able to average them.
    cube_to_stack = [cube[0]]
    for i in range(len(cube)-1):
        default(imregrid)
        imagename = cube[i+1]
        template = cube[0]
        output = imagename +'.imregrid'
        #axes=3
        asvelocity = True
        overwrite = True
        inp(imregrid)
        imregrid()
        cube_to_stack.append(output)
    # Get RMS of the cubes
    imstat_cube = []
    for i in range(len(cube_to_stack)):
        imstat_cube.append(imstat(cube_to_stack[i], box='50,50,300,300'))
        a =np.array(imstat_cube[i]['rms'])
        #print('RMS of '+cube_to_stack[i]+' is %1.2e Jy/b' % a.mean())
        
    ## Define weights for stacking:
    weight_total = sum(1.0/item['rms']**2 for item in imstat_cube)
    print('Weight normalization factor: ',weight_total)
    weights= []
    for i in range(len(cube)):
        weights.append(1.0/imstat_cube[i]['rms'][0]**2)
    weights = weights/weight_total
    print('Weights: ',weights)
    
    ## Stack Cubes
    stacked_image = new_path+'stacked_cube.image'
    #os.system('rm -r -f '+stacked_image)
    default(immath)
    imagename = cube_to_stack
    mode = 'evalexpr'
    outfile = stacked_image
    expr = '(IM0*'+str(weights[0])
    for i in range(len(weights)-1):
        expr = expr + ' + IM'+str(i+1)+'*'+str(weights[i+1])
    expr = expr + ')'

    inp(immath)
    immath()
    imstat_cube.append(imstat(new_path+'stacked_cube.image', box='50,50,300,300'))
    cube_to_stack.append("stacked_cube.image")
    for i in range(len(imstat_cube)):
        a =np.array(imstat_cube[i]['rms'])
        print('RMS of  '+cube_to_stack[i]+' is %1.2e Jy/b' % a.mean())


def export_image(img_name):
    img=''
    path_conti='/data/esanchez/RRL_in_Ionized_Jets_from_Rosero2016_Emmanuel_Sanchez/Rosero_2016_all_data/TAR/Survey_work_images/*'
    select='/data/esanchez/RRL_in_Ionized_Jets_from_Rosero2016_Emmanuel_Sanchez/Rosero_2016_all_data/TAR/Survey_work_images/IRAS20126_4104/C_band/I20126_9000px_wide_res0.05.pbcor/*'
    while True:
        folder=glob.glob(path_conti)
        for i in folder:
            print i
        select= raw_input('\nSelect Folder: ')
        if '.image' in select:
            img=select
            break
        else:
            path_conti=select+'/*'

    if img=='':
        pass
    else:
        image='stacked_cube2.image' #'spw5-Halpha-H(63)alpha.image'
        imview(raster={'file':new_path+image,'colorwedge':True} , contour={'file': img, 'levels': [-2,3,4.5,6,7.5,10.5,13] , 'unit':5e-6})
    
    #os.chdir('/data/esanchez/RRL_in_Ionized_Jets_from_Rosero2016_Emmanuel_Sanchez/ANALYSIS')
 


def sub_images():
    os.chdir(new_path)
    files = glob.glob("*.image")
    for f in files:
        if "image." not in f:
            print f
            stats=imstat(imagename=new_path+f,  box='50,50,300,300' ,axes=[0,1])
            a =np.array(stats['rms'])
            num_chans=len(a)
            #print num_chans
            imsubimage(imagename=new_path+f,outfile=new_path+f+'.sub2',chans='1~'+str(num_chans-1),overwrite=True )
            #region='centerbox[[307.8deg , 40.0545deg],[1000pix,1000pix]]'chans='1~'+str(num_chans-1)
    os.chdir(path_analysis)

def view_img(image_name):
    global raster
    global contour
    level=[]
    with open(path_analysis+'/'+'Rosero_Export_Images_K.csv') as image_file:
        Reader=csv.reader(image_file,delimiter=',')
        next(Reader)#Skip the header
        for row in Reader:
            if row[1]==image_name:
                cont=row[2]
                levels2=row[3].split(",")
                for i in levels2:
                    if '[' in i:
                        
                        level.append(float(i[1:]))
                    if ']' in i:
                        
                        level.append(float(i[:-1]))
                    elif '[' not in i and ']' not in i:
                        level.append(float(i))
                uni=float(row[4])
    img='/data/esanchez/RRL_in_Ionized_Jets_from_Rosero2016_Emmanuel_Sanchez/ANALYSIS/Output/K_band/stacked_images/'+image_name+'_stacked_cube.image'
    imview(raster={'file':img,'colorwedge':True} , contour={'file':cont, 'levels': level , 'unit':uni})


def sub_stacked(image_name):
    global imagename
    global outfile
    global region
    global overwrite
    stack_folder='/data/esanchez/RRL_in_Ionized_Jets_from_Rosero2016_Emmanuel_Sanchez/ANALYSIS/Output/K_band/stacked_images/'
    os.chdir(stack_folder)
    default(imsubimage)
    imagename=image_name+'_stacked_cube.image'
    outfile=imagename+'.sub2'
    region='regions/'+imagename+'.reg2'
    overwrite=True 
    inp(imsubimage)
    go(imsubimage)
    os.chdir(path_analysis)


#ima_var='IRAS20126_4104K_band'
#sub_stacked(ima_var)
#view_img(ima_var)
    
