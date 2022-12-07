from django.shortcuts import render
from io import BytesIO
from django.http import HttpResponse
import pandas as pd
import numpy as np
from datetime import timedelta





def home(request):
    return render(request,r'buffer\index.html')




def traitement(request):
    if request.method == 'POST':

        buffer_file=request.FILES['zpp'].temporary_file_path()
    # file= r'C:\Users\L0005082\Documents\Projets\rim\Classeur1.xlsx'
        df= pd.read_excel(buffer_file)


        df['planned_madlog_week']=df['PLANED MADLOG'].dt.week.fillna(0).astype(int)
        df['planned_madlog_year']=df['PLANED MADLOG'].dt.year.fillna(0).astype(int)
        df['planned_madlog_period']=df['planned_madlog_year'].astype(str)+df['planned_madlog_week'].astype(str)

        df['planned_liv_week']=df['PLANED LIV'].dt.week.fillna(0).astype(int)
        df['planned_liv_year']=df['PLANED LIV'].dt.year.fillna(0).astype(int)
        df['planned_liv_period']=df['planned_liv_year'].astype(str)+df['planned_liv_week'].astype(str)


        df['performed_madlog_week']=df['PERFORMED MADLOG'].dt.week.fillna(0).astype(int)
        df['performed_madlog_year']=df['PERFORMED MADLOG'].dt.year.fillna(0).astype(int)
        df['performed_madlog_period']=df['performed_madlog_year'].astype(str)+df['performed_madlog_week'].astype(str)


        df['performed_liv_week']=df['PERFORMED LIV'].dt.week.fillna(0).astype(int)
        df['performed_liv_year']=df['PERFORMED LIV'].dt.year.fillna(0).astype(int)
        df['performed_liv_period']=df['performed_liv_year'].astype(str)+df['performed_liv_week'].astype(str)

        planned_madlog=df.groupby("planned_madlog_period")["MSN"].count().reset_index()
        planned_madlog['type']='planned_madlog'
        planned_madlog['period']=planned_madlog['planned_madlog_period']
        del planned_madlog['planned_madlog_period']

        planned_liv=df.groupby("planned_liv_period")["MSN"].count().reset_index()
        planned_liv['type']='planned_liv'
        planned_liv['period']=planned_liv['planned_liv_period']
        del planned_liv['planned_liv_period']



        performed_madlog=df.groupby("performed_madlog_period")["MSN"].count().reset_index()
        performed_madlog['type']='performed_madlog'
        performed_madlog['period']=performed_madlog['performed_madlog_period']
        del performed_madlog['performed_madlog_period']



        performed_liv=df.groupby("performed_liv_period")["MSN"].count().reset_index()
        performed_liv['type']='performed_liv'
        performed_liv['period']=performed_liv['performed_liv_period']
        del performed_liv['performed_liv_period']



        frames = [planned_madlog, planned_liv,performed_madlog,performed_liv]

        concat = pd.concat(frames)

        result=concat.groupby(['period','type'])['MSN'].sum().unstack().fillna(0).stack().reset_index()


        table = pd.pivot_table(result, values=0, index=['period'],
                            columns=['type'], aggfunc=np.sum).reset_index()

        # Gap Calucluation 
        table['gap_liv']=table['performed_liv'] - table['planned_liv']
        table['gap_madlog']=table['performed_madlog'] - table['planned_madlog']


        df['buffer_planned']=np.where( ~(df['planned_madlog_period'] == df['planned_liv_period']),True,False)
        df['buffer_performed']=np.where( ~(df['performed_madlog_period'] == df['performed_liv_period']),True,False)

        df_buffer_planned=df[df['buffer_planned']==True]
        df_buffer_performed=df[df['buffer_performed']==True]
        df_buffer_performed_liv=df[~(df['performed_liv_period']  == "00" )]

        if df_buffer_planned.empty:
            df_buffer_planned['buffer_planned_day']=0
        else:
            df_buffer_planned['buffer_planned_day'] = df_buffer_planned.apply(lambda x: diff_date(x['ODD Customer'] , x['PLANED MADLOG']),axis=1)
        if df_buffer_performed.empty:
            df_buffer_performed['buffer_performed_day'] = 0
        else:
            df_buffer_performed['buffer_performed_day'] = df_buffer_performed.apply(lambda x: diff_date(x['ODD Customer'] , x['PERFORMED MADLOG']),axis=1)
        df_buffer_performed_liv['buffer_performed_liv_day'] = df_buffer_performed_liv.apply(lambda x: diff_date(x['ODD Customer'] , x['PERFORMED LIV']),axis=1)


        buffer_planned_day = df_buffer_planned.groupby("planned_madlog_period")["buffer_planned_day"].mean().round(0) .reset_index()
        buffer_performed_day = df_buffer_performed.groupby("planned_madlog_period")["buffer_performed_day"].mean().round(0) .reset_index()

        buffer_performed_liv_day = df_buffer_performed_liv.groupby("performed_liv_period")["buffer_performed_liv_day"].mean().round(0) .reset_index()
        advance_delay = df_buffer_performed_liv.groupby("performed_liv_period")["Avance/retard"].mean().round(0) .reset_index()

        buffer_planned_day_dict=dict(zip(buffer_planned_day['planned_madlog_period'],buffer_planned_day['buffer_planned_day']))
        buffer_performed_day_dict=dict(zip(buffer_performed_day['planned_madlog_period'],buffer_performed_day['buffer_performed_day']))
        buffer_performed_liv_day_dict=dict(zip(buffer_performed_liv_day['performed_liv_period'],buffer_performed_liv_day['buffer_performed_liv_day']))
        advance_delay_dict=dict(zip(advance_delay['performed_liv_period'],advance_delay['Avance/retard']))


        buffer_planned_msn=df_buffer_planned.groupby("planned_madlog_period")["buffer_planned"].count().reset_index()
        buffer_performed_msn=df_buffer_performed.groupby("performed_madlog_period")["buffer_performed"].count().reset_index()

        buffer_planned_msn_dict=dict(zip(buffer_planned_msn['planned_madlog_period'],buffer_planned_msn['buffer_planned']))
        buffer_performed_msn_dict=dict(zip(buffer_performed_msn['performed_madlog_period'],buffer_performed_msn['buffer_performed']))

        table['buffer_planned_msn']=table['period'].map(buffer_planned_msn_dict)
        table['buffer_performed_msn']=table['period'].map(buffer_performed_msn_dict)
        table['buffer_planned_day']=table['period'].map(buffer_planned_day_dict)
        table['buffer_performed_day']=table['period'].map(buffer_performed_day_dict)
        table['buffer_performed_liv_day']=table['period'].map(buffer_performed_liv_day_dict)
        table['advance_delay_odd']=table['period'].map(advance_delay_dict)

        #Cleaning
        #Rename
        table.rename ( columns={
            'performed_liv':'Nbr MSN performed LIV',
            'performed_madlog':'Nbr MSN performed MADLOG',
            'planned_liv':'Nbr MSN planned LIV',
            'planned_madlog':'Nbr MSN planned madlog',
            'buffer_planned_msn':'Buffer planned MADLOG per msn',
            'buffer_performed_msn':'Buffer performed MADLOG per msn',
            'buffer_planned_day':'Buffer planned MADLOG per day',
            'buffer_performed_day':'Buffer performed MADLOG per day',
            'buffer_performed_liv_day':'Buffer performed LIV per day',
            'advance_delay_odd':'Advance delay ODD',
            },
            inplace=True )
        #Ordring
        table=table.loc[:, ["period",
                    "Nbr MSN planned madlog",
                    "Nbr MSN performed MADLOG",
                    "gap_madlog",
                    "Nbr MSN planned LIV",
                    "Nbr MSN performed LIV",
                    "gap_liv",
                    "Buffer planned MADLOG per msn",
                    "Buffer performed MADLOG per msn",	
                    "Buffer planned MADLOG per day"	,
                    "Buffer performed MADLOG per day",
                    "Buffer performed LIV per day",
                    "Advance delay ODD",
                    ]]
        table.drop([0], axis=0, inplace=True)
        table['period'] = table['period'].apply(lambda x: str(x[:4]) + '_' + str(x[4:]))
        table=table.fillna(0)

        # df_buffer_performed.to_excel(r'C:\Users\L0005082\Documents\Projets\rim\df_buffer_performed.xlsx')

        with BytesIO() as b:
        # Use the StringIO object as the filehandle.
            writer = pd.ExcelWriter(b, engine='xlsxwriter')
            table.to_excel(writer, sheet_name='Sheet1')
            writer.save()
            # Set up the Http response.
            filename = 'buffer.xlsx'
            response = HttpResponse(
                b.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response


def diff_date(reordo,available):
    diff=0
    if pd.isnull(reordo) is None:
        diff=0
    if pd.isnull(available):
        diff=0
    else:
        if reordo < available:
            delta=available-reordo
            for i in range(delta.days):
                day = reordo + timedelta(days=i)
                if day.weekday()>4: 
                        # if a weekend or  holiday, skip
                        continue
                else:
                    # if a workday, count as a day
                    diff+= 1
        else:
            delta = reordo - available       # as timedelta
            for i in range(delta.days):
                day = available + timedelta(days=i)

                if day.weekday()>4: 
                        # if a weekend or  holiday, skip
                        continue
                else:
                    # if a workday, count as a day
                    diff+= 1


        if reordo < available:
            diff= diff*(-1)
    return diff+1