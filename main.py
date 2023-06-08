from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['covid_vaccination_booking']
users_collection = db['users']
centers_collection = db['vaccination_centers']
bookings_collection = db['bookings']

# Routes for user functionalities

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    #if 'user_id' in session:
     #   return redirect('/dashboard')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({'username': username, 'password': password})
        
        
        if user and user['role'] == 'admin':
            session['user_id'] = str(user['_id'])
            return redirect('/admin_dashboard')
        
        else:
            
            if user:
                session['user_id'] = str(user['_id'])
                return redirect('/dashboard')
            
            else :
            
                return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    #if 'user_id' in session:
    #   return redirect('/dashboard')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = users_collection.find_one({'username': username})

        if existing_user:
            return render_template('signup.html', error='Username already exists')

        user_data = {'username': username, 'password': password, "role": "user"}
        user_id = users_collection.insert_one(user_data).inserted_id

        session['user_id'] = str(user_id)
        return redirect('/dashboard')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html',msg='You have been logged out')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        return render_template('dashboard.html', user=user, filter_centers=centers_collection.find(), bookings=bookings_collection.find())
    else:
        return redirect('/login')

# Routes for admin functionalities

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        return render_template('admin_dashboard.html', user=user, centers=centers_collection.find(), bookings=bookings_collection.find())
    else:
        return redirect('/login')
    
@app.route('/add_center', methods=['POST'])
def add_center():
    center_name = request.form['center_name']
    location = request.form['location']
    center={'name':center_name, 'location':location, 'from_time':'7:00 AM', 'to_time':'10:00 PM'}
    center_id=centers_collection.insert_one(center).inserted_id
    return redirect('/admin_dashboard')

@app.route('/remove_center',methods=['POST'])
def remove_center():
    center_id=request.form['center_id']
    centers_collection.delete_one({'_id':ObjectId(center_id)})
    return redirect('/admin_dashboard')

@app.route('/filter',methods=['POST'])
def filter():
    filter_loc = request.form['filter_loc']
    
    if filter_loc:
        if 'user_id' in session:
            user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if filter_loc == 'all':
            centers = centers_collection.find()
        else:
            centers = centers_collection.find({'location': filter_loc})

        return render_template('dashboard.html', user=user,bookings=bookings_collection.find(),centers=centers)
    redirect('/dashboard')
    
@app.route('/booking',methods=['POST'])
def booking():
    book_user = request.form['book_user']
    book_location = request.form['book_location']
    book_centre = request.form['book_centre']
    book_slot = request.form['book_slot']
    book_date = request.form['book_date']
    
    hash = '#'+ book_location + book_slot + book_date
    
    existing_hash = bookings_collection.find_one({'hash': hash})

    if existing_hash:
        if 'user_id' in session:
            user_id = session['user_id']
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        return render_template('dashboard.html', user=user, centers=centers_collection.find(), bookings=bookings_collection.find(),error='Slot already Booked !!!, Please select another slot')
        
    
    booking={'hash':hash,'user':book_user,'location':book_location, 'centre':book_centre, 'slot':book_slot, 'date':book_date, 'status':'Booked'}
    booking_id=bookings_collection.insert_one(booking).inserted_id
    return redirect('/dashboard')
    
    
  

if __name__ == '__main__':
    app.run(debug=True)
