import serial
import threading
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import module_db2


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Database GUI")
        self.geometry("750x600")  # Setze die Größe des Fensters

        self.tabControl = ttk.Notebook(self)

        self.page1 = Page1(self.tabControl)
        self.tabControl.add(self.page1, text="DB Config")

        self.page2 = Page2(self.tabControl)
        self.tabControl.add(self.page2, text="DB List")

        self.tabControl.pack(expand=1, fill="both")


class Page1(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        label = tk.Label(self, text="DB Config")
        label.pack(padx=20, pady=20)

        self.com_port_var = tk.StringVar()
        self.com_port_var.set("COM-Port not selected")  # Standardwert auswählen

        com_port_label = tk.Label(self, text="COM Port:")
        com_port_label.pack()

        com_port_dropdown = ttk.Combobox(
            self,
            textvariable=self.com_port_var,
            values=[
                "COM1", "COM2", "COM3", "COM4", "COM5",
                "COM6", "COM7", "COM8", "COM9", "COM10"
            ],
            width=22,
            state="readonly"
        )
        com_port_dropdown.pack()

        button_frame = tk.Frame(self)
        button_frame.pack(pady=(10, 20))

        select_button = tk.Button(button_frame, text="Select", command=self.select_com_port)
        select_button.pack(side="left", padx=5)

        stop_button = tk.Button(button_frame, text="Stop", command=self.stop_serial_read)
        stop_button.pack(side="left", padx=5)

        catched_data_label = tk.Label(self, text="Catched Data:")
        catched_data_label.pack(pady=(20, 5))

        catched_data_frame = tk.Frame(self)
        catched_data_frame.pack()

        scrollbar = tk.Scrollbar(catched_data_frame)
        scrollbar.pack(side="right", fill="y")

        self.catched_data_text = tk.Text(catched_data_frame, height=10, width=int(80))  # Feld um 1,5-fach verlängern
        self.catched_data_text.pack(side="left", fill="both")

        self.catched_data_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.catched_data_text.yview)

        self.catched_data_text.config(state="disabled")  # Textfeld schreibgeschützt machen

        status_label = tk.Label(self, text="Status:")
        status_label.pack(pady=10)

        self.status_var = tk.StringVar()
        self.status_var.set("Not in work")

        status_text = tk.Label(self, textvariable=self.status_var)
        status_text.pack()

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        start_write_button = tk.Button(button_frame, text="Start Write", command=self.start_write)
        start_write_button.pack(side="left", padx=5)

        stop_write_button = tk.Button(button_frame, text="Stop Write", command=self.stop_write)
        stop_write_button.pack(side="left", padx=5)

        self.serial_thread = None
        self.stop_serial_flag = False
        self.nrf_data = None

    def select_com_port(self):
        selected_com_port = self.com_port_var.get()
        print("Selected COM Port:", selected_com_port)

        # Hier wird die nrfData-Variable mit dem ausgewählten COM-Port initialisiert
        try:
            self.nrf_data = serial.Serial(selected_com_port, 115200)
            self.start_serial_read(self.nrf_data)  # Daten vom COM-Port lesen
            # Weitere Aktionen mit der nrfData-Verbindung...
        except serial.SerialException:
            messagebox.showerror(
                "Serial Port Error",
                f"Failed to open {selected_com_port}. Make sure the port is available and try again.",
            )
            self.com_port_var.set("COM-Port not selected")  # Zurück zum Standardwert
            return

        self.focus_set()  # Fokus auf ein anderes Widget setzen

    def start_serial_read(self, nrf_data):
        if self.serial_thread is not None and self.serial_thread.is_alive():
            return

        self.stop_serial_flag = False
        self.serial_thread = threading.Thread(target=self.read_serial_data, args=(nrf_data,))
        self.serial_thread.start()

    def read_serial_data(self, nrf_data):
        while not self.stop_serial_flag:
            while nrf_data.inWaiting() == 0:
                pass

            timestamp = 1

            data_packet = nrf_data.readline()
            data_packet = str(data_packet, "utf-8")

            split_packet = data_packet.split(",")

            if len(split_packet) == 5:
                module_name = split_packet[0]
                qw = float(split_packet[1])
                qx = float(split_packet[2])
                qy = float(split_packet[3])
                qz = float(split_packet[4])
                output = f"ModuleNr = {module_name}, qw = {qw}, qx = {qx}, qy = {qy}, qz = {qz}"
                self.update_catched_data_text(output)

                if self.status_var.get() == "Writing in Database":
                    # Einlesen der Quaternion-Daten in die Datenbank
                    module_db2.insert_quaternion_data(module_name, timestamp, qw, qx, qy, qz)

            elif len(split_packet) == 4:
                module_name = split_packet[0]
                x = float(split_packet[1])
                y = float(split_packet[2])
                z = float(split_packet[3])
                output = f"ModuleNr = {module_name}, X = {x}, Y = {y}, Z = {z}"
                self.update_catched_data_text(output)

                if self.status_var.get() == "Writing in Database":
                    # Einlesen der IMU-Daten in die Datenbank
                    module_db2.insert_imu_data(module_name, timestamp, x, y, z)

            self.catched_data_text.see(tk.END)  # Zum Ende des Textfeldes scrollen

    def stop_serial_read(self):
        self.stop_serial_flag = True
        self.nrf_data = None
        self.com_port_var.set("COM-Port not selected")

    def update_catched_data_text(self, output):
        self.catched_data_text.config(state="normal")  # Textfeld bearbeitbar machen
        self.catched_data_text.insert(tk.END, output + "\n")
        self.catched_data_text.config(state="disabled")  # Textfeld wieder schreibgeschützt machen

    def start_write(self):
        module_db2.init_db()
        self.status_var.set("Writing in Database")



    def stop_write(self):
        self.status_var.set("Stop Writing in Database")


class Page2(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        label = tk.Label(self, text="DB List")
        label.pack(padx=20, pady=20)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=(0, 10))

        self.load_button = tk.Button(button_frame, text="Load", command=self.load_data)
        self.load_button.pack(side="left", padx=5)

        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_data, state="disabled")
        self.delete_button.pack(side="left", padx=5)

        data_frame = tk.Frame(self)
        data_frame.pack()

        scrollbar = tk.Scrollbar(data_frame)
        scrollbar.pack(side="right", fill="y")

        self.data_text = tk.Text(data_frame, height=10, width=80)
        self.data_text.pack(side="left", fill="both")

        self.data_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.data_text.yview)

        button_frame2 = tk.Frame(self)
        button_frame2.pack(pady=(10, 5))

        self.module_button = tk.Button(button_frame2, text="Modules", command=self.show_module_data, state="disabled")
        self.module_button.pack(side="left", padx=5)

        self.imu_button = tk.Button(button_frame2, text="IMU", command=self.show_imu_data, state="disabled")
        self.imu_button.pack(side="left", padx=5)

        self.quaternion_button = tk.Button(button_frame2, text="Quaternion", command=self.show_quaternion_data, state="disabled")
        self.quaternion_button.pack(side="left", padx=5)

        search_frame = tk.Frame(self)
        search_frame.pack(pady=(10, 5))

        self.search_text = tk.Entry(search_frame)
        self.search_text.pack(side="left", padx=5)

        self.search_button = tk.Button(search_frame, text="Search", command=self.search_data, state="disabled")
        self.search_button.pack(side="left", padx=5)

        self.data_text.config(state="disabled")

    def load_data(self):
        data = module_db2.read_modules_data_from_database()  # Daten aus der Datenbank auslesen

        if data:
            self.data_text.config(state="normal")  # Textfeld bearbeitbar machen
            self.data_text.delete(1.0, tk.END)  # Aktuellen Inhalt des Textfeldes löschen

            # Daten in das Textfeld einfügen
            for row in data:
                self.data_text.insert(tk.END, f"{row}\n")

            self.data_text.config(state="disabled")  # Textfeld wieder schreibgeschützt machen

            self.imu_button.config(state="normal")  # IMU-Button aktivieren
            self.quaternion_button.config(state="normal")  # Quaternion-Button aktivieren
            self.search_button.config(state="normal")  # Suchtextfeld aktivieren
            self.delete_button.config(state="normal")  # Delete-Button aktivieren
            self.load_button.config(state="disabled")  # Load-Button deaktivieren
        else:
            messagebox.showerror("Error", "No data found in the database.")

        self.focus_set()  # Fokus auf ein anderes Widget setzen

    def delete_data(self):
        # Datenfeld leeren
        self.data_text.config(state="normal")
        self.data_text.delete("1.0", tk.END)
        module_db2.delete_database()

        self.module_button.config(state="disabled")
        self.data_text.config(state="disabled")  # Textfeld wieder schreibgeschützt machen
        self.imu_button.config(state="disabled")  # IMU-Button aktivieren
        self.quaternion_button.config(state="disabled")  # Quaternion-Button aktivieren
        self.search_button.config(state="disabled")  # Suchtextfeld aktivieren
        self.delete_button.config(state="disabled")  # Delete-Button aktivieren
        self.load_button.config(state="normal")  # Load-Button deaktivieren

    def show_module_data(self):
        self.data_text.config(state="normal")  # Textfeld bearbeitbar machen
        self.data_text.delete(1.0, tk.END)  # Aktuellen Inhalt des Textfeldes löschen

        # Daten in das Textfeld einfügen
        data = module_db2.read_modules_data_from_database()  # Daten aus der Datenbank auslesen
        if data:
            for row in data:
                self.data_text.insert(tk.END, f"{row}\n")
        else:
            self.data_text.insert(tk.END, "No module data available.")

        self.data_text.config(state="disabled")  # Textfeld wieder schreibgeschützt machen
        self.module_button.config(state="disabled")  # Modul-Button deaktivieren
        self.imu_button.config(state="normal")
        self.quaternion_button.config(state="normal")


    def show_imu_data(self):
        self.data_text.config(state="normal")  # Textfeld bearbeitbar machen
        self.data_text.delete(1.0, tk.END)  # Aktuellen Inhalt des Textfeldes löschen

        # Daten in das Textfeld einfügen
        data = module_db2.read_imu_data_from_database()  # Daten aus der Datenbank auslesen
        if data:
            for row in data:
                self.data_text.insert(tk.END, f"{row}\n")
        else:
            self.data_text.insert(tk.END, "No IMU data available.")

        self.data_text.config(state="disabled")  # Textfeld wieder schreibgeschützt machen
        self.module_button.config(state="normal")  # Modul-Button deaktivieren
        self.imu_button.config(state="disabled")
        self.quaternion_button.config(state="normal")

    def show_quaternion_data(self):
        self.data_text.config(state="normal")  # Textfeld bearbeitbar machen
        self.data_text.delete(1.0, tk.END)  # Aktuellen Inhalt des Textfeldes löschen

        # Daten in das Textfeld einfügen
        data = module_db2.read_quat_data_from_database()  # Daten aus der Datenbank auslesen
        if data:
            for row in data:
                self.data_text.insert(tk.END, f"{row}\n")
        else:
            self.data_text.insert(tk.END, "No quaternion data available.")

        self.data_text.config(state="disabled")  # Textfeld wieder schreibgeschützt machen
        self.module_button.config(state="normal")  # Modul-Button deaktivieren
        self.imu_button.config(state="normal")
        self.quaternion_button.config(state="disabled")

    def search_data(self):
        search_term = self.search_text.get()
        if len(search_term) == 0:
            messagebox.showerror("Error", "Please enter a search term.")
            return

        data = module_db2.read_data(search_term)
        if data is None:
            messagebox.showerror("Error", "Please enter a correct search term.")
        else:
            self.data_text.config(state="normal")  # Textfeld bearbeitbar machen
            self.data_text.delete(1.0, tk.END)  # Aktuellen Inhalt des Textfeldes löschen
            for row in data:
                self.data_text.insert(tk.END, f"{row}\n")

        self.data_text.config(state="disabled")  # Textfeld wieder schreibgeschützt machen




if __name__ == "__main__":
    gui = GUI()
    gui.mainloop()
