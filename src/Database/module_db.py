import sqlite3      # Library allows to use sqlite functionalies to create DB
#import sys
#import os

def init_db():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    # Erstellen der Tabelle "Modules"
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Modules (
            ID INTEGER PRIMARY KEY,
            ModuleNR TEXT UNIQUE,
            Type TEXT CHECK(Type IN ('IMU', 'QUATERNION'))
        )
    """)

    # Erstellen der Tabelle "QuatData"
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS QuatData (
            Timestamp TEXT,
            qw REAL,
            qx REAL,
            qy REAL,
            qz REAL,
            ModuleID INTEGER,
            FOREIGN KEY(ModuleID) REFERENCES Modules(ID)
        )
    """)

    # Erstellen der Tabelle "IMUData"
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS IMUData (
            Timestamp TEXT,
            x REAL,
            y REAL,
            z REAL,
            ModuleID INTEGER,
            FOREIGN KEY(ModuleID) REFERENCES Modules(ID)
        )
    """)

    # Änderungen in der Datenbank speichern
    conn.commit()

    # Datenbankverbindung schließen
    conn.close()

def insert_quaternion_data(module_name, timestamp, qw, qx, qy, qz):
    # Verbindung zur Datenbank herstellen oder eine neue Datenbank erstellen
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    # Überprüfen, ob der Modulname bereits in der Tabelle "Modules" vorhanden ist
    cursor.execute("SELECT ID FROM Modules WHERE ModuleNR = ?", (module_name,))
    result = cursor.fetchone()
    if result is None:
        # Modulname ist noch nicht vorhanden, füge einen neuen Eintrag hinzu
        cursor.execute("INSERT INTO Modules (ModuleNR, Type) VALUES (?, 'QUATERNION')", (module_name,))
        module_id = cursor.lastrowid
    else:
        # Modulname ist bereits vorhanden, verwende die vorhandene ID
        module_id = result[0]

    # Daten in der Tabelle "QuatData" speichern
    cursor.execute("INSERT INTO QuatData (Timestamp, qw, qx, qy, qz, ModuleID) VALUES (?, ?, ?, ?, ?, ?)",
                   (timestamp, qw, qx, qy, qz, module_id))

    # Änderungen in der Datenbank speichern
    conn.commit()

    # Datenbankverbindung schließen
    conn.close()

def insert_imu_data(module_name, timestamp, x, y, z):
    # Verbindung zur Datenbank herstellen oder eine neue Datenbank erstellen
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    # Überprüfen, ob das Modul bereits in der Tabelle "Modules" vorhanden ist
    cursor.execute("SELECT ID FROM Modules WHERE ModuleNR = ?", (module_name,))
    module_id = cursor.fetchone()

    if module_id is None:
        # Modulname ist noch nicht vorhanden, füge einen neuen Eintrag hinzu
        cursor.execute("INSERT INTO Modules (ModuleNR, Type) VALUES (?, 'IMU')", (module_name,))
        module_id = cursor.lastrowid
    else:
        module_id = module_id[0]

    # IMU-Daten in die Tabelle "IMUData" einfügen
    cursor.execute("INSERT INTO IMUData (Timestamp, x, y, z, ModuleID) VALUES (?, ?, ?, ?, ?)",
                   (timestamp, x, y, z, module_id))

    # Änderungen in der Datenbank speichern
    conn.commit()

    # Datenbankverbindung schließen
    conn.close()

def read_data(module_name):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    # Modul-ID anhand des Modulnamens abrufen
    cursor.execute("SELECT ID, Type FROM Modules WHERE ModuleNR = ?", (module_name,))
    module_info = cursor.fetchone()

    if module_info is None:
        print("Modul nicht gefunden")
        return module_info

    module_id, module_type = module_info

    # IMU-Daten oder Quaternion-Daten abhängig vom Modultyp abrufen und ausgeben
    if module_type == "IMU":
        cursor.execute("SELECT Timestamp, x, y, z FROM IMUData WHERE ModuleID = ?", (module_id,))
        imu_data = cursor.fetchall()


        print("IMU-Daten:")
        for data in imu_data:
            timestamp, x, y, z = data
            print("Timestamp:", timestamp, "x:", x, "y:", y, "z:", z)

        return imu_data

    elif module_type == "QUATERNION":
        cursor.execute("SELECT Timestamp, qw, qx, qy, qz FROM QuatData WHERE ModuleID = ?", (module_id,))
        quat_data = cursor.fetchall()


        print("Quaternion-Daten:")
        for data in quat_data:
            timestamp, qw, qx, qy, qz = data
            print("Timestamp:", timestamp, "qw:", qw, "qx:", qx, "qy:", qy, "qz:", qz)

        return quat_data


    # Datenbankverbindung schließen
    conn.close()


def read_modules_data_from_database():
    # Verbindung zur Datenbank im Speicher herstellen
    #conn = sqlite3.connect(":memory:")
    #cursor = conn.cursor()

    connection = sqlite3.connect("your_database.db")
    cursor = connection.cursor()

    # Pfad zur Datenbank angeben
    database_path = 'your_database.db'

    # Versuche, die Tabelle "Modules" abzurufen
    try:
        cursor.execute("SELECT * FROM Modules")
        module_data = cursor.fetchall()

        print("Modules Data:")
        for row in module_data:
            print(row)

        return module_data
    except sqlite3.OperationalError:
        print("Table 'Modules' does not exist or database is empty.")
        return None

    # Verbindung schließen
    conn.close()


def read_quat_data_from_database():
    connection = sqlite3.connect("your_database.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM QuatData")
    quat_data = cursor.fetchall()

    connection.close()

    print("QuatData:")
    for row in quat_data:
        print(row)

    connection.close()

    return quat_data


def read_imu_data_from_database():
    connection = sqlite3.connect("your_database.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM IMUData")
    imu_data = cursor.fetchall()

    connection.close()

    print("IMUData:")
    for row in imu_data:
        print(row)

    connection.close()

    return imu_data

def delete_database():
    # Pfad zur aktuellen Datenbank angeben
    database_path = 'your_database.db'

    # Überprüfen, ob die Datenbankdatei existiert
    if os.path.exists(database_path):
        # Verbindung zur Datenbank herstellen und Cursor erstellen
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Alle Tabellen in der Datenbank löschen
        cursor.execute("DROP TABLE IF EXISTS Modules")
        cursor.execute("DROP TABLE IF EXISTS QuatData")
        cursor.execute("DROP TABLE IF EXISTS IMUData")

        # Änderungen in der Datenbank speichern und Verbindung schließen
        conn.commit()
        conn.close()

        # Datenbankdatei löschen
        os.remove(database_path)
        print("Database deleted.")
    else:
        print("Database does not exist.")
