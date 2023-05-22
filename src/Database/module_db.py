import sqlite3      # Library allows to use sqlite functionalies to create DB
import sys

# Establish Connection to Databse
# Initialize File where DB is saved
con = sqlite3.connect('myDB.db')
cursor = con.cursor()

# Table Modules contains ID, Module nr.
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Modules (
        ID INTEGER PRIMARY KEY,
        ModuleNr INTEGER UNIQUE
    )
''')

# Table Data, save all necessary Data we need for project
# Furthermore it tells us with the foreign key to which module the data belongs to
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Data (
        TimeStamp TEXT,
        x REAL,
        y REAL,
        z REAL,
        ModuleID INTEGER,
        FOREIGN KEY(ModuleID) REFERENCES Modules(ID)
    )
''')

# Inserting data in table Data
def insert_data(timestamp, x, y, z, module_id):
    timestamp = round(timestamp, 6)  # Round to 6 decimal places
    cursor.execute('INSERT INTO Data (TimeStamp, x, y, z, ModuleID) VALUES (?, ?, ?, ?, ?)',
                   (timestamp, x, y, z, module_id))
    con.commit()

# Help function: to check if there is already an entry for the module -> unique
def module_exists(module_nr):
    cursor.execute('SELECT ID FROM Modules WHERE ModuleNr = ?', (module_nr,))
    result = cursor.fetchone()
    return result is not None

# Inserting ModuleNr. in table Module
def insert_module(module_nr):
    if not module_exists(module_nr):
        cursor.execute('INSERT INTO Modules (ModuleNr) VALUES (?)', (module_nr,))
        con.commit()
        #print("Module {module_nr} inserted successfully.")
    else:
        pass
        #print("Module {module_nr} already exists. Skipping insertion.")

# Read all data from Data
def read_data():
    cursor.execute('SELECT * FROM Data')
    rows = cursor.fetchall()

    for row in rows:
        timestamp = row[0]
        x = row[1]
        y = row[2]
        z = row[3]
        module_id = row[4]

        print("Timestamp: {}, x: {}, y: {}, z: {}, Module ID: {}".format(timestamp, x, y, z, module_id)) # :.6f for Timestamp
        sys.stdout.flush()  # Flush the output to the console, force the output to be immediately displayed on the console

    con.commit()
