from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False, server_default="false")
    seeking_description = db.Column(db.String(250), nullable=True)
    shows = db.relationship('Show', backref='listVenues', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Venue {self.id} {self.name} {self.city} {self.state}, {self.address}, {self.genres}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False, server_default="false")
    seeking_description = db.Column(db.String(250), nullable=True)
    shows = db.relationship('Show', backref='listArtists', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Artist {self.id} {self.name} {self.city} {self.state}, {self.genres}>'


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    def __repr__(self) -> str:
        return f'<Show id: {self.id}, artist_id: {self.artist_id}, venue_id: {self.venue_id}, {self.start_time}>'
