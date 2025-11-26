from app import db
from datetime import datetime

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    neighborhood = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    property_type = db.Column(db.String(50))  # apartment, house, condo, etc.
    amenities = db.Column(db.JSON)  # storing amenities as JSON
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    available_from = db.Column(db.Date)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    image_filename = db.Column(db.String(255))
    
    # Foreign Keys
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    applications = db.relationship('Application', backref='property', lazy=True)
    saved_by = db.relationship('SavedProperty', backref='property', lazy=True)
    reviews = db.relationship('Review', backref='property', lazy=True)
    messages = db.relationship('Message', backref='property', lazy=True)
    images = db.relationship('PropertyImage', backref='property', lazy=True,
                           order_by='PropertyImage.is_primary.desc(), PropertyImage.created_at.asc()')
    
    @property
    def image_url(self):
        primary_image = next((img for img in self.images if img.is_primary), None)
        if primary_image:
            return primary_image.url
        elif self.images:
            return self.images[0].url
        elif self.image_filename:
            return f'/static/uploads/{self.image_filename}'
        return None
    
    @property
    def all_images(self):
        return sorted(self.images, key=lambda x: (not x.is_primary, x.created_at))
    
    @property
    def average_rating(self):
        if not self.reviews:
            return 0
        return sum(review.rating for review in self.reviews) / len(self.reviews)
