#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from forms import *
from datetime import date
from models import Venue, Artist, Show, db

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    data = []
    venue_locations = Venue.query.with_entities(Venue.city, Venue.state).group_by(
        Venue.city, Venue.state).all()

    for (city, state) in venue_locations:
        venues = Venue.query.filter_by(state=state, city=city).all()
        data.append({
            'city': city,
            'state': state,
            'venues': venues
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    response = {}
    venues = []
    search_term = request.form.get('search_term', '').lower()
    search_result = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%')).all()

    for venue in search_result:
        venue_shows_count = Show.query.join(Venue).filter(Venue.id == venue.id).count()

        venues.append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': venue_shows_count
        })

    response['count'] = len(search_result)
    response['data'] = venues

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    past_shows = []
    upcoming_shows = []

    venue = Venue.query.filter_by(id=venue_id).first()
    venue_shows = Show.query.join(Venue).filter(Venue.id == venue_id).all()
    print ('Venue shows: ', venue_shows)

    for show in filter(lambda show: show.start_time.date() < date.today(), venue_shows):
        artist = Artist.query.filter_by(id=show.artist_id).first()
        past_shows.append({
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': str(show.start_time)
        })

    for show in filter(lambda show: show.start_time.date() > date.today(), venue_shows):
        artist = Artist.query.filter_by(id=show.artist_id).first()
        upcoming_shows.append({
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': str(show.start_time)
        })

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(','),
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = request.form
    error = False
    my_form = VenueForm()
    if not my_form.validate_on_submit():
        print('Validation error: ', my_form.errors)
        flash(my_form.errors)
        return render_template('forms/new_venue.html', form=my_form)
    try:
        db.session.add(
            Venue(
                name=form['name'],
                city=form['city'],
                state=form['state'],
                address=form['address'],
                phone=form['phone'],
                genres=','.join(form.getlist('genres')),
                image_link=form['image_link'],
                facebook_link=form['facebook_link'],
                website_link=form['website_link'],
                seeking_talent=form.get('seeking_talent') != None,
                seeking_description=form['seeking_description'])
        )
        db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print(e)
        print(sys.exc_info())
    finally:
        db.session.close()
        if error == True:
            flash('An error occurred. Venue ' +
                  form['name'] + ' could not be listed.')
            abort(500)
        else:
            flash('Venue ' + form['name'] + ' was successfully listed!')
            return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        Venue.query().filter_by(id=venue_id).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        print(sys.exc_info())
    finally:
        db.session.close()
    #  BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    return render_template('pages/artists.html', artists=Artist.query.all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    response = {}
    artists = []
    search_term = request.form.get('search_term', '').lower()
    search_result = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')).all()

    for artist in search_result:
        artist_shows_count = Show.query.join(Artist).filter(Artist.id == artist.id).count()

        artists.append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': artist_shows_count
        })

    response['count'] = len(search_result)
    response['data'] = artists

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id

    artist = Artist.query.filter_by(id=artist_id).first()
    artist_shows = Show.query.join(Artist).filter(Artist.id == artist_id).all()
    past_shows = []
    upcoming_shows = []

    for show in filter(lambda show: show.start_time.date() < date.today(), artist_shows):
        venue = Venue.query.filter_by(id=show.venue_id).first()
        past_shows.append({
            'venue_id': venue.id,
            'venue_name': venue.name,
            'venue_image_link': venue.image_link,
            'start_time': str(show.start_time)
        })

    for show in filter(lambda show: show.start_time.date() > date.today(), artist_shows):
        venue = Venue.query.filter_by(id=show.venue_id).first()
        upcoming_shows.append({
            'venue_id': venue.id,
            'venue_name': venue.name,
            'venue_image_link': venue.image_link,
            'start_time': str(show.start_time)
        })

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(','),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = request.form
    error = False

    my_form = ArtistForm()
    if not my_form.validate_on_submit():
        print('Validation error: ', my_form.errors)
        flash(my_form.errors)
        return redirect(url_for('edit_artist', artist_id=artist_id))

    try:
        artist = Artist.query.filter_by(id=artist_id).first()
        artist.name = form['name']
        artist.city = form['city']
        artist.state = form['state']
        artist.phone = form['phone']
        artist.genres = ','.join(form.getlist('genres'))
        artist.image_link = form['image_link'],
        artist.facebook_link = form['facebook_link']
        artist.website_link = form['website_link']
        artist.seeking_venue = form.get('seeking_venue') != None
        artist.seeking_description = form['seeking_description']
        db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print(e)
        print(sys.exc_info())
    finally:
        db.session.close()
        if error == True:
            flash('An error occurred. Artist ' +
                  form['name'] + ' could not be updated.')
            abort(500)
        else:
            flash('Artist ' + form['name'] + ' was updated successfully!')
            return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()
    form = VenueForm(obj=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = request.form
    error = False

    my_form = VenueForm()
    if not my_form.validate_on_submit():
        print('Validation error: ', my_form.errors)
        flash(my_form.errors)
        return redirect(url_for('edit_venue', venue_id=venue_id))

    try:
        venue = Venue.query.filter_by(id=venue_id).first()
        venue.name = form['name']
        venue.city = form['city']
        venue.state = form['state']
        venue.address = form['address']
        venue.phone = form['phone']
        venue.genres = ','.join(form.getlist('genres'))
        venue.image_link = form['image_link']
        venue.facebook_link = form['facebook_link']
        venue.website_link = form['website_link']
        venue.seeking_talent = form.get('seeking_talent') != None
        venue.seeking_description = form['seeking_description']
        db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print(e)
        print(sys.exc_info())
    finally:
        db.session.close()
        if error == True:
            flash('An error occurred. Venue ' +
                  form['name'] + ' could not be updated.')
            abort(500)
        else:
            flash('Venue ' + form['name'] + ' was updated successfully!')
            return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = request.form
    error = False
    my_form = ArtistForm()
    if not my_form.validate_on_submit():
        print('Validation error: ', my_form.errors)
        flash(my_form.errors)
        return render_template('forms/new_artist.html', form=my_form)
    try:
        db.session.add(
            Artist(
                name=form['name'],
                city=form['city'],
                state=form['state'],
                phone=form['phone'],
                genres=','.join(form.getlist('genres')),
                image_link=form['image_link'],
                facebook_link=form['facebook_link'],
                website_link=form['website_link'],
                seeking_venue=form.get('seeking_venue') != None,
                seeking_description=form['seeking_description'])
        )
        db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print(e)
        print(sys.exc_info())
    finally:
        db.session.close()
        if error == True:
            flash('An error occurred. Artist ' +
                  form['name'] + ' could not be listed.')
            abort(500)
        else:
            flash('Artist ' + form['name'] + ' was successfully listed!')
            return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    data = []
    for show in Show.query.all():
        data.append({
            'venue_id': show.venue_id,
            'venue_name': Venue.query.filter_by(id=show.venue_id).first().name,
            'artist_id': show.artist_id,
            'artist_name': Artist.query.filter_by(id=show.artist_id).first().name,
            'artist_image_link': Artist.query.filter_by(id=show.artist_id).first().image_link,
            'start_time': str(show.start_time)
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = request.form
    error = False
    try:
        db.session.add(
            Show(
                start_time=form['start_time'],
                artist_id=form['artist_id'],
                venue_id=form['venue_id'])
        )
        db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print(e)
        print(sys.exc_info())
    finally:
        db.session.close()
        if error == True:
            flash('An error occurred. Show could not be listed.')
            abort(500)
        else:
            flash('Show was successfully listed!')
            return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


app.register_error_handler(404, not_found_error)
app.register_error_handler(500, server_error)


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)
