from django.db import models

class Foodies(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    food_name = models.CharField(max_length=200)
    calories = models.IntegerField(default=0)
    serving_size = models.IntegerField(default=100)
    carbohydrates = models.IntegerField(default=0)
    cholesterol = models.IntegerField(default=0)
    saturated_fat = models.IntegerField(default=0)
    total_fat = models.IntegerField(default=0)
    fiber_content = models.IntegerField(default=0)
    potassium = models.IntegerField(default=0)
    protein = models.IntegerField(default=0)
    sodium = models.IntegerField(default=0)
    sugar = models.IntegerField(default=0)
