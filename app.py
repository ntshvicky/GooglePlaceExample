from flask import Flask,render_template, request, jsonify,session,redirect
from googleplaces import GooglePlaces, types, lang 
import requests 
import json 
import geocoder  
import hashlib
import time

from database.db import initialize_db
from database.models import User, Comment

app = Flask(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
#google map api details
API_KEY = 'Write API Key Here'

#set database connection details
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost:27017/testdb'
}

db = initialize_db(app)

@app.route('/')
def index_func():
    return render_template("index.html")

@app.route('/dashboard')
def dashboard_func():
    print(session)
    if session["user"]==False:
        return redirect("/")
    # Read Your LATLNG
    google_places = GooglePlaces(API_KEY) 
    g = geocoder.ip('me')

    # Read Places
    query_result = google_places.nearby_search( 
        # lat_lng ={'lat': 46.1667, 'lng': -1.15}, 
        lat_lng ={'lat': g.latlng[0], 'lng': g.latlng[1]}, 
        radius = 5000, 
        # types =[types.TYPE_HOSPITAL] or 
        # [types.TYPE_CAFE] or [type.TYPE_BAR] 
        # or [type.TYPE_CASINO]) 
        types =[types.TYPE_CAFE,types.TYPE_BAR,types.TYPE_CASINO]) 

    # If any attributions related  
    # with search results print them 
    if query_result.has_attributions: 
        print (query_result.html_attributions) 
    
    
    # Iterate over the search results 
    list = []
    for place in query_result.places: 
        # print(type(place)) 
        #print(dir(place)) 
        #print (place.name) 
        #print("Latitude", place.geo_location['lat']) 
        #print("Longitude", place.geo_location['lng']) 
        #print() 
        plc = {}
        plc['place']=place.name
        plc['place_id']=place.id
        plc['icon']=place.icon
        plc['lat']=str(place.geo_location['lat'])
        plc['lang']=str(place.geo_location['lng'])
        list.append(plc)
        
    return render_template('dashboard.html', maps=list)


@app.route('/map')
def map_func():
    args = request.args
    import folium
    map = folium.Map(location=[args["lat"],args["lang"]], tiles="Stamen Terrain")
    map.add_child(folium.Marker(location=[args["lat"],args["lang"]], popup="Hi! You are welcome", tooltip="marker", icon=folium.Icon(color="red")))
    import os
    if os.path.exists("templates/map2.html"):
        os.remove("templates/map2.html")
    map.save("templates/map2.html")
    return render_template('map.html')

@app.route('/frame')
def frame():
    return render_template('map2.html')

@app.route('/register', methods=["post"])
def register():
    form = request.form
    dbs = User(phone=form["phone"], fullname=form["name"], mailid=form["email"], password=form["psw"]).save()
    resp = jsonify({'message' : 'data successful update'})
    resp.status_code = 200
    return resp  

@app.route('/savecomment', methods=["post"])
def savecomment():
    form = request.form
    print(form)
    phone = session["user"]["phone"]
    dbs = Comment(place_id=form["plcid"], comment=form["comment"], user_id=phone).save()
    resp = jsonify({'message' : 'comment successful update'})
    resp.status_code = 200
    return resp 

@app.route("/authenticate_form", methods=["post"])
def authenticate_form():
    if request.form['username']!="" or request.form["password"]!="":
        phone = request.form["username"]
        password = request.form["password"]
        for x in User.objects(phone=phone, password=password):
            session["user"] = x
            resp = jsonify({'message' : 'Successful login'})
            resp.status_code = 200
            return resp
    else:
        resp = jsonify({'message' : '0'})
        resp.status_code = 400
        return resp

    resp = jsonify({'message' : '0'})
    resp.status_code = 400
    return resp

@app.route("/logout", methods=["post","get"])
def logout():
    session.clear()
    try:
        del session['user']
    except:
        pass
    app.secret_key = hashlib.sha256(str(time.time()).encode()).hexdigest()
    return redirect('/')

@app.route('/loadcomment', methods=['POST','GET'])
def loadcomment():
    try:
        table = "<table><tr><td>Phone Number</td><td>Comment</td></tr>"
        tkno = request.form
        print(tkno)
        for ticket in Comment.objects(place_id=tkno["plcid"]):
            table += "<tr><td>{}</td><td>{}</td></tr>".format(ticket.user_id, ticket.comment)
        table += "</table>"
        print(table)
        errors = {}
        errors['message'] = 'success'
        errors['data'] = table
        resp = jsonify(errors)
        resp.status_code = 201
        return resp
    except:
        resp = jsonify({'message':'No data found'})
        resp.status_code = 400
        return resp

if __name__ == '__main__':
    app.run(debug = True)    