'''
db_model.py
'''

import sqlite3
import os

TABLE_MODULES = 'Modules'
TABLE_QUATDATA = 'QuatData'
TABLE_IMUDATA = 'IMUData'
TABLE_TIMERECORD = 'TimeRecord'

class DBModel:

    DATABASE_FILE = 'your_database.db'


    def __init__(self):
        pass

    def init_db(self):
        """
        Erstellt die erforderlichen Tabellen in der Datenbank, falls sie nicht bereits vorhanden sind.
        """
        conn, cursor = self.get_database_connection()

        # Erstellen der Tabelle "Modules"
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_MODULES} (
                ID INTEGER PRIMARY KEY,
                ModuleNR TEXT UNIQUE,
                Type TEXT CHECK(Type IN ('IMU', 'QUATERNION'))
            )
        """)

        # Erstellen der Tabelle "QuatData"
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_QUATDATA} (
                Timestamp TEXT,
                qw REAL,
                qx REAL,
                qy REAL,
                qz REAL,
                ModuleID INTEGER,
                FOREIGN KEY(ModuleID) REFERENCES {TABLE_MODULES}(ID)
            )
        """)

        # Erstellen der Tabelle "IMUData"
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_IMUDATA} (
                Timestamp TEXT,
                x REAL,
                y REAL,
                z REAL,
                ModuleID INTEGER,
                FOREIGN KEY(ModuleID) REFERENCES {TABLE_MODULES}(ID)
            )
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_TIMERECORD} (
                Starttime TEXT UNIQUE,
                Endtime TEXT UNIQUE,
                ModuleID INTEGER,
                FOREIGN KEY(ModuleID) REFERENCES {TABLE_MODULES}(ID)
            )
        """)

        # Schließe die Verbindung zur Datenbank und führe ein Commit durch
        self.close_database_connection(conn)

    def get_database_connection(self):
        """
        Stellt eine Verbindung zur Datenbank her und gibt die Verbindungs- und Cursor-Objekte zurück.
        """
        conn = sqlite3.connect(self.DATABASE_FILE)
        cursor = conn.cursor()
        return conn, cursor

    def close_database_connection(self, conn):
        """
        Schließt die Verbindung zur Datenbank und führt ein Commit durch.

        Args:
            conn: Die Verbindungsinstanz zur Datenbank.
        """
        conn.commit()
        conn.close()

    def insert_quaternion_data(self, module_name, timestamp, qw, qx, qy, qz, starttime, endtime):
        """
        Fügt Quaternion-Daten in die Datenbank ein.

        Args:
            module_name (str): Der Name des Moduls.
            timestamp (str): Der Zeitstempel der Messung.
            qw (float): Der Wert der W-Komponente des Quaternions.
            qx (float): Der Wert der X-Komponente des Quaternions.
            qy (float): Der Wert der Y-Komponente des Quaternions.
            qz (float): Der Wert der Z-Komponente des Quaternions.
        """
        conn, cursor = self.get_database_connection()

        # Überprüfen, ob der Modulname bereits in der Tabelle "Modules" vorhanden ist
        cursor.execute(f"SELECT ID FROM {TABLE_MODULES} WHERE ModuleNR = ?", (module_name,))
        result = cursor.fetchone()
        if result is None:
            # Modulname ist noch nicht vorhanden, füge einen neuen Eintrag hinzu
            cursor.execute(f"INSERT INTO {TABLE_MODULES} (ModuleNR, Type) VALUES (?, 'QUATERNION')", (module_name,))
            module_id = cursor.lastrowid
        else:
            # Modulname ist bereits vorhanden, verwende die vorhandene ID
            module_id = result[0]

        # Daten in der Tabelle "QuatData" speichern
        cursor.execute(f"INSERT INTO {TABLE_QUATDATA} (Timestamp, qw, qx, qy, qz, ModuleID) VALUES (?, ?, ?, ?, ?, ?)",
                       (timestamp, qw, qx, qy, qz, module_id))

        # Startzeitpunkt in der Tabelle "TimeRecord" speichern oder aktualisieren
        cursor.execute(f"INSERT OR REPLACE INTO {TABLE_TIMERECORD} (StartTime, ModuleID) VALUES (?, ?)",
                       (starttime, module_id))

        # Endzeitpunkt in der Tabelle "TimeRecord" speichern oder aktualisieren
        cursor.execute(f"INSERT OR REPLACE INTO {TABLE_TIMERECORD} (EndTime, ModuleID) VALUES (?, ?)",
                       (endtime, module_id))

        # Schließe die Verbindung zur Datenbank und führe ein Commit durch
        self.close_database_connection(conn)

    def insert_imu_data(self, module_name, timestamp, x, y, z, starttime, endtime):
        """
        Fügt IMU-Daten in die Datenbank ein.

        Parameter:
        - module_name: Name des Moduls
        - timestamp: Zeitstempel der Messung
        - x, y, z: IMU-Daten

        Rückgabewert:
        None
        """
        conn, cursor = self.get_database_connection()

        # Überprüfen, ob das Modul bereits in der Tabelle "Modules" vorhanden ist
        cursor.execute(f"SELECT ID FROM {TABLE_MODULES} WHERE ModuleNR = ?", (module_name,))
        module_id = cursor.fetchone()

        if module_id is None:
            # Modulname ist noch nicht vorhanden, füge einen neuen Eintrag hinzu
            cursor.execute(f"INSERT INTO {TABLE_MODULES} (ModuleNR, Type) VALUES (?, 'IMU')", (module_name,))
            module_id = cursor.lastrowid
        else:
            module_id = module_id[0]

        # IMU-Daten in die Tabelle "IMUData" einfügen
        cursor.execute(f"INSERT INTO {TABLE_IMUDATA} (Timestamp, x, y, z, ModuleID) VALUES (?, ?, ?, ?, ?)",
                       (timestamp, x, y, z, module_id))

        # Startzeitpunkt in der Tabelle "TimeRecord" speichern oder aktualisieren
        cursor.execute(f"INSERT OR REPLACE INTO {TABLE_TIMERECORD} (StartTime, ModuleID) VALUES (?, ?)",
                       (starttime, module_id))

        # Endzeitpunkt in der Tabelle "TimeRecord" speichern oder aktualisieren
        cursor.execute(f"INSERT OR REPLACE INTO {TABLE_TIMERECORD} (EndTime, ModuleID) VALUES (?, ?)",
                       (endtime, module_id))


        # Schließe die Verbindung zur Datenbank und führe ein Commit durch
        self.close_database_connection(conn)

    def read_data(self, module_name):
        """
        Liest Daten aus der Datenbank basierend auf dem Modulnamen.

        Args:
            module_name (str): Der Name des Moduls.

        Returns:
            list: Eine Liste der abgerufenen Daten. Wenn das Modul nicht gefunden wird, wird None zurückgegeben.

        """
        # Verbindung zur Datenbank herstellen
        conn, cursor = self.get_database_connection()

        # Modul-ID anhand des Modulnamens abrufen
        cursor.execute("SELECT ID, Type FROM Modules WHERE ModuleNR = ?", (module_name,))
        module_info = cursor.fetchone()

        if module_info is None:
            print("Modul nicht gefunden")
            # Datenbankverbindung schließen
            self.close_database_connection(conn)
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

            # Datenbankverbindung schließen
            self.close_database_connection(conn)
            return imu_data

        elif module_type == "QUATERNION":
            cursor.execute("SELECT Timestamp, qw, qx, qy, qz FROM QuatData WHERE ModuleID = ?", (module_id,))
            quat_data = cursor.fetchall()

            print("Quaternion-Daten:")
            for data in quat_data:
                timestamp, qw, qx, qy, qz = data
                print("Timestamp:", timestamp, "qw:", qw, "qx:", qx, "qy:", qy, "qz:", qz)

            # Datenbankverbindung schließen
            self.close_database_connection(conn)
            return quat_data

    def read_modules_data_from_database(self):
        """
        Liest Daten aus der Tabelle "Modules" der Datenbank.

        Returns:
            list: Eine Liste der abgerufenen Daten. Wenn die Tabelle "Modules" nicht existiert oder die Datenbank leer ist, wird None zurückgegeben.

        Raises:
            None

        """
        conn, cursor = self.get_database_connection()

        # Versuche, die Tabelle "Modules" abzurufen
        try:
            cursor.execute("SELECT * FROM Modules")
            module_data = cursor.fetchall()

            print("Modules Data:")
            for row in module_data:
                print(row)

            self.close_database_connection(conn)
            return module_data
        except sqlite3.OperationalError:
            print("Table 'Modules' does not exist or database is empty.")
            self.close_database_connection(conn)
            return None

    def read_quat_data_from_database(self):
        """
        Liest Daten aus der Tabelle "QuatData" der Datenbank.

        Returns:
            list: Eine Liste der abgerufenen Daten.

        Raises:
            None

        """
        conn, cursor = self.get_database_connection()

        cursor.execute("SELECT * FROM QuatData")
        quat_data = cursor.fetchall()

        self.close_database_connection(conn)

        print("QuatData:")
        for row in quat_data:
            print(row)

        return quat_data

    def read_imu_data_from_database(self):
        """
        Liest Daten aus der Tabelle "IMUData" der Datenbank.

        Returns:
            list: Eine Liste der abgerufenen Daten.

        Raises:
            None

        """
        conn, cursor = self.get_database_connection()

        cursor.execute("SELECT * FROM IMUData")
        imu_data = cursor.fetchall()

        self.close_database_connection(conn)

        print("IMUData:")
        for row in imu_data:
            print(row)

        return imu_data

    def delete_database(self):
        """
        Löscht die gesamte Datenbank, einschließlich aller Tabellen.

        Args:
            None

        Returns:
            None

        Raises:
            None

        """
        conn, cursor = self.get_database_connection()

        # Alle Tabellen in der Datenbank löschen
        cursor.execute("DROP TABLE IF EXISTS Modules")
        cursor.execute("DROP TABLE IF EXISTS QuatData")
        cursor.execute("DROP TABLE IF EXISTS IMUData")

        self.close_database_connection(conn)

         # Datenbankdatei löschen
        database_path = "your_database.db"  # Passe den Dateipfad entsprechend an
        if os.path.exists(database_path):
            os.remove(database_path)
            print("Database deleted.")
        else:
            print("Database file not found.")
            print("Database deleted.")
        print("Database deleted.")

    def read_modules(self, database_file):
        """
        Liest Daten aus der Tabelle "Modules" der Datenbank.

        Returns:
            list: Eine Liste der abgerufenen Daten. Wenn die Tabelle "Modules" nicht existiert oder die Datenbank leer ist, wird None zurückgegeben.

        Raises:
            None

        """
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()

        # Versuche, die Tabelle "Modules" abzurufen
        try:
            cursor.execute("SELECT * FROM Modules")
            module_data = cursor.fetchall()

            print("Modules Data:")
            for row in module_data:
                print(row)

            self.close_database_connection(conn)
            return module_data
        except sqlite3.OperationalError:
            print("Table 'Modules' does not exist or database is empty.")
            self.close_database_connection(conn)
            return None

    def get_last_timestamp(self, module_name):
        """
        Ruft den letzten Timestamp basierend auf dem Modulnamen ab.

        Args:
            module_name (str): Der Name des Moduls.

        Returns:
            str: Der letzte Timestamp für das angegebene Modul. Wenn das Modul nicht gefunden wird oder keine Daten vorhanden sind, wird None zurückgegeben.

        """
        conn, cursor = self.get_database_connection()

        # Modul-ID anhand des Modulnamens abrufen
        cursor.execute("SELECT ID, Type FROM Modules WHERE ModuleNR = ?", (module_name,))
        module_info = cursor.fetchone()

        if module_info is None:
            print("Modul nicht gefunden")
            # Datenbankverbindung schließen
            self.close_database_connection(conn)
            return None

        module_id, module_type = module_info

        # IMU-Daten oder Quaternion-Daten abhängig vom Modultyp abrufen und den letzten Timestamp zurückgeben
        if module_type == "IMU":
            cursor.execute("SELECT MAX(Timestamp) FROM IMUData WHERE ModuleID = ?", (module_id,))
            last_timestamp = cursor.fetchone()[0]

        elif module_type == "QUATERNION":
            cursor.execute("SELECT MAX(Timestamp) FROM QuatData WHERE ModuleID = ?", (module_id,))
            last_timestamp = cursor.fetchone()[0]

        # Datenbankverbindung schließen
        self.close_database_connection(conn)

        return last_timestamp

    def get_starttime(self, module_name):
        """
        Gibt den Startzeitpunkt für das angegebene Modul zurück.

        Args:
            module_name (str): Der Name des Moduls.

        Returns:
            str: Der Startzeitpunkt oder None, wenn das Modul nicht gefunden wurde.
        """
        conn, cursor = self.get_database_connection()

        # Startzeitpunkt für das Modul abrufen
        cursor.execute(f"SELECT StartTime FROM {TABLE_TIMERECORD} "
                       f"INNER JOIN {TABLE_MODULES} ON {TABLE_TIMERECORD}.ModuleID = {TABLE_MODULES}.ID "
                       f"WHERE {TABLE_MODULES}.ModuleNR = ?", (module_name,))
        result = cursor.fetchone()

        # Schließe die Verbindung zur Datenbank
        self.close_database_connection(conn)

        if result is not None:
            return result[0]
        else:
            return None

    def get_endtime(self, module_name):
        """
        Gibt den Startzeitpunkt für das angegebene Modul zurück.

        Args:
            module_name (str): Der Name des Moduls.

        Returns:
            str: Der Startzeitpunkt oder None, wenn das Modul nicht gefunden wurde.
        """
        conn, cursor = self.get_database_connection()

        # Startzeitpunkt für das Modul abrufen
        cursor.execute(f"SELECT StartTime FROM {TABLE_TIMERECORD} "
                       f"INNER JOIN {TABLE_MODULES} ON {TABLE_TIMERECORD}.ModuleID = {TABLE_MODULES}.ID "
                       f"WHERE {TABLE_MODULES}.ModuleNR = ?", (module_name,))
        result = cursor.fetchone()

        # Schließe die Verbindung zur Datenbank
        self.close_database_connection(conn)

        if result is not None:
            return result[0]
        else:
            return None
