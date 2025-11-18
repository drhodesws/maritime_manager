# routes/items.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, admin_required
from models import db, Item
from forms import ItemForm

items_bp = Blueprint('items', __name__, url_prefix='/items')

@items_bp.route('/')
@login_required
def items_page():
    items = Item.query.all()
    return render_template('items.html', items=items)

@items_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_item():
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(
            name=form.name.data,
            description=form.description.data,
            unit_price=form.unit_price.data
        )
        db.session.add(item)
        db.session.commit()
        flash('Item created successfully!', 'success')
        return redirect(url_for('items.items_page'))
    return render_template('item_form.html', form=form, action='Create')

@items_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_item(id):
    item = Item.query.get_or_404(id)
    form = ItemForm(obj=item)
    if form.validate_on_submit():
        item.name = form.name.data
        item.description = form.description.data
        item.unit_price = form.unit_price.data
        db.session.commit()
        flash('Item updated!', 'success')
        return redirect(url_for('items.items_page'))
    return render_template('item_form.html', form=form, item=item, action='Edit')

@items_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete_item(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted!', 'success')
    return redirect(url_for('items.items_page'))