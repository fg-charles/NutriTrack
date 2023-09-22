from app import create_app, db
from app.models import User, NutritionInfo, MealPlan, FoodItem

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User,
            'FoodItem': FoodItem, 'NutritionInfo':NutritionInfo, 'MealPlan': MealPlan
            }
