from django.shortcuts import render
import glob
import os
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from datetime import date
# Create your views here.


def home(request):
    return render(request,'exchange\index.html')


def traitement(request):

    if request.method == 'POST':

        divisions = {
        "division": [2000, 2010, 2020,2030, 2110, 2200, 2300, 2400, 2500, 2600],
        }
        df = pd.DataFrame(divisions)
        #get files with last modification
        directory_t001=glob.glob(r"\\centaure\Extract_SAP\SE16N-T001\*")
        t001_file= max(directory_t001,key=os.path.getmtime)

        directory_t001k=glob.glob(r"\\centaure\Extract_SAP\SE16N-T001K\*")
        t001k_file= max(directory_t001k,key=os.path.getmtime)

        directory_tcurr=glob.glob(r"\\centaure\Extract_SAP\SE16N-TCURR\*")
        tcurr_file=max(directory_tcurr,key=os.path.getmtime)

        df_t001=pd.read_excel(t001_file)
        df_t001k=pd.read_excel(t001k_file)
        df_tcurr=pd.read_excel(tcurr_file)

        df_t001k = df_t001k.iloc[:, [0,1]]
        df_t001k.rename(columns={'Domaine valorisation':'division','Société':'company'},  inplace = True)

        df_t001=df_t001.iloc[:, [0,4]]
        df_t001.rename(columns={'Société':'company','Devise':'currency'},  inplace = True)

        df_tcurr=df_tcurr[ ( df_tcurr['Type de cours'].isin(['M','P']) ) & (df_tcurr['Devise cible']=='EUR') ]
        # df_tcurr=df_tcurr.iloc[:, [2,3,4]]
        df_tcurr.rename(columns={'Dev. source':'target_currency','Début validité':'date','Taux':'rate'},  inplace = True)
        df_tcurr['date']=pd.to_datetime( df_tcurr['date'])


        df_tcurr=df_tcurr.sort_values(['target_currency', 'date'],ascending = [True, False])

        df_tcurr=df_tcurr.groupby(['target_currency'])['rate'].first().reset_index() 

        df_t001k_dict=dict(zip(df_t001k['division'],df_t001k['company']))
        df['company']=df['division'].map(df_t001k_dict)
        # Get currency from t001
        df_t001_dict=dict(zip(df_t001['company'],df_t001['currency']))
        df['currency']=df['company'].map(df_t001_dict)
        # Get rate  from tcurr
        df_tcurr_dict=dict(zip(df_tcurr['target_currency'],df_tcurr['rate']))
        df['rate']=df['currency'].map(df_tcurr_dict)
        df['rate'] = df['rate'].str.replace(',','.')
        df['rate'] = df['rate'].str.lstrip('/').str[0:]
        df['rate']=df['rate'].fillna(1)
        df['rate']=df['rate'].astype(float)
        
        with BytesIO() as b:
        # Use the StringIO object as the filehandle.
            writer = pd.ExcelWriter(b, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1')
            writer.save()
            # Set up the Http response.
            filename = 'exchange.xlsx'
            response = HttpResponse(
                b.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response