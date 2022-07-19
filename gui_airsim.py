# -*- coding: utf-8 -*-
"""
Created on Tue Jun 15 20:09:18 2021

@author: Guilherme Claudino e Silva
"""

import tkinter as tk
import setup_path
import airsim
import numpy as np
import matplotlib.pyplot as plt
import os
import tempfile
import time
import pprint
import cv2
import threading
import datetime
import imageio
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from mpl_toolkits import mplot3d


"""

THREADS

"""

"""

Thread movManager - Coordena qual tipo de comando de movimentação
será passado à aeronave. Trabalha com dados de posição gerados pela posUpdater
e por meio de uma "flag" chamada "currStat", sabe quando a aeronave deve
voar e qual movimento executar

"""

def movManager():
    global posplot # Variável global para a criação de gráficos
    while(True):
        # Definição da possição e status atuais
        currStat = stat.get("1.0",'end-1c')
        currPos = pos2
        posplot = currPos 
        
        # Checagem do status
        if currStat == 'voando':
            
            # Verificação de qual tipo de movimentação foi escolhida
            currMov = tkvar.get()
            if currMov == 'Ponto à ponto':
                flyToPosition()
            elif currMov == 'Bate e Volta':
                flyBateVolta(currPos)
            elif currMov == 'Voo Retangular':
                flySquare(currPos)
            else:
                flyCircle(currPos)
            # Atualização do status após execução
            stat.config(state = 'normal')
            stat.delete(1.0,'end-1c')
            stat.insert('end-1c','parado')
            stat.config(state = 'disabled')
        time.sleep(0.1)
        
        # Encerramento
        if kill3:
            break


"""

Thread posUpdater - Roda paralelamente ao código principal. Serve para retirar
informações importantes do programa em tempo real como posição, velocidade
e também serve para criar a variável que trabalha com a câmera

"""   

def posUpdater():
    # Definição de variáveis globais que serão acessadas 
    # externamente
     global pos
     global pos2
     global pos3
     global vel
     global responses
     while(True):
          # getKinematics --> Obtém informações do movimento
         pos = client.simGetGroundTruthKinematics().position 
         pos2 = pos
         vel = client.simGetGroundTruthKinematics().linear_velocity
         # Salva as informações no log 
         f.write('Posição [X, Y, Z]: [' + str(pos.x_val) + ', ' + str(pos.y_val) + ', ' + str(pos.z_val) + '] \n' )
          # getImages --> Captura imagens da camera
         responses = client.simGetImages([ 
        airsim.ImageRequest("1", airsim.ImageType.Scene, False, False) #scene vision image in png format
])  
         time.sleep(0.1)
         
          # Encerramento
         if kill:
             break

"""

Thread posSaver - Roda paralelamente ao código principal. Trabalha com as in-
formações da posUpdater 

"""   

def posSaver():
    # Definição de variáveis globais
    global responses
    
    # Definição de flags e variáveis de apoio
    cap = 0 
    pos_real = np.empty((0,3), float)
    flag0 = 0
    flag1 = 0
    lastpos = []
    
    # Salva foto
    takePicture(flag1)
    
    while(True):         
        # Atualização da posição atual
        posplot = pos2
        lastpos = [posplot.x_val, posplot.y_val, -posplot.z_val]
        while(True):
            posplot = pos
            velplot = vel
            velcalc = np.sqrt(vel.x_val**2 + vel.y_val**2 + vel.z_val**2)
            
            # Verificação se a velocidade está abaixo de um determinado 
            # limite. Caso esteja acima, assume-se movimento
            
            if velcalc <= 5*10**-3:
               time.sleep(0.1)
               if flag0 == 1:
                   flag0 = 0
                   flag1 = flag1 + 1
            else:
               append = [posplot.x_val, posplot.y_val, -posplot.z_val]
               print(append)
               
               # Plot e atualização da última posição 
               ax.plot([lastpos[0], append[0]],[lastpos[1], append[1]],[lastpos[2], append[2]], 'b', label = 'Posição Real')
               lastpos = [posplot.x_val, posplot.y_val, -posplot.z_val]
               print('Velocidade Calculada')
               print(velcalc)
               time.sleep(0.1)
               
               # Verificação do tempo para tirar novas fotos
               if cap % 10 == 0:
                   takePicture(flag1)
                   flag0 = 1
                   #  updateChart()
                   print('Tirando Foto')
               # Atualização do contador de foto para que ocorra uma vez por
               # segundo apenas. 
            cap = cap+1
               # takePicture()
               
        if kill2:
         break
     


"""

FUNÇÕES

""" 

"""

Rotina build - Serve para atualizar os status dos botões e os widgets
presentes na GUI após a escolha do tipo de movimento. pack() faz os widgets
aparecerem enquanto pack_forget() os faz sumir. 

"""
    
def build(mov):
    if mov == 'Ponto à ponto':
        b2['text'] = 'Ponto à ponto'
        llr.pack_forget()
        tlr.pack_forget()
        lcr.pack_forget()
        tcr.pack_forget()
        pvt.pack_forget()
        tt.pack_forget()
        lr.pack_forget()
        tr.pack_forget()
        lpx.pack()
        pxt.pack()
        lpy.pack()
        pyt.pack()
        lpz.pack()
        pzt.pack()
        pvt.pack()
        tt.pack()
        
    elif mov == 'Bate e Volta':
        b2['text'] = 'Bate e Volta'
        llr.pack_forget()
        tlr.pack_forget()
        lcr.pack_forget()
        tcr.pack_forget()
        pvt.pack_forget()
        tt.pack_forget()
        lr.pack_forget()
        tr.pack_forget()
        lpx.pack()
        pxt.pack()
        lpy.pack()
        pyt.pack()
        lpz.pack()
        pzt.pack()
        pvt.pack()
        tt.pack()
        
    elif mov == 'Voo Retangular':
        b2['text'] = 'Voo Retangular'
        lpx.pack_forget()
        pxt.pack_forget()
        lpy.pack_forget()
        pyt.pack_forget()
        lpz.pack_forget()
        pzt.pack_forget()
        pvt.pack_forget()
        tt.pack_forget()
        lr.pack_forget()
        tr.pack_forget()
        llr.pack()
        tlr.pack()
        lcr.pack()
        tcr.pack()
        pvt.pack()
        tt.pack()
        
    else:
        b2['text'] = 'Voo em Circulo'
        lpx.pack_forget()
        pxt.pack_forget()
        lpy.pack_forget()
        pyt.pack_forget()
        lpz.pack_forget()
        pzt.pack_forget()
        pvt.pack_forget()
        tt.pack_forget()
        llr.pack_forget()
        tlr.pack_forget()
        lcr.pack_forget()
        tcr.pack_forget()
        lr.pack()
        tr.pack()
        pvt.pack()
        tt.pack()
        

"""

Rotina chooseMov - Apenas uma interface para chamar a função build


"""  
 
def chooseMov(*args):
    print("Entrando no ChooseMov")
    print(tkvar.get())
    # Verifica a variável e chama a rotina build
    build(tkvar.get())
    
"""

Rotina cleanChart - Serve para apagar o gráfico ao pousar.

"""

def cleanChart():
    ax.clear()
    print('Gráfico Limpo')


"""

Rotina closeWindow - Define procedimentos para o fechamento da janela
da GUI. Os comandos kill = true servem para encerrar as Threads em 
execução paralela. 

"""
        
def closeWindow():
    #    if messagebox.askokcancel("Sair", "Você realmente deseja sair?"):
    try:
        # reset()
        global kill
        kill = True
        global kill2
        kill2 = True
        global kill3
        kill3 = True
        window.destroy()
    except:
        window.destroy()

"""

Rotina connect - Cria algumas variáveis globais caso não tenha 
sido feito ainda. A rotina é responsável por se conectar ao cliente
do Airsim, permitir o controle deste pela API. Também é possível obter
algumas informações da aeronave como informações de GPS. Aqui se 
inicia a Thread posUpdater

"""
        
def connect():
    try:
        global client
        global Running
        global kill
        global kill2
        global kill3
    except: 
        pass
    
    kill = False
    kill2 = False
    kill3 = False
    Running = True
    
    # Conexão
    client = airsim.MultirotorClient()
    client.confirmConnection()
    
    # Controle da API
    client.enableApiControl(True)
    client.armDisarm(True)
    
    # Levantamento de informações e print
    state = client.getMultirotorState()
    s = pprint.pformat(state)
    print("state: %s" % s)
    
    imu_data = client.getImuData()
    s = pprint.pformat(imu_data)
    print("imu_data: %s" % s)
    
    barometer_data = client.getBarometerData()
    s = pprint.pformat(barometer_data)
    print("barometer_data: %s" % s)
    
    magnetometer_data = client.getMagnetometerData()
    s = pprint.pformat(magnetometer_data)
    print("magnetometer_data: %s" % s)
    
    gps_data = client.getGpsData()
    s = pprint.pformat(gps_data)
    print("gps_data: %s" % s)
    
    # Alteração em tempo real do Layout da GUI
    b0['text'] = 'Ambiente de Execução Conectado'
    b0['bg'] = 'green'
    turnButton(b0)
    turnButton(b10)
    labelframe.pack(side = tk.LEFT, fill="both", expand="yes")
    try: # Tentativa de execução da thread posUpdater
        thread.start()
    except Exception:
        pass    
    print('Thread Iniciada')
    time.sleep(2)   

"""

Rotina fly - Serve para atualizar a flag da thread movManager. 
A função também pode iniciar a thread caso seja sua primeira execução.

"""

def fly():
    # Atualização da flag
    stat.config(state = 'normal')
    stat.delete(1.0,'end-1c')
    stat.insert('end-1c','voando')
    stat.config(state = 'disabled')
    
    try: # Tentativa de execução da thread movManager
        threadmov.start()
    except Exception:
        pass    

"""

Rotina flyBateVolta - Define as funções necessárias para realizar um voo
do tipo bate e volta, indo de uma posição inicial, até uma posição
intermediária e retornando. 

"""


def flyBateVolta(position_current):
    # Define posições iniciais
    init_pos_bv = position_current
    init_x = init_pos_bv.x_val
    init_y = init_pos_bv.y_val
    init_z = init_pos_bv.z_val
    
    # Definição do ponto alvo
    mid_x = float(pxt.get("1.0",'end-1c'))
    mid_y = float(pyt.get("1.0",'end-1c'))
    mid_z = float(pzt.get("1.0",'end-1c'))
    positionmod = np.sqrt((mid_x-init_x)**2+(mid_y-init_y)**2+(mid_z-init_z)**2)
    vmod = float(tt.get("1.0",'end-1c'))
    t = positionmod/vmod
    
    # Voo até o alvo
    flyToPosition()
    time.sleep(0.01)
    time.sleep(t)
    
    # Atualização do ponto alvo como sendo a origem do movimento
    pxt.delete(1.0,'end-1c')
    pxt.insert('end-1c', str(init_x))
    pyt.delete(1.0,'end-1c')
    pyt.insert('end-1c',str(init_y))
    pzt.delete(1.0,'end-1c')
    pzt.insert('end-1c',str(-init_z))
    
    # Voo até a origem
    flyToPosition()
    time.sleep(t)

"""

Rotina flyCircle - Define as rotinas para a realização de um voo circular

"""
    
def flyCircle(starting_position, discret=10):
    vc = float(tt.get("1.0",'end-1c'))
    radius = float(tr.get('1.0','end-1c'))
    omega_c = vc/radius
    tc = 2*np.pi/omega_c
    tc_control = tc/discret
    xc = starting_position.x_val-radius
    yc = starting_position.y_val
    zc = starting_position.z_val
    xold = starting_position.x_val
    yold = yc
    zold = -zc
    for i in range(1, discret+1):
        t_use = tc_control*i
        angle = omega_c*t_use
        startPlot = [xold, yold, zold]   
        x_now = xc + np.cos(angle)*radius
        y_now = yc + np.sin(angle)*radius
        client.moveToPositionAsync(x_now, y_now, zc, vc)
        endPoint = [x_now, y_now, zold]
        ax.plot([startPlot[0],endPoint[0]],[startPlot[1],endPoint[1]],[startPlot[2],endPoint[2]], 'r', label = 'Posição Desejada')
        time.sleep(tc_control)
        xold = x_now
        yold = y_now
        print(tc_control)
        print("Voo circular")
    

"""

Rotina flyToPosition - Define as relações para que a aeronave possa voar de um
ponto à outro

"""

def flyToPosition():
    print("Andando em Frente...")
    labelframe2.pack(fill="both", expand="yes")
    init_pos = pos
    print(init_pos.x_val)
    print(init_pos.y_val)
    print(init_pos.z_val)
    trajectoryDesired(tkvar.get())
    
    #for i in range(5):
    #    client.moveToPositionAsync(-init_pos.x_val + i/5*int(pxt.get("1.0",'end-1c')),-init_pos.y_val + i/5*int(pyt.get("1.0",'end-1c')),-init_pos.z_val -i/5*int(pzt.get("1.0",'end-1c')), int(tt.get("1.0",'end-1c'))).join()
    try:
        client.moveToPositionAsync(float(pxt.get("1.0",'end-1c')),\
                                   float(pyt.get("1.0",'end-1c')),\
                                       -float(pzt.get("1.0",'end-1c')),\
                                           float(tt.get("1.0",'end-1c')))#.join()
        #takePicture()
        try:
            threadchart.start()
        except:
            pass  
    except:
        tk.messagebox.showerror('Impossível chegar até a posição','Parece que \
                                você esqueceu que as posições precisam ser \
                                valores numéricos. Por favor corrija antes \
                                    de executar o código novamente.') 

"""

Rotina flySquare - Define as relações para o voo retangular

"""


def flySquare(position_current):
    print("Voo retangular")
    comp = float(tcr.get("1.0",'end-1c'))
    larg = float(tlr.get("1.0",'end-1c'))
    curr_speed = float(tt.get("1.0",'end-1c'))
    init_pos_r = position_current
    init_xr = init_pos_r.x_val
    init_yr = init_pos_r.y_val
    init_zr = init_pos_r.z_val
    t1 = comp/curr_speed
    t3 = t1
    t2 = larg/curr_speed
    t4 = t2
    print(init_zr)
    client.moveToPositionAsync(init_xr+comp, init_yr, init_zr, curr_speed)
    startPlot = [init_xr, init_yr, -init_zr]
    endPoint = [init_xr + comp, init_yr, -init_zr]
    ax.plot([startPlot[0],endPoint[0]],[startPlot[1],endPoint[1]],[startPlot[2],endPoint[2]], 'r', label = 'Posição Desejada')
    #time.sleep(0.01)
    time.sleep(t1)
    client.moveToPositionAsync(init_xr+comp, init_yr+larg, init_zr, curr_speed)
    startPlot = [init_xr + comp, init_yr, -init_zr]
    endPoint = [init_xr + comp, init_yr + larg, -init_zr]
    ax.plot([startPlot[0],endPoint[0]],[startPlot[1],endPoint[1]],[startPlot[2],endPoint[2]], 'r', label = 'Posição Desejada')
    #time.sleep(0.01)
    time.sleep(t2)
    client.moveToPositionAsync(init_xr, init_yr+larg, init_zr, curr_speed)
    startPlot = [init_xr+comp, init_yr+ larg, -init_zr]
    endPoint = [init_xr, init_yr + larg, -init_zr]
    ax.plot([startPlot[0],endPoint[0]],[startPlot[1],endPoint[1]],[startPlot[2],endPoint[2]], 'r', label = 'Posição Desejada')
    #time.sleep(0.01)
    time.sleep(t3)
    client.moveToPositionAsync(init_xr, init_yr, init_zr, curr_speed)
    startPlot = [init_xr, init_yr+ larg, -init_zr]
    endPoint = [init_xr, init_yr, -init_zr]
    ax.plot([startPlot[0],endPoint[0]],[startPlot[1],endPoint[1]],[startPlot[2],endPoint[2]], 'r', label = 'Posição Desejada')
    #time.sleep(0.01)
    time.sleep(t4)
    
    
    
    
    
"""

Rotina gifSaver - Objetivo: Criar um gif com as imagens capturadas em 
takePictures

"""   

def gifSaver():
    png_dir = os.path.dirname(os.path.abspath(__file__)) + "/" + gt.get("1.0",'end-1c')
    images = []
    for file_name in sorted(os.listdir(png_dir)):
        if file_name.endswith('.png'):
            file_path = os.path.join(png_dir, file_name)
            images.append(imageio.imread(file_path))
    imageio.mimsave(png_dir + '/video.gif', images)


"""

Rotina Landing - Função para pousar a aeronave e atualizar os botões. 

"""

def landing():
    print("Landing...")
    client.landAsync()
    b1['text'] = 'Drone Pousou - Decole Novamente'
    b1['bg'] = 'red'    
    turnButton(b10)
    turnButton(b1)
    cleanChart()
    #labelframe2.pack(side = tk.LEFT, fill="both", expand="yes")
    #labelframe3.pack(side = tk.LEFT, fill="both", expand="yes") 


       
"""

Rotina reset - visa retornar o drone à sua posição inicial fazendo com que
o drone pouse. 

"""
        
def reset():
    client.reset()
    b1['text'] = 'Drone de volta ao estado inicial'
    b1['bg'] = 'red'
    b0['text'] = 'Ambiente Desconectado'
    b0['bg'] = 'red'
    turnButton(b0)    
    turnButton(b1)
    turnButton(b10)
    labelframe.pack_forget()
    labelframe2.pack_forget()
    cleanChart()
    try:
        client.landAsync()
    except:
        pass

    
"""

Rotina takeoff - Objetivo: Fazer com que o drone decole, liberar os widgets
escondidos do tkinter e atualizar o comportamento de botões

"""   

def takeoff():
    print("Taking off...")
    client.takeoffAsync()
    #client.moveToPositionAsync(0, 0, -10, 2).join()
    b1['text'] = 'Drone Decolou'
    b1['bg'] = 'green'    
    turnButton(b1)
    turnButton(b10)
    labelframe2.pack(side = tk.LEFT, fill="both", expand="yes")
    labelframe3.pack(side = tk.LEFT, fill="both", expand="yes")
    

"""

Rotina takePicture - Objetivo: Receber o arquivo da camera do Airsim, criar as
pastas corretas e salvar o arquivo em formato PNG

"""   


def takePicture(flag):
#scene vision image in uncompressed RGBA array
    response = responses[0]
    folderNumb = str(flag)
    #print(response)
    pictime = datetime.datetime.now()
    pichour = pictime.strftime('%H_%M_%S')
    picname = pictime.strftime('%b-%d-%Y')
    try:
        os.mkdir('Pics')
    except Exception:
        pass
    try:
        os.mkdir('Pics/' + picname + ' Manobra ' + folderNumb)
    except Exception:
        pass
    gt.delete(1.0,'end-1c')
    gt.insert('end-1c','Pics/' + picname + ' Manobra ' + folderNumb)
    try:
        img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8) # get numpy array        
        img_rgb = img1d.reshape(response.height, response.width, 3) # reshape array to 4 channel image array H X W X 3
        cv2.imwrite('Pics/' + picname + ' Manobra ' + folderNumb + '/' + pichour + '.png', img_rgb) 
        print('Imagem Feita em' + pichour)
    except Exception:
        return
    #print("Type %d, size %d" % (responses[4].image_type, len(responses[4].image_data_uint8)))
    #cv2.imwrite('Pics/' + pichour + '_hr.png', responses[4].image_data_uint8)


"""

Rotina tracjetoryDesired - auxilia a geração de gráficos caso a trajetória seja
bate e volta ou ponto à ponto.

"""


def trajectoryDesired(mov):
    # plt.clf()
    if mov == 'Ponto à ponto' or mov == 'Bate e Volta':
        startPoint = pos
        startPlot = [float(startPoint.x_val), float(startPoint.y_val), float(-startPoint.z_val)]
        endPoint = [float(pxt.get("1.0",'end-1c')), float(pyt.get("1.0",'end-1c')), float(pzt.get("1.0",'end-1c'))]
        ax.plot([startPlot[0],endPoint[0]],[startPlot[1],endPoint[1]],[startPlot[2],endPoint[2]], 'r', label = 'Posição Desejada')
    #else:
        #tk.messagebox.showinfo('Nenhuma trajetória encontrada', 'Nenhuma trajetória encontrada')    
    #updateChart()
    
    
"""

Rotina turnButton - serve para definir se um botão é editável ou não

"""
    
    
def turnButton(button_name):
    if button_name['state'] == 'normal':
        button_name['state'] = 'disabled'
    else:
        button_name['state'] = 'normal'  
    
    
""" 

Rotina updateChart - pode ser chamada por outras rotinas para atualizar
o gráfico após a movimentação. 

"""
    
def updateChart():
    canvas.draw()
    ax.legend(['Trajetória Desejada', 'Trajetória Real'])

"""

INTERFACE GRÁFICA

"""

# Informações genéricas
window = tk.Tk()
window.geometry("1920x1080")
window.protocol("WM_DELETE_WINDOW", closeWindow)
window.title('AirSim Controller')

# Criando o arquivo de log
day = datetime.datetime.now()
day_hour = day.strftime("%b-%d-%Y %H_%M_%S")
try:
    os.mkdir('Arquivos Txt')
except Exception:
    pass
f = open('Arquivos Txt/'+ day_hour + '.txt', "x")

# Definição de threads
thread = threading.Thread(target=posUpdater, name="Position Updater")
threadchart = threading.Thread(target=posSaver, name="Position Saver")
threadmov = threading.Thread(target=movManager, name="Gerente de Movimentação")

# Interface inicial - conexão da aeronave
greeting = tk.Label(text="AirSim CONTROLLER")
greeting.pack()
b0 = tk.Button(window, text ="Conectar a aeronave", command = connect)
b0.pack()
to = 0

# Criação do primeiro subgrupo - pouso e decolagem
labelframe = tk.LabelFrame(window, text="Principal")
b1 = tk.Button(labelframe, text="Decolagem", command = takeoff)
b1.pack()
b10 = tk.Button(labelframe, text="Pouso", command = landing)
b10.pack()


# Criação do espaço de movimentação na Gui
labelframe2 = tk.LabelFrame(window, text="Movimentação")

tkvar = tk.StringVar(window)
tkvar2 = tk.StringVar(window)

# Criação da lista de movimentos 
mov_types = { 'Ponto à ponto', 'Bate e Volta','Voo Retangular','Voo em Círculo'}
tkvar.set('Ponto à ponto') # set the default option
tkvar.trace('w', chooseMov)
popupMenu = tk.OptionMenu(labelframe2, tkvar, *mov_types)
popupMenu.pack()

# Botão de Reset
b3 = tk.Button(labelframe2, text="Resetar a Simulação", command = reset)
b3.pack()

# Espaço para o gráfico de movimentação
fig = plt.Figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')
ax.grid(True)
ax.set(title = "Trajetória Real x Desejada",
        xlabel = "X (m)",
  ylabel = "Y (m)", 
  zlabel = "Z (m)")
plt.show()
canvas = FigureCanvasTkAgg(fig, master=labelframe2)
canvas.draw()
canvas.get_tk_widget().pack()

# Criação do botão de voo
b2 = tk.Button(labelframe2, text="Voo Reto", command = fly)
b2.pack()

# Caixas de texto para as manobras ponto à ponto e bate e volta
pxt = tk.Text(labelframe2, height = 1, width = 52)
lpx = tk.Label(labelframe2, text = "Posição em x")
pyt = tk.Text(labelframe2, height = 1, width = 52)
pxt.insert('end-1c','0')
lpy = tk.Label(labelframe2, text = "Posição em y")
pzt = tk.Text(labelframe2, height = 1, width = 52)
pyt.insert('end-1c','0')
lpz = tk.Label(labelframe2, text = "Posição em z")
tt = tk.Text(labelframe2, height = 1, width = 52)
pzt.insert('end-1c','0')
pvt = tk.Label(labelframe2, text = "Velocidade da manobra")
tt.insert('end-1c','1')
lpx.pack()
pxt.pack()
lpy.pack()
pyt.pack()
lpz.pack()
pzt.pack()
pvt.pack()
tt.pack()

# Caixas de texto para a manobra retangular
llr = tk.Label(labelframe2, text = "Largura do Retângulo")
tlr = tk.Text(labelframe2, height = 1, width = 52)
tlr.insert('end-1c','0')
lcr = tk.Label(labelframe2, text = "Comprimento do Retângulo")
tcr = tk.Text(labelframe2, height = 1, width = 52)
tcr.insert('end-1c','0')

# Caixas de texto para a manobra circular
tcr.insert('end-1c','1')
lr = tk.Label(labelframe2, text = "Raio do Círculo")
tr = tk.Text(labelframe2, height = 1, width = 52)
tr.insert('end-1c','0')


# Criação do espaço para funções auxiliares
labelframe3 = tk.LabelFrame(window, text="Outras Funções")

# Botão de atualizar gráfico
b4 = tk.Button(labelframe3, text="Update Plot", command = updateChart)
b4.pack()

# Criação da interface para geração de animação
gt = tk.Text(labelframe3, height = 1, width = 52)
#gt.config(state='disabled')
lg = tk.Label(labelframe3, text = "Caminho GIF")
lg.pack()
gt.pack()
b4 = tk.Button(labelframe3, text="Gerar Gif", command = gifSaver)
b4.pack()

# Interface para flag do movManager
stat = tk.Text(labelframe3, height = 1, width = 52)
lstat = tk.Label(labelframe3, text = "Status - Por favor não mexa")
lstat.pack()
stat.pack()
stat.insert('end-1c','parado')
stat.config(state = 'disabled')

# Para salvar posições 
pxt2 = tk.Text(labelframe2, height = 1, width = 52)
lpx2 = tk.Label(labelframe2, text = "Última Posição em x")
pyt2 = tk.Text(labelframe2, height = 1, width = 52)
pxt2.insert('end-1c','0')
lpy2 = tk.Label(labelframe2, text = "Última Posição em y")
pzt2 = tk.Text(labelframe2, height = 1, width = 52)
pyt2.insert('end-1c','0')
lpz2 = tk.Label(labelframe2, text = "Última Posição em z")
pzt2.insert('end-1c','0')

# Criação do loop do tkinter
window.mainloop()

