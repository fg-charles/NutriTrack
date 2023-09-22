#!/usr/bin/env python
from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import User, MealPlan, NutritionInfo, FoodItem
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class CascadeDeleteCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_cascade_user_mealplan(self):
        u = User(username='susan')
        m = MealPlan(name='plan 1', user=u)
        db.session.add(u)
        db.session.add(m)
        db.session.commit()
        self.assertEqual(u, m.user)
        self.assertEqual(m, u.mealplans.first())

        db.session.delete(u)
        db.session.commit()
        self.assertEqual(None, MealPlan.query.first())

    def test_cascade_user_info(self):
        u = User(username='susan')
        i = NutritionInfo()
        db.session.add(u)
        db.session.add(i)
        u.info = i
        db.session.commit()
        self.assertEqual(i, u.info)

        db.session.delete(u)
        db.session.commit()
        self.assertEqual(None, NutritionInfo.query.first())

    def test_cascade_mealplan_fooditem(self):
        u = MealPlan(name='susan')
        m = FoodItem(mealplan=u)
        db.session.add(u)
        db.session.add(m)
        db.session.commit()
        self.assertEqual(u, m.mealplan)
        self.assertEqual(m, u.fooditems.first())

        db.session.delete(u)
        db.session.commit()
        self.assertEqual(None, FoodItem.query.first())

    def test_cascade_mealplan_info(self):
        u = MealPlan(name='susan')
        i = NutritionInfo()
        db.session.add(u)
        db.session.add(i)
        u.info = i
        db.session.commit()
        self.assertEqual(i, u.info)

        db.session.delete(u)
        db.session.commit()
        self.assertEqual(None, NutritionInfo.query.first())

    def test_cascade_fooditem_info(self):
        u = FoodItem()
        i = NutritionInfo()
        db.session.add(u)
        db.session.add(i)
        u.info = i
        db.session.commit()
        self.assertEqual(i, u.info)

        db.session.delete(u)
        db.session.commit()
        self.assertEqual(None, NutritionInfo.query.first())


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_mealplans(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four mealplans
        now = datetime.utcnow()
        p1 = MealPlan(name="mealplan from john", user=u1,
                  timestamp=now + timedelta(seconds=1))
        p2 = MealPlan(name="mealplan from susan", user=u2,
                  timestamp=now + timedelta(seconds=4))
        p3 = MealPlan(name="mealplan from mary", user=u3,
                  timestamp=now + timedelta(seconds=3))
        p4 = MealPlan(name="mealplan from david", user=u4,
                  timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check the followed mealplans of each user
        f1 = u1.followed_mealplans().all()
        f2 = u2.followed_mealplans().all()
        f3 = u3.followed_mealplans().all()
        f4 = u4.followed_mealplans().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
