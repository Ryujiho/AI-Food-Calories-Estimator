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
    
    chart_today = [0 for i in range(6)]
    chart_weekly = [0 for i in range(6)]
    
    if len(today) != 0:
        for data in today:
            chart_today[0] += data['calories']
            chart_today[1] += data['carbohydrates']
            chart_today[2] += data['total_fat']
            chart_today[3] += data['protein']
            chart_today[4] += data['sodium']
            chart_today[5] += data['sugar']
            
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
            api  = get_model_results(filename)
            
        if 'query' in request.POST:
            query = request.POST['query']
            api_url = 'https://api.api-ninjas.com/v1/nutrition?query='
            api_request = requests.get(
                api_url + query, headers={'X-Api-Key': 'uF82Rnp+3IHaDuVRJ157GA==We7LxVlYDzefzxtx'})
            try:
                api = json.loads(api_request.content)
                print(api)
                api = api[0]
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
    v =  api
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
    CALORIES = 'calories'
    DETECT = 'detect'
    IMAGES = 'resultImages'
    API_URI = 'http://a23a-34-80-148-202.ngrok.io/'
    
    fname = 'input.png'
    img = open(fname, 'rb')
    upload = {'image': img}
    
    '''
    ## 1. Predict Food 
    api_request = requests.post(f'{API_URI}{DETECT}', files = upload)
    print(api_request.content)
    food_name = api_request.content['food_name']
    ## 3. Get Inference Images
    api_request = requests.get(f'{API_URI}{IMAGES}')
    print(api_request.files)
    '''
    
    ## 2. Predict Ingredients
    api_request = requests.post(f'{API_URI}{CALORIES}', files = upload)   
    response = api_request.content.decode('utf8')
    print(response)
    if len(response) != 0:
        response_data = json.loads(response)
    print(response_data)
    
    food_name = 'hamburger'
    response_data['name'] = food_name
    ## Post Process Image : bounding box -> output.jpg
    '''items': [{'ingredient': 'bread', 'ratio': 0.31}, {'ingredient': 'background', 'ratio': 0.23}, {'ingredient': 'steak', 'ratio': 0.13}, {'ingredient': 'lettuce', 'ratio': 0.12}, {'ingredient': 'tomato', 'ratio': 0.11}, {'ingredient': 'onion', 'ratio': 0.04}, {'ingredient': 'sauce', 'ratio': 0.01}, {'ingredient': 'other ingredients', 'ratio': 0.01}, {'ingredient': 'cheese butter', 'ratio': 0.01}, {'ingredient': 'sausage', 'ratio': 0.01}, {'ingredient': 'cucumber', 'ratio': 0.01}, {'ingredient': 'chicken duck', 'ratio': 0.0}], 
    'estimated_calories': 325}
    '''
    
    ''''
     json.load(st_json)
    {
    "confidence": 0.9913035035133362,
    "elapsed_time": 8.349461555480957,
    "food_name": "hamburger",
    'bb': (252.65716552734375, 213.94979858398438, 480.865966796875, 537.388671875)
    }'''
    return response_data
