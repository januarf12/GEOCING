# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         CÁLCULO DE SUSCEPTIBILIDAD ANTE MM A TRAVÉS DEL MÉTODO WOE
# Version:         1.0.5
# Fecha :       2 Feb 2021
# Purpose:      Obtener una zonificación de susceptibilidad
# Conditions:   - Tener en cuenta que los raster de entrada estén todos en formato .tiff
#               y con la misma resolución espacial (recomendado 10m)
#               - Las rutas no deben ser demasiado largas ni contener caracteres espaciales ni espacios
#               - Se debe correr con un interprete de PYTHON con capacidad de consumir Python 2.7 de Arcgis (Vs. más estable Arcmap 10.2.2)
# Author:      Ing. Felipe Riaño                afrianoq@unal.edu.co
#
# Created:     28/12/2020
# Copyright:   (c)
# Licence:     <>
#-------------------------------------------------------------------------------
# -----------------------Importación de modulos---------------------------------
# -*- coding: utf-8 -*-
import arcpy
import os
import shutil
import glob
from arcpy import env
from arcpy.sa import *
import numpy as np
import pandas as pd
import sys
from Tkinter import *
import Tkinter as tk
import ttk
import tkFileDialog as filedialog
import tkMessageBox
import PIL.Image
import PIL.ImageTk
import math
import copy
import shutil
from itertools import combinations
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = 1
np.version.full_version


#------------------------Definición de funciones-------------------------------
    # 1. Definición del espacio de trabajo
def Workspace(ruta):
    global Workspace
    Workspace = arcpy.env.workspace = (ruta)

def ListaenGDB(RutaParaGDBGeneradas,myList,NombreGDB):

    if not myList:
        # Create directory
        dirName = os.path.join(RutaParaGDBGeneradas, "GDBs")
        if not os.path.exists(dirName):
            os.mkdir(dirName)
            print("Directory " , dirName ,  " Created ")
        else:
            print("Directory " , dirName ,  " already exists")

        out_folder_path = dirName
        out_name = NombreGDB+".gdb"
        # Execute CreateFileGDB
        arcpy.CreateFileGDB_management(out_folder_path, out_name)

        OutGDB = os.path.join(dirName, out_name)
        return OutGDB
    else:
        dirName = os.path.join(RutaParaGDBGeneradas, "GDBs")
        if not os.path.exists(dirName):
            os.mkdir(dirName)
            print("Directory " , dirName ,  " Created ")
        else:
            print("Directory " , dirName ,  " already exists")

        out_folder_path = dirName
        out_name = NombreGDB+".gdb"
        # Execute CreateFileGDB
        GDB = arcpy.CreateFileGDB_management(out_folder_path, out_name)
        ListGDB = arcpy.RasterToGeodatabase_conversion(myList, GDB)
        return ListGDB.getOutput(0)

def TakeRasters(ruta):
    inws = ruta
    rasters = []
    walk = arcpy.da.Walk(inws, topdown=True, datatype= "RasterDataset", type = "TIF")
    for dirpath, dirnames, filenames in walk:
        for filename in filenames:
            rasters.append(os.path.join(dirpath, filename))
    return rasters

def DeleteFilesInFolder(ruta):
    for root, dirs, files in os.walk(ruta):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
#FUNCIONES PARA GUI:
def myClick():
    global LimiteContraste
    LimiteContraste = contraste_entry.get()
    contraste_entry.delete(0,'end')
    button2['state'] = DISABLED
##    if LimiteContraste is null:
##        LimiteContraste = 0
def ReclassBinarias(LimiteContraste):
    myRemapVal = []
    arcpy.env.workspace =(ReclassGDB)
    for key, value in RangosDeClasificacion.items():
        print(key)
        if VariablesEntrada[var] == key:
            print(key)
            print(RangosDeClasificacion[key][0])
            MapValues = []
            for index, row in data.iterrows():
                    print(row)
                    i = 0
                    claseAntParaBin = row[0]
                    if (row[8]) >= float(LimiteContraste):
                        claseNuevParaBin = 1
                        Mapvalues1 = [claseAntParaBin,claseNuevParaBin]
                        MapValues.append(Mapvalues1)
                    else:
                        claseNuevParaBin = 0
                        Mapvalues1 = [claseAntParaBin,claseNuevParaBin]
                        MapValues.append(Mapvalues1)
            myRemapVal = RemapValue(MapValues)
            indice = str('re_'+key.lower())
            VarRECLAS = VariablesReclasificadas.index(indice)
            arcpy.Reclassify_3d(VariablesReclasificadas[VarRECLAS], "VALUE", str(myRemapVal), temporales + "\\" +"BIN_"+key, "DATA")
    root.destroy()
    root.update()

def select():
    if not list_independendientes:
        list_independendientes.append(variables_list.get(ANCHOR))
        current_value = label_Var.cget("text")
        new_value = current_value  + str(variables_list.get(ANCHOR))
        label_Var.config(text=new_value)
    else:
        if variables_list.get(ANCHOR) not in list_independendientes:
            list_independendientes.append(variables_list.get(ANCHOR))
            current_value = label_Var.cget("text")
            new_value = current_value  +', '+ str(variables_list.get(ANCHOR))
            label_Var.config(text=new_value)

def delete():
    global list_independendientes
    label_Var.config(text='La susceptibilidad se calculará usando las \n siguientes variables independientes: \n')
    list_independendientes = []

def susceptibilidad():
    print('Calcular susceptibilidad')
    global VariablesEntradaGDB
    DeleteFilesInFolder(temporales)
    myRemapVal = []
    outras = 0
    susceptibilidadRuta = os.path.join(rutaGDBs, "Susceptibilidad")
    if not os.path.exists(susceptibilidadRuta):
        os.mkdir(susceptibilidadRuta)
        print("Directory " , susceptibilidadRuta ,  " Created ")
    else:
        print("Directory " , susceptibilidadRuta ,  " already exists")

    RangosPesoContraste = copy.deepcopy(RangosDeClasificacion)
    for VarIndependiente in list_independendientes:
        for key, value in RangosPesoContraste.items():
            arcpy.env.workspace = (VariablesEntradaGDB)
            print('Lista de variables: '+key)
            if VarIndependiente == key:
                print('Independientes: '+ VarIndependiente)
                print(RangosPesoContraste[VarIndependiente][0])
                for r in range(len(RangosPesoContraste[VarIndependiente][0])):
                    rangoss=[]
                    RangosPesoContraste[VarIndependiente][0][r][2] = round(RangosPesoContraste[key][0][r][2],5)
                    RangosPesoContraste[VarIndependiente][0][r][2] = int(RangosPesoContraste[key][0][r][2] * 100000)
                MapValues = RangosPesoContraste[key][0]
                myRemapVal = RemapValue(MapValues)
                i = 0
                NombreArchivo = "Sus_"+key
                while len(NombreArchivo) > 13:
                    i+=1
                    NombreArchivo = "Sus_"+key[:-i]
                    print(NombreArchivo)
                arcpy.Reclassify_3d(key, "VALUE", str(myRemapVal), temporales + "\\" + NombreArchivo, "DATA")
                listras = Raster(temporales + "\\" + NombreArchivo)
                outras += listras
    arcpy.env.workspace = (temporales)
    outras.save('mapa_suscep')

    arcpy.AddField_management(outras, 'SUSCEP','DOUBLE')
    arcpy.CalculateField_management(outras ,'SUSCEP',"[VALUE] /100000","VB","#")
##    arcpy.RasterToPolygon_conversion(outras,'mapa_suscep.shp',simplify="SIMPLIFY",raster_field="SUSCEP")
    Variab_SuscepGDB = ListaenGDB(rutaGDBs,'',"Susceptibilidad")
    arcpy.env.workspace = (Variab_SuscepGDB)
    arcpy.CopyRaster_management(outras,'Mapa_Suscept')
##    arcpy.PolygonToRaster_conversion('mapa_suscep.shp','SUSCEP', 'mapa_suscep.tif' ,cell_assignment="CELL_CENTER",priority_field="NONE",cellsize = ResolucionEspacial)

    button3['state'] = DISABLED

##########################################################################################################################################################
#-------------------------------ENTRADAS-----------------------------------------
##########################################################################################################################################################
# Lectura del directorio del código:
    #a. Pregunta la ruta:
##rutacodigo = raw_input(u'Indique la ruta del directorio donde se almacena el presente script:\n Tipo: FOLDER ')
    #b. Ruta predifinda:
rutacodigo = u'D:\\FR_GEOCING\\Codigos_Python\\Susceptibilidad_MM_WOE\\Scripts_Python'
# A. Lectura de las Variables de entrada:
    #a. Pregunta la ruta:
##rutabuena = raw_input(u'Indique la ruta de almacenamiento de las variables de entrada al modelo:\n Tipo: FOLDER ')
    #b. Ruta predifinda:
rutabuena = u'D:\\FR_GEOCING\\Codigos_Python\\Susceptibilidad_MM_WOE\\Insumos_Correr\\variables'
arcpy.env.workspace =(rutabuena)
# Get and print a list of Rasters from the workspace
VariablesEntrada = arcpy.ListRasters()

# A1. Fijación de la ruta de almacenamiento de resultados:
    #a. Pregunta la ruta:
##rutaGDBs = raw_input(u'Indique la ruta de almacenamiento de las GDB a generar:\n Tipo: FOLDER ')
    #b. Ruta predifinda:
rutaGDBs = u'D:\\FR_GEOCING\\Codigos_Python\\Susceptibilidad_MM_WOE\\Prueba_Febrero_2021\\09_02'

#A2. GDB con Variables de entrada:
VariablesEntradaGDB = ListaenGDB(rutaGDBs,VariablesEntrada,"Entradas")
#--------------------------------------------------------------------------------------
#C1. Llamamos raster de MM
    #a. Pregunta la ruta:
##MMurl = raw_input(u'Indique la ruta del raster de MM: \n(1- Presencia/ 0- No Presencia)\n Tipo: .TIFF ')
    #b. Ruta predifinda:
MMurl = u'D:\FR_GEOCING\Codigos_Python\Susceptibilidad_MM_WOE\Insumos_Correr\Procesos\\mm.tif'
#-------------------------------Reclasificar-----------------------------------------

# B1. Condiciones para Clasificación de Raster Continuos:
Reclasificados = []
Workspace(VariablesEntradaGDB)
VariablesEntrada = arcpy.ListRasters()
RangosDeClasificacion={}
ResolucionEspacial = float (arcpy.GetRasterProperties_management (VariablesEntrada[0], "CELLSIZEX").getOutput (0))
#B2. Creación de la carpeta para temporales
temporales = os.path.join(rutaGDBs, "Resultados_Temporales")
if not os.path.exists(temporales):
    os.mkdir(temporales)
    print("Directory " , temporales ,  " Created ")
else:
    print("Directory " , temporales ,  " already exists")
#-------------------------------------------------------------------------------------
#B3. Reclasificación de los Rasters:

for x in VariablesEntrada:
    user_answer = raw_input("Desea reclasificar la variable:\n " + str(x)+"  ").lower().strip()
    ReMapRangeVar = []
    if user_answer == "si":
        NoClases = input("Especifique un No. de clases para la variable:\n " + str(x)+"  ")
        RangoInicial = "i"
        RangoFinal = "f"
        for i in range(1,NoClases+1):
            if i < NoClases:
                if RangoInicial == "i":
                    RangoInicial = float (arcpy.GetRasterProperties_management (x, "MINIMUM").getOutput (0))
                else:
                    RangoInicial = RangoFinal
                RangoFinal = input("El valor inicial de la clase "+ str(i)+" es "+str(RangoInicial)+ " Especifique un valor final para esta clase ")
                ReMap = [RangoInicial,RangoFinal,i]
                ReMapRangeVar.append(ReMap)
            else:
                RangoInicial = RangoFinal
                RangoFinal = float (arcpy.GetRasterProperties_management (x, "MAXIMUM").getOutput (0))+1
                ReMap = [RangoInicial,RangoFinal,i]
                ReMapRangeVar.append(ReMap)
        #Aquí se debería hacer el reclassify
        ReclasificadoRaster = ("re_"+x[:9])
        MyRemapRange = RemapRange(ReMapRangeVar)
        ruta = os.path.join(temporales,ReclasificadoRaster)
        arcpy.Reclassify_3d(x, "VALUE", str(MyRemapRange), ruta, "DATA")
##        arcpy.Reclassify_3d(x,"Value","-21.157510757446289 0 1;0 10 2;10 22.439783096313477 3","C:/Users/Geocing/Documents/ArcGIS/Default.gdb/Reclass_curv4","DATA")
    elif user_answer == "no":
        ClaseMax = int (arcpy.GetRasterProperties_management (x, "MAXIMUM").getOutput (0))
        NoClases = ClaseMax
        for s in range (1, ClaseMax+1):
            ReMap = [s,s,s]
            ReMapRangeVar.append(ReMap)
        ReclasificadoRaster = ("re_"+x+".tif")
        arcpy.CopyRaster_management(x, temporales + "\\" + ReclasificadoRaster)
    else:
        print("Error: Answer must be True or False")
#B4. Acumulación de datos de clasificación en un diccionario
    RangosDeClasificacion[x] = [ReMapRangeVar,"No. de Clases de la Var.: "+str(NoClases),"Raster inicialmente continuo: "+user_answer]
######################################################################################################################################################################
#------------------------------------------------------------------------------------------------------
######################################################################################################################################################################
#B5. Subimos los reclasificados a la GDB y borramos de temporal:
arcpy.env.workspace =(temporales)
Reclass_List = arcpy.ListRasters()
ReclassGDB = ListaenGDB(rutaGDBs,Reclass_List,"Reclass")
arcpy.env.workspace =(ReclassGDB)
VariablesReclasificadas = arcpy.ListRasters()
DeleteFilesInFolder(temporales)

#-------------------------------Combinatorias con MM-----------------------------------------

#C. Ejecución de combinatorias por variable con MM:
#-------------------------------------------------------------------------------------------
#C1. Combinatorias multiples:
combine = []
CombiMMGDB = ListaenGDB(rutaGDBs,combine,"CombiMM")
arcpy.env.workspace =(ReclassGDB)
for variable in VariablesReclasificadas:
    RasterPasajero = os.path.join(temporales,variable)+".tif"
    arcpy.CopyRaster_management(variable, RasterPasajero)
    print RasterPasajero
    combine = []
    combine.append(MMurl)
    combine.append(variable)
    combi = Combine(combine)
    SALIDA = combi.save(os.path.join(CombiMMGDB,"COM_"+variable[3:10]))
    print SALIDA
DeleteFilesInFolder(temporales)

#C2. -------------------------------Manejo de Tablas-----------------------------------------
#C3.1. Creación de la carpeta para tablas
tablas = os.path.join(rutaGDBs, "Tablas")
if not os.path.exists(tablas):
    os.mkdir(tablas)
    print("Directory " , tablas ,  " Created ")
else:
    print("Directory " , tablas ,  " already exists")
#--------------------------------------------------------------------------------------------
arcpy.env.workspace =(CombiMMGDB)
combinatoriasMM = arcpy.ListRasters()
TablasCombinatoria = {}
var = 0
for combi in combinatoriasMM:
    contrasteslist = []
    #Pasamos las combi a DBF"
    ListTablaCombi = []
    arcpy.env.workspace =(CombiMMGDB)
    csv = arcpy.TableToTable_conversion(combi,temporales,combi[4:]+".dbf")
    arcpy.env.workspace =(temporales)

    #Pasamos los DBF a EXCEL"
    arcpy.TableToExcel_conversion(os.path.join(temporales,combi[4:]+".dbf"),combi[4:]+".xls")
    rutaxls = os.path.join(temporales,combi[4:]+".xls")
    data = pd.read_excel(rutaxls,combi[4:])
    data.head()

    #Eliminamos columnas innecesarias"
    data = data.drop(['OID','Value'],axis=1)

    #Ordenamos por clases de la variable"
    data.sort(data.columns[2], inplace=True)

    #Asociamos los valores de reclasificación"
    print("Columna del DF: "+ data.columns[2][3:])
    rangosDF= []
    data["Rangos de Clas."] = ""
    for rango in RangosDeClasificacion:
        print("Evaluare Rangos de : "+ str(rango[:7]))
        if str(rango[:7]).lower() == str(data.columns[2][3:]).lower() and RangosDeClasificacion[rango][2] == 'Raster inicialmente continuo: si':
            print("Cumple Rangos de : "+ str(rango))
            rangosDF.append(RangosDeClasificacion[rango][0])
            for i in range(len(rangosDF[0])):
                data.loc[data[data.columns[2]] == rangosDF[0][i][2],"Rangos de Clas."] = ("("+str(rangosDF[0][i][0])+','+str(rangosDF[0][i][1])+")")

    #Calculo de A1 (Pxls con MM en la clase)
    data["A1"] = ""
    # Asigna valor de count a las filas donde la columna MenM es 1
    data.loc[data[data.columns[1]] == 1,"A1"] = data[data.columns[0]]

    #Calculo de A3 (Pxls sin MM en la clase)
    data["A3"] = ""
    # Asigna valor de count a las filas donde la columna MenM es 0
    data.loc[data[data.columns[1]] == 0,"A3"] = data[data.columns[0]]

    data = data.reset_index(drop = True)
    indicesMM = []
    indicesMM = data.index[data[data.columns[1]] == 1].tolist()

    indicesSinMM = []
    indicesSinMM = data.index[data[data.columns[1]] == 0].tolist()

    #Recorremos la lista de indices sinMM:
    for indiceMM in indicesMM:
        clase = data.get_value(indiceMM,data.columns[2])
        for indiceSinMM in indicesSinMM:
            if data.get_value(indiceSinMM,data.columns[2]) == clase:
                A3 = data.get_value(indiceSinMM,'A3')
        data.iloc[indiceMM, data.columns.get_loc('A3')] = A3

    data = data.sort([data.columns[2],data.columns[4]]).drop_duplicates(data.columns[2])
        #Eliminamos columnas innecesarias"
    data = data.drop(['Count',data.columns[1]],axis=1)
    for indiceMM in indicesMM:
        if pd.isnull(data.loc[indiceMM,'A3']) == True:
            tkMessageBox.showerror(title="Reclasificar!", message="Para continuar por favor modifique los rangos de clasificacion de la variable: "+combi[4:])
            sys.exit()

    #Calculo de A2 (Pxls con MM que no pertenecen a la clase)
    data["A2"] = ""
    data['A1'] = data['A1'].replace('', 0)
    data['A1'] = data['A1'].astype(float)
    TotalA1 = data['A1'].sum()
    data["A2"] = TotalA1 - data["A1"]
    #Calculo de A4 (Pxls sin MM que no pertenecen a la clase)
    data["A4"] = ""
    TotalA3 = data['A3'].sum()
    data["A4"] = TotalA3 - data["A3"]

    #Reordenar las columnas de la tabla data:
    data = data[[data.columns[0],data.columns[1],"A1","A2","A3","A4"]]

    #Cálculo de pesos positivos W+

    data["W1"] = ""
    data["W1"] = data['A1']/(data['A1']+data['A2'])
    data["W2"] = ""
    data["W2"] = data['A3']/(data['A3']+data['A4'])
    data["W1/W2"] = ((data["W1"]/data["W2"])).astype(float)

    data["W+"] = ""
    data["W+"] = np.where(data['W1/W2']==0, 0, np.log(data["W1/W2"]))
    del data["W1/W2"]
    del data["W1"]
    del data["W2"]

    #Cálculo de pesos negativos W-

    data["W3"] = ""
    data["W3"] = data['A2']/(data['A1']+data['A2'])
    data["W4"] = ""
    data["W4"] = data['A4']/(data['A3']+data['A4'])
    data["W3/W4"] = ((data["W3"]/data["W4"])).astype(float)

    data["W-"] = ""
    data["W-"] = np.where(data['W3/W4']==0, "ERROR", np.log(data["W3/W4"]))
    del data["W3/W4"]
    del data["W3"]
    del data["W4"]

    #Cálculo del Peso de Contraste (C)
    data["C"] = ""
    data["C"] = data["W+"].astype(float) - data["W-"].astype(float)
    contrasteslist = data["C"].tolist()
#Desplegar una ventana con la tabla de pesos para la variable
#Fuente: https://www.youtube.com/watch?v=PgLjwl6Br0k&ab_channel=RamonWilliams
#           https://gist.github.com/RamonWill/0686bd8c793e2e755761a8f20a42c762

#METER UN FRAME CON CONVENCIONES DE LAS COLUMNAS

    root = tk.Tk()
##    root = tk.Toplevel()

    root.title("TABLAS DE WOE PARA LAS VARIABLES ANALIZADAS")
    root.geometry("1500x730") # set the root dimensions
    root.pack_propagate(False) # tells the root to not let the widgets inside it determine its size.
    root.resizable(0, 0) # makes the root window fixed in size.
    root.option_add( "*font", "Corbel 10" )
    #####

    ####

    # Frame for Table
    frame1 = tk.LabelFrame(root, text= VariablesEntrada[var])
    frame1.place(height=300, width=1480, rely=0.005, relx=0.005)


    # Frame for Insert variables
    file_frame = tk.LabelFrame(root, text=u'Binarización de las clases')
    file_frame.place(height=80, width=1480, rely=0.42, relx=0.005)

    # Frame for Descripción de Columnas
    details_frame = tk.LabelFrame(root, text=u'Descripción de Columnas')
    details_frame.place(height=330, width=1480, rely=0.54, relx=0.005)
    #To load an image:
    image_filename = os.path.join(rutacodigo, "Descripcion_Desarrollo.png")
    # create the PIL image object:
    my_pic = PIL.Image.open(image_filename)
##    load = PIL.Image.open(image_filename)
    resized = my_pic.resize((480,1000), PIL.Image.ANTIALIAS)
    new_pic = PIL.ImageTk.PhotoImage(my_pic)
    #Then associate it with the label:
    img = Label(details_frame, image=new_pic)
    img.image = new_pic
    img.place(rely=0, relx=0.18)

    # Buttons
    button1 = tk.Button(file_frame, text="Pasar la variable", command=lambda: ReclassBinarias(LimiteContraste))
    button1.place(rely=0.45, relx=0.50)

    button2 = tk.Button(file_frame, text="Asignar valor", command=lambda: myClick())
    button2.place(rely=0.45, relx=0.30)
    #Limite de peso de contraste:
    contraste_entry = tk.Entry(file_frame,width=8, font=('Helvetica',12), textvariable='0')
    contraste_entry.insert(END, '0')
    contraste_entry.place(rely=0, relx=0.14)
    # Label que explica el contraste
    label_file = ttk.Label(file_frame, text="Indique el limite de peso de contraste:")
    label_file.place(rely=0, relx=0)
    label_file2 = ttk.Label(file_frame, text="(Si no es asignado ningun valor en la caja de texto el valor por defecto asignado será 'cero')")
    label_file2.place(rely=0, relx=0.2)
    ## Treeview Widget
    tv1 = ttk.Treeview(frame1)
    tv1.place(relheight=1, relwidth=1) # set the height and width of the widget to 100% of its container (frame1).

    treescrolly = tk.Scrollbar(frame1, orient="vertical", command=tv1.yview) # command means update the yaxis view of the widget
    treescrollx = tk.Scrollbar(frame1, orient="horizontal", command=tv1.xview) # command means update the xaxis view of the widget
    tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set) # assign the scrollbars to the Treeview Widget
    treescrollx.pack(side="bottom", fill="x") # make the scrollbar fill the x axis of the Treeview widget
    treescrolly.pack(side="right", fill="y") # make the scrollbar fill the y axis of the Treeview widget

    #Intentaré modificar el Cod. original:
    #Aquí va a cargar el DF en la ventana automaticamente:
    tv1["column"] = list(data.columns)
    tv1["show"] = "headings"
    for column in tv1["columns"]:
        tv1.heading(column, text=column) # let the column heading = column name

    data_rows = data.values.tolist() # turns the dataframe into a list of lists
    for row in data_rows:
        tv1.insert("", "end", values=row) # inserts each list into the treeview. For parameters see https://docs.python.org/3/library/tkinter.ttk.html#tkinter.ttk.Treeview.insert

    tk.mainloop()

    # Pesos de contraste para reclasificar la variable:
    contrasteslist = data["C"].tolist()
    for i in range(len( RangosDeClasificacion[VariablesEntrada[var]][0])):
        RangosDeClasificacion[VariablesEntrada[var]][0][i][2] = contrasteslist[i]
    data.to_excel(os.path.join(tablas,'WOE_'+VariablesEntrada[var]+'.xls'),sheet_name=VariablesEntrada[var], index = False)
    #añadimos los valores de C a los rangos de clasificación de las clases
    var += 1
##############################################################################################################

#C3. Subimos los binarios a la GDB:

temporalfiles = os.listdir(temporales)
for file in temporalfiles:
    if file.endswith('.xls') or file.endswith('.dbf'):
        shutil.move(os.path.join(temporales,file), os.path.join(tablas,file))

arcpy.env.workspace =(temporales)
Binarias_List = arcpy.ListRasters()
BinariasGDB = ListaenGDB(rutaGDBs,Binarias_List,"Binarias")
arcpy.env.workspace =(BinariasGDB)
VariablesBinarias = arcpy.ListRasters()
##DeleteFilesInFolder(temporales)
#-------------------------------TEST DE INDEPENDENCIA X2: -----------------------------------------

#D. TEST DE INDEPENDENCIA X2: Este método se aplica utilizando una tabla de contingencia r x c. Donde r: filas según cierto criterio de clasificación y
# c: columnas para otro criterio de clasificación. Para aplicar un test de idenpendencia se construye una matriz, bajo la consideración de que
# los dos criterios de clasificación comparados son totalmente independientes entre si. Posteriormente, las frecueencias esperadas y las frecuencias
# observadas serán comparadas entre sí lo cual permitirá determinar los grados de libertad y el valor crítico de X2. Por tanto el valor de X2 resultante
# se podrá considerar como un estadístico con un buen criterio de bondad de ajuste.
#-------------------------------------------------------------------------------------------

# D1. Posibles combinatorias con las binarias disponibles https://www.geeksforgeeks.org/permutation-and-combination-in-python/
# Get all combinations of BINARIAS and length 2 elements:
comb = combinations(VariablesBinarias, 2)
arcpy.env.workspace =(temporales)
index = 0
dicCHI2 = {}
lisCHI2 = []
# Print the obtained combinations
for i in list(comb):
    extra = {}
    lisextra = []
    print(i)
    tablacontigenciaE = pd.DataFrame()
    tablacontigenciaO = pd.DataFrame()
    CombINDEP = 'INDEP'+str(index)+'.tif'
    combine = []
    combine.append(i[0])
    combine.append(i[1])
    combine.append(MMurl)
    print (combine)
    combinacion = Combine(combine)
    combinacion.save(os.path.join(temporales,CombINDEP))


    csvCOMBI = arcpy.TableToTable_conversion(CombINDEP,temporales,'Indep_'+combine[0][4:8]+'_'+combine[1][4:8]+".dbf")
    arcpy.TableToExcel_conversion(os.path.join(temporales,'Indep_'+combine[0][4:8]+'_'+combine[1][4:8]+".dbf"),'Indep_'+combine[0][4:8]+'_'+combine[1][4:8]+".xls")
    rutaxls = os.path.join(temporales,'Indep_'+combine[0][4:8]+'_'+combine[1][4:8]+".xls")
    fobser = pd.read_excel(rutaxls,'Indep_'+combine[0][4:8]+'_'+combine[1][4:8])
    fobser.head()
    fRESPALDO = pd.DataFrame()
    fRESPALDO = fobser

    #Vamos a configurar los campos de la tabla de contingencia de frecuencias observadas:
    fobser = fobser.drop([fobser.columns[0],fobser.columns[1]],axis=1)

        #Eliminamos entradas de ausencia de movimientos en masa
    fobser = fobser.drop(fobser[(fobser[fobser.columns[3]] == 0)].index)
        #Tabla de contingencia de frecuencia observada
    if tablacontigenciaO.empty:
        tablacontigenciaO = pd.crosstab(fobser[fobser.columns[1]],fobser[fobser.columns[2]], margins = True,aggfunc='sum',values = fobser[fobser.columns[0]])
        #Tabla de contingencia de frecuencia esperada
        tablacontigenciaE = tablacontigenciaO.copy()
        tablacontigenciaE[0][0] = tablacontigenciaO['All'][0]*tablacontigenciaO[0]['All']/tablacontigenciaO['All']['All']
        tablacontigenciaE[1][0] = tablacontigenciaO['All'][0]*tablacontigenciaO[1]['All']/tablacontigenciaO['All']['All']
        tablacontigenciaE[0][1] = tablacontigenciaO['All'][1]*tablacontigenciaO[0]['All']/tablacontigenciaO['All']['All']
        tablacontigenciaE[1][1] = tablacontigenciaO['All'][1]*tablacontigenciaO[1]['All']/tablacontigenciaO['All']['All']
        OE00 = ((tablacontigenciaO[0][0] - tablacontigenciaE[0][0])**2)/tablacontigenciaO[0][0]
        OE01 = ((tablacontigenciaO[0][1] - tablacontigenciaE[0][1])**2)/tablacontigenciaO[0][1]
        OE10 = ((tablacontigenciaO[1][0] - tablacontigenciaE[1][0])**2)/tablacontigenciaO[1][0]
        OE11 = ((tablacontigenciaO[1][1] - tablacontigenciaE[1][1])**2)/tablacontigenciaO[1][1]
        CHI2 = OE00 + OE01 + OE10 + OE11
        lisextra = [i[0][4:],i[1][4:],CHI2]
        lisCHI2.append(lisextra)
    index += 1

## TABLA DE CONTINGENCIA DE INDEPENDENCIA CONDICIONAL
del CombINDEP
del combinacion
v1 = []
v2 = []
values = []

for par in lisCHI2:
    print(par)
    v1.append(par[0])
    v2.append(par[1])
    values.append(par[2])

for i in range(len(v1)):
    print v1[i]
    if v1[i] not in v2:
        v2.append(v1[i])

for i in range(len(v2)):
    print v2[i]
    if v2[i] not in v1:
        v1.append(v2[i])
        values.append('0')



antecontingencia = pd.DataFrame(list(zip(values,v1,v2)), columns =['chi2','v1','v2'])

contigencia = pd.crosstab(antecontingencia['v1'],antecontingencia['v2'],aggfunc = 'sum', values = antecontingencia['chi2'])
contigencia = contigencia.fillna(0)
contigencia_reset = contigencia.reset_index()
#Desplegar una ventana con la tabla de independencia condicional para escoger las variables
#Fuente: https://www.youtube.com/watch?v=PgLjwl6Br0k&ab_channel=RamonWilliams
#           https://gist.github.com/RamonWill/0686bd8c793e2e755761a8f20a42c762

######################## VENTANA DE TABLA DE CONTINGENCIA #############################################################

root = tk.Tk()
##    root = tk.Toplevel()
global label_Var
global list_independendientes
global RangosDeClasificacion
global VariablesEntrada
list_independendientes = []

root.title("TABLA DE CONTINGENCIA DE INDEPENDECIA CONDICIONAL")
root.geometry("1500x730") # set the root dimensions
root.pack_propagate(False) # tells the root to not let the widgets inside it determine its size.
root.resizable(0, 0) # makes the root window fixed in size.
root.option_add( "*font", "Corbel 10" )
#####

####

# Frame for Table
frame1 = tk.LabelFrame(root, text= ' Tabla de contingencia ')
frame1.place(height=300, width=800, rely=0.005, relx=0.005)


# Frame for Insert variables
file_frame = tk.LabelFrame(root, text=u' Selección de las variables independientes ')
file_frame.place(height=80, width=1480, rely=0.42, relx=0.005)

# Frame for Descripción de Columnas
variables_frame = tk.LabelFrame(root, text=u' Variables incluidas en el análisis ')
variables_frame.place(height=300, width=1480-810, rely=0.005, relx=0.545)


## Treeview Widget
tv1 = ttk.Treeview(frame1)
tv1.place(relheight=1, relwidth=1) # set the height and width of the widget to 100% of its container (frame1).

treescrolly = tk.Scrollbar(frame1, orient="vertical", command=tv1.yview) # command means update the yaxis view of the widget
treescrollx = tk.Scrollbar(frame1, orient="horizontal", command=tv1.xview) # command means update the xaxis view of the widget
tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set) # assign the scrollbars to the Treeview Widget
treescrollx.pack(side="bottom", fill="x") # make the scrollbar fill the x axis of the Treeview widget
treescrolly.pack(side="right", fill="y") # make the scrollbar fill the y axis of the Treeview widget

#Intentaré modificar el Cod. original:
#Aquí va a cargar el DF en la ventana automaticamente:
tv1["column"] = list(contigencia_reset.columns)
tv1["show"] = "headings"
for column in tv1["columns"]:
    tv1.heading(column, text=column) # let the column heading = column name

data_rows = contigencia_reset.values.tolist() # turns the dataframe into a list of lists
for row in data_rows:
    tv1.insert("", "end", values=row) # inserts each list into the treeview. For parameters see https://docs.python.org/3/library/tkinter.ttk.html#tkinter.ttk.Treeview.insert

####      LIST BOX #######################

variables_list = Listbox(variables_frame)
##variables_Check = Checkbutton(variables_frame)
variables_list.place(rely=0.05, relx=0.35, height=250, width=100)
##variables_Check.pack(pady = 15)
# Add items to listbox
for key, value in RangosDeClasificacion.items():
    variables_list.insert(0,key)
treescrolly = tk.Scrollbar(variables_list, orient="vertical", command=variables_list.yview) # command means update the yaxis view of the widget
treescrollx = tk.Scrollbar(variables_list, orient="horizontal", command=variables_list.xview) # command means update the xaxis view of the widget
variables_list.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set) # assign the scrollbars to the Treeview Widget
treescrollx.pack(side="bottom", fill="x") # make the scrollbar fill the x axis of the Treeview widget
treescrolly.pack(side="right", fill="y") # make the scrollbar fill the y axis of the Treeview widget
############################################

# Buttons
button1 = tk.Button(variables_frame, text=" Añadir a selección ", command= select)
button1.place(rely=0.1, relx=0.08, width=145)

button2 = tk.Button(variables_frame, text=" Borrar la selección ", command= delete)
button2.place(rely=0.1+0.3, relx=0.08, width=145)

button3 = tk.Button(variables_frame, text=" Calcular Susceptibilidad ", command= susceptibilidad)
button3.place(rely=0.1+0.6, relx=0.08, width=145)

# Label que indica variables escogidas:

label_Var = Label(file_frame, text= 'La susceptibilidad se calculará usando las \n siguientes variables independientes: \n')
label_Var.place(height=50, width=1400, rely=0, relx=0)

tk.mainloop()
DeleteFilesInFolder(temporales)
contigencia.to_excel(os.path.join(tablas,'TABLA_PESOS_INDEPENDENCIA'+'.xls'),sheet_name='TABLA DE INDEPENDENCIA ', index = True)
#######################################################################################################################################################
################################# MAPA DE SUSCEPTIBILIDAD ###############################################
##############################################################################################################
