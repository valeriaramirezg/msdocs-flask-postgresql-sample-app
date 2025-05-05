from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import validates

from app import db

class ImageCloud(db.Model):
    __tablename__ = 'image_cloud'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    username = db.Column(db.Text, nullable=False)
    filename = db.Column(db.Text, nullable=False)
    pixels = db.Column(db.Text, nullable=False)
