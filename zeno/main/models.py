from django.db import models

# Create your models here.
class Element(models.Model):
    types = [
        ('Video','Video'),
        ('Document','Document'),
        ('Tool','Tool'),
        ('Intranet Link','Intranet Link')
        ]

    name=models.CharField(max_length=200)
    description=models.CharField(max_length=200,null=True)
    link=models.CharField(max_length=2000)
    color1=models.CharField(max_length=20)
    color2=models.CharField(max_length=20)
    type=models.CharField(max_length=50,choices=types)
    tag=models.CharField(max_length=300)

    def __str__(self):
        return self.name
