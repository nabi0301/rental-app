from app import db
from datetime import datetime

class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    caption = db.Column(db.String(255))
    
    # Foreign Keys
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    
    @property
    def url(self):
        return f'/static/uploads/{self.filename}'
