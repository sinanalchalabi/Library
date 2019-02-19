#!/usr/bin/env python

from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   jsonify,
                   url_for,
                   flash)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Library, Book, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Library Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///library.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already \
        connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: \
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    """Create a new user

    Args:
         login_session: object with user data

    Returns:
         user_id: Unique ID for the generated user
    """
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Getting user Info

    Args:
        user_id: Unique ID of the user

    Returns:
        user: Object that contain user info
    """
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """Getting user Info

    Args:
        email: email of the user

    Returns:
         user_id: Unique ID for the generated user
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/\
    revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token\
        for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Show Libraries


@app.route('/')
@app.route('/library/')
def showLibrary():
    """Show libraryies

    Returns:
        all libraries
    """
    library = session.query(Library).order_by(asc(Library.name))
    if 'username' not in login_session:
        return render_template('publicLibrary.html', library=library)
    else:
        return render_template('library.html', library=library)

# Create a new library


@app.route('/library/add/', methods=['GET', 'POST'])
def addLibrary():
    """Add a new library

    Returns:
        on GET: Page to add a new library
        on POST: Redirct to main page after adding a new library
    """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newLibrary = Library(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newLibrary)
        flash('New Library %s Successfully Created' % newLibrary.name)
        session.commit()
        return redirect(url_for('showLibrary'))
    else:
        return render_template('addLibrary.html')


# Edit a library


@app.route('/library/<int:library_id>/edit/', methods=['GET', 'POST'])
def editLibrary(library_id):
    """Edit a specific library

    Args:
        library_id: The id of the library

    Returns:
        on GET: Page to edit library
        on POST: Redirct to main page after library has been edited
    """
    if 'username' not in login_session:
        return redirect('/login')
    editedLibrary = session.query(Library).filter_by(id=library_id).one()
    if editedLibrary.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized \
        to edit this library. Please create your own library \
        in order to edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedLibrary.name = request.form['name']
            flash('Library Successfully Edited %s' % editedLibrary.name)
            return redirect(url_for('showLibrary'))
    else:
        return render_template('editLibrary.html', library=editedLibrary)


# Delete a library
@app.route('/library/<int:library_id>/delete/', methods=['GET', 'POST'])
def deleteLibrary(library_id):
    """Delete a specific library

    Args:
        library_id: The id of the library

    Returns:
        on GET: Page to delete a library
        on POST: Redirct to main page after library has been deleted
    """
    if 'username' not in login_session:
        return redirect('/login')
    libraryToDelete = session.query(
        Library).filter_by(id=library_id).one()
    if libraryToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized \
        to delete this library. Please create your own library \
        in order to delete.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(libraryToDelete)
        bookToDelete = \
            session.query(Book).filter_by(library_id=library_id).delete()
        flash('%s Successfully Deleted' % libraryToDelete.name)
        session.commit()
        return redirect(url_for('showLibrary', library_id=library_id))
    else:
        return render_template('deleteLibrary.html', library=libraryToDelete)


# Show a book

@app.route('/library/<int:library_id>/')
@app.route('/library/<int:library_id>/book/')
def showBook(library_id):
    """Show library's books

     Args:
        library_id: The id of the library required

    Returns:
        all books belong to the library
    """
    library = session.query(Library).filter_by(id=library_id).one()
    creator = getUserInfo(library.user_id)
    books = session.query(Book).filter_by(
        library_id=library_id).all()
    if 'username' not in login_session or creator.id != \
       login_session['user_id']:
        return render_template('publicBook.html',
                                books=books,
                                library=library,
                                creator=creator)
    else:
        return render_template('book.html',
        books=books, library=library, creator=creator)


# Add a new book
@app.route('/library/<int:library_id>/book/add/', methods=['GET', 'POST'])
def addBook(library_id):
    """Add a new book

    Args:
        library_id: The id of the library which will own the book

    Returns:
        on GET: Page to add a new book
        on POST: Redirct to book page after adding a new book
    """
    if 'username' not in login_session:
        return redirect('/login')
    library = session.query(Library).filter_by(id=library_id).one()
    if login_session['user_id'] != library.user_id:
        return "<script>function myFunction() {alert('You are not authorized \
        to add books to this library. Please create your own library \
        in order to add books.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
            newBook = Book(name=request.form['name'],
            description=request.form['description'],
            author=request.form['author'],
            category=request.form['category'],
            library_id=library_id, user_id=library.user_id)
            session.add(newBook)
            session.commit()
            flash('New Book %s Item Successfully Added' % (newBook.name))
            return redirect(url_for('showBook', library_id=library_id))
    else:
        return render_template('addBook.html', library_id=library_id)


# Edit a Book


@app.route('/library/<int:library_id>/Book/<int:book_id>/edit',
methods=['GET', 'POST'])
def editBook(library_id, book_id):
    """Edit a specific book

    Args:
        library_id: The id of the library which own the book
        book_id: The id of the book required

    Returns:
        on GET: Page to edit a book
        on POST: Redirct to book page after book has been edited
    """
    if 'username' not in login_session:
        return redirect('/login')
    editedBook = session.query(Book).filter_by(id=book_id).one()
    library = session.query(Library).filter_by(id=library_id).one()
    if login_session['user_id'] != library.user_id:
        return "<script>function myFunction() {alert('You are not authorized \
        to edit books to this library. Please create your own library \
        in order to edit books.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedBook.name = request.form['name']
        if request.form['description']:
            editedBook.description = request.form['description']
        if request.form['author']:
            editedBook.author = request.form['author']
        if request.form['category']:
            editedBook.category = request.form['category']
        session.add(editedBook)
        session.commit()
        flash('Book Successfully Edited')
        return redirect(url_for('showBook', library_id=library_id))
    else:
        return render_template('editBook.html', library_id=library_id,
        book_id=book_id, book=editedBook)


# Delete a book
@app.route('/library/<int:library_id>/book/<int:book_id>/delete',
methods=['GET', 'POST'])
def deleteBook(library_id, book_id):
    """Delete a specific book

    Args:
        library_id: The id of the library which own the book
        book_id: The id of the book required

    Returns:
        on GET: Page to delete a book
        on POST: Redirct to book page after book has been deleted
    """
    if 'username' not in login_session:
        return redirect('/login')
    library = session.query(Library).filter_by(id=library_id).one()
    bookToDelete = session.query(Book).filter_by(id=book_id).one()
    if login_session['user_id'] != library.user_id:
        return "<script>function myFunction() {alert('You are not authorized \
        to delete books to this library. Please create your own library \
        in order to delete books.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(bookToDelete)
        session.commit()
        flash('Book Successfully Deleted')
        return redirect(url_for('showBook', library_id=library_id))
    else:
        return render_template('deleteBook.html', book=bookToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showLibrary'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showLibrary'))


# JSON end points
@app.route('/library.json')
def libraryEndpoints():
    """Generate JSON file for all books

    Returns:
        JSON file for all books in all libraries
    """
    books = session.query(Book).all()
    return jsonify(Books=[i.serialize for i in books])


# JSON end points for specific book

@app.route('/book/<int:book_id>/JSON')
def bookEndpoints(book_id):
    """Generate JSON file for a book info

    Args:
        book_id: The id of the book required

    Returns:
        JSON file for book information based on book_id sent
    """

    books = session.query(Book).filter_by(id=book_id)
    return jsonify(Book=[i.serialize for i in books])

# Server Setup
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000, threaded=False)
