from .forms import UploadFileForm
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from django.shortcuts import render, redirect
from counter.models import Foodies
from django.views.decorators.csrf import ensure_csrf_cookie
import json
import requests
import os
from datetime import date, timedelta


@ensure_csrf_cookie
def home(request):
    global api
    
    # READ DB
    today = date.today()
    one_week_ago = today - timedelta(days=7)
    today = Foodies.objects.filter(created_date__date=today).values()
    weekly = Foodies.objects.filter(created_date__gte=one_week_ago).values()
    
    chart_today = []
    chart_weekly = [0 for i in range(6)]
    
    if len(today) != 0:
        today = today[0]
        chart_today = [today['calories'], today['carbohydrates'], today['total_fat'], today['protein'], today['sodium'], today['sugar']]

    for data in weekly:
        chart_weekly[0] += data['calories']
        chart_weekly[1] += data['carbohydrates']
        chart_weekly[2] += data['total_fat']
        chart_weekly[3] += data['protein']
        chart_weekly[4] += data['sodium']
        chart_weekly[5] += data['sugar']
        
    params = {}
    params['chart_today'] = chart_today
    params['chart_weekly'] = chart_weekly
    
    if request.method == 'POST':
        if 'upload' in request.FILES:
            file = request.FILES['upload']
            print(file)
            
            newFileName = "input.png"
            fs = FileSystemStorage()
            if fs.exists(newFileName):
                os.remove(newFileName)
            filename = fs.save(newFileName, file)
            params['query'] = filename
        
        if 'query' in request.POST:
            query = request.POST['query']
            api_url = 'https://api.api-ninjas.com/v1/nutrition?query='
            api_request = requests.get(
                api_url + query, headers={'X-Api-Key': 'uF82Rnp+3IHaDuVRJ157GA==We7LxVlYDzefzxtx'})
            try:
                api = json.loads(api_request.content)
                print(api_request.content)
            except Exception as e:
                api = "oops! There was an error"
                print(e)
            params['api'] = api
    else:
        params['query'] = 'Enter a valid query'
    
    return render(request, 'home.html', params)


# Insert into DB
def save(request):
    global api
    v =  api[0]
    f = Foodies()
    f.food_name=v['name']
    f.serving_size=v['serving_size_g']
    f.calories=v['calories']
    f.carbohydrates=v['carbohydrates_total_g']
    f.cholesterol=v['cholesterol_mg']
    f.saturated_fat=v['fat_saturated_g']
    f.total_fat=v['fat_total_g']
    f.fiber_content=v['fiber_g']
    f.potassium=v['potassium_mg']
    f.protein=v['protein_g']
    f.sodium=v['sodium_mg']
    f.sugar=v['sugar_g']
    f.save()
    
    return redirect('home')

## Colab Flask API
def get_model_results(request):
    api_name = 'calories'
    api_name = 'detect'
    api_name = 'resultImages'
    api_url = f'http://27bd-34-143-177-75.ngrok.io/'
    #api_request = requests.get()
    img = open('input.png', 'rb')
    upload = {'image': img}
    api_request = requests.post(f'{api_url}{api_name}', files = upload)
    print(api_request.content)
    print(api_request)
    ## Post Process Image : bounding box -> output.jpg
    ''''
     json.load(st_json)
    {
    "confidence": 0.9913035035133362,
    "elapsed_time": 8.349461555480957,
    "food_name": "hamburger",
    'bb': (252.65716552734375, 213.94979858398438, 480.865966796875, 537.388671875)
    }'''
    return redirect('home')


def downloadFile(request, param):
    print(f"[downloadFile] param (File Name) : {param}")
    
    # Download file
    BASE_DIR = os.getcwd()
    fs = FileSystemStorage(BASE_DIR)
    file_name = os.path.basename(param)
    response = FileResponse(fs.open(file_name, 'rb'),
                            content_type='video/mp4')
    response['Content-Disposition'] = f'attachment; filename="{param}"'

    return response


def handle_uploaded_file(f):
    with open(f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)