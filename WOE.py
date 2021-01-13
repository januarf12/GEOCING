# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        CÁLCULO DE SUSCEPTIBILIDAD ANTE MM A TRAVÉS DEL MÉTODO WOE
# Purpose:
#
# Author:      Ing. Felipe Riaño
#
# Created:     28/12/2020
# Copyright:   (c) ingenieria2b 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# -----------------------Importación de modulos---------------------------------
# -*- coding: utf-8 -*-
import arcpy
import os
import shutil
import glob
from arcpy import env
from arcpy.sa import *
import numpy
import pandas as pd
import sys
import tkMessageBox
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = 1
numpy.version.full_version

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
#-------------------------------Pruebas-----------------------------------------
# A. Lectura de las Variables de entrada:
rutabuena = raw_input(u'Indique la ruta de almacenamiento de las variables de entrada al modelo: ')
arcpy.env.workspace =(rutabuena)
# Get and print a list of Rasters from the workspace
VariablesEntrada = arcpy.ListRasters()

# A1. Fijación de la ruta de almacenamiento de resultados:
rutaGDBs = raw_input(u'Indique la ruta de almacenamiento de las GDB a generar: ')

#A2. GDB con Variables de entrada:
VariablesEntradaGDB = ListaenGDB(rutaGDBs,VariablesEntrada,"Entradas")

#-------------------------------Reclasificar-----------------------------------------

# B1. Condiciones para Clasificación de Raster Continuos:
Reclasificados = []
Workspace(VariablesEntradaGDB)
VariablesEntrada = arcpy.ListRasters()
RangosDeClasificacion={}

#B2. Creación de la carpeta para temporales
temporales = os.path.join(rutaGDBs, "Resultados_Temporales")
if not os.path.exists(temporales):
    os.mkdir(temporales)
    print("Directory " , temporales ,  " Created ")
else:
    print("Directory " , temporales ,  " already exists")
#-------------------------------------------------------------------------------------
#B3. Reclasificación de los Rasters:
arcpy.CheckOutExtension("Spatial")
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
        ReclasificadoRaster = ("re_"+x)
        MyRemapRange = RemapRange(ReMapRangeVar)
        arcpy.Reclassify_3d(x, "VALUE", str(MyRemapRange), temporales + "\\" +ReclasificadoRaster, "DATA")
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
#------------------------------------------------------------------------------------------------------
#B5. Subimos los reclasificados a la GDB y borramos de temporal:
arcpy.env.workspace =(temporales)
Reclass_List = arcpy.ListRasters()
ReclassGDB = ListaenGDB(rutaGDBs,Reclass_List,"Reclass")
arcpy.env.workspace =(ReclassGDB)
VariablesReclasificadas = arcpy.ListRasters()
DeleteFilesInFolder(temporales)

#-------------------------------Combinatorias con MM-----------------------------------------

#C. Ejecución de combinatorias por variable con MM:

#C1. Llamamos raster de MM
MMurl = raw_input(u'Indique la ruta del raster de MM: \n(1- Presencia/ 0- No Presencia) ')
#-------------------------------------------------------------------------------------------
# Combinatorias multiples:
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

#-------------------------------Manejo de Tablas-----------------------------------------
arcpy.env.workspace =(CombiMMGDB)
combinatoriasMM = arcpy.ListRasters()
TablasCombinatoria = {}

for combi in combinatoriasMM:
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
    data["Rangos"] = ""
    for rango in RangosDeClasificacion:
        print("Evaluare Rangos de : "+ str(rango[:7]))
        if str(rango[:7]).lower() == str(data.columns[2][3:]).lower() and RangosDeClasificacion[rango][2] == 'Raster inicialmente continuo: si':
            print("Cumple Rangos de : "+ str(rango))
            rangosDF.append(RangosDeClasificacion[rango][0])
            for i in range(len(rangosDF[0])):
                data.loc[data[data.columns[2]] == rangosDF[0][i][2],"Rangos"] = (str(rangosDF[0][i][0])+'-'+str(rangosDF[0][i][1]))

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
    data = data.drop(['Count','MenM'],axis=1)
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

    data2 = data.sort_index(inplace = True, axis = 1) #https://stackoverflow.com/questions/54786139/pandas-df-sort-on-index-but-exclude-first-column-from-sort




    #Añadimos el DF resultante a un diccionario que acumula todas"
    ListTablaCombi.append(data)
    TablasCombinatoria[combi] = ListTablaCombi


