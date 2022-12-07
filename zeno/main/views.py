from io import StringIO
from django.shortcuts import render
from django.db.models import Q
import pandas as pd
import psycopg2
import time

from main.models import Element

def home(request):
    print(request.GET)
    if request.GET :
        input_search = request.GET['q']
        input_type = request.GET['cat']
        if input_search and input_type :

            start_time=time.time()
            name_conditions  = Q()
            tag_conditions  = Q()
            description_conditions  = Q()
            for tag in input_search.split():
                name_conditions |= Q(name__icontains=tag)
                tag_conditions |= Q(tag__icontains=tag)
                description_conditions |= Q(description__icontains=tag)

            elements=Element.objects.filter( (Q(type=input_type)) & ((tag_conditions) | (name_conditions) | (description_conditions))).all() # use icontains to avoid Case-insensitive
            if input_type == 'all':
                elements=Element.objects.filter(((tag_conditions) | (name_conditions) | (description_conditions))).all() # use icontains to avoid Case-insensitive
            end_time=time.time()
            count=elements.count()
            total_time=end_time - start_time
            return render(request,r'main\index.html',{'elements':elements,'total_time':total_time,'count':count,'input_search': input_search,'input_type':input_type})


    if request.method == 'POST':
        input_search=request.POST.get('input_search')
        input_type='alliq'
        start_time=time.time()

        name_conditions  = Q()
        tag_conditions  = Q()
        description_conditions  = Q()
        for tag in input_search.split():
            name_conditions |= Q(name__icontains=tag)
            tag_conditions |= Q(tag__icontains=tag)
            description_conditions |= Q(description__icontains=tag)
        elements=Element.objects.filter((tag_conditions) | (name_conditions) | (description_conditions)).all() # use icontains to avoid Case-insensitive
        end_time=time.time()
        count=elements.count()
        total_time=end_time - start_time
    
        return render(request,r'main\index.html',{'elements':elements,'total_time':total_time,'count':count,'input_search': input_search,'input_type':input_type})

    input_search=''
    total_time=''
    count=''
    elements=''
    return render(request,r'main\index.html',{'elements':elements,'total_time':total_time,'count':count,'input_search': input_search})
    


# Pagination


def import_db():
    conn = psycopg2.connect(host='localhost',dbname='zeno_db',user='postgres',password='054Ibiza',port='5432') 

    df=pd.read_excel(r'\\prfoufiler01\donnees$\Public\tags.xlsx')
    print(df)
    coois = StringIO()
    coois.write(df.to_csv(index=None , header=None,sep=';'))
    coois.seek(0)
    with conn.cursor() as c:
        c.copy_from(
            file=coois,
            table="main_element",
            columns=[
                    'name',
                    'description',
                    'link',
                    'color1',
                    'color2',
                    'type',
                    'tag',
            ],
            null="",
            sep=";",
        )
    conn.commit()