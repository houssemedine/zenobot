from django.shortcuts import render
from io import BytesIO
from django.http import HttpResponse
import pandas as pd
import numpy as np




def home(request):
    return render(request,'matching/index.html')




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

        table['gap_liv']=table['performed_liv'] - table['planned_liv']
        table['gap_madlog']=table['performed_madlog'] - table['planned_madlog']


        df['buffer_planned_msn']=np.where( ~(df['planned_madlog_period'] == df['planned_liv_period']),True,False)
        df['buffer_performed_msn']=np.where( ~(df['performed_madlog_period'] == df['performed_liv_period']),True,False)

        df_buffer_planned_msn=df[df['buffer_planned_msn']==True]
        df_buffer_performed_msn=df[df['buffer_performed_msn']==True]
        buffer_planned_msn=df_buffer_planned_msn.groupby("planned_madlog_period")["buffer_planned_msn"].count().reset_index()
        buffer_performed_msn=df_buffer_performed_msn.groupby("planned_madlog_period")["buffer_performed_msn"].count().reset_index()

        buffer_planned_msn_dict=dict(zip(buffer_planned_msn['planned_madlog_period'],buffer_planned_msn['buffer_planned_msn']))
        buffer_performed_msn_dict=dict(zip(buffer_performed_msn['planned_madlog_period'],buffer_performed_msn['buffer_performed_msn']))

        table['buffer_planned_msn']=table['period'].map(buffer_planned_msn_dict)
        table['buffer_performed_msn']=table['period'].map(buffer_performed_msn_dict)



        # table.to_excel(r'C:\Users\L0005082\Documents\Projets\rim\table2.xlsx')

        with BytesIO() as b:
        # Use the StringIO object as the filehandle.
            writer = pd.ExcelWriter(b, engine='xlsxwriter')
            table.to_excel(writer, sheet_name='Sheet1')
            writer.save()
            # Set up the Http response.
            filename = 'matching_wo_command.xlsx'
            response = HttpResponse(
                b.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
