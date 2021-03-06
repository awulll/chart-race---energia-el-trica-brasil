# By João Paulo Jankowski Saboia - July 2021
# Contact: awulll@gmail.com

# Imports
import re
import os
import xlrd
import numpy as np
import pandas as pd
from copy import copy
from datetime import *
from operator import itemgetter
from dateutil.relativedelta import *

# Matplotlib and image libs
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.animation as animation
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox
from PIL import Image

# Parameters - here you can change
output_file         = 'consumo.mp4'                                    # output file
first_image         = 'figuras/energia.jpg'                            # first image
file_input          = 'consumo.xlsx'                                   # main input file
num_interp          = 2                                                # number of interpolation - race frames
num_of_elements     = 5                                                # number of elements showed in each race
fps                 = 10                                               # frames per second
wfig                = 36                                               # figure width  (1 = 100 pixels)
hfig                = 20                                               # figure height (1 = 100 pixels)
cols                = 4                                                # number of columns - elements presentation table
lins                = 4                                                # number of rows - elements presentation table
mval                = lins*cols                                        # table max elements
font_name           = "Arial"                                          # font     
colinfo             = '#000000'                                        # color for info text
logo_image          = 'figuras/Original on Transparent_900.png'        # logo image
title               = 'Consumo de energia elétrica no Brasil\nde 1979 a 2021' # title for the beginning
final_text          = 'Obrigado por assistir!\nSe gostou, por favor se inscreva!\nSe não, não.'                                           # title for ending   
meses               = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']  # months in portuguese

# Parameters - just change if you know what you're doing
fig_left            = 0.01                                             # subplot adjust (left) 
fig_right           = 0.99                                             # subplot adjust (right)
fig_top             = 0.95                                             # subplot adjust (top)
fig_bottom          = 0.48                                             # subplot adjust (bottom)   
fig_wspace          = 0.2                                              # subplot adjust (width space)
fig_hspace          = 0.2                                              # subplot adjust (height space)
bar_height          = 0.8                                              # bar height  
bar_linewidth       = 3                                                # bar linewidth
num_ele_cover       = 5.2                                              # number of cover elements (just to calculate cover figures - pilots)
base                = 1/(2**num_interp)                                # auxiliar to fix bar positions 
height_images_cover = hfig*100*(1-(fig_hspace**2+fig_wspace**2)**0.5)*(fig_top-fig_bottom)*bar_height/num_ele_cover    # height cover images - presentation elements
width_images_cover  = height_images_cover                                                                              # width cover images - presentation elements 
height_images       = hfig*100*(1-(fig_hspace**2+fig_wspace**2)**0.5)*(fig_top-fig_bottom)*bar_height/(num_of_elements+1) # height bar images
ratio_width_height  = 1                                                # image size ratio
width_images        = height_images*ratio_width_height                 # width bar image
total               = 0.875*wfig*100*(1-(fig_hspace**2+fig_wspace**2)**0.5) # aux for text and figure position insert
width2              = int(total*(1-fig_right)*0.005)                        # aux for text and figure position insert
dims_details        = [0.50, 0.53, 0.48, 0.10]                         # axis dimension - details about a certain date
min_value           = 0                                                # min value to plot bars
cover               = {}                                               # dictionary for cover frames
final               = {}                                               # dictionary for end text frames
all_frms            = []                                               # index list for all frames 
start               = 1                                                # auxiliar for chart race 
positions_race      = []                                               # auxiliar for chart race
previous            = None                                             # auxiliar for chart race 
first               = True                                             # auxiliar for chart race 
dates_consumption   = []                                               # list time series - datetime
consumption         = {}                                               # dictionary for consumption


# Get details   
def get_details():    
    sht = xlrd.open_workbook(file_input).sheet_by_name('destaques')    
    out = {}
    for n in range(sht.nrows):
        if n > 1 and sht.row(n)[0].value != '':
            dat = datetime(int(float(sht.row(n)[0].value)),int(float(sht.row(n)[1].value)),1)
            out[dat] = str(sht.row(n)[3].value)
    return out     
    
# Get names    
def get_names():    
    sht = xlrd.open_workbook(file_input).sheet_by_name('nomes')    
    out = []
    for n in range(sht.nrows):
        if n > 0: out.append(str(sht.row(n)[0].value))
    return out       

# Data for cover frames - video title
def create_cover_frames(title,fps):
    
    global cover
    out  = []
    a    = 0
    for i in range(3):
        if i == 1: text = title
        else:      text = '' 
        if i == 1:  
            for j in range(2*fps):      cover[a] = text ; out.append(['cover',a]) ; a = a + 1
        else: 
            for j in range(int(fps/2)): cover[a] = text ; out.append(['cover',a]) ; a = a + 1
    return out
   
# Data for final text frames - end of the video
def create_final_frames(final_text,fps):
    
    global final
    out  = []
    a    = 0
    for i in range(3):
        if i == 1: text = final_text
        else:      text = '' 
        if i >= 1:  
            for j in range(3*fps):      final[a] = text ; out.append(['final',a]) ; a = a + 1
        else: 
            for j in range(int(fps/2)): final[a] = text ; out.append(['final',a]) ; a = a + 1
    return out   


# Draw frames - cover (video title)        
def draw_cover(z):
    
    ax1.clear() ; ax2.clear() ; ax2.set_facecolor([1,1,1,0]) ; ax2.set_position([200,200,1,1]) ; ax3.clear() ; ax3.set_facecolor([1,1,1,0]) ; ax3.set_position([200,200,1,1])    
    ax1.set_xlim([0,cols+1])
    ax1.set_ylim([0,lins+1])    
    ax1.text((cols+1)/2, (lins+1)/2, str(cover[z]), size = 120, ha = 'center', va = 'center', fontdict = {'fontname': font_name})   
    ax1.get_xaxis().set_visible(False)
    ax1.get_yaxis().set_visible(False)
    ax1.set_facecolor([1,1,1,.5])
    ax1.set_xlim([0,cols+1])
    ax1.set_ylim([0,lins+1])  


# Draw frames - final text (end of the video)        
def draw_final(z):
    
    ax1.clear() ; ax2.clear() ; ax2.set_facecolor([1,1,1,0]) ; ax2.set_position([200,200,1,1])  ; ax3.clear() ; ax3.set_facecolor([1,1,1,0]) ; ax3.set_position([200,200,1,1])      
    ax1.set_xlim([0,cols+1])
    ax1.set_ylim([0,lins+1])
    ax1.text((cols+1)/2, 2.3*(lins+1)/3, str(final[z]), size = 78, ha = 'center', va = 'center', fontdict = {'fontname': font_name})       
    imagebox = OffsetImage(mpimg.imread(logo_image),alpha=1)
    ab       = AnnotationBbox(imagebox, ((cols+1)/2, (lins+1)/3)) ; ab.set_alpha(0)   
    aaa      = ax1.add_artist(ab)      ; aaa.patch.set_facecolor([1,1,1,0]) ; aaa.patch.set_edgecolor([1,1,1,0])    
    ax1.get_xaxis().set_visible(False) ; ax1.get_yaxis().set_visible(False)
    ax1.set_facecolor([1,1,1,.5])
   
    
# Draw chart race frames 
def draw_race(Time):

    print ('Generating frame for time ',Time)

    global previous,namebefore,current,namecurrent,base,start,positions_race,first,maxtime
    ax1.clear() ; ax2.clear() ; ax2.set_facecolor([1,1,1,0]) ; ax2.set_position([200,200,1,1]) ; ax3.clear() ; ax3.set_facecolor([1,1,1,0]) ; ax3.set_position([200,200,1,1])     
    df_frame = df[df['Time'].eq(Time)].sort_values(by = 'value', ascending = True).tail(num_of_elements)
    dx       = float(df_frame['value'].max())/20
    tmp      = int(float(re.sub(r'\^(.*)', r'', str(Time))))

    # Verify the instant of the frame    
    if start == 1:
        if previous == None:
            previous     = [v for v in df_frame['value']] ; current     = copy(previous)
            namebefore   = [n for n in df_frame['Name']]  ; namecurrent = copy(namebefore)
        else: 
            current      = [v for v in df_frame['value']]
            namecurrent  = [n for n in df_frame['Name']]
    
    # Verify if the current time is an interpolated time 
    if str(Time).__contains__('^'): 
        # Verify if current values are different from previous - then a element position now is different than was before
        if previous != current:
            # Loop for names
            positions_race = [] ; values = []
            for inew,name in enumerate(namecurrent):
                try:    ibefore = namebefore.index(name) 
                except: ibefore = 0
                positions_race.append(ibefore+((inew-ibefore)*(start*base))) ; values.append(previous[ibefore]+((current[inew]-previous[ibefore])*(start*base)))
            start = start + 1     
        else: positions_race = list(range(num_of_elements)) ; values = current[-num_of_elements:]
    else: 
        positions_race = list(range(num_of_elements)) ; values = current[-num_of_elements:] ; start = 1   
        if first == False: previous = current ; namebefore = namecurrent
        else:              first = False

    # Organizing lists
    positions_race              = positions_race[-num_of_elements:]
    values                      = values[-num_of_elements:]
    all_data                    = sorted(zip(*[positions_race,values,namecurrent[-num_of_elements:]]),key=itemgetter(0))
    positions_race,values,names = list(zip(*all_data))
     
    # Maximum value and current datetime
    maximum                      = 48000
    datatmp = datetime(1979,1,1)+relativedelta(months=tmp)
    
    if maximum != min_value:

        # Getting colors for each element
        c1 = [colors[c][0] for c in names] ; c2 = [colors[c][1] for c in names]
            
        # Ploting bars for all elements
        ax1.barh(positions_race,  values,      color = c1,     height = bar_height, alpha = 0.6, edgecolor = c2,     linewidth = bar_linewidth)
         
        # aux for text and figure insert
        pos    = width_images*maximum/total/2*1.03 

        # Loop for insertion of names and figures 
        for i, value, name in zip(positions_race,values, names):
            if name not in consumption: consumption[name] = [value]
            else:                       consumption[name].append(value)
            if value >=min_value:
                ax1.text(value, i + (num_of_elements / 35), '    ' + name              , size = 30, ha = 'left', va = 'center', weight = 'bold', fontdict = {'fontname': font_name})
                ax1.text(value, i - (num_of_elements / 35), '    %i GWh' % int(value), size = 30, ha = 'left', va = 'center',                  fontdict = {'fontname': font_name})
                
        # Configuring axis 1
        ax1.set_yticks([]) ; ax1.set_xticks([])
        ax1.margins(0, 0.01)
        ax1.set_facecolor([1,1,1,.5])
        ax1.set_xlim(0,maximum)
        
        # Ploting salary time series
        dates_consumption.append(datatmp)
        for c in consumption: 
            ax2.plot(dates_consumption,consumption[c],c=colors[c][0],label=c)
            ax2.text(dates_consumption[-1],consumption[c][-1], str(int(consumption[c][-1])), color = colors[c][0], size = 30, ha = 'center', va = 'center', weight = 'bold', fontdict = {'fontname': font_name})
        
        # Configuring axis 2
        plt.rcParams.update({'font.size':25,'font.weight':'bold'})
        ax2.set_yticks([])
        ax2.set_facecolor([1,1,1,.6])
        ax2.set_position([0.01,.03,.98,.44])
        ax2.xaxis.set_major_formatter( mdates.DateFormatter('%Y'))
        ax2.set_xlim(datetime(1976,12,1),datetime(2024,6,1))
        ax2.legend(loc='upper left', ncol=5) #, bbox_to_anchor=(0.01, 0.)
        ax2.set_ylim(-1000,45000)
        ax2.tick_params(axis='x', colors='white')
        
        # Inserting information about current time
        ax3.text(1, 1, 'Mês\n%s de %.4i' % (meses[datatmp.month-1],datatmp.year),     color = colinfo, size = 42, ha = 'center', va = 'center', weight = 'bold', fontdict = {'fontname': font_name})
        if datatmp in details: 
            print (datatmp,details[datatmp].replace('||','\n'))
            ax3.text(1, 0.01, details[datatmp].replace('||','\n'), color = colinfo, size = 42, ha = 'center', va = 'center', fontdict = {'fontname': font_name}) 
        
        # Configuring axis 3
        ax3.set_position(dims_details)
        ax3.set_yticks([]) ; ax3.set_xticks([])
        ax3.set_xlim(0,2) ; ax3.set_ylim(0,2)
        ax3.set_facecolor([1,1,1,0])
        ax3.spines['right'].set_visible(False)
        ax3.spines['top'].set_visible(False)
        ax3.spines['left'].set_visible(False)
        ax3.spines['bottom'].set_visible(False)

             
# Drawing frames - calling specific function to each one
def draw_frame(z):
    if z[0] == 'cover':    draw_cover(z[1])
    if z[0] == 'racing':   draw_race(z[1])
    if z[0] == 'final':    draw_final(z[1])


# Getting data about elements and details
details   = get_details()

# Getting colors for elements bars
Crs       = pd.read_excel(file_input, sheet_name='cores')
colors    = {c:[c1,c2] for c,c1,c2 in zip(Crs['Name'],Crs['Color1'],Crs['Color2'])}
    
# Info for cover frames
idscover  = create_cover_frames(title,fps)

# Info for final frames
idsfinal  = create_final_frames(final_text,fps)

# Getting data for a season - points for each club, each time
df         = pd.read_csv('entrada/consumo.csv',sep=';', usecols=['Name', 'Time', 'Value'])
maxtime    = max(df['Time'])  
df         = df.pivot(index = 'Name', columns = 'Time', values = 'Value') ; df = df.reset_index()
                          

# Interpolation - smoothing the race, adapting code from "https://www.datasciencecoffee.com/2020-smooth-bar-chart-race/"
for p in range(num_interp):
    i = 0
    while i < len(df.columns):
        tmp = int(float(re.sub(r'\^(.*)', r'', str(df.iloc[:, i + 1].name) + '^' + str(len(df.columns)))))
        if tmp >= 0:
            try:    df.insert(i+2, str(df.iloc[:, i + 1].name) + '^' + str(len(df.columns)), (np.array(df.iloc[:, i + 1]) + np.array(df.iloc[:, i + 2])) / 2)
            except: print("\n Interpolação {p + 1} concluída")
        i = i + 2

# Organizing data 
df          = pd.melt(df, id_vars = 'Name', var_name = 'Time')
frames_list = df["Time"].unique().tolist()

for i in range(50): frames_list.append(df['Time'].iloc[-1])

# Ordering all frames
all_frms = all_frms + idscover
all_frms = all_frms + [['racing',f] for f in frames_list]
all_frms = all_frms + idsfinal

# Figure, main axis, secoundary, subplot adjust and background image
fig, ax1 = plt.subplots(figsize = (wfig, hfig)) ; ax1.set_facecolor([1,1,1,.6])
ax2      = fig.add_subplot(212) ; ax2.set_facecolor([1,1,1,0]) ; ax2.set_position([200,200,1,1])
ax3      = fig.add_subplot(221) ; ax3.set_facecolor([1,1,1,0]) ; ax3.set_position([200,200,1,1]) ; ax3.set_yticks([]) ; ax3.set_xticks([])
im       = fig.figimage(plt.imread(first_image),cmap='Greys_r')
plt.subplots_adjust(left = fig_left, right = fig_right, top = fig_top, bottom = fig_bottom, wspace = fig_wspace, hspace = fig_hspace)

# This is required for matplotlib 3
ax1.set_zorder(1)
ax2.set_zorder(2)
ax3.set_zorder(3)
im.set_zorder(0)

# Animation
animator = animation.FuncAnimation(fig, draw_frame, frames = all_frms)
Writer   = animation.writers['ffmpeg']
writer   = Writer(fps=fps, metadata=dict(artist='Awulll'), bitrate=1800)
animator.save(output_file, writer=writer)
