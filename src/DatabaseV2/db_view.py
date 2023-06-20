
'''
db_view.py
'''

import time
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkinter.messagebox as messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DBView(tk.Tk):


    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.title("Database GUI")
        self.geometry("1000x750")  # Setze die Größe des Fensters
        self.tabControl = ttk.Notebook(self)

        # Erster Tab: Daten speichern
        self.tab_save = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab_save, text="Daten speichern")
        self.add_save_tab_content()

        # Zweiter Tab: Daten auslesen
        self.tab_read = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab_read, text="Daten auslesen")
        self.add_read_tab_content()

        # Dritter Tab: Daten visualisieren
        self.tab_visualize = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab_visualize, text="Daten visualisieren")
        self.add_visualize_tab_content()

        self.tabControl.pack(expand=1, fill="both")

    def main(self):
        self.mainloop()


    def add_save_tab_content(self):
        # Frame für den Inhalt des "Daten speichern"-Tabs
        frame = ttk.Frame(self.tab_save)
        frame.pack(padx=20, pady=20)

        # Buttons in einer Zeile (0) anlegen
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

        # Dropdown-Menü für die COM-Port-Auswahl
        port_label = ttk.Label(button_frame, text="COM-Port:")
        port_label.pack(side=tk.LEFT, padx=(0, 5))

        self.port_var = tk.StringVar()
        port_dropdown = ttk.Combobox(button_frame, textvariable=self.port_var, state="readonly")
        port_dropdown["values"] = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10"]
        port_dropdown.pack(side=tk.LEFT, padx=(0, 5))
        port_dropdown.set("Wähle einen Port")  # Standardtext hinzugefügt

        # Buttons in einer Zeile (1) anlegen
        button_frame1 = ttk.Frame(frame)
        button_frame1.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        # Bestätigungsbutton
        self.confirm_button = ttk.Button(button_frame1, text="Bestätigen", command=self.controller.confirm_button)
        self.confirm_button.pack(side=tk.LEFT, padx=(0, 5))

        # Verbindungsabbrechen-Button
        self.disconnect_button = ttk.Button(button_frame1, text="Verbindung trennen", command=self.controller.disconnect_button, state="disabled")
        self.disconnect_button.pack(side=tk.LEFT, padx=(0, 5))

        # Buttons in einer Zeile (2) anlegen
        button_frame2 = ttk.Frame(frame)
        button_frame2.grid(row=2, column=0, columnspan=4, padx=5, pady=5)

        '''
        from tkinter import scrolledtext

        # Feld zur Anzeige der Datenbankinhalte
        self.database_text = scrolledtext.ScrolledText(button_frame2, height=20, width=90, state="disabled")
        self.database_text.pack(side=tk.LEFT, padx=(0, 5))
        '''

        # Textfeld für die abgefangenen Daten
        self.data_text = tk.Text(button_frame2, height=20, width=90, state="disabled")
        self.data_text.pack(side=tk.LEFT, padx=(0, 5))

        # Scrollbar für das Textfeld
        scrollbar = ttk.Scrollbar(button_frame2, command=self.data_text.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.data_text.config(yscrollcommand=scrollbar.set)

        # Buttons in einer Zeile (3) anlegen
        button_frame3 = ttk.Frame(frame)
        button_frame3.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

        # Textfeld zur Beschreibung der Datenbankoptionen
        status_label = ttk.Label(button_frame3, text="Daten in Datenbank einlesen")
        status_label.pack(side=tk.LEFT, padx=(0, 5))

        # Buttons in einer Zeile (4) anlegen
        button_frame4 = ttk.Frame(frame)
        button_frame4.grid(row=4, column=0, columnspan=4, padx=5, pady=5)

        # Start-Button
        self.start_button = ttk.Button(button_frame4, text="Start", command=self.controller.start_write, state="disabled")
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))

        # Stop-Button
        self.stop_button = ttk.Button(button_frame4, text="Stop", command=self.controller.stop_write, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))

        # Datenbank anlegen-Button
        self.create_db_button = ttk.Button(button_frame4, text="Datenbank anlegen", command=self.controller.create_database)
        self.create_db_button.pack(side=tk.LEFT)

        # Datenbank-Datei auswählen-Button
        self.choose_db_button = ttk.Button(button_frame4, text="Datenbank-Datei auswählen", command=self.controller.choose_database_tab1)
        self.choose_db_button.pack(side=tk.LEFT)

        # Buttons in einer Zeile (5) anlegen
        button_frame5 = ttk.Frame(frame)
        button_frame5.grid(row=5, column=0, columnspan=4, padx=5, pady=5)

        # Statusfeld für den Prozess
        status_label = ttk.Label(button_frame5, text="Status:")
        status_label.pack(side=tk.LEFT, padx=(0, 5))

        self.status_field = ttk.Label(button_frame5, text="Idle")
        self.status_field.pack(side=tk.LEFT, padx=(0, 5))

        # Buttons in einer Zeile (6) anlegen
        button_frame5 = ttk.Frame(frame)
        button_frame5.grid(row=6, column=0, columnspan=4, padx=5, pady=5)

        # Statusfeld für die Datenbank-Datei
        db_file_label = ttk.Label(button_frame5, text="Ausgewählte Datei: ")
        db_file_label.pack(side=tk.LEFT, padx=(0, 5))

        self.db_file_field_tab1 = ttk.Label(button_frame5, text="your_database.db")
        self.db_file_field_tab1.pack(side=tk.LEFT, padx=(0, 5))

    """
    Verwendete Funktionen um die Widgets zu aktualisieren
    """

    def update_catched_data_text(self, data):
        self.data_text.configure(state="normal")  # Textfeld bearbeitbar machen
        self.data_text.insert(tk.END, data + "\n")  # Daten am Ende des Textfeldes hinzufügen
        self.data_text.configure(state="disabled")  # Textfeld wieder schreibgeschützt machen
        self.data_text.see(tk.END)  # Zum Ende des Textfeldes scrollen

    def switch_confirm_button_off(self):
        self.confirm_button.config(state="disabled")
        self.disconnect_button.config(state="normal")
        self.start_button.config(state="normal")
        self.create_db_button.config(state="disabled")
        self.choose_db_button.config(state="disabled")

    def switch_disconnect_button_off(self):
        self.confirm_button.config(state="normal")
        self.disconnect_button.config(state="disabled")
        self.start_button.config(state="disabled")
        self.create_db_button.config(state="normal")
        self.choose_db_button.config(state="normal")

    def switch_start_button_off(self):
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

    def switch_stop_button_off(self):
        self.stop_button.config(state="disabled")
        self.start_button.config(state="normal")

    def switch_status_field(self, status):
        if status == 1:
            self.status_field.config(text="Starte das Einlesen der Datenbankdateien")
        if status == 2:
            self.status_field.config(text="Stoppe das Einlesen der Datenbankdateien")
            self.status_field.after(2500, lambda: self.status_field.config(text="Idle"))

    def switch_file_field_tab1(self, db_file):
        self.db_file_field_tab1.config(text=db_file)





    def add_read_tab_content(self):
        # Frame für den Inhalt des "Daten auslesen"-Tabs
        frame = ttk.Frame(self.tab_read)
        frame.pack(padx=20, pady=20)

        # Buttons in einer Zeile (0) anlegen
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

        # Button zum Hochladen der Datenbankdatei
        self.upload_button = ttk.Button(button_frame, text="Datenbank-Datei auswählen", command=self.controller.choose_database_tab2)
        self.upload_button.pack(side=tk.LEFT, padx=(0, 5))

        # Button zum Löschen der Datenbank
        self.delete_button = ttk.Button(button_frame, text="Datenbank löschen", command=self.controller.delete_database, state="disabled")
        self.delete_button.pack(side=tk.LEFT, padx=(0, 5))

        # Buttons in einer Zeile (1) anlegen
        button_frame1 = ttk.Frame(frame)
        button_frame1.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        # Statusfeld für die Datenbank-Datei
        db_file_label = ttk.Label(button_frame1, text="Ausgewählte Datei: ")
        db_file_label.pack(side=tk.LEFT, padx=(0, 5))

        self.db_file_field_tab2 = ttk.Label(button_frame1, text="your_database.db")
        self.db_file_field_tab2.pack(side=tk.LEFT, padx=(0, 5))

        # Buttons in einer Zeile (2) anlegen
        button_frame2 = ttk.Frame(frame)
        button_frame2.grid(row=2, column=0, columnspan=4, padx=5, pady=5)

        # Feld zur Anzeige der Datenbankinhalte
        self.database_text = tk.Text(button_frame2, height=20, width=90, state="disabled")
        self.database_text.pack(side=tk.LEFT, padx=(0, 5))

        '''
        # Container für den Treeview und die Scrollbars
        container = ttk.Frame(frame)
        container.pack()

        # Canvas erstellen
        canvas = tk.Canvas(container)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars erstellen und mit dem Canvas verbinden
        scrollbar_x = ttk.Scrollbar(container, orient=tk.HORIZONTAL, command=canvas.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        scrollbar_y = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview im Canvas platzieren
        self.database_treeview = ttk.Treeview(canvas, height=13, columns=column_labels, show='headings')
        self.database_treeview.pack(side=tk.LEFT, padx=(0, 5))

        # Scrollbars mit dem Canvas und dem Treeview verbinden
        canvas.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)
        canvas.create_window((0, 0), window=self.database_treeview, anchor='nw')
        '''


        # Buttons in einer Zeile (3) anlegen
        button_frame3 = ttk.Frame(frame)
        button_frame3.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

        # Button zum Ausgeben des ersten Tables
        self.table1_button = ttk.Button(button_frame3, text="Module Tabelle", command=self.controller.show_module_data, state="disabled")
        self.table1_button.pack(side=tk.LEFT, padx=(0, 5))

        # Button zum Ausgeben des zweiten Tables
        self.table2_button = ttk.Button(button_frame3, text="IMU Tabelle", command=self.controller.show_imu_data, state="disabled")
        self.table2_button.pack(side=tk.LEFT, padx=(0, 5))

        # Button zum Ausgeben des dritten Tables
        self.table3_button = ttk.Button(button_frame3, text="Quaternion Tabelle", command=self.controller.show_quaternion_data, state="disabled")
        self.table3_button.pack(side=tk.LEFT, padx=(0, 5))

        # Buttons in einer Zeile (4) anlegen
        button_frame4 = ttk.Frame(frame)
        button_frame4.grid(row=4, column=0, columnspan=4, padx=5, pady=5)

        # Statusfeld für die Datenbank-Datei
        db_file_label = ttk.Label(button_frame4, text="Daten für bestimmten Modul finden: ")
        db_file_label.pack(side=tk.LEFT, padx=(0, 5))

        # Buttons in einer Zeile (5) anlegen
        button_frame5 = ttk.Frame(frame)
        button_frame5.grid(row=5, column=0, columnspan=4, padx=5, pady=5)

        # Suchfeld
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(button_frame5, textvariable=self.search_var, state="readonly")
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))

        # Button zum Bestätigen der Suche
        self.search_button = ttk.Button(button_frame5, text="Suchen", command=self.controller.search_database, state="disabled")
        self.search_button.pack(side=tk.LEFT, padx=(0, 5))

    def switch_file_field_tab2(self, db_file):
        self.db_file_field_tab2.config(text=db_file)

    def switch_upload_button_off(self):
        self.delete_button.config(state="normal")
        self.table1_button.config(state="disabled")
        self.table2_button.config(state="normal")
        self.table3_button.config(state="normal")
        self.search_entry.config(state="normal")
        self.search_button.config(state="normal")

    def switch_delete_button_off(self):
        self.upload_button.config(state="normal")
        self.delete_button.config(state="disabled")
        self.table1_button.config(state="disabled")
        self.table2_button.config(state="disabled")
        self.table3_button.config(state="disabled")
        self.search_entry.config(state="readonly")
        self.search_button.config(state="disabled")

    def switch_table1_off(self):
        self.table1_button.config(state="disabled")
        self.table2_button.config(state="normal")
        self.table3_button.config(state="normal")

    def switch_table2_off(self):
        self.table1_button.config(state="normal")
        self.table2_button.config(state="disabled")
        self.table3_button.config(state="normal")

    def switch_table3_off(self):
        self.table1_button.config(state="normal")
        self.table2_button.config(state="normal")
        self.table3_button.config(state="disabled")

    def switch_table_on(self):
        self.search_entry.config(text=" ")
        self.table1_button.config(state="normal")
        self.table2_button.config(state="normal")
        self.table3_button.config(state="normal")




    def update_database_text(self, data):
        if data:
            self.database_text.config(state="normal")  # Textfeld bearbeitbar machen
            self.database_text.delete(1.0, tk.END)  # Aktuellen Inhalt des Textfeldes löschen
            '''
            formatted_data = []

            for row in data:

                formatted_row = [str(item) for item in row] # Konvertiere die Elemente in Strings
            formatted_data.append(' | '.join(formatted_row)) # Verbinde die Elemente mit Trennzeichen

            # Füge die Spaltenbeschriftungen zur formatierten Datenliste hinzu
            formatted_data.insert(0, ' | '.join(column_labels))

            # Konvertiere die formatierte Datenliste in einen einzigen Textstring
            text_data = '\n'.join(formatted_data)
            '''
            # Daten in das Textfeld einfügen
            for row in data:
                self.database_text.insert(tk.END, f"{row}\n")


            self.database_text.config(state="disabled")  # Textfeld wieder schreibgeschützt machen
            return

        self.database_text.config(state="normal")
        self.database_text.delete("1.0", tk.END)
        self.database_text.config(state="disabled")  # Textfeld wieder schreibgeschützt machen

    '''
    def update_database_text(self, data, typ):
        if data:
            self.database_treeview.delete(*self.database_treeview.get_children())

            if typ == 1:
                # Spaltenbeschriftung
                column_labels = ['ID', 'Modulname', 'Type']

                # Konfiguriere die Spaltenbeschriftungen
                for col in column_labels:
                    self.database_treeview.heading(col, text=col)

                for row in data:
                    self.database_treeview.insert('', tk.END, values=row, tags=('centered',))

                # Mittig ausrichten
                self.database_treeview.tag_configure('centered', anchor='center')

                self.database_treeview.pack()

            if typ == 2:
                column_labels = ['Zeitstempel', 'X', 'Y', 'Z', 'ModulID']

                self.database_treeview['columns'] = column_labels

                # Konfiguriere die Spaltenbeschriftungen
                for col in column_labels:
                    self.database_treeview.heading(col, text=col)

                for row in data:
                    self.database_treeview.insert('', tk.END, values=row, tags=('centered',))

                # Mittig ausrichten
                self.database_treeview.tag_configure('centered', anchor='center')

                self.database_treeview.pack()

            if typ == 3:
                column_labels = ['Zeitstempel', 'QW', 'QX', 'QY', 'QZ', 'ModulID']

                self.database_treeview['columns'] = column_labels

                # Konfiguriere die Spaltenbeschriftungen
                for col in column_labels:
                    self.database_treeview.heading(col, text=col)

                for row in data:
                    self.database_treeview.insert('', tk.END, values=row, tags=('centered',))

                # Mittig ausrichten
                self.database_treeview.tag_configure('centered', anchor='center')

                self.database_treeview.pack()
    '''





    def add_visualize_tab_content(self):
        # Frame für den Inhalt des "Daten visualisieren"-Tabs
        frame = ttk.Frame(self.tab_visualize)
        frame.pack(padx=20, pady=20)

        # Hier kannst du die benötigten Widgets für die Datenvisualisierung hinzufügen
        # und die Platzhalter für den Graphen und die Buttons einfügen

        # Buttons in einer Zeile (0) anlegen
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

        # Button zum Öffnen des Dateiauswahlfensters
        file_button = ttk.Button(button_frame, text="Datei auswählen", command=self.controller.select_file)
        file_button.pack(side=tk.LEFT, padx=(0, 5))

        # Buttons in einer Zeile (1) anlegen
        button_frame1 = ttk.Frame(frame)
        button_frame1.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        # Statusfeld für die Datenbank-Datei
        db_file_label = ttk.Label(button_frame1, text="Ausgewählte Datei: ")
        db_file_label.pack(side=tk.LEFT, padx=(0, 5))

        self.db_placeholder = ttk.Label(button_frame1, text="your_database.db")
        self.db_placeholder.pack(side=tk.LEFT, padx=(0, 5))

        # Buttons in einer Zeile (2) anlegen
        button_frame2 = ttk.Frame(frame)
        button_frame2.grid(row=2, column=0, columnspan=4, padx=5, pady=5)

        # Feld zur Anzeige der Module
        self.module_text = tk.Text(button_frame2, height=6, width=30, state="disabled")
        self.module_text.pack(side=tk.LEFT, padx=(0, 5))

        # Buttons in einer Zeile (3) anlegen
        button_frame3 = ttk.Frame(frame)
        button_frame3.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

        # Statusfeld für die Datenbank-Datei
        visualize_notice = ttk.Label(button_frame3, text="Wähle ein Modul aus, welches Sie visualisieren möchten: ")
        visualize_notice.pack(side=tk.LEFT, padx=(0, 5))


        # Buttons in einer Zeile (4) anlegen
        button_frame4 = ttk.Frame(frame)
        button_frame4.grid(row=4, column=0, columnspan=4, padx=5, pady=5)

        # Suchfeld
        self.search_var = tk.StringVar()
        self.search_module = ttk.Entry(button_frame4, textvariable=self.search_var, state="readonly")
        self.search_module.pack(side=tk.LEFT, padx=(0, 5))

        # Button zum Visualisieren
        self.visualize_button = ttk.Button(button_frame4, text="Visualisieren", command=self.controller.visualize_data, state="disabled")
        self.visualize_button.pack(side=tk.LEFT, padx=(0, 5))

        # Buttons in einer Zeile (5) anlegen
        button_frame5 = ttk.Frame(frame)
        button_frame5.grid(row=5, column=0, columnspan=4, padx=5, pady=5)

        # Button zum Speichern des Graphen
        self.save_button = ttk.Button(button_frame4, text="Graphen speichern", state="disabled", command=self.controller.save_graph)
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))

        # Button zum Zurücksetzen des Graphen
        self.reset_button = ttk.Button(button_frame4, text="Graphen zurücksetzen", state="disabled")#, command=self.controller.reset_graph)
        self.reset_button.pack(side=tk.LEFT, padx=(0, 5))

    def plot_graph(self, data):
        # Überprüfen des Datenformats
        if len(data[0]) == 4:  # Datenformat: timestamp, x, y, z
            x_data = list(range(1, len(data) + 1))
            timestamps = [row[0] for row in data]
            x_data = [row[1] for row in data]
            y_data = [row[2] for row in data]
            z_data = [row[3] for row in data]

            # Matplotlib-Figur erstellen
            self.fig, ax = plt.subplots()
            ax.plot(x_data, x_data, label='x')
            ax.plot(x_data, y_data, label='y')
            ax.plot(x_data, z_data, label='z')
            ax.legend()

        elif len(data[0]) == 5:  # Datenformat: timestamp, qw, qx, qy, qz
            x_data = list(range(1, len(data) + 1))
            timestamps = [row[0] for row in data]
            qw_data = [row[1] for row in data]
            qx_data = [row[2] for row in data]
            qy_data = [row[3] for row in data]
            qz_data = [row[4] for row in data]

            # Matplotlib-Figur erstellen
            self.fig, ax = plt.subplots()
            ax.plot(x_data, qw_data, label='qw')
            ax.plot(x_data, qx_data, label='qx')
            ax.plot(x_data, qy_data, label='qy')
            ax.plot(x_data, qz_data, label='qz')
            ax.legend()
        else:
            print("Ungültiges Datenformat")
            return

        # Achsenbeschriftungen festlegen
        ax.set_xlabel('Zeitstempel (in sek)')
        ax.set_ylabel('Achsen')

        # Matplotlib-Figur in Tkinter-Fenster einbetten
        canvas = FigureCanvasTkAgg(self.fig, master=self.tab_visualize)
        canvas.draw()
        canvas.get_tk_widget().pack()


    def update_selected_file(self, file_path):
        self.selected_file_path = file_path
        self.db_placeholder.configure(text=file_path)

    def show_warning_message(self, title, message):
        self.port_var.set("Wähle einen Port")
        messagebox.showwarning(title, message)

    def show_info_message(self, title, message):
        messagebox.showwarning(title, message)

    def switch_file_button_on(self):
        self.search_module.config(state="normal")
        self.visualize_button.config(state="normal")

    def switch_visualize_button_on(self):
        self.search_module.config( text=" ", state="readonly")
        self.visualize_button.config(state="disabled")
        self.save_button.config(state="normal")
        self.reset_button.config(state="normal")






    def update_module_text(self, data):
        if data:
            self.module_text.config(state="normal")  # Textfeld bearbeitbar machen
            self.module_text.delete(1.0, tk.END)  # Aktuellen Inhalt des Textfeldes löschen

            # Daten in das Textfeld einfügen
            for row in data:
                self.module_text.insert(tk.END, f"{row}\n")

            self.module_text.config(state="disabled")  # Textfeld wieder schreibgeschützt machen
            return

        self.module_text.config(state="normal")
        self.module_text.delete("1.0", tk.END)
        self.module_text.config(state="disabled")  # Textfeld wieder schreibgeschützt machen


