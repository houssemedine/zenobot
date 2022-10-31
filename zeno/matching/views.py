from io import BytesIO
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import numpy as np


# Create your views here.
def home(request):
    return render(request,'matching/index.html')


def traitement(request):
    if request.method == 'POST':

        zpp_file=request.FILES['zpp'].temporary_file_path()

        df=pd.read_csv( zpp_file,sep='\t', encoding='utf-16le',names=['A','Article','Date', 'D', 'Elém. MRP','Don. élém.plan.', 'MsEx', 'Entr/bes.', 'Qté disp.','Date réord','Fourn.','Client','UQ Base','Qté Unité de saisie','Unité de saisie'])

        ######################################
        #
        #Start Cleaning Data
        #
        #######################################
        df=df[~df['Article'].isna() & df['Article'].str.startswith('IS')]
        # Get Action type based on Elém. MRP 
        df['action_type']=np.where(df['Elém. MRP'].isin(['OF','ORDPLA']), 'order','')
        df['action_type']=np.where(df['Elém. MRP']=="CDECLI", 'cmd',df['action_type'])
        df['action_type']=np.where(df['Elém. MRP']=="Stock", 'a_stock',df['action_type'])
        df['action_type']=np.where(df['Elém. MRP']=="STKMAG", 'z_STKMAG',df['action_type'])
        df['action_type']=np.where(df['Elém. MRP']=="Livr.", 'Livr',df['action_type'])

        # Action date 
        df['action_date']=np.where(df['Date réord'].isna(), df['Date'], df['Date réord'])
        df['action_date']=np.where(df['action_type']=='a_stock','1.1.1990', df['action_date'])
        df['action_date']=np.where(df['action_type']=='z_STKMAG','1.1.2200', df['action_date'])

        #Convert date to standard format
        df['action_date']=pd.to_datetime(df['action_date'], format='%d.%m.%Y').dt.date

        #Convert numbers to English format

        df['Entr/bes.']=df['Entr/bes.'].astype(str).str.rsplit("000").str[0]
        df['Entr/bes.']=df['Entr/bes.'].astype(str).str.rsplit(",").str[0].astype(int)
        df['Qté disp.']=df['Qté disp.'].astype(str).str.rsplit("000").str[0]
        df['Qté disp.']=df['Qté disp.'].astype(str).str.rsplit(",").str[0].astype(int)

        #Sort Data
        df=df.sort_values(by=['Article', 'action_date','action_type'],ascending=True)

        ######################################
        #
        #End Cleaning Data
        #
        #######################################

        #Make key 
        df['key']=df['Article'].astype(str)+df['action_date'].astype(str)
        #Split table to 2 based on action type

        df_cmd=df[df['action_type'].isin(['Livr','cmd'])].reset_index()    #DataFrame for commande 
        df_order=df[df['action_type']=='order'].reset_index() #DataFrame for orders

        #Initialization varaibale 
        df_cmd['closed']=False
        df_order['cmd']=None
        df_order['date_cmd']=None
        df_order['element_type']=None
        # df_order['sum']=None

        #Loop on Orders
        for i in range(len(df_order)):
            #Loops on Cmd
            for j in range(len(df_cmd)):
                if ( (df_order.loc[i,'key']==df_cmd.loc[j,'key']) \
                        and (df_cmd.loc[j,'closed']==False) \
                        and (df_order.loc[i,'Entr/bes.'] + df_cmd.loc[j,'Entr/bes.'] == 0) #to Avoid many cmd and many orders in same day
                        ):

                    df_order.loc[i,'cmd']=df_cmd.loc[j,'Don. élém.plan.']
                    df_order.loc[i,'date_cmd']=df_cmd.loc[j,'action_date']
                    df_cmd.loc[j,'closed']=True
                    df_order.loc[i,'element_type']=df_cmd.loc[j,'Elém. MRP']


                    break    
                if ( (df_order.loc[i,'key']==df_cmd.loc[j,'key']) and (df_cmd.loc[j,'closed']==False) ):
                    
                    df_cmd.loc[j,'Entr/bes.']=df_cmd.loc[j,'Entr/bes.']+df_order.loc[i,'Entr/bes.']
                    df_order.loc[i,'cmd']=df_cmd.loc[j,'Don. élém.plan.']
                    df_order.loc[i,'date_cmd']=df_cmd.loc[j,'action_date']
                    df_order.loc[i,'element_type']=df_cmd.loc[j,'Elém. MRP']

        #refine the display of cmd : if duplicate keep one line
        # df_order['cmd'] = df_order['cmd'].mask(df_order['cmd'].ne(df_order['cmd'].shift()).cumsum().duplicated(), '')

        #Get original data 
        dict_cmd_qte=dict(zip(df['Don. élém.plan.'],df['Entr/bes.']))
        dict_cmd_date=dict(zip(df['Don. élém.plan.'],df['Date']))
        #Cleaning Table
        df_order['intial_cmd_needs']=df_order['cmd'].map(dict_cmd_qte)
        df_order['intial_cmd_date']=df_order['cmd'].map(dict_cmd_date)
        df_order['Poste Besoin']=df_order['cmd'].str.split('/').str[1]
        df_order['Poste Besoin']=df_order['Poste Besoin'].str.lstrip('0')
        df_order['Don. élém.plan.']=df_order['Don. élém.plan.'].str.split('/').str[0]
        df_order['cmd']=df_order['cmd'].str.split('/').str[0]
        df_order['Don. élém.plan.']=df_order['Don. élém.plan.'].str.lstrip('0')
        df_order['cmd']=df_order['cmd'].str.lstrip('0')

        df_order['action_date']=pd.to_datetime(df_order['action_date']).dt.strftime('%d/%m/%Y')
        df_order['date_cmd']=pd.to_datetime(df_order['date_cmd']).dt.strftime('%d/%m/%Y')

        del df_order['index']
        del df_order['A']
        del df_order['D']
        del df_order['Qté disp.']
        del df_order['Fourn.']
        del df_order['Client']
        del df_order['Qté Unité de saisie']
        del df_order['Unité de saisie']
        del df_order['key']
        del df_order['action_type']

        df=df_order.rename(columns={
            'Date'	    : 'Date Format SAP' ,
            'Elém. MRP'	: 'Elément MRP' ,
            'Don. élém.plan.' :	'Elément Planification (OP/OF)' ,
            'MsEx'	 : 'MEXEP' ,
            'Entr/bes.' : 	'Qté OF' ,
            'Date réord'	: 'Date de réordo' ,
            'UQ Base' : 	'Unité de Base' ,
            'action_date': 	'Date Elément' ,
            'cmd': 	'Besoin (Cmd / Livr / BIP …)' ,
            'date_cmd': 	'Date Besoin' ,
            'element_type': 	'Besoin Type' ,
            'intial_cmd_needs': 	'Qté Besoin' ,
            'intial_cmd_date': 	'Date Besoin format SAP' ,

            },inplace=True)
        

        with BytesIO() as b:
        # Use the StringIO object as the filehandle.
            writer = pd.ExcelWriter(b, engine='xlsxwriter')
            df_order.to_excel(writer, sheet_name='Sheet1')
            writer.save()
            # Set up the Http response.
            filename = 'matching_wo_command.xlsx'
            response = HttpResponse(
                b.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response


    