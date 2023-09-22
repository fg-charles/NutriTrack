from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm, EmptyForm, EditNutritionForm, MealPlanForm
from app.models import User, MealPlan, FoodItem, NutritionInfo
from app.main import bp
from sqlalchemy import inspect


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    mealplans = current_user.followed_mealplans().paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    next_url = url_for('main.index', page=mealplans.next_num) \
        if mealplans.has_next else None
    prev_url = url_for('main.index', page=mealplans.prev_num) \
        if mealplans.has_prev else None
    return render_template('index.html', title='Home',
                           mealplans=mealplans.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    mealplans = MealPlan.query.order_by(MealPlan.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    next_url = url_for('main.explore', page=mealplans.next_num) \
        if mealplans.has_next else None
    prev_url = url_for('main.explore', page=mealplans.prev_num) \
        if mealplans.has_prev else None
    return render_template('index.html', title='Explore',
                           mealplans=mealplans.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    mealplans = user.mealplans.order_by(MealPlan.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    next_url = url_for('main.user', username=user.username,
                       page=mealplans.next_num) if mealplans.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=mealplans.prev_num) if mealplans.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, mealplans=mealplans.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('generic_form.html', title='Edit Profile',
                           form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/edit_nutrition', methods=['GET', 'POST'])
@login_required
def edit_nutrition():
    form = EditNutritionForm()
    if form.validate_on_submit():
        current_user.age = form.age.data
        current_user.height = form.height.data
        current_user.weight = form.weight.data
        current_user.exercise = form.exercise.data
        current_user.sex = form.sex.data
        current_user.set_nutri_info()
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.nutrition_goals', username=current_user.username))
    elif request.method == 'GET':
        form.age.data = current_user.age
        form.height.data = current_user.height
        form.weight.data = current_user.weight
        form.exercise.data = current_user.exercise
        form.sex.data = current_user.sex
    return render_template('generic_form.html',title='Edit Nutrition Information',
                           form=form)


@bp.route('/nutrition_goals', methods=['GET'])
@login_required
def nutrition_goals():
    if current_user.height == None:
        flash('Add nutrition information to see your goals!')
        return redirect(url_for('main.user', username=current_user.username))
    goals=current_user.info.get_data(display=True)
    return render_template('nutrition_goals.html', title='Daily Nutrition Goals', goals=goals)


@bp.route('/user/<username>/mealplans')
@login_required
def user_mealplans(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    return render_template('user_mealplans.html', user=user)


@bp.route('/<mealplan_id>')
@login_required
def show_mealplan(mealplan_id):
    mealplan = MealPlan.query.filter_by(id=mealplan_id).first()
    if mealplan is None:
        flash('Meal plan not found.')
        return redirect(url_for('main.index'))
    nutri_attrs = inspect(NutritionInfo).columns.keys()[1:-3]
    nutri_attrs.remove('protein_low')
    nutri_attrs.remove('fat_low')
    nutri_attrs.remove('carbs_low')
    return render_template('show_mealplan.html', mealplan=mealplan, nutri_attrs=nutri_attrs)


@bp.route('/<mealplan_id>/form', methods=['POST', 'GET'])
@login_required
def mealplan_form(mealplan_id):
    is_newplan = mealplan_id == 'new'
    if is_newplan:
        flashcomment = 'created'
        mealplan = MealPlan()
        db.session.add(mealplan)
    else:
        mealplan = MealPlan.query.filter_by(id=mealplan_id).first()
        flashcomment = 'updated'
        if mealplan is None:
            flash('Meal plan not found.')
            return redirect(url_for('main.index'))
        elif mealplan.user.username != current_user.username:
            flash("You can't modify other user's mealplans!")
    form = MealPlanForm()
    if form.validate_on_submit():
        mealplan.name = form.name.data
        mealplan.length = form.length.data
        mealplan.user = current_user
        for item in mealplan.fooditems:
            db.session.delete(item)
        for fooditem_data in form.fooditems.data:
            fooditem = FoodItem()
            db.session.add(fooditem)
            fooditem.mealplan = mealplan
            fooditem.name = fooditem_data['name']
            fooditem.no_servings = fooditem_data['no_servings']
            fooditem.info = NutritionInfo()
            for field, value in fooditem_data.items():
                setattr(fooditem.info, field, value)
        mealplan.set_nutri_info()
        db.session.commit()
        flash('Meal plan '+ flashcomment + '!')
        return redirect(url_for('main.index', username=current_user.username))
    elif request.method == 'GET':
        form.name.data = mealplan.name
        form.length.data = mealplan.length
        for item in mealplan.get_item_data():
            form.fooditems.append_entry(item)
    return render_template('mealplan_form.html', title=(mealplan.name), form=form)


@bp.route('/<mealplan_id>/delete')
def delete_mealplan(mealplan_id):
    mealplan = MealPlan.query.filter_by(id=mealplan_id).first()
    db.session.delete(mealplan)
    db.session.commit()
    return redirect(url_for('main.user_mealplans', username=current_user.username))
