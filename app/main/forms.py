from flask_wtf import FlaskForm, Form
from wtforms import (StringField, SubmitField, TextAreaField, IntegerField,
                      DecimalField, RadioField, SelectField, FieldList,
                      FormField)
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me',
                             validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class EditNutritionForm(FlaskForm):
    age = IntegerField('Age', validators=[DataRequired()])
    height = DecimalField('Height (m)', validators=[DataRequired()])
    weight = DecimalField('Weight (kg)', validators=[DataRequired()])
    exercise = SelectField('Exercise',
                           choices=[(1.2, 'Sedentary (office job)'),
                                    (1.375, 'Light Exercise (1/2 days/week)'),
                                    (1.55, 'Moderate Exercise (3-5 days/week)'),
                                    (1.725, 'Heavy Exercise (6-7 days/week)'),
                                    (1.9, 'Athlete (2x per day)')],
                            validators=[DataRequired()])
    sex = RadioField('Sex', choices=[('M', 'Male'), ('F', 'Female')], validators=[DataRequired()])
    submit = SubmitField('Submit')

class FoodItemForm(Form):
    name = StringField('Food Item Name',  default='New Food Item')
    no_servings = DecimalField('Number of Servings Eaten', default=1)
    calories = IntegerField('Calories (kcal)',  default=0)
    protein = IntegerField('Protein (g)',  default=0)
    carbs = IntegerField('Carbohydrates (g)',  default=0)
    fiber = IntegerField('Fiber (g)',  default=0)
    sugar = IntegerField('Added Sugars (g)',  default=0)
    fat = IntegerField('Total Fat (g)',  default=0)
    sat_fat = IntegerField('Saturated Fat (g)',  default=0)
    calcium = IntegerField('Calcium (mg)',  default=0)
    iron = IntegerField('Iron (mg)',  default=0)
    magnesium = IntegerField('Magnesium (mg)',  default=0)
    phosphorus = IntegerField('Phosphorus (mg)',  default=0)
    potassium = IntegerField('Potassium (mg)',  default=0)
    sodium = IntegerField('Sodium (mg)',  default=0)
    zinc = IntegerField('Zinc (mg)',  default=0)
    vitA = IntegerField('Vitamin A (mcg RAE)',  default=0)
    vitE = IntegerField('Vitamin E (mg AT)',  default=0)
    vitD = IntegerField('Vitamin D (IU)',  default=0)
    vitC = IntegerField('Vitamin C (mg)',  default=0)
    thiamin = IntegerField('Thiamin (mg)',  default=0)
    riboflavin = IntegerField('Riboflavin (mg)',  default=0)
    niacin = IntegerField('Niacin (mg)',  default=0)
    vitB6 = IntegerField('Vitamin B6 (mg)',  default=0)
    vitB12 = IntegerField('Vitamin B12 (mcg)',  default=0)
    chlorine = IntegerField('Chlorine (mg)',  default=0)
    vitK = IntegerField('Vitamin K (mcg)',  default=0)
    folate = IntegerField('Folate (mcg DFE)',  default=0)
    
class MealPlanForm(FlaskForm):
    name = StringField('Meal Plan Name', default='New Meal Plan')
    length = IntegerField('Meal Plan Length (days)', default=0, validators=[DataRequired()])
    fooditems = FieldList(FormField(FoodItemForm))
    submit = SubmitField('Submit')
    
