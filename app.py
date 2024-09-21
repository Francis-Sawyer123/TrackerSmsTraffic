from flask import Flask, render_template, request, redirect, url_for
from twilio.rest import Client
import folium
import requests


account_sid = ''
auth_token = ''
twilio_number = ''


opencellid_api_key = ''


app = Flask(__name__)

client = Client(account_sid, auth_token)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_sms', methods=['POST'])
def send_sms():

    to_number = request.form['submitnumber']
    if not to_number.startswith('+') or not to_number[1:].isdigit():
        return "Invalid phone number format. Please use E.164 format.", 400

    try:
        message = client.messages.create(
            body=request.form['message'],
            from_=twilio_number,
            to=to_number,
            status_callback=request.url_root + 'sms-status'
        )
    except Exception as e:
        return str(e), 400

    return redirect(url_for('index'))

@app.route('/map')
def map_view():
    lat = 116.727462768555
    lon = 115.55592346191
    radius = 1000

    url = 'https://us1.unwiredlabs.com/v2/process.php'
    payload = {
        'token': opencellid_api_key,
        'radio': 'gsm',
        'mcc': 515, 
        'mnc': 2,  
        'cells': 1,
        'cells_limit': 10,
        'lat': lat,
        'lon': lon,
        'range': radius
    }
    
    response = requests.post(url, json=payload)
    data = response.json()
    
    if 'cells' in data:
        cell_towers = data['cells']
    else:
        cell_towers = []

    m = folium.Map(location=[lat, lon], zoom_start=18)

    for tower in cell_towers:
        folium.Marker(
            location=[tower["lat"], tower["lon"]],
            popup=f'Cell Tower ID: {tower["cellId"]}',
            icon=folium.Icon(icon='cloud')
        ).add_to(m)

    m.save('templates/cell_tower_map.html')

    return render_template('cell_tower_map.html')

if __name__ == '__main__':
    app.run(debug=True)
