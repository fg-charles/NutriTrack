from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt, sys
import pandas as pd
from app import db, login


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Personal Nutrition Information
    age = db.Column(db.Integer)
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    exercise = db.Column(db.Float)
    sex = db.Column(db.String(1))

    # Relationships
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    info = db.relationship('NutritionInfo', uselist=False,
                           cascade="all, delete-orphan")
    mealplans = db.relationship('MealPlan', back_populates='user',
                            lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_mealplans(self):
        followed = MealPlan.query.join(
            followers, (followers.c.followed_id == MealPlan.user_id)).filter(
                followers.c.follower_id == self.id)
        own = MealPlan.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(MealPlan.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
    
    def set_nutri_info(self):
        if self.info is None:
            self.info = NutritionInfo()
        sex = -161 if self.sex == 'F' else 5
        TDEE = float(self.exercise) * (10 * float(self.weight) + 6.25 * 100 * float(self.height) - 5 * float(self.age) + sex)
        all_goals = pd.read_csv('app/static/micronutrients.csv')
        indiv_goals = all_goals[(all_goals.sex == self.sex) & (all_goals.age < self.age)].nlargest(1, 'age').squeeze()
        
        # Finds the gram values (upper and lower range) for macronutrients
        find_g = {'protein':4, 'carbs':4, 'fat':9}
        for key, value in find_g.items():
            lower_upper = list(map(int, indiv_goals.at[key + '_p'].split('-')))
            indiv_goals.at[key + '_low'] = (lower_upper[0] * TDEE) / (100 * value)
            indiv_goals.at[key] = (lower_upper[1] * TDEE) / (100 * value)

        # Finds the gram values for sat fat sugar and fiber
        indiv_goals.at['sat_fat'] = int((.1 * TDEE) / 9)
        indiv_goals.at['sugar'] = int((.1 * TDEE) / 4)
        indiv_goals.at['fiber'] = int(.014 * TDEE)
        indiv_goals.iloc[2] = TDEE

        # fixes up labels
        indiv_goals.drop(labels=['rowtype', 'sex', 'protein_p', 'carbs_p',
                                'sugar_p', 'fat_p', 'sat_fat_p'], inplace=True)
        indiv_goals.rename({'age':'calories'}, inplace=True)

        indiv_goals = indiv_goals.to_dict()
        for key, value in indiv_goals.items():
            setattr(self.info, key, value)
        



@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class NutritionInfo(db.Model):
    __tablename__ = 'nutri_info'
    id = db.Column(db.Integer, primary_key=True)

    calories = db.Column(db.Float)
    protein = db.Column(db.Float)
    protein_low = db.Column(db.Float)
    carbs = db.Column(db.Float)
    carbs_low = db.Column(db.Float)
    fiber = db.Column(db.Float)
    sugar = db.Column(db.Float)
    fat = db.Column(db.Float)
    fat_low = db.Column(db.Float)
    sat_fat = db.Column(db.Float)
    calcium = db.Column(db.Float)
    iron = db.Column(db.Float)
    magnesium = db.Column(db.Float)
    phosphorus = db.Column(db.Float)
    potassium = db.Column(db.Float)
    sodium = db.Column(db.Float)
    zinc = db.Column(db.Float)
    vitA = db.Column(db.Float)
    vitE = db.Column(db.Float)
    vitD = db.Column(db.Float)
    vitC = db.Column(db.Float)
    thiamin = db.Column(db.Float)
    riboflavin = db.Column(db.Float)
    niacin = db.Column(db.Float)
    vitB6 = db.Column(db.Float)
    vitB12 = db.Column(db.Float)
    chlorine = db.Column(db.Float)
    vitK = db.Column(db.Float)
    folate = db.Column(db.Float)

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mealplan_id = db.Column(db.Integer, db.ForeignKey('mealplan.id'))
    fooditem_id = db.Column(db.Integer, db.ForeignKey('fooditem.id'))

    def __repr__(self):
        return '<NutritionInfo {}>'.format(self.id)
    
    def get_data(self, display=False):
        data = self.__dict__
        is_user_info = True if User.query.filter_by(info=self).first() != None else False
        del (data['_sa_instance_state'], data['id'], data['user_id'],
            data['mealplan_id'], data['fooditem_id'])
        if not is_user_info:
            del data['protein_low'], data['carbs_low'], data['fat_low']
        if display:
            data = {'Calories (kcal)': int(self.calories), 'Protein (g)': int(self.protein), 'Carbohydrates (g)': self.carbs, 'Fiber (g)': int(self.fiber), 'Added Sugars (g)': str(int(self.sugar)), 'Total Fat (g)': int(self.fat), 'Saturated Fat (g)': str(int(self.sat_fat)), 'Calcium (mg)': int(self.calcium), 'Iron (mg)': int(self.iron), 'Magnesium (mg)': int(self.magnesium), 'Phosphorus (mg)': int(self.phosphorus), 'Potassium (mg)': int(self.potassium), 'Sodium (mg)': int(self.sodium), 'Zinc (mg)': int(self.zinc), 'Vitamin A (mcg RAE)': int(self.vitA), 'Vitamin E (mg AT)': int(self.vitE), 'Vitamin D (IU)': int(self.vitD), 'Vitamin C (mg)': int(self.vitC), 'Thiamin (mg)': int(self.thiamin), 'Riboflavin (mg)': int(self.riboflavin), 'Niacin (mg)': int(self.niacin), 'Vitamin B6 (mg)': int(self.vitB6), 'Vitamin B12 (mcg)': int(self.vitB12), 'Chlorine (mg)': int(self.chlorine), 'Vitamin K (mcg)': int(self.vitK), 'Folate (mcg DFE)': int(self.folate)}
            if is_user_info:
                data['Protein (g)'] = str(int(self.protein_low)) + '-' + str(int(self.protein))
                data['Carbohydrates (g)'] = str(int(self.carbs_low)) + '-' + str(int(self.carbs))
                data['Total Fat (g)'] = str(int(self.fat_low)) + '-' + str(int(self.fat))
                data['Added Sugars (g)'] = '<' + str(int(self.sugar))
                data['Saturated Fat (g)'] = '<' + str(int(self.sat_fat))
        return data


class MealPlan(db.Model):
    __tablename__ = 'mealplan'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    length = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='mealplans')
    info = db.relationship('NutritionInfo', uselist=False,
                           cascade="all, delete-orphan")
    fooditems = db.relationship('FoodItem', back_populates='mealplan',
                                lazy='dynamic',cascade="all, delete-orphan")

    def __repr__(self):
        return '<NutritionInfo {}>'.format(self.name)
    
    def get_item_data(self):
        item_data = []
        for fooditem in self.fooditems:
            item_info = fooditem.info.__dict__
            print(item_info, file=sys.stderr)
            item_info.pop('_sa_instance_state')
            item_info.pop('id')
            item_info['name'] = fooditem.name
            item_data.append(fooditem.info.__dict__)
        return item_data

    def set_nutri_info(self):
        if (self.info is None):
            self.info = NutritionInfo()
        averages = {'calories': 0,'protein': 0,'carbs': 0,'fiber': 0,'sugar': 0,'fat': 0,'sat_fat': 0,'calcium': 0,'iron': 0,'magnesium': 0,'phosphorus': 0,'potassium': 0,'sodium': 0,'zinc': 0,'vitA': 0,'vitE': 0,'vitD': 0,'vitC': 0,'thiamin': 0,'riboflavin': 0,'niacin': 0,'vitB6': 0,'vitB12': 0,'chlorine': 0,'vitK': 0,'folate': 0}
        for attr in averages.keys():
            for item in self.fooditems:
                averages[attr] += (getattr(item.info, attr) * float(item.no_servings))
            averages[attr] /= self.length
            setattr(self.info, attr, averages[attr])

            

class FoodItem(db.Model):
    __tablename__ = 'fooditem'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    no_servings = db.Column(db.Float())

    # Relationships
    mealplan_id = db.Column(db.Integer, db.ForeignKey('mealplan.id'))
    mealplan = db.relationship('MealPlan', back_populates='fooditems')
    info = db.relationship('NutritionInfo', uselist=False,
                           cascade="all, delete-orphan")

    def __repr__(self):
        return '<FoodItem {}>'.format(self.name)
