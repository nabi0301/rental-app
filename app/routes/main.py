from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.property import Property
from app.models.application import Application
from app.models.saved_property import SavedProperty
from app.models.review import Review
from app.models.message import Message
from app.models.user import User
from app.models.property_image import PropertyImage
from app.utils.image_handler import save_image, delete_image
from datetime import datetime
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    featured_properties = Property.query.filter_by(is_available=True).order_by(Property.created_at.desc()).limit(6).all()
    return render_template('index.html', featured_properties=featured_properties)


@main.route('/portfolio')
def portfolio():
    """Render the personal portfolio page."""
    return render_template('portfolio.html')

@main.route('/profile')
@login_required
def profile():
    if current_user.is_landlord:
        properties = Property.query.filter_by(owner_id=current_user.id).all()
        received_applications = Application.query.join(Property).filter(
            Property.owner_id == current_user.id
        ).order_by(Application.created_at.desc()).all()
        return render_template('profile.html', properties=properties, received_applications=received_applications)
    else:
        applications = Application.query.filter_by(applicant_id=current_user.id).all()
        saved_properties = Property.query.join(
            SavedProperty, Property.id == SavedProperty.property_id
        ).filter(SavedProperty.user_id == current_user.id).all()
        return render_template('profile.html', applications=applications, saved_properties=saved_properties)

@main.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # Update user information
        current_user.first_name = request.form.get('first_name', '').strip()
        current_user.last_name = request.form.get('last_name', '').strip()
        current_user.phone_number = request.form.get('phone_number', '').strip()
        current_user.bio = request.form.get('bio', '').strip()
        current_user.address = request.form.get('address', '').strip()
        current_user.city = request.form.get('city', '').strip()
        current_user.state = request.form.get('state', '').strip()
        current_user.zip_code = request.form.get('zip_code', '').strip()
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                # Delete old profile picture if it exists
                if current_user.profile_picture:
                    old_picture_path = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles', current_user.profile_picture)
                    if os.path.exists(old_picture_path):
                        os.remove(old_picture_path)
                
                # Save new profile picture
                filename = save_image(file, 'profiles')
                current_user.profile_picture = filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('profile_edit.html')

@main.route('/properties')
def properties():
    # List of US states for the dropdown
    states = [
        'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
        'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
        'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan',
        'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
        'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio',
        'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
        'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia',
        'Wisconsin', 'Wyoming'
    ]

    page = request.args.get('page', 1, type=int)
    query = Property.query.filter_by(is_available=True)

    # Apply filters
    if request.args.get('min_price'):
        try:
            query = query.filter(Property.price >= float(request.args.get('min_price')))
        except ValueError:
            pass
    if request.args.get('max_price'):
        try:
            query = query.filter(Property.price <= float(request.args.get('max_price')))
        except ValueError:
            pass
    if request.args.get('bedrooms'):
        try:
            query = query.filter(Property.bedrooms >= int(request.args.get('bedrooms')))
        except ValueError:
            pass
    if request.args.get('bathrooms'):
        try:
            query = query.filter(Property.bathrooms >= int(request.args.get('bathrooms')))
        except ValueError:
            pass

    # Location filters
    if request.args.get('city'):
        query = query.filter(Property.city.ilike(f"%{request.args.get('city')}%"))
    if request.args.get('state'):
        query = query.filter(Property.state == request.args.get('state'))
    if request.args.get('zip_code'):
        query = query.filter(Property.zip_code.startswith(request.args.get('zip_code')))

    # General search
    if request.args.get('q'):
        search_query = f"%{request.args.get('q')}%"
        query = query.filter(
            db.or_(
                Property.title.ilike(search_query),
                Property.description.ilike(search_query),
                Property.address.ilike(search_query),
                Property.city.ilike(search_query)
            )
        )

    properties = query.order_by(Property.created_at.desc()).paginate(page=page, per_page=9)
    return render_template('property_list.html', properties=properties, states=states)
