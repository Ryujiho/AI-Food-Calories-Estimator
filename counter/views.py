from django.shortcuts import render, redirect
from django.core import serializers
from counter.models import Foodies
import json
import requests
from datetime import date, timedelta


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
        query = request.POST['query']
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query='
        api_request = requests.get(
            api_url + query, headers={'X-Api-Key': 'uF82Rnp+3IHaDuVRJ157GA==We7LxVlYDzefzxtx'})
        try:
            api = json.loads(api_request.content)
            GLOBAL_Request = api
            print(api_request.content)
        except Exception as e:
            api = "oops! There was an error"
            print(e)
        params['api'] = api
        return render(request, 'home.html', params)
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
