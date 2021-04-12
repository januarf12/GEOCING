#!interpreter [optional-arg]
# -*- coding: utf-8 -*-

"""
{Description: 
 El cálculo de umbrales de lluvia empíricos para la implementanción en la zonificación de la amenaza
 ante Deslizamientos.
 
 Versión: 0.1
 5/04/2021
 
 Instrucciones:
     - Todas las lineas están comentariadas con su respectiva explicación
     - Las lineas comentariadas con un ¡MOD! al inicio, SON LINEAS PARA MODIFICAR!!!
 
 
 Insumos:
     - Datos de intensidad de precipitación diaria puntuales tomados por estaciones en tierra. (IDEAM,2021)
         Formato: CSV
     - Base de datos de deslizamientos (ID, dia del evento, mes del evento, año del evento, Fecha del evento, Localización, Estación IDEAM asociada)
         Formato: CSV
     
 Salidas:
    - Dataframe de todos los eventos de deslizamiento con condiciones de precipitación asignadas (LA0,...,LAA90)
         Formato: CSV
    - Gráficas de eventos de precipitación (LA vs LAA) (?)
    - Ecuación para umbral crítico de lluvia (LA vs LAA) (?)

 PENDIENTE:
     - Modelo de probabilidad ajustado !!!!!!!!!!!!!!

                                                                                        afrianoq@unal.edu.co
 }
{License_info}
"""
###########################################################################################################################################################
"""
    1. Importación de Librerias
"""
#Use to import pandas
import pandas as pd
import datetime
import numpy as np
# Import the os module
import os

###########################################################################################################################################################


###########################################################################################################################################################
"""
    2. Construcción de dataframes: 
        - Datos de precipitación (mm/dia) por estación y por fecha. NOMBRE DE LA VARIABLE: "db_precipitacion"
        - Datos de eventos de deslizamientos con fecha y estación asignada para joins. NOMBRE DE LA VARIABLE: "db_desliz"
"""
# ¡MOD!:
#   Asignar un directorio de trabajo (Siempre poner la ruta con doble slash: "\\")
os.chdir('D:\\FR_GEOCING\\455-AVR CAUCA\\Amenaza\\Lluvia\\Pruebas_Codigo_Umbrales')

####################################################### DATABASE DESLIZAMIENTOS ###############################################################################

#   Importar database de deslizamientos 
db_desliz = pd.read_csv("Entradas\\Deslizamientos.csv")# ¡MOD!: ingrese la ruta del csv correspondiente
print(db_desliz.head())

#   Se asignan los encabezados del DF de deslizamientos a utilizar como variables:
id_desliz = "FID"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.
id_estacionD = "CODIGO"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.
dia_desliz = "D"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.
mes_desliz = "M"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.
anio_desliz = "A"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.
fecha_desliz = "D_M_A"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.
este_desliz = "ESTE"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.
norte_desliz = "NORTE"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.

#   Se eliminan columnas del DF de deslizamientos innecesarias:
db_desliz = db_desliz[[id_desliz,id_estacionD,dia_desliz,mes_desliz,anio_desliz,fecha_desliz,este_desliz,norte_desliz]]
db_desliz[fecha_desliz] = pd.to_datetime(db_desliz[fecha_desliz], format="%d/%m/%Y") #Convertimos a tipo fecha la columna FECHA

############################################################ DATABASE PRECIPITACION ##########################################################################

#   Importar database de precipitación  
db_precipitacion = pd.read_csv("Entradas\\Estaciones_compiladoF.csv")# ¡MOD!: ingrese la ruta del csv correspondiente
print(db_precipitacion.head())

#   Se asignan los encabezados del DF de precipitación a utilizar como variables:
id_estacionP = "CodigoEstacion"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.
estacion = "NombreEstacion"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.
dia_preci = "D"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.
mes_preci = "M"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.
anio_preci = "A"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.
fecha_preci = "Fecha"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.
este_preci = "Longitud"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.
norte_preci = "Latitud"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.
precip = "Valor"  #¡MOD!: Digite el nombre de la columna relacionada en su DF.

#   Se eliminan columnas del DF de precipitacion innecesarias:
db_precipitacion = db_precipitacion[[id_estacionP,estacion,dia_preci,mes_preci,anio_preci,fecha_preci,este_preci,norte_preci,precip]]
db_precipitacion[fecha_preci] = pd.to_datetime(db_precipitacion[fecha_preci], format="%d/%m/%Y") #Convertimos a tipo fecha la columna FECHA

# Se acota el rango temporal de datos de precipitación al rango temporal de deslizamientos:(fechaprimerdesliz,fechaultimodesliz)
fechaprimerdesliz = min(db_desliz[fecha_desliz])
freq = 'D'                                                                                  # 'H' for hours, etc.
fechaprimerdesliz_95 = fechaprimerdesliz + pd.Timedelta(-95, unit=freq)                       # Perform the action

fechaultimodesliz = max(db_desliz[fecha_desliz])

db_precipitacion = db_precipitacion[db_precipitacion[fecha_preci].between(fechaprimerdesliz_95, fechaultimodesliz, inclusive=False)]

db_precipitacion = db_precipitacion[~db_precipitacion.duplicated()] #Se van a eliminar filas duplicadas del registro total de lluvias
print (db_precipitacion)
####################################################### DATABASE LLUVIA 95 DIAS ############################################################################
"""
    3. Construcción dataframe lluvia 95 días: 
        - Datos de precipitación (mm/dia) por estación y por fecha y sus 95 dias anteriores. NOMBRE DE LA VARIABLE: "db_lluvia95"
        - Se calcula para todas las estaciones en el rango temporal de los deslizamientos reportados valores de lluvia antecedente para 95 dias anteriores a la fecha.
        - Cuando no existe dato de precip. para la fecha se completa la entrada con un "ND"
        - Se crea un campo que relaciona la cantidad de datos ausentes (o proporción?) para cada fecha.
        - Se relaciona la detonación de un deslizamiento en el área de influencia
        - Base de datos de lluvia 95 días (ID estacion, dia del evento, mes del evento, año del evento, Fecha del evento, Evento de deslizamiento, L0 ... L95)
            Formato: CSV
"""
db_lluvia95 = pd.DataFrame(columns=['ID_ESTACION','ESTACION', 'D', 'M','A','FECHA','DESLIZ']) # Creamos las columnas del DF
for i in range(1,96):
    db_lluvia95["L"+str(i)] = ""
    i += 1
db_lluvia95['Proporcion_ausentes'] = np.nan #Creamos la columna de datos ausentes

estaciones = db_precipitacion[id_estacionP].unique() #Creamos un numpy.ndarray con los codigos de las estaciones

index_db_lluvia95 = 0 #Iterador de filas en la base de datos final de lluvias 95, recorro las filas desde la 0

#Empieza el iterador por estaciones
for estacion in estaciones:
 
    df_estacion = db_precipitacion[db_precipitacion[id_estacionP] == estacion] #Creamos un df de solo la estacion evaluada 
            #Vamos a tomar datos a partir del 95 de registros
    fechaprimerlluvia = min(df_estacion[fecha_preci])
    fechaprimerlluviamas95 = fechaprimerlluvia + pd.Timedelta(+95, unit=freq)
    fechaultimalluvia = max(df_estacion[fecha_preci])
    df_estacion = df_estacion[df_estacion[fecha_preci].between(fechaprimerlluviamas95, fechaultimalluvia, inclusive=False)]
    
    
    df_estacion.sort_values(by=[fecha_preci]) #Ordenamos los registros de esta estación del más antiguo al último tomado
    
    df_estacion.reset_index(drop=True) #Reasignamos indices al dataframe de la estación
        
    for index, row in df_estacion.iterrows(): #Iteramos sobre cada fila del dataframe construido para la estación

        
        db_lluvia95.at[index_db_lluvia95, db_lluvia95.columns[0]] = df_estacion.loc[index, df_estacion.columns[0]] #Asignamos a la tabla de lluvia el ID de la estacion
        db_lluvia95.at[index_db_lluvia95, db_lluvia95.columns[1]] = df_estacion.loc[index, df_estacion.columns[1]] #Asignamos a la tabla de lluvia el nombre de la estacion       
        db_lluvia95.at[index_db_lluvia95, db_lluvia95.columns[2]] = df_estacion.loc[index, df_estacion.columns[2]] #Asignamos a la tabla de lluvia el dia de lluvia       
        db_lluvia95.at[index_db_lluvia95, db_lluvia95.columns[3]] = df_estacion.loc[index, df_estacion.columns[3]] #Asignamos a la tabla de lluvia el mes de lluvia       
        db_lluvia95.at[index_db_lluvia95, db_lluvia95.columns[4]] = df_estacion.loc[index, df_estacion.columns[4]] #Asignamos a la tabla de lluvia el año de lluvia       
        db_lluvia95.at[index_db_lluvia95, db_lluvia95.columns[5]] = df_estacion.loc[index, df_estacion.columns[5]] #Asignamos a la tabla de lluvia la fecha de lluvia
        
        # en la columna 'desliz' va: 1 si hubo desliz ese día y 0 si no hubo desliz
        db_desliz_temp = db_desliz[db_desliz[id_estacionD] == estacion ] #Creamos una db de deslizamientos con influencia en la estacion
        fecha_evento = str(row[fecha_preci].date())
        exist_desliz = db_desliz_temp.isin([datetime.datetime.strptime(fecha_evento,'%Y-%m-%d')]).any().any() #Buscamos si exsite la fecha en el df temporal
        if exist_desliz == True: #Si la fecha existe
            db_lluvia95.at[index_db_lluvia95, db_lluvia95.columns[6]] = 1 #Asignamos el evento de lluvia a un evento de desliz
        else:                    #Si la fecha no existe
            db_lluvia95.at[index_db_lluvia95, db_lluvia95.columns[6]] = 0  #Asignamos el evento de lluvia a un no evento de desliz
        
        db_lluvia95.at[index_db_lluvia95, db_lluvia95.columns[7]] = df_estacion.loc[index, df_estacion.columns[8]] #Asignamos L1
        
        # Empezamos a calcular los valores de lluvia antecedente hasta 95 dias
        encabe_lluvia95 = list(db_lluvia95)
        dias_menos = -1 #Variable de cambio según numero de días a la fecha evaluada
        for i in encabe_lluvia95[8:]:

            dia_evaluacion = row[fecha_preci] + pd.Timedelta(dias_menos, unit = freq)
            preci_dia_evaluacion_serie = db_precipitacion.loc[((db_precipitacion[id_estacionP] == estacion) & (db_precipitacion[fecha_preci] == dia_evaluacion)), precip]
            if preci_dia_evaluacion_serie.empty is True:
                db_lluvia95[i][index_db_lluvia95] = 'ND' 
            else:
                preci_dia_evaluacion = db_precipitacion.loc[((db_precipitacion[id_estacionP] == estacion) & (db_precipitacion[fecha_preci] == dia_evaluacion)), precip].values[0]
                db_lluvia95[i][index_db_lluvia95] = preci_dia_evaluacion
            # print (db_lluvia95[i][index]) # corresponde a los valores de precipitación antecedente para la entrada en particular
            dias_menos -= 1        
               
        print(row[id_estacionP]," / ", row[fecha_preci].date()," / ", row[precip]," / ",str(db_lluvia95.at[index_db_lluvia95, db_lluvia95.columns[6]])," / ",str(db_lluvia95.at[index_db_lluvia95, db_lluvia95.columns[7]]))
        index_db_lluvia95 += 1 #Avanzamos una fila en el DF de lluvia95   
        

        # db_lluvia95['Proporcion_ausentes'][index_db_lluvia95] = ausencia_proporcion
        #Contamos la proporción de datos de lluvia antecedente faltante por fila

ausencia_numero = (db_lluvia95 == 'ND').sum(axis='columns')
ausencia_proporcion = (ausencia_numero*100)/95
db_lluvia95['Proporcion_ausentes'] = ausencia_proporcion
db_lluvia95.to_csv('db_lluvia95.csv', header=True, index=False) #Extraer la tabla de lluvia antecedente como un csv
df_estacion.to_csv('aguada.csv', header=True, index=False) #Extraer la tabla de lluvia antecedente como un csv













