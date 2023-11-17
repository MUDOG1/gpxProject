# from flask import render_template, request
# import sqlite3
# from . import tracking_bp

# @tracking_bp.route('/eingabe', methods=['GET', 'POST'])
# def tracking():
#     if request.method == 'POST':
#         # Get form data from request
#         initials        = request.form['initials']
#         license_plate = request.form['license-plate']
#         #datefrom    = request.form['datefrom']
#         #dateto      = request.form['dateto']
        
#         # Connect to database and execute query
#         conn    = sqlite3.connect('gps_tracking.db')
#         c       = conn.cursor()
#         query   = '''SELECT tp.latitude, tp.longitude, tp.elevation FROM person AS p
#                         INNER JOIN track        AS t    ON t.person_id  = p.id
#                         INNER JOIN vehicle      AS v    ON v.id         = t.vehicle_id
#                         INNER JOIN trackpoint   AS tp   ON tp.track_id  = t.id
#                         WHERE p.initials = ? AND v.license_plate = ? AND (SELECT is_valid FROM protocol WHERE is_valid = '1')'''
#         c.execute(query, (initials, license_plate))
#         trackpoints = c.fetchall()
#         for trackpoint in trackpoints:
#             print(trackpoint)
#         conn.close()

#         # Convert trackpoints to coordinates list and render template
#         coordinates = [(track[0], track[1]) for track in trackpoints]
#         return render_template('map.html', coordinates=coordinates)