# app.py
from flask import Flask, render_template, request
from views import tracking_bp
from model import db
import sqlite3

app = Flask(__name__)

# Register the tracking blueprint
app.register_blueprint(tracking_bp)

@app.route('/')
def home():
    db.create_tables()
    tables_are_valid = db.test_created_tables()

    if not tables_are_valid:
        print("The tables were not created successfully. Please check the database and try again.")
        exit()
    else:
        db.import_gpx_files()
        return render_template('index.html')
    
@app.route('/index.html', methods=['GET', 'POST'])
def forward_to_index():
    return render_template('index.html')


@app.route('/query', methods=['GET', 'POST'])
def forward_to_map():
    if request.method == 'POST':
        if "such-button" in request.form:

            # Get form data from request
            initials        = request.form['initials']
            license_plate   = request.form['license-plate']
            datefrom        = request.form['date-from']
            dateto          = request.form['date-to']
        
            # Connect to database and execute query
            conn    = sqlite3.connect('gps_tracking.db')
            c       = conn.cursor()
            query   = '''SELECT tp.latitude, tp.longitude, tp.elevation FROM person AS p
                        INNER JOIN track        AS t    ON t.person_id  = p.id
                        INNER JOIN vehicle      AS v    ON v.id         = t.vehicle_id
                        INNER JOIN trackpoint   AS tp   ON tp.track_id  = t.id
                        WHERE p.initials = ? AND v.license_plate = ? AND (SELECT is_valid FROM protocol WHERE is_valid = '1') AND tp.date BETWEEN ? AND ?'''
            

            c.execute(query, (initials, license_plate, datefrom, dateto))
            print(query)
            trackpoints = c.fetchall()
            conn.close()

            # Convert trackpoints to coordinates list and render template
            coordinates = [(track[0], track[1]) for track in trackpoints]

            # weitere querys für z.b. Gesamtlänge des Tracks: {{distance}}<br></br>Durchschnittliche Geschwindigkeit: {{avg_velocity}}<br></br>Durchschnittliche Höhe der Strecke: {{avg_height}}<br></br>



            return render_template('map.html', coordinates = coordinates, initials = initials, license_plate = license_plate, datefrom = datefrom, dateto = dateto)



if __name__ == '__main__':       
    app.run(debug=True)

    