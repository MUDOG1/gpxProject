import sqlite3
import os
import gpxpy


def create_tables():
    conn = sqlite3.connect('gps_tracking.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS person
                (id        INTEGER PRIMARY KEY,
                initials   TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS vehicle
                (id            INTEGER PRIMARY KEY,
                license_plate  TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS track
                (id            INTEGER PRIMARY KEY,
                filename       TEXT,
                person_id      INTEGER,
                vehicle_id     INTEGER,
                date           TEXT,
                FOREIGN KEY (person_id)    REFERENCES person(id),
                FOREIGN KEY (vehicle_id)   REFERENCES vehicle(id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS trackpoint
                (id            INTEGER PRIMARY KEY,
                track_id       INTEGER,
                latitude       REAL,
                longitude      REAL,
                elevation      REAL,
                date           TEXT,
                time           TEXT,
                temperature    REAL,
                hr             INTEGER,
                FOREIGN KEY (track_id) REFERENCES track(id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS protocol
                (id            INTEGER PRIMARY KEY,
                filename       TEXT,
                track_id       INTEGER,
                is_valid       VARCHAR(1),
                FOREIGN KEY (track_id) REFERENCES track(id))''')

    conn.close()


def test_created_tables():
    conn = sqlite3.connect('gps_tracking.db')
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()

    assert ('person',) in tables
    assert ('vehicle',) in tables
    assert ('track',) in tables
    assert ('trackpoint',) in tables
    assert ('protocol',) in tables

    print("All tables were created successfully.")
    conn.close()
    return True


def parse_gpx_file(filename):
    with open(filename, 'r') as gpx_file:
        return gpxpy.parse(gpx_file)


def extract_person_data(filename):
    filename_parts = filename.split("_")
    if len(filename_parts) >= 3:
        initials = filename_parts[0]
        return initials
    else:
        return None


def extract_track_data(filename):
    return filename[:-4]


def extract_vehicle_data(filename):
    filename_parts = filename.split("_")
    if len(filename_parts) >= 3:
        vehicle_license_plate = filename_parts[1]
        vehicle_license_plate = vehicle_license_plate.replace("-", "")
        return vehicle_license_plate
    else:
        return None


def extract_trackpoint_data(c, track_id, gpx, filename):
    print(filename)
    if gpx.tracks is not None:
        if len(gpx.tracks) > 0:
            for track in gpx.tracks:
                if len(track.segments) > 0:
                    for segment in track.segments:
                        for point in segment.points:
                            lat = point.latitude
                            lon = point.longitude
                            ele = point.elevation
                            tp_time = point.time
                            atemp = None
                            hr = None
                            if point.extensions is not None:
                                for extension in point.extensions:
                                    if extension.tag.endswith("TrackPointExtension"):
                                        for child in extension.iter():
                                            if child.tag.endswith("atemp"):
                                                atemp = child.text
                                            elif child.tag.endswith("hr"):
                                                hr = child.text

                            is_valid = lat is not None or lon is not None or ele is not None

                            if not is_valid:
                                is_valid_value = '0'
                                c.execute("INSERT INTO protocol (filename, track_id, is_valid) VALUES (?, ?, ?)", (
                                    filename, track_id, is_valid_value))
                                break
                            else:
                                is_valid_value = '1'
                                if tp_time is not None:
                                    tp_time_date = tp_time.date()
                                    tp_time_time = tp_time.time()
                                else:
                                    tp_time_date = None
                                    tp_time_time = None
                                c.execute("INSERT INTO trackpoint (track_id, latitude, longitude, elevation, date, time, temperature, hr) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
                                    track_id, lat, lon, ele, str(tp_time_date), str(tp_time_time), atemp, hr))
                                c.execute(
                                    "UPDATE track SET date = ? WHERE id = ?", (tp_time_date, track_id))
                else:
                    is_valid_value = '0'
            c.execute("INSERT INTO protocol (filename, track_id, is_valid) VALUES (?, ?, ?)",
                      (filename, track_id, is_valid_value))
        else:
            if gpx.waypoints is not None:
                for waypoint in gpx.waypoints:
                    lat = waypoint.latitude
                    lon = waypoint.longitude
                    ele = waypoint.elevation
                    tp_time = waypoint.time

                    is_valid = lat is not None or lon is not None or ele is not None

                    if not is_valid:
                        is_valid_value = '0'
                        c.execute("INSERT INTO protocol (filename, track_id, is_valid) VALUES (?, ?, ?)", (
                            filename, track_id, is_valid_value))
                        break
                    else:
                        is_valid_value = '1'
                        if tp_time is not None:
                            tp_time_date = tp_time.date()
                            tp_time_time = tp_time.time()
                        else:
                            tp_time_date = None
                            tp_time_time = None
                        c.execute("INSERT INTO trackpoint (track_id, latitude, longitude, elevation, date, time) VALUES (?, ?, ?, ?, ?, ?)", (
                            track_id, lat, lon, ele, str(tp_time_date), str(tp_time_time)))
                        c.execute("UPDATE track SET date = ? WHERE id = ?",
                                  (tp_time_date, track_id))

                c.execute("INSERT INTO protocol (filename, track_id, is_valid) VALUES (?, ?, ?)",
                          (filename, track_id, is_valid_value))


def insert_person_data(c, initials):
    c.execute("INSERT INTO person (initials) VALUES (?)", (initials,))
    return c.lastrowid


def insert_vehicle_data(c, vehicle_license_plate):
    c.execute("INSERT INTO vehicle (license_plate) VALUES (?)",
              (vehicle_license_plate,))
    return c.lastrowid


def insert_track_data(c, filename, person_id, vehicle_id):
    c.execute("INSERT INTO track (filename, person_id, vehicle_id) VALUES (?, ?, ?)",
              (filename, person_id, vehicle_id))
    return c.lastrowid


def import_gpx_files():
    conn = sqlite3.connect('gps_tracking.db')
    c = conn.cursor()

    imported_files = set()

    c.execute("SELECT filename FROM protocol")
    existing_files = c.fetchall()
    for existing_file in existing_files:
        imported_files.add(existing_file[0])

    for filename in os.listdir('./gpx'):
        if filename.endswith('.gpx') and filename not in imported_files:
            gpx = parse_gpx_file('./gpx/' + filename)
            # gpx = parse_gpx_file(os.path.join('./data/gpx', filename))
            person_initials = extract_person_data(filename)
            person_id = insert_person_data(c, person_initials)
            vehicle_license_plate = extract_vehicle_data(filename)
            vehicle_id = insert_vehicle_data(c, vehicle_license_plate)
            track_filename = extract_track_data(filename)
            track_id = insert_track_data(
                c, track_filename, person_id, vehicle_id)
            extract_trackpoint_data(c, track_id, gpx, filename)
            conn.commit()

            imported_files.add(filename)
    conn.close()



