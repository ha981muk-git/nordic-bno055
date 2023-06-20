
'''
db_controller.py
'''
import serial
import sqlite3
import time
import threading
from tkinter import filedialog

from db_view import DBView
from db_model import DBModel



class DBController:

    def __init__(self):
        self.db_view  = DBView(self)
        self.db_model = DBModel()

        self.serial_thread = None
        self.stop_serial_flag = False
        self.nrf_data = None
        self.write = False
        self.timeflag = []

    def main(self):
        self.db_view.main()

    '''
    Funktionaler Teil für den ersten Tab
    '''

    def confirm_button(self):
        selected_port = self.db_view.port_var.get()
        if selected_port != "Wähle einen Port":
            self.connect_to_serial(selected_port)
            self.start_serial_read(self.nrf_data)  # Daten vom COM-Port lesen
            self.db_view.switch_confirm_button_off()
        else:
            self.db_view.show_warning_message("Fehler", "Bitte wähle einen COM-Port aus.")

    def connect_to_serial(self, selected_port):
        try:
            self.nrf_data = serial.Serial(selected_port, 115200)
            self.start_serial_read(self.nrf_data)  # Daten vom COM-Port lesen
        except serial.SerialException:
            self.db_view.show_warning_message(
                "Serial Port Error",
                f"Failed to open {selected_port}. Make sure the port is available and try again.",
            )
        # Beispielcode zur Veranschaulichung:
        print("Verbindung mit Port:", selected_port)

    def start_serial_read(self, nrf_data):
        if self.serial_thread is not None and self.serial_thread.is_alive():
            return

        self.stop_serial_flag = False
        self.serial_thread = threading.Thread(target=self.read_serial_data, args=(nrf_data,))
        self.serial_thread.start()

    '''
    def read_serial_data(self, nrf_data):
        while not self.stop_serial_flag:
            #while self.nrf_data.inWaiting() == 0:
                #pass

            data_packet = self.nrf_data.readline()
            data_packet = str(data_packet, "utf-8")
            split_packet = data_packet.split(",")

            if len(split_packet) == 5:
                self.module_name = split_packet[0]
                qw = float(split_packet[1])
                qx = float(split_packet[2])
                qy = float(split_packet[3])
                qz = float(split_packet[4])
                output = f"ModuleNr = {self.module_name}, qw = {qw}, qx = {qx}, qy = {qy}, qz = {qz}"
                self.db_view.update_catched_data_text(output)

                timestamp = None
                last_timestamp = None  # Initialisierung mit Standardwert
                if self.write == True:
                    timestamp = self.get_last_timestamp()
                    if self.timeflag is not None:
                        last_timestamp_var = self.db_model.get_last_timestamp(self.module_name)
                    if last_timestamp_var is not None:
                        last_timestamp = float(last_timestamp_var)
                        self.timeflag = None
                    if last_timestamp is not None:
                        timestamp += last_timestamp
                    # Einlesen der Quaternion-Daten in die Datenbank
                    self.db_model.insert_quaternion_data(self.module_name, timestamp, qw, qx, qy, qz, self.start_time, self.current_time)

            elif len(split_packet) == 4:
                self.module_name = split_packet[0]
                x = float(split_packet[1])
                y = float(split_packet[2])
                z = float(split_packet[3])
                output = f"ModuleNr = {self.module_name}, X = {x}, Y = {y}, Z = {z}"
                self.db_view.update_catched_data_text(output)

                if self.write == True:
                    timestamp = self.get_last_timestamp()
                    # Einlesen der IMU-Daten in die Datenbank
                    self.db_model.insert_imu_data(self.module_name, timestamp, x, y, z, self.start_time, self.current_time)
    '''
    def read_serial_data(self, nrf_data):
        while not self.stop_serial_flag:
            # while self.nrf_data.inWaiting() == 0:
            # pass

            data_packet = self.nrf_data.readline()
            data_packet = str(data_packet, "utf-8")
            split_packet = data_packet.split(",")

            if len(split_packet) == 5:
                self.process_quaternion_data(split_packet)

            elif len(split_packet) == 4:
                self.process_imu_data(split_packet)


    def process_quaternion_data(self, split_packet):
        try:
            self.module_name = split_packet[0]
            qw = float(split_packet[1])
            qx = float(split_packet[2])
            qy = float(split_packet[3])
            qz = float(split_packet[4])
            output = f"ModuleNr = {self.module_name}, qw = {qw}, qx = {qx}, qy = {qy}, qz = {qz}"
            self.db_view.update_catched_data_text(output)

            timestamp = None
            last_timestamp = None  # Initialisierung mit Standardwert
            if self.write:
                timestamp = self.get_last_timestamp()
                if self.timeflag is not None:
                    last_timestamp_var = self.db_model.get_last_timestamp(self.module_name)
                if last_timestamp_var is not None:
                    last_timestamp = float(last_timestamp_var)
                    self.timeflag = None
                if last_timestamp is not None:
                    timestamp += last_timestamp
                # Einlesen der Quaternion-Daten in die Datenbank
                self.db_model.insert_quaternion_data(self.module_name, timestamp, qw, qx, qy, qz, self.start_time,
                                                 self.current_time)
        except (ValueError, IndexError):
            # Falsch abgefangene Daten ignorieren und Schleife fortsetzen
            pass

    def process_imu_data(self, split_packet):
        try:
            self.module_name = split_packet[0]
            x = float(split_packet[1])
            y = float(split_packet[2])
            z = float(split_packet[3])
            output = f"ModuleNr = {self.module_name}, X = {x}, Y = {y}, Z = {z}"
            self.db_view.update_catched_data_text(output)

            if self.write:
                timestamp = self.get_last_timestamp()
                # Einlesen der IMU-Daten in die Datenbank
                self.db_model.insert_imu_data(self.module_name, timestamp, x, y, z, self.start_time, self.current_time)
        except (ValueError, IndexError):
            # Falsch abgefangene Daten ignorieren und Schleife fortsetzen
            pass

    def disconnect_button(self):
        self.stop_serial_flag = True
        self.nrf_data = None
        self.db_view.port_var.set("Wähle einen Port")
        self.db_view.switch_disconnect_button_off()
        print("Verbindung getrennt")


    def start_write(self):
        self.db_model.init_db()
        self.timeflag = 1;
        self.start_time = time.time()
        self.write = True
        self.db_view.switch_start_button_off()
        self.db_view.switch_status_field(1)

    def stop_write(self):
        self.timeflag = None
        self.write = False
        self.db_view.switch_stop_button_off()
        self.db_view.switch_status_field(2)

    def get_last_timestamp(self):
        # Calcuating time since new catched data
        self.current_time = time.time()
        elapsed_time = self.current_time - self.start_time
        return elapsed_time

    def create_database(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite Database", "*.db")])
        # Überprüfe, ob eine Datei ausgewählt wurde
        if file_path:
            # Erstelle eine Verbindung zur Datenbank
            conn = sqlite3.connect(file_path)
            conn.close()
            self.db_model.DATABASE_FILE = file_path
            file_name = file_path.split('/')[-1]  # Extrahiere den Dateinamen aus dem Pfad
            self.db_view.switch_file_field_tab1(file_name)
            print("Datenbankdatei wurde erfolgreich erstellt:", file_path)
        else:
            print("Es wurde keine Datei ausgewählt.")

    def choose_database_tab1(self):
        filetypes = [("Datenbankdateien", "*.db"), ("Alle Dateien", "*.*")]
        file_path = filedialog.askopenfilename(filetypes=filetypes)

        if file_path:
            self.db_model.DATABASE_FILE = file_path
            file_name = file_path.split('/')[-1]  # Extrahiere den Dateinamen aus dem Pfad
            self.db_view.switch_file_field_tab1(file_name)


    '''
    Funktionaler Teil für den zweiten Tab
    '''

    def choose_database_tab2(self):
        filetypes = [("Datenbankdateien", "*.db"), ("Alle Dateien", "*.*")]
        file_path = filedialog.askopenfilename(filetypes=filetypes)

        if file_path:
            self.db_model.DATABASE_FILE = file_path

        data = self.db_model.read_modules_data_from_database()

        if data:
            self.db_view.update_database_text(data)
            file_name = file_path.split('/')[-1]  # Extrahiere den Dateinamen aus dem Pfad
            self.db_view.switch_file_field_tab2(file_name)
            self.db_view.switch_upload_button_off()

        else:
            self.db_view.show_warning_message(
                "Error",
                f"No data found in the database.",
            )

    def delete_database(self):
        self.db_view.update_database_text(None)
        self.db_model.delete_database()
        self.db_view.switch_delete_button_off()


    def show_module_data(self):
        data = self.db_model.read_modules_data_from_database()

        if data:
            self.db_view.update_database_text(data)
            self.db_view.switch_table1_off()

        else:
            self.db_view.show_warning_message(
                "Error",
                f"No data found in the database.",
            )

    def show_imu_data(self):
        data = self.db_model.read_imu_data_from_database()

        if data:
            self.db_view.update_database_text(data)
            self.db_view.switch_table2_off()

        else:
            self.db_view.show_warning_message(
                "Error",
                f"No data found in the database.",
            )

    def show_quaternion_data(self):
        data = self.db_model.read_quat_data_from_database()

        if data:
            self.db_view.update_database_text(data)
            self.db_view.switch_table3_off()

        else:
            self.db_view.show_warning_message(
                "Error",
                f"No data found in the database.",
            )

    def search_database(self):
        search_term = self.db_view.search_entry.get()
        if len(search_term) == 0:
            self.db_view.show_warning_message(
                "Error",
                f"Please enter a search term.",
            )
            return

        data = self.db_model.read_data(search_term)
        if data is None:
            self.db_view.show_warning_message(
                "Error",
                f"Please enter a correct search term.",
            )
        else:
            self.db_view.update_database_text(data)
            self.db_view.switch_table_on()




    def select_file(self):
        filetypes = [("Datenbankdateien", "*.db"), ("Alle Dateien", "*.*")]
        file_path = filedialog.askopenfilename(filetypes=filetypes)

        if file_path:
            file_name = file_path.split('/')[-1]  # Extrahiere den Dateinamen aus dem Pfad
            self.db_view.update_selected_file(file_name)
            data = self.db_model.read_modules(file_name)

            if data:
                self.db_view.update_module_text(data)
                self.db_view.switch_file_button_on()
            else:
                self.db_view.show_warning_message(
                    "Error",
                    f"No data found in the database.",
                )

    def visualize_data(self):
        search_term = self.db_view.search_module.get()
        if len(search_term) == 0:
            self.db_view.show_warning_message(
                "Error",
                f"Please enter a search term.",
            )
            return

        data = self.db_model.read_data(search_term)
        if data is None:
            self.db_view.show_warning_message(
                "Error",
                f"Please enter a correct search term.",
            )
        else:
            self.db_view.switch_visualize_button_on()
            self.db_view.plot_graph(data)

    def save_graph(self):
        if hasattr(self, "selected_file_path"):
            # Überprüfe, ob eine Datei ausgewählt wurde
            # Speichere den Graphen an dem ausgewählten Speicherort
            self.db_view.show_info_message("Erfolg", "Graph erfolgreich gespeichert.")
        else:
            self.db_view.show_warning_message("Fehler", "Bitte wähle eine Datei aus.")

    def reset_graph(self):
        self.db_view.graph_placeholder.configure(text="Graph Placeholder")
        # Setze den Graphen zurück

