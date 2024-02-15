import calendar
import time
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime, timedelta
from time import strftime
from pyfingerprint.pyfingerprint import PyFingerprint
from werkzeug.security import check_password_hash, generate_password_hash
import json
from threading import Thread
import copy
import random
import sqlite3
from PIL import Image, ImageTk
from functools import partial
import os
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class EmployeeAttendanceSystem:
    """Class representing the Employee Attendance System GUI."""

    def __init__(self, root):
        """Initialize the EmployeeAttendanceSystem instance.

        Parameters:
            root (tk.Tk): The root Tkinter window.
        """
        self.root = root
        self.root.title("Employee Attendance System")
        self.root.iconbitmap('files/icon/icon.ico')
        self.frames = {}
        self.module_password = 1234
        self.module_port = '/dev/ttyUSB0'
        self.baud_rate = 57600
        self.module_address = 0xFFFFFFFF
        self.repeat_password_entry = None
        self.bg_label = None
        self.motion = "forward"
        self.display_frame = None
        self.signup_form = None
        self.login_form = None
        self.position_y = 0
        self.position_x = 0
        self.tracked_list = []
        self.password_entry = None
        self.email_entry = None
        self.first_name_entry = None
        self.last_name_entry = None
        self.userid_entry = None
        self.submit_btn = None
        self.finger_print_data = None
        self.animator = None
        self.clock_label = None
        self.user_image_path = None
        self.user_info = None
        self.current_plot = None
        self.toplevel_window = None
        self.expected_time_of_arrival = 8  # 8am
        self.database_url = "files/instance/attendance_database.db"
        self.attendance_data = self.get_all_attendance_records()
        self.users = self.get_user_info()
        self.list_of_years = self.get_listofyears()
        self.list_of_months = list(calendar.month_name[1:])
        self.read_app_settings()

        # Set window geometry and center it on the screen
        self.root.geometry("1200x760")
        self.center_window()
        # self.create_database()

        self.root.update()
        # create a background label with a solid color
        self.bg_label = ctk.CTkLabel(self.root, text="", height=self.root.winfo_height(),
                                     width=self.root.winfo_width(), bg_color="#F0F0F0", fg_color="#f0f0f0")
        self.bg_label.place(relx=0, rely=0)

        # Initially hide other frames
        self.create_base_view()
        self.create_attendance_list()

    def create_base_view(self):
        """create the first view of the app upon loading"""
        # create a frame for the base_view widgets
        self.root.update()
        base_frame = ctk.CTkFrame(self.root, bg_color="#F0F0F0", fg_color="#E0E0E0",
                                  height=int(self.root.winfo_height() * 0.98),
                                  width=int(self.root.winfo_width() * 0.98))
        base_frame.place(relx=0.02, rely=0.02)
        self.root.update()

        # create a frame to display the clocked in users
        display_frame = ctk.CTkScrollableFrame(base_frame, fg_color="#ffffff", scrollbar_button_color="#E0E0E0",
                                               width=int(base_frame.winfo_width() * 0.196),
                                               scrollbar_fg_color="#ffffff",
                                               height=int(base_frame.winfo_height() * 0.25))
        display_frame.place(relx=0.1, rely=0)
        self.display_frame = display_frame

        # create a frame for nav buttons
        btn_frame = ctk.CTkFrame(base_frame, bg_color='#F0F0F0', fg_color="#E0E0E0",
                                 width=int(base_frame.winfo_width() * 0.05),
                                 height=int(base_frame.winfo_height()))
        btn_frame.place(relx=0, rely=0)
        self.root.update()

        # add buttons to the btn frame
        attendance_btn = ctk.CTkButton(btn_frame, text="Show Attendance", text_color="#333333",
                                       bg_color="#E0E0E0", fg_color="#28A745", height=50,
                                       width=int(btn_frame.winfo_width() * 0.4),
                                       command=self.create_attendance_list)
        attendance_btn.place(relx=0.1, rely=0.025)

        admin_btn = ctk.CTkButton(btn_frame, text="Admin Login", text_color="#333333",
                                  bg_color="#E0E0E0", fg_color="#28A745", height=50,
                                  width=int(btn_frame.winfo_width() * 0.4),
                                  command=self.create_login_form)
        admin_btn.place(relx=0.1, rely=0.05)

    def hide_frames(self):
        """Hide all frames except the login frame."""
        for frame in self.frames.values():
            frame.place_forget()

        # Show login frame
        self.frames["login"].place(relx=0.5, rely=0.5, anchor="center")

    def center_window(self):
        """Center the window on the screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 1200
        window_height = 760
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def create_login_form(self, event=None):
        """creates a form for user login"""
        # reset repeat_password
        self.repeat_password_entry = None

        # destroy the form if it exists
        if self.login_form:
            self.login_form.pack_forget()

        # remove all existing widgets within the display frame
        self.remove_all_widgets(self.display_frame)

        # create a label to hold the login form fields
        self.root.update()
        h = int(self.display_frame.cget('height')) - 10
        w = int(self.display_frame.winfo_width()) - 10
        login_label_label = ctk.CTkLabel(self.display_frame, text="", bg_color="#F0F0F0", fg_color="#e0e0e0",
                                         width=w, height=h, text_color="#000000")
        login_label_label.pack(anchor=tk.NW, padx=5, pady=5)
        self.login_form = login_label_label

        self.root.update()
        h = (int(login_label_label.cget('height')) // 2) - 100
        w = (int(login_label_label.cget("width")) // 2) - 80
        y = (int(login_label_label.cget('height')) - h) // 2
        x = ((int(login_label_label.cget("width")) // 2) - w) // 2
        login_label = ctk.CTkLabel(login_label_label, text="", bg_color="#F0F0F0", fg_color="#F0F0F0",
                                   width=w, height=h, text_color="#000000")
        login_label.place(x=x, y=y)

        # create title
        w = int(12.5 * 20)  # 5 is the number of char
        h = 40
        y = 0
        x = (int(login_label.cget('width')) - w) // 2
        title_label = ctk.CTkLabel(login_label, text="Admin Login", bg_color="#F0F0F0",
                                   font=("Trebuchet Ms", 22, "bold"),
                                   text_color="#000000", fg_color="#F0F0F0", width=w, height=h)
        title_label.place(x=x, y=y)

        # create login forms
        w = int(12.5 * 9)
        x = 25
        y = y + int(title_label.cget('height')) + 10
        email_label = ctk.CTkLabel(login_label, text="Email:", bg_color="#f0f0f0",
                                   text_color="#000000",
                                   fg_color="#e0e0e0", width=w, height=h)
        email_label.place(x=x, y=y)

        x = x + int(email_label.cget('width')) + 20
        self.email_entry = ctk.CTkEntry(login_label, fg_color="transparent", width=350, height=h,
                                        text_color="#000000")
        self.email_entry.place(x=x, y=y)

        x = 25
        y = y + int(self.email_entry.cget('height')) + 10
        password_label = ctk.CTkLabel(login_label, text="Password:", bg_color="#f0f0f0",
                                      text_color="#000000",
                                      fg_color="#e0e0e0", width=w, height=h)
        password_label.place(x=x, y=y)

        x = x + int(password_label.cget('width')) + 20
        self.password_entry = ctk.CTkEntry(login_label, fg_color="transparent", width=350, height=h,
                                           text_color="#000000", show="*")
        self.password_entry.place(x=x, y=y)

        w = 100
        x = ((int(login_label.cget('width')) - w) // 2) - int(12.5 * 7)
        y = y + int(self.password_entry.cget('height')) + 15
        submit_btn = ctk.CTkButton(login_label, text="Submit", font=("Trebuchet Ms", 14, "normal"),
                                   text_color="#000000", bg_color="#f0f0f0", fg_color="#28A745", height=h, width=w)
        submit_btn.place(x=x, y=y)
        submit_btn.configure(command=lambda: self.validate_input("login"))
        self.submit_btn = submit_btn

        w = int(12.5 * 7)
        x = x + int(submit_btn.cget('width')) + 10
        signup_btn = ctk.CTkLabel(login_label, text="Sign up here.", bg_color="#f0f0f0",
                                  font=("Trebuchet Ms", 13, "normal"), text_color="#000000",
                                  fg_color="#f0f0f0", width=w, height=h, cursor="hand2")
        signup_btn.place(x=x, y=y)
        # bind a click event to the text
        signup_btn.bind("<Button-1>", self.create_signup_form)

        return

    def create_signup_form(self, event=None):
        """creates a form for user signup"""
        # reset repeat_password
        self.repeat_password_entry = None

        # destroy the form if it exists
        if self.signup_form:
            self.signup_form.pack_forget()

        # remove all existing widgets within the display frame
        self.remove_all_widgets(self.display_frame)

        # create a label to hold the signup form fields
        self.root.update()
        h = int(self.display_frame.cget('height')) - 10
        w = int(self.display_frame.winfo_width()) - 10
        signup_label_label = ctk.CTkLabel(self.display_frame, text="", bg_color="#F0F0F0", fg_color="#e0e0e0",
                                          width=w, height=h, text_color="#000000")
        signup_label_label.pack(anchor=tk.NW, padx=5, pady=5)
        self.signup_form = signup_label_label

        self.root.update()
        h = (int(signup_label_label.cget('height')) // 2) + 180
        w = (int(signup_label_label.cget("width")) // 2) - 80
        y = (int(signup_label_label.cget('height')) - h) // 2
        x = ((int(signup_label_label.cget("width")) // 2) - w) // 2
        signup_label = ctk.CTkLabel(signup_label_label, text="", bg_color="#F0F0F0", fg_color="#F0F0F0",
                                    width=w, height=h, text_color="#000000")
        signup_label.place(x=x, y=y)

        # create title
        w = int(12.5 * 20)  # 5 is the number of char
        h = 40
        y = 0
        x = (int(signup_label.cget('width')) - w) // 2
        title_label = ctk.CTkLabel(signup_label, text="Admin Signup", bg_color="#F0F0F0",
                                   font=("Trebuchet Ms", 22, "bold"),
                                   text_color="#000000", fg_color="#F0F0F0", width=w, height=h)
        title_label.place(x=x, y=y)

        # create signup forms
        w = int(12.5 * 9)
        x = 25
        y = y + int(title_label.cget('height')) + 10
        first_name = ctk.CTkLabel(signup_label, text="First Name:", bg_color="#f0f0f0",
                                  text_color="#000000",
                                  fg_color="#e0e0e0", width=w, height=h)
        first_name.place(x=x, y=y)

        x = x + int(first_name.cget('width')) + 20
        self.first_name_entry = ctk.CTkEntry(signup_label, fg_color="transparent", width=350, height=h,
                                             text_color="#000000")
        self.first_name_entry.place(x=x, y=y)

        w = int(12.5 * 9)
        x = 25
        y = y + int(self.first_name_entry.cget('height')) + 10
        last_name = ctk.CTkLabel(signup_label, text="Last Name:", bg_color="#f0f0f0",
                                 text_color="#000000",
                                 fg_color="#e0e0e0", width=w, height=h)
        last_name.place(x=x, y=y)

        x = x + int(last_name.cget('width')) + 20
        self.last_name_entry = ctk.CTkEntry(signup_label, fg_color="transparent", width=350, height=h,
                                            text_color="#000000")
        self.last_name_entry.place(x=x, y=y)

        w = int(12.5 * 9)
        x = 25
        y = y + int(self.last_name_entry.cget('height')) + 10
        userid = ctk.CTkLabel(signup_label, text="User ID:", bg_color="#f0f0f0",
                              text_color="#000000",
                              fg_color="#e0e0e0", width=w, height=h)
        userid.place(x=x, y=y)

        x = x + int(userid.cget('width')) + 20
        self.userid_entry = ctk.CTkEntry(signup_label, fg_color="transparent", width=350, height=h,
                                         text_color="#000000")
        self.userid_entry.place(x=x, y=y)

        w = int(12.5 * 9)
        x = 25
        y = y + int(self.userid_entry.cget('height')) + 10
        email_label = ctk.CTkLabel(signup_label, text="Email:", bg_color="#f0f0f0",
                                   text_color="#000000",
                                   fg_color="#e0e0e0", width=w, height=h)
        email_label.place(x=x, y=y)

        x = x + int(email_label.cget('width')) + 20
        self.email_entry = ctk.CTkEntry(signup_label, fg_color="transparent", width=350, height=h,
                                        text_color="#000000")
        self.email_entry.place(x=x, y=y)

        x = 25
        y = y + int(self.email_entry.cget('height')) + 10
        password_label = ctk.CTkLabel(signup_label, text="Password:", bg_color="#f0f0f0",
                                      text_color="#000000",
                                      fg_color="#e0e0e0", width=w, height=h)
        password_label.place(x=x, y=y)

        x = x + int(password_label.cget('width')) + 20
        self.password_entry = ctk.CTkEntry(signup_label, fg_color="transparent", width=350, height=h,
                                           text_color="#000000", show="*")
        self.password_entry.place(x=x, y=y)

        x = x + int(self.password_entry.cget('width')) + 10
        self.repeat_password_entry = ctk.CTkEntry(signup_label, fg_color="transparent", width=300, height=h,
                                                  text_color="#000000", show="*",
                                                  placeholder_text="Repeat password")
        self.repeat_password_entry.place(x=x, y=y)

        x = 25
        y = y + int(self.repeat_password_entry.cget('height')) + 10 + ((80 - h) // 2)
        user_image_btn = ctk.CTkButton(signup_label, text="Select Photo", font=("Trebuchet Ms", 14, "normal"),
                                       text_color="#000000", bg_color="#f0f0f0", fg_color="#28A745", height=h, width=w)
        user_image_btn.place(x=x, y=y)

        x = x + int(user_image_btn.cget('width')) + 20
        y = y - ((80 - h) // 2)
        user_image_label = ctk.CTkLabel(signup_label, text="No files selected", bg_color="#f0f0f0",
                                        font=("Trebuchet Ms", 22, "normal"),
                                        text_color="#f0f0f0",
                                        fg_color="#ffffff", width=300, height=80)
        user_image_label.place(x=x, y=y)
        user_image_btn.configure(command=lambda: self.select_image_and_update_widget(user_image_label))

        x = 25
        y = y + int(user_image_label.cget('height')) + 10 + ((80 - h) // 2)
        finger_print = ctk.CTkButton(signup_label, text="Capture Finger", font=("Trebuchet Ms", 14, "normal"),
                                     text_color="#000000", bg_color="#f0f0f0", fg_color="#28A745", height=h, width=w)
        finger_print.place(x=x, y=y)

        x = x + int(finger_print.cget('width')) + 20
        y = y - ((80 - h) // 2)
        finger_print_label = ctk.CTkLabel(signup_label, text="", bg_color="#f0f0f0",
                                          text_color="#000000",
                                          fg_color="#ffffff", width=300, height=80)
        finger_print_label.place(x=x, y=y)
        finger_print.configure(command=lambda: self.capture_finger_print(finger_print_label))

        w = 100
        x = ((int(signup_label.cget('width')) - w) // 2) - int(12.5 * 7)
        y = y + int(finger_print_label.cget('height')) + 15
        submit_btn = ctk.CTkButton(signup_label, text="Submit", font=("Trebuchet Ms", 14, "normal"),
                                   text_color="#000000", bg_color="#f0f0f0", fg_color="#28A745", height=h, width=w)
        submit_btn.place(x=x, y=y)
        submit_btn.configure(command=lambda: self.validate_input('signup'))
        self.submit_btn = submit_btn

        w = int(12.5 * 7)
        x = x + int(submit_btn.cget('width')) + 10
        login_btn = ctk.CTkLabel(signup_label, text="Login here.", bg_color="#f0f0f0",
                                 font=("Trebuchet Ms", 13, "normal"), text_color="#000000",
                                 fg_color="#f0f0f0", width=w, height=h, cursor="hand2")
        login_btn.place(x=x, y=y)
        # bind a click event to the text
        login_btn.bind("<Button-1>", self.create_login_form)

        return

    def remove_all_widgets(self, container):
        for widget in container.winfo_children():
            widget.pack_forget()
            self.clock_label = None

    def create_attendance_list(self):
        """displays a list of users who have clocked in or out for the day"""
        # first remove all widgets within the display
        self.remove_all_widgets(self.display_frame)

        # Get the current date
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Create a header label with the current date
        header_text = f"Today in Attendance {current_date}"
        h = 50
        self.root.update()
        w = int(self.display_frame.winfo_width()) - 40
        header_label = ctk.CTkLabel(self.display_frame, text=header_text, bg_color="#F0F0F0", fg_color="#e0e0e0",
                                    font=("Helvetica", 16, "bold"), width=w, height=h, text_color="#000000")
        header_label.pack(anchor=tk.NW, padx=10, pady=10)

        # create a label inside the header label for displaying clock
        w = (w // 8) - 10
        h = h - 10
        y = 5
        x = (int(header_label.cget('width')) // 2) - (w + 10)
        clock_label = ctk.CTkLabel(header_label, font=('calibri', 18, 'bold'), text_color="#000000",
                                   bg_color='#e0e0e0', fg_color='#ffffff', width=w, height=h)
        clock_label.place(x=x, y=y)
        self.clock_label = clock_label
        self.display_clock(clock_label)

        # track attendance
        self.track_attendance()
        # self.create_attendance_instance(month=1)

    def display_clock(self, window):
        """displays clock at the center of the given window"""
        string = strftime("%I:%M:%S %p")
        window.configure(text=string)
        window.after(1000, lambda: self.display_clock(window))

    def animate_button(self, canvas, button, end):
        if self.finger_print_data:
            return
        if button.position_x == 0:
            self.motion = "forward"
        elif button.position_x == end - 20:
            self.motion = "reverse"

        def forward():
            button.position_x += 5

        def reverse():
            button.position_x -= 5

        if self.motion == "forward":
            forward()
        elif self.motion == "reverse":
            reverse()

        button.place(x=button.position_x, y=button.position_y)
        canvas.after(10, self.animate_button, canvas, button, end)

    def create_animation(self, window):
        w = (int(window.cget("width")) * 2) - 10
        h = (int(window.cget("height")) * 2) - 10
        canvas = tk.Canvas(window, width=w, height=h, bg="#ffffff")
        canvas.place(x=5, y=5)

        y = ((h // 2) - 20) // 2
        end = w // 2
        button = ctk.CTkButton(canvas, text="", height=20, width=20, corner_radius=50, bg_color="#ffffff",
                               fg_color="#000000")
        button.position_x = 0
        button.position_y = y
        button.place(x=0, y=y)

        self.animator = canvas

        return canvas, button, end

    def capture_finger_print(self, window):
        """captures fingerprint data from fingerprint sensor"""
        msg = "The system is about to scan your fingerprint. Place your finger firmly on the fingerprint sensor. "
        msg += "When you are ready click OK to continue, or Cancel to abort."

        if self.alert_user(msg):

            canvas, button, end = self.create_animation(window)
            self.animate_button(canvas, button, end)
            try:
                # Initialize the fingerprint sensor
                fingerprint_sensor = PyFingerprint(self.module_port, self.baud_rate, self.module_address,
                                                   self.module_password)

                if not fingerprint_sensor.verifyPassword():
                    raise ValueError('The given fingerprint sensor password is wrong!')

                # Wait for a finger to be detected
                print('Place your finger on the sensor...')

                while not fingerprint_sensor.readImage():
                    pass

                # Convert the read image to characteristics
                fingerprint_sensor.convertImage(0x01)
                self.finger_print_data = fingerprint_sensor.downloadCharacteristics(0x01)

            except Exception as e:
                error = f'Error: {e}'
                # print(error)
                self.notify_user(error)
                # time.sleep(5)
                if self.animator:
                    time.sleep(5)
                    self.animator.destroy()
                    self.animator = None
                self.display_tif(window)

        return False

    def notify_user(self, msg=None):
        """ Pops a message when there is need to. Message to be displayed can be given as an arg """
        if msg is None:
            messagebox.showinfo("Alert!", f"I am a message button.")
        else:
            messagebox.showinfo("Alert!", "{}".format(msg))

    def alert_user(self, msg):
        """ Pops an alert in which user is expected to click ok to proceed or cancel to abort operation """
        response = messagebox.askokcancel("Confirmation", msg)

        # Check the user's response
        if response:
            return True
        else:
            return False

    def ask_user(self, question):
        """Ask the user a yes or no question."""
        # Display a message box with the question
        answer = messagebox.askyesno("Question", question)
        return answer  # returns True for yes, False for No

    def show_user(self, message):
        root = ctk.CTk()
        root.withdraw()  # Hide the main window

        notification = ctk.CTkToplevel(root, fg_color="#ffcd6e")
        notification.geometry("300x50")
        notification.title("")
        notification.overrideredirect(True)

        label = ctk.CTkLabel(notification, text=message, fg_color="#ffcd6e", text_color="#000000")
        label.pack(padx=10, pady=10)

        notification.after(3000, notification.destroy)  # Close the notification after 3 seconds

        notification.mainloop()

    def display_tif(self, window):
        """displays tif fingerprint images"""
        image_path = "files/tif/100__M_Left_index_finger.tif"

        # fingerprint_test = cv2.imread(image_path)
        # cv2.imshow("Original", cv2.resize(fingerprint_test, None, fx=1, fy=1))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # process with PIL
        image = Image.open(image_path)

        # Convert the PIL Image to a Tkinter PhotoImage
        # photo = ImageTk.PhotoImage(image)
        ctk_image = ctk.CTkImage(image, size=(90, 90))

        # Create a Label widget to display the image
        window.configure(image=ctk_image)
        # Keep a reference to the image to prevent it from being garbage collected
        window.image = ctk_image

    def create_database(self):
        """creates sqlite database with two tables"""
        conn = sqlite3.connect(self.database_url)
        cursor = conn.cursor()

        # Create User table
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS User (
                    id INTEGER PRIMARY KEY,
                    company_id TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT,
                    reg_date DATETIME,
                    admin_type TEXT,
                    password TEXT
                )
            ''')

        # Create Attendance table
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS Attendance (
                    attendance_id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    time_in DATETIME,
                    time_out DATETIME,
                    remarks TEXT,
                    FOREIGN KEY (user_id) REFERENCES User(id)
                )
            ''')

        # Commit changes and close connection
        conn.commit()
        conn.close()

    def select_image_and_update_widget(self, window):
        """allows user to select image from  device and then modifies a widget using the file information"""

        def remove_image(event):
            """deletes the uploaded image"""
            window.unbind("<Button-1>")
            window.configure(text="No files selected", text_color="#f0f0f0",
                             font=("Trebuchet Ms", 22, "normal"))
            self.user_image_path = None
            return

        path = "/"
        f_types = [("PNG file", "*.PNG"), ("png file", "*.png"), ("JPEG file", "*.JPEG"),
                   ("JPG file", "*.JPG"), ("JPG File", "*.jpg")]
        file_path = tk.filedialog.askopenfilename(filetypes=f_types)

        if file_path:
            self.user_image_path = file_path
            # extract the file name
            file_name = os.path.basename(file_path)
            window_text = f"{file_name[:21]}...remove"
            window.configure(text=window_text, text_color="#000000", cursor="hand2",
                             font=("Trebuchet Ms", 18, "normal"))
            window.bind("<Button-1>", remove_image)

    def is_valid_email(self, email: str) -> bool:
        """
        Checks if the given string is a valid email address.
        Returns True if it's a valid email, False otherwise.
        """
        # Regular expression pattern for validating an email address
        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        # Using the re.match function to check if the email matches the pattern
        if re.match(email_pattern, email):
            return True
        else:
            return False

    def validate_input(self, input_type):
        """validates user inputs from the forms"""
        if input_type == "signup":
            # check that image is valid
            if not self.is_valid_email(self.email_entry.get()):
                self.notify_user("Email is not valid!")
                return
            if not self.userid_entry.get():
                self.notify_user("User_id is required!")
                return
            if not self.first_name_entry.get():
                self.notify_user("First name is required!")
                return
            if not self.last_name_entry.get():
                self.notify_user("Last name is required!")
                return

            # check that email and user_id are unique
            if self.item_exists("User", "email", self.email_entry.get()):
                self.notify_user("This email already exists for another user!")
                return
            if self.item_exists("User", "company_id", self.userid_entry.get()):
                self.notify_user("This user_id already exists for another user!")
                return
            # validate password
            if self.password_entry.get() != self.repeat_password_entry.get():
                self.notify_user("The two password entries do not match!")
                return
            password_strength = self.check_password_strength(self.password_entry.get())
            if password_strength['status'] > 1:
                message = ''
                count = 1
                for x in password_strength['error']:
                    message += f'{count}. {x}.\n'
                    count += 1
                self.notify_user(message)
                return

            # check that fingerprint data was captured
            if not self.finger_print_data:
                self.notify_user("Fingerprint must be captured before you can proceed")
                # return

            # compute user data
            data = {}
            data['first_name'] = self.first_name_entry.get().title()
            data['last_name'] = self.last_name_entry.get().title()
            data['company_id'] = self.userid_entry.get()
            data['email'] = self.email_entry.get()
            data['admin_type'] = 'admin'
            data['reg_date'] = datetime.now()
            data['password'] = generate_password_hash(self.password_entry.get())

            # save all user data
            try:
                self.save_user_info(data)
                self.process_image(data['company_id'])
                self.save_fingerprint_data(data['company_id'])
                self.notify_user("Signup was successful! You can now login.")
                self.create_login_form()
            except Exception as e:
                self.notify_user(f'{e}')

            return

        elif input_type == "login":
            # check that email is valid
            if not self.is_valid_email(self.email_entry.get()):
                self.notify_user("You provided an invalid email format.")
                return

            # compute user data
            data = {}
            data['email'] = self.email_entry.get()
            data['password'] = self.password_entry.get()

            # validate user
            resp = self.validate_user(data)
            self.notify_user(resp['message'])
            if resp['status'] == 1:
                self.create_admin_view()

            return

        elif input_type == "enroll":
            if not self.userid_entry.get():
                self.notify_user("User_id is required!")
                return
            if not self.first_name_entry.get():
                self.notify_user("First name is required!")
                return
            if not self.last_name_entry.get():
                self.notify_user("Last name is required!")
                return

            # check that user_id is unique
            if self.item_exists("User", "company_id", self.userid_entry.get()):
                self.notify_user("This user_id already exists for another user!")
                return

            # check that fingerprint data was captured
            if not self.finger_print_data:
                self.notify_user("Fingerprint must be capture before you can proceed")
                # return

            # compute user data
            data = {}
            data['first_name'] = self.first_name_entry.get().title()
            data['last_name'] = self.last_name_entry.get().title()
            data['company_id'] = self.userid_entry.get()
            data['email'] = None
            data['admin_type'] = 'user'
            data['reg_date'] = datetime.now()
            data['password'] = None

            # save all user data
            try:
                self.save_user_info(data)
                self.process_image(data['company_id'])
                self.save_fingerprint_data(data['company_id'])
                self.notify_user("User enrollment was successful!")
                self.create_enrol_form()
            except Exception as e:
                self.notify_user(f'{e}')

            return

    def item_exists(self, table, column, item, exclude=None):
        """connects to database and checks if item exists"""
        conn = sqlite3.connect(self.database_url)
        cursor = conn.cursor()

        # Construct the WHERE clause based on the exclude parameter
        where_clause = f'{column} = ?'
        if exclude is not None:
            where_clause += ' AND ' + ' AND '.join(f'{col} != ?' for col, val in exclude)

        # Execute a SELECT query to check if the value exists in the table
        query = f'SELECT * FROM {table} WHERE {where_clause}'
        cursor.execute(query, (item, *[val for _, val in exclude]) if exclude else (item,))
        result = cursor.fetchone()

        # Close the connection
        conn.close()

        # If result is not None, value exists in the table; otherwise, it doesn't
        return result is not None

    def check_password_strength(self, password: str) -> dict:
        """validates password for certain criteria """
        error = []
        special = '[@_!#$%^&*()<>?/\|}{~:]'
        if len(password) < 8:
            error.append("Password cannot be less than 8 characters ")
        if re.search('[0-9]', password) is None:
            error.append("Password must include at least one number!")
        if re.search("[a-zA-Z]", password) is None:
            error.append("Password must include at least one letter!")
        if re.search('[A-Z]', password) is None:
            error.append("Password must include at least one UPPERCASE letter!")
        if re.search('[a-z]', password) is None:
            error.append("Password must include at least one LOWERCASE letter!")
        if (re.compile(special).search(password) == None):
            error.append("Password must include at least one special character: {}".format(special))
        if len(error) > 0:
            return {'status': 2, "message": "Password Not Ok", 'error': error}
        return {"status": 1, "message": "Password Ok", "error": []}

    def process_image(self, image_name):
        f"""
        Opens an image file using PIL, generates a thumbnail image of size (200x200),
        and saves the thumbnail with name "{image_name}.PNG" to the location "files/thumbs".

        Args:
            image_name (str): The name for the generated thumbnail.

        Returns:
            None
        """
        if self.user_image_path:
            try:
                # Define the save path for the thumbnail image
                save_dir = "files/thumbs"
                os.makedirs(save_dir, exist_ok=True)  # Ensure the directory exists

                # Generate the save path for the thumbnail image
                save_path = os.path.join(save_dir, f"{image_name}.PNG")

                # Open the image file using PIL and generate a thumbnail image
                with Image.open(self.user_image_path) as image:
                    thumbnail = image.copy()
                    thumbnail.thumbnail((200, 200))

                    # Save the thumbnail image
                    thumbnail.save(save_path)
                    self.user_image_path = None
            except Exception as e:
                error = f'AN error occurred:\n {e}'
                self.notify_user(error)

        return

    def save_fingerprint_data(self, filename):
        """saves the captured fingerprint data as a bin file"""
        if self.finger_print_data:
            # Save the fingerprint template to a file
            new_file_path = f'files/bin/{filename}.bin'
            with open(new_file_path, 'wb') as f:
                f.write(self.finger_print_data)
                self.finger_print_data = None

    def save_user_info(self, info: dict):
        """Saves the user information to the database."""
        # Connect to the SQLite database
        conn = sqlite3.connect(self.database_url)
        cursor = conn.cursor()

        # SQL query with placeholders for the values
        columns = ', '.join(info.keys())
        placeholders = ', '.join(['?' for _ in info.keys()])
        sql = f"INSERT INTO User ({columns}) VALUES ({placeholders})"

        # Extract values from the dictionary and execute the query
        values = tuple(info.values())
        cursor.execute(sql, values)

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

    def validate_user(self, user_data: dict):
        """Validates user credentials."""
        # Connect to the SQLite database
        conn = sqlite3.connect(self.database_url)
        cursor = conn.cursor()

        # Check if the user email exists in the User table
        email = user_data.get('email')
        password = user_data.get('password')
        cursor.execute("SELECT * FROM User WHERE email = ?", (email,))
        user_record = cursor.fetchone()

        # If user email doesn't exist, return False
        if user_record is None:
            message = "User not found!"
            conn.close()
            return {'status': 2, 'message': message}

        # If user email exists, check if the password matches
        if check_password_hash(user_record[7], password):  # Assuming password is stored in the 8th column
            message = "User has been validated!"
            info = {}
            info['id'] = user_record[0]
            info['company_id'] = user_record[1]
            info['first_name'] = user_record[2]
            info['last_name'] = user_record[3]
            info['email'] = user_record[4]
            info['reg_date'] = user_record[5]  # .strftime("%d-%m-%Y %I:%M:%S %p")
            info['admin_type'] = user_record[6]

            user = AdminUser(info)
            self.user_info = user

            conn.close()
            return {'status': 1, 'message': message}
        else:
            message = "Wrong user credentials."
            conn.close()
            return {'status': 2, 'message': message}

    def create_admin_view(self):
        """creates the admin work window"""

        # create a frame for the base_view widgets
        self.root.update()
        base_frame = ctk.CTkFrame(self.root, bg_color="#F0F0F0", fg_color="#E0E0E0",
                                  height=int(self.root.winfo_height() * 0.98),
                                  width=int(self.root.winfo_width() * 0.98))
        base_frame.place(relx=0.02, rely=0.02)
        self.root.update()

        # create the work window
        display_frame = ctk.CTkScrollableFrame(base_frame, fg_color="#ffffff", scrollbar_button_color="#E0E0E0",
                                               width=int(base_frame.winfo_width() * 0.196),
                                               scrollbar_fg_color="#ffffff",
                                               height=int(base_frame.winfo_height() * 0.25))
        display_frame.place(relx=0.1, rely=0)
        self.display_frame = display_frame

        # create a frame for nav buttons
        btn_frame = ctk.CTkFrame(base_frame, bg_color='#F0F0F0', fg_color="#E0E0E0",
                                 width=int(base_frame.winfo_width() * 0.05),
                                 height=int(base_frame.winfo_height()))
        btn_frame.place(relx=0, rely=0)
        self.root.update()

        # add widgets to the btn frame

        # welcome label
        self.root.update()
        h = 100
        w = int(btn_frame.winfo_width() * 0.5)
        x, y = 0, 0
        img = Image.open('files/image/biomedance.png')
        text = f"Welcome {self.user_info.first_name}."
        ctk_image = ctk.CTkImage(img, size=(h, h))
        logo_label = ctk.CTkLabel(btn_frame, text=text, image=ctk_image,
                                  bg_color="#E0E0E0", fg_color="#f0f0f0", height=h,
                                  width=w, compound='left')
        logo_label.place(x=x, y=y)

        y = y + int(logo_label.cget('height')) + 20
        x = 25
        enroll_btn = ctk.CTkButton(btn_frame, text="Enroll User", text_color="#333333",
                                   bg_color="#E0E0E0", fg_color="#28A745", height=50,
                                   width=int(btn_frame.winfo_width() * 0.4),
                                   command=self.create_enrol_form)
        enroll_btn.place(x=x, y=y)

        y = y + int(enroll_btn.cget('height')) + 20
        view_users_btn = ctk.CTkButton(btn_frame, text="View Users", text_color="#333333",
                                       bg_color="#E0E0E0", fg_color="#28A745", height=50,
                                       width=int(btn_frame.winfo_width() * 0.4),
                                       command=self.list_enrolled_users)
        view_users_btn.place(x=x, y=y)

        y = y + int(view_users_btn.cget('height')) + 20
        history_btn = ctk.CTkButton(btn_frame, text="Attendance History", text_color="#333333",
                                    bg_color="#E0E0E0", fg_color="#28A745", height=50,
                                    width=int(btn_frame.winfo_width() * 0.4),
                                    command=self.create_attendance_history)
        history_btn.place(x=x, y=y)

        y = y + int(history_btn.cget('height')) + 20
        daily_report_btn = ctk.CTkButton(btn_frame, text="Run Daily Report", text_color="#333333",
                                         bg_color="#E0E0E0", fg_color="#28A745", height=50,
                                         width=int(btn_frame.winfo_width() * 0.4),
                                         command=lambda: self.run_attendance_trend('daily'))
        daily_report_btn.place(x=x, y=y)

        y = y + int(daily_report_btn.cget('height')) + 20
        monthly_report_btn = ctk.CTkButton(btn_frame, text="Run Monthly Report", text_color="#333333",
                                           bg_color="#E0E0E0", fg_color="#28A745", height=50,
                                           width=int(btn_frame.winfo_width() * 0.4),
                                           command=lambda: self.run_attendance_trend('monthly'))
        monthly_report_btn.place(x=x, y=y)

        y = y + int(monthly_report_btn.cget('height')) + 20
        settings_btn = ctk.CTkButton(btn_frame, text="Settings", text_color="#333333",
                                     bg_color="#E0E0E0", fg_color="#28A745", height=50,
                                     width=int(btn_frame.winfo_width() * 0.4),
                                     command=self.create_settings_form)
        settings_btn.place(x=x, y=y)

        y = y + int(settings_btn.cget('height')) + 170
        logout_btn = ctk.CTkButton(btn_frame, text="Log Out", text_color="#333333",
                                   bg_color="#E0E0E0", fg_color="#f0f0f0", height=50,
                                   width=int(btn_frame.winfo_width() * 0.3), corner_radius=15,
                                   command=self.create_base_view)
        logout_btn.place(x=x, y=y)

        return

    def create_enrol_form(self):
        """creates a form for user enrolment"""
        # reset necessary attributes
        self.repeat_password_entry = None
        self.finger_print_data = None
        self.user_image_path = None

        # remove all existing widgets within the display frame
        self.remove_all_widgets(self.display_frame)

        # create a label to hold the signup form fields
        self.root.update()
        h = int(self.display_frame.cget('height')) - 10
        w = int(self.display_frame.winfo_width()) - 10
        signup_label_label = ctk.CTkLabel(self.display_frame, text="", bg_color="#F0F0F0", fg_color="#e0e0e0",
                                          width=w, height=h, text_color="#000000")
        signup_label_label.pack(anchor=tk.NW, padx=5, pady=5)

        self.root.update()
        h = (int(signup_label_label.cget('height')) // 2) + 100
        w = (int(signup_label_label.cget("width")) // 2) - 80
        y = (int(signup_label_label.cget('height')) - h) // 2
        x = ((int(signup_label_label.cget("width")) // 2) - w) // 2
        signup_label = ctk.CTkLabel(signup_label_label, text="", bg_color="#F0F0F0", fg_color="#F0F0F0",
                                    width=w, height=h, text_color="#000000")
        signup_label.place(x=x, y=y)

        # create title
        w = int(12.5 * 20)  # 5 is the number of char
        h = 40
        y = 0
        x = (int(signup_label.cget('width')) - w) // 2
        title_label = ctk.CTkLabel(signup_label, text="Enroll User", bg_color="#F0F0F0",
                                   font=("Trebuchet Ms", 22, "bold"),
                                   text_color="#000000", fg_color="#F0F0F0", width=w, height=h)
        title_label.place(x=x, y=y)

        # create signup forms
        w = int(12.5 * 9)
        x = 25
        y = y + int(title_label.cget('height')) + 10
        first_name = ctk.CTkLabel(signup_label, text="First Name:", bg_color="#f0f0f0",
                                  text_color="#000000",
                                  fg_color="#e0e0e0", width=w, height=h)
        first_name.place(x=x, y=y)

        x = x + int(first_name.cget('width')) + 20
        self.first_name_entry = ctk.CTkEntry(signup_label, fg_color="transparent", width=350, height=h,
                                             text_color="#000000")
        self.first_name_entry.place(x=x, y=y)

        w = int(12.5 * 9)
        x = 25
        y = y + int(self.first_name_entry.cget('height')) + 10
        last_name = ctk.CTkLabel(signup_label, text="Last Name:", bg_color="#f0f0f0",
                                 text_color="#000000",
                                 fg_color="#e0e0e0", width=w, height=h)
        last_name.place(x=x, y=y)

        x = x + int(last_name.cget('width')) + 20
        self.last_name_entry = ctk.CTkEntry(signup_label, fg_color="transparent", width=350, height=h,
                                            text_color="#000000")
        self.last_name_entry.place(x=x, y=y)

        w = int(12.5 * 9)
        x = 25
        y = y + int(self.last_name_entry.cget('height')) + 10
        userid = ctk.CTkLabel(signup_label, text="User ID:", bg_color="#f0f0f0",
                              text_color="#000000",
                              fg_color="#e0e0e0", width=w, height=h)
        userid.place(x=x, y=y)

        x = x + int(userid.cget('width')) + 20
        self.userid_entry = ctk.CTkEntry(signup_label, fg_color="transparent", width=350, height=h,
                                         text_color="#000000")
        self.userid_entry.place(x=x, y=y)

        x = 25
        y = y + int(self.userid_entry.cget('height')) + 10 + ((80 - h) // 2)
        user_image_btn = ctk.CTkButton(signup_label, text="Select Photo", font=("Trebuchet Ms", 14, "normal"),
                                       text_color="#000000", bg_color="#f0f0f0", fg_color="#28A745", height=h, width=w)
        user_image_btn.place(x=x, y=y)

        x = x + int(user_image_btn.cget('width')) + 20
        y = y - ((80 - h) // 2)
        user_image_label = ctk.CTkLabel(signup_label, text="No files selected", bg_color="#f0f0f0",
                                        font=("Trebuchet Ms", 22, "normal"),
                                        text_color="#f0f0f0",
                                        fg_color="#ffffff", width=300, height=80)
        user_image_label.place(x=x, y=y)
        user_image_btn.configure(command=lambda: self.select_image_and_update_widget(user_image_label))

        x = 25
        y = y + int(user_image_label.cget('height')) + 10 + ((80 - h) // 2)
        finger_print = ctk.CTkButton(signup_label, text="Capture Finger", font=("Trebuchet Ms", 14, "normal"),
                                     text_color="#000000", bg_color="#f0f0f0", fg_color="#28A745", height=h, width=w)
        finger_print.place(x=x, y=y)

        x = x + int(finger_print.cget('width')) + 20
        y = y - ((80 - h) // 2)
        finger_print_label = ctk.CTkLabel(signup_label, text="", bg_color="#f0f0f0",
                                          text_color="#000000",
                                          fg_color="#ffffff", width=300, height=80)
        finger_print_label.place(x=x, y=y)
        finger_print.configure(command=lambda: self.capture_finger_print(finger_print_label))

        w = 100
        x = ((int(signup_label.cget('width')) - w) // 2) - int(12.5 * 7)
        y = y + int(finger_print_label.cget('height')) + 15
        submit_btn = ctk.CTkButton(signup_label, text="Submit", font=("Trebuchet Ms", 14, "normal"),
                                   text_color="#000000", bg_color="#f0f0f0", fg_color="#28A745", height=h, width=w)
        submit_btn.place(x=x, y=y)
        submit_btn.configure(command=lambda: self.validate_input('enroll'))
        self.submit_btn = submit_btn

        return

    def list_enrolled_users(self):
        """creates a list view of enrolled users"""
        # remove all existing widgets within the display frame
        self.remove_all_widgets(self.display_frame)

        # fetch user records
        user_info = self.get_user_info()

        # create a label to hold the user info items
        self.root.update()
        h = int(self.display_frame.cget('height')) - 10
        w = (int(self.display_frame.winfo_width()) - 10) // 2
        base_label = ctk.CTkLabel(self.display_frame, text="", bg_color="#F0F0F0", fg_color="#e0e0e0",
                                  width=w, height=h, text_color="#000000")
        base_label.pack(anchor=tk.NW, padx=5, pady=5)

        # title label
        h = 80
        x, y = 0, 0
        total_count = len(user_info)  # total number of enrolled users
        title_label = ctk.CTkLabel(base_label, text=f"LIST OF ENROLLED USERS - {total_count}", width=w, height=h,
                                   bg_color="#ffffff", fg_color="#f0f0f0", corner_radius=8, text_color="#333333",
                                   font=("Trebuchet Ms", 18, "bold"))
        title_label.pos_x, title_label.pos_y = x, y
        title_label.place(x=x, y=y)

        y = title_label.pos_y + int(title_label.cget('height')) + 20
        h = 25

        # display each user info one at a time
        for user in user_info:
            # name label
            w = 360
            x = title_label.pos_x + 20
            name_label = ctk.CTkLabel(base_label, text=f"{user['full_name']}", width=w, height=h,
                                      bg_color="#e0e0e0", fg_color="#ffffff", corner_radius=8, text_color="grey",
                                      font=("Trebuchet Ms", 14, "normal"))
            name_label.place(x=x, y=y)

            # company ID
            w = int(8.5 * 14)
            x = x + int(name_label.cget('width')) + 20
            id_label = ctk.CTkLabel(base_label, text=f"{user['company_id']}", width=w, height=h,
                                    bg_color="#e0e0e0", fg_color="#ffffff", corner_radius=8, text_color="grey",
                                    font=("Trebuchet Ms", 14, "normal"))
            id_label.place(x=x, y=y)

            # admin type
            w = int(8.5 * 14)
            x = x + int(id_label.cget('width')) + 20
            admin_type_label = ctk.CTkLabel(base_label, text=f"{user['admin_type']}", width=w, height=h,
                                            bg_color="#e0e0e0", fg_color="#ffffff", corner_radius=8,
                                            text_color="grey", font=("Trebuchet Ms", 14, "normal"))
            admin_type_label.place(x=x, y=y)

            # edit btn
            w = 100
            x = x + int(admin_type_label.cget('width')) + 20
            edit_btn = ctk.CTkButton(base_label, text="Edit", font=("Trebuchet Ms", 13, "normal"),
                                     text_color="#000000", bg_color="#e0e0e0", fg_color="#28A745", height=h,
                                     width=w)
            edit_btn.place(x=x, y=y)
            edit_btn.configure(command=partial(self.edit_user_info, user))

            # delete btn
            x = x + int(edit_btn.cget('width')) + 20
            delete_btn = ctk.CTkButton(base_label, text="Delete", font=("Trebuchet Ms", 13, "normal"),
                                       text_color="#000000", bg_color="#e0e0e0", fg_color="#28A745", height=h,
                                       width=w)
            delete_btn.place(x=x, y=y)
            delete_btn.configure(command=None)

            # callbacks
            def delete_callback(last_name, user_company_id):
                """attempts to delete a user record using their company id"""
                msg = f"You are about to delete {last_name}'s records from database. Would you like to proceed?"
                if self.ask_user(msg):
                    self.delete_user_info(user_company_id)
                    self.notify_user('User record deleted successfully.')
                    self.list_enrolled_users()
                return

            delete_btn.configure(command=partial(delete_callback, user['last_name'], user['company_id']))

            y += h + 10

        return

    def get_user_info(self, company_id: str = None, user_id: int = None):
        # Connect to the SQLite database
        conn = sqlite3.connect(self.database_url)
        cursor = conn.cursor()

        # If company_id is provided, fetch the user record with the given company_id
        if company_id is not None:
            # Execute the SELECT query to fetch the user record by user_id
            cursor.execute("SELECT * FROM User WHERE company_id = ?", (company_id,))
            user_record = cursor.fetchone()

            # If user_id is not found, return an empty dictionary
            if user_record is None:
                data = {}
            else:
                # Convert the user record tuple to a dictionary
                user_info = {
                    'id': user_record[0],
                    'full_name': f'{user_record[3]} {user_record[2]}',
                    'company_id': user_record[1],
                    'first_name': user_record[2],
                    'last_name': user_record[3],
                    'email': user_record[4],
                    'reg_date': user_record[5],
                    'admin_type': user_record[6]
                }
                data = user_info

        elif user_id is not None:
            # Execute the SELECT query to fetch the user record by user_id
            cursor.execute("SELECT * FROM User WHERE id = ?", (user_id,))
            user_record = cursor.fetchone()

            # If user_id is not found, return an empty dictionary
            if user_record is None:
                data = {}
            else:
                # Convert the user record tuple to a dictionary
                user_info = {
                    'id': user_record[0],
                    'full_name': f'{user_record[3]} {user_record[2]}',
                    'company_id': user_record[1],
                    'first_name': user_record[2],
                    'last_name': user_record[3],
                    'email': user_record[4],
                    'reg_date': user_record[5],
                    'admin_type': user_record[6]
                }
                data = user_info

        # If user_id is not provided, fetch all user records
        else:
            # Execute the SELECT query to fetch all user records
            cursor.execute("SELECT * FROM User")
            user_records = cursor.fetchall()

            # Convert the list of user record tuples to a list of dictionaries
            users = []
            for user_record in user_records:
                user_info = {
                    'id': user_record[0],
                    'company_id': user_record[1],
                    'full_name': f'{user_record[3]} {user_record[2]}',
                    'first_name': user_record[2],
                    'last_name': user_record[3],
                    'email': user_record[4],
                    'reg_date': user_record[5],
                    'admin_type': user_record[6]
                }
                users.append(user_info)

            data = users

        # Close the database connection
        conn.close()

        return data

    def delete_user_info(self, company_id=None):
        """deletes user record if company_id is provided, else deletes all non-admin users"""
        # Connect to the SQLite database
        conn = sqlite3.connect(self.database_url)
        cursor = conn.cursor()

        # If company_id is provided, delete the user record(s) with the given company_id
        if company_id is not None:
            # Check if the user record exists
            cursor.execute("SELECT * FROM User WHERE company_id = ?", (company_id,))
            user_record = cursor.fetchone()
            if user_record is None:
                conn.close()
                return

            # Delete the user record from the database
            cursor.execute("DELETE FROM User WHERE company_id = ?", (company_id,))
            conn.commit()

            # Remove the fingerprint file if it exists
            fingerprint_file_path = f'files/bin/{company_id}.bin'
            if os.path.exists(fingerprint_file_path):
                os.remove(fingerprint_file_path)

            # Remove user's thumbnail file if it exists
            thumbnail_path = f'files/thumbs/{company_id}.PNG'
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)

        else:
            # Remove fingerprint and thumbnail files for each deleted user
            cursor.execute("SELECT company_id FROM User WHERE admin_type != 'admin'")
            company_ids = [record[0] for record in cursor.fetchall()]
            for company_id in company_ids:
                fingerprint_file_path = f'files/bin/{company_id}.bin'
                if os.path.exists(fingerprint_file_path):
                    os.remove(fingerprint_file_path)

                thumbnail_path = f'files/thumbs/{company_id}.PNG'
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)

            # Delete user records whose admin_type is not 'admin'
            cursor.execute("DELETE FROM User WHERE admin_type != 'admin'")
            conn.commit()

        # Close the database connection
        conn.close()
        return

    def edit_user_info(self, user_info: dict):
        """creates a toplevel window for editing user's information"""

        if self.toplevel_window is None:
            customer_window = ctk.CTkToplevel(self.root)
            width = 420
            height = 350
            self.root.update()
            position_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            position_y = (self.root.winfo_screenheight() // 2) - (height // 2)
            customer_window.geometry("{}x{}+{}+{}".format(width, height, position_x, position_y))
            customer_window.title(f"Editing {user_info['full_name']}'s Information.")
            customer_window.iconbitmap('files/icon/icon.ico')

            ctk.CTkLabel(customer_window, text="First Name:").grid(row=0, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Last Name:").grid(row=1, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Email: (optional)").grid(row=2, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Admin Type:").grid(row=3, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Password: (optional)").grid(row=4, column=0, padx=5, pady=10)
            ctk.CTkLabel(customer_window, text="Confirm Password:").grid(row=5, column=0, padx=5, pady=10)

            first_name_entry = ctk.CTkEntry(customer_window, width=250)
            last_name_entry = ctk.CTkEntry(customer_window, width=250)
            email_entry = ctk.CTkEntry(customer_window, width=250)
            admin_type_entry = ctk.CTkComboBox(customer_window, values=["user", "admin"],
                                               width=250)
            password_entry = ctk.CTkEntry(customer_window, width=250)
            confirm_password_entry = ctk.CTkEntry(customer_window, width=250)
            admin_type_entry.set('Select')  # Set default value
            if user_info:
                first_name_entry.insert(0, user_info['first_name'])
                last_name_entry.insert(0, user_info['last_name'])
                if user_info['email']:
                    email_entry.insert(0, user_info['email'])
                admin_type_entry.set(user_info['admin_type'])

            first_name_entry.grid(row=0, column=1, padx=5, pady=10)
            last_name_entry.grid(row=1, column=1, padx=5, pady=10)
            email_entry.grid(row=2, column=1, padx=5, pady=10)
            admin_type_entry.grid(row=3, column=1, padx=5, pady=10)
            password_entry.grid(row=4, column=1, padx=5, pady=10)
            confirm_password_entry.grid(row=5, column=1, padx=5, pady=10)

            submit_btn = ctk.CTkButton(customer_window, text="Save")
            submit_btn.grid(row=6, column=1, padx=5, pady=10)

            def save_user_info():
                """
                Fetches user information from entry fields, creates a dictionary,
                and modifies the database.
                """
                user_to_admin = False
                admin_to_user = False

                # check if there is admin type change
                if user_info['admin_type'] == 'admin' and admin_type_entry.get() == 'user':
                    admin_to_user = True
                if user_info['admin_type'] == 'user' and admin_type_entry.get() == 'admin':
                    user_to_admin = True

                submit_btn.configure(text="Processing...", state='disabled')

                first_name = first_name_entry.get() if first_name_entry.get() else user_info['first_name']
                last_name = last_name_entry.get() if last_name_entry.get() else user_info['last_name']
                email = email_entry.get() if admin_type_entry.get() == 'admin' else None
                admin_type = admin_type_entry.get() if admin_type_entry.get() else 'user'

                # validate email if admin_type is admin
                if admin_type == 'admin':
                    if not self.is_valid_email(email):
                        submit_btn.configure(text='Save', state='enabled')
                        self.notify_user('Not a valid email!')
                        self.toplevel_window.focus()
                        return

                # validate password only if admin type is changing from user to admin
                if user_to_admin:
                    password_strength = self.check_password_strength(password_entry.get())
                    if password_strength['status'] > 1:
                        message = ''
                        count = 1
                        for x in password_strength['error']:
                            message += f'{count}. {x}.\n'
                            count += 1
                        submit_btn.configure(text='Save', state='enabled')
                        self.notify_user(message)
                        self.toplevel_window.focus()
                        return

                    if password_entry.get() != confirm_password_entry.get():
                        submit_btn.configure(text='Save', state='enabled')
                        self.notify_user('The two passwords do not match!')
                        self.toplevel_window.focus()
                        return

                password = password_entry.get()

                user_data = {
                    'first_name': first_name.title(),
                    'last_name': last_name.title(),
                    'email': email,
                    'company_id': user_info['company_id'],
                    'admin_type': admin_type,
                    'password': generate_password_hash(password) if user_to_admin else None
                }

                # modify database here
                if self.modify_user_info(user_data):
                    submit_btn.configure(text="Finished!")
                    customer_window.destroy()
                    self.toplevel_window = None
                    self.list_enrolled_users()
                else:
                    submit_btn.configure(text="Save", state="enabled")
                return

            def cancel_window():
                """
                Closes the haulier information window without saving any data.
                """
                self.toplevel_window = None
                customer_window.destroy()

            submit_btn.configure(command=save_user_info)

            cancel_btn = ctk.CTkButton(customer_window, text="Cancel", command=cancel_window)
            cancel_btn.grid(row=6, column=0, padx=5, pady=10)

            customer_window.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.toplevel_window = customer_window

        else:
            self.toplevel_window.focus()

    def on_closing(self):
        """this function executes when a toplevel window is about to close"""
        self.toplevel_window.destroy()
        self.toplevel_window = None

    def modify_user_info(self, new_data):
        """Modify a user's record in the User table."""
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(self.database_url)
            cursor = conn.cursor()

            # Construct the SET clause for the UPDATE query
            set_clause = ', '.join([f"{key} = ?" for key in new_data.keys()])

            # Execute the UPDATE query to modify the user's record
            cursor.execute(f"UPDATE User SET {set_clause} WHERE company_id = ?", (*new_data.values(),
                                                                                  new_data['company_id']))
            conn.commit()

            # Close the database connection
            conn.close()
            response = True
        except Exception as e:
            self.notify_user(f'An error occurred: {e}')
            response = False
        return response

    def log_attendance(self, user_id, timestamp):
        """Logs attendance for a user with the given company_id and timestamp."""
        # Connect to the SQLite database
        conn = sqlite3.connect(self.database_url)
        cursor = conn.cursor()

        # Get the last attendance record for the user
        cursor.execute("SELECT * FROM Attendance WHERE user_id = ? ORDER BY attendance_id DESC LIMIT 1",
                       (user_id,))
        last_record = cursor.fetchone()

        # If no record exists or if the last record has a non-null time_out
        if last_record is None or last_record[3] is not None:
            # Check if the user has already clocked in within the last hour
            if last_record:
                if (timestamp - datetime.strptime(last_record[3], '%Y-%m-%d %H:%M:%S')) < timedelta(
                        minutes=60):
                    # self.show_user("User has already clocked out.")
                    conn.close()
                    return

            # Insert a new record with time_in assigned to timestamp
            cursor.execute("INSERT INTO Attendance (user_id, time_in) VALUES (?, ?)",
                           (user_id, timestamp))
            # self.show_user("User clocked in successfully.")
        else:
            # Check if the user has already signed off within the last h
            if (timestamp - datetime.strptime(last_record[2], '%Y-%m-%d %H:%M:%S')) < timedelta(minutes=60):
                # self.show_user("User has already clocked in.")
                conn.close()
                return
            else:
                # Update the last record's time_out with timestamp
                cursor.execute("UPDATE Attendance SET time_out = ? WHERE attendance_id = ?",
                               (timestamp, last_record[0]))
                # self.show_user("User clocked out successfully.")

        # Commit changes and close the connection
        conn.commit()
        conn.close()
        return

    def show_attendance(self, user_info: dict):
        """displays user data on the attendance window"""
        # pack(anchor=tk.NW, padx=10, pady=10)

        # create a label to hold the user data
        self.root.update()
        w = int(self.display_frame.winfo_width()) - 40
        label = ctk.CTkFrame(self.display_frame, height=60, width=w, bg_color="#e0e0e0", fg_color="#ffffff",
                             corner_radius=0, border_width=2, border_color="#e0e0e0")
        # create label for photo
        x, y = 5, 5
        img = Image.open(f'files/thumbs/{user_info["company_id"]}.PNG')
        ctk_image = ctk.CTkImage(img, size=(50, 50))
        photo_label = ctk.CTkLabel(label, text="", image=ctk_image, corner_radius=5, width=50, height=50)
        photo_label.place(x=x, y=y)

        # create name label
        h = 25
        x = x + int(photo_label.cget('width')) + 40
        y = (int(photo_label.cget('height')) - h) // 2
        name_label = ctk.CTkLabel(label, text=f"{user_info['full_name']}", height=h, width=int(25 * 8.5),
                                  bg_color="#ffffff", fg_color="#ffffff", corner_radius=0, anchor="w",
                                  font=("Trebuchet Ms", 18, "bold"))
        name_label.place(x=x, y=y)

        # create time label
        x = x + int(name_label.cget('width')) + 40
        w = 80
        name_label = ctk.CTkLabel(label, text=f"{user_info['time_in']}", height=h, width=w,
                                  bg_color="#ffffff", fg_color="#ffffff", corner_radius=0, anchor="w",
                                  font=("Trebuchet Ms", 18, "bold"))
        name_label.place(x=x, y=y)
        label.pack(side=tk.BOTTOM, padx=10, pady=5)

    def track_attendance(self):
        """runs continuously checking the fingerprint sensor to detect fingerprint and logging attendance"""
        # check fingerprint sensor and try to detect a finger
        timestamp = datetime.now()

        def get_data(mylist):
            while True:
                item = random.choice(mylist)
                if item not in self.tracked_list:
                    self.tracked_list.append(item)
                    return item

        users = self.get_user_info()
        user_data = get_data(users)
        user_data['time_in'] = timestamp.strftime("%A, %B %d, %Y |    %I:%M:%S %p")
        if self.clock_label:
            self.show_attendance(user_data)

        self.root.after(10000, self.track_attendance)

    def create_attendance_instance(self, month: int):
        """randomly generates attendance instance for all users"""
        users = self.get_user_info()

        while month < 13:
            days = self.get_working_days(month)
            for day in days:
                random.shuffle(users)
                for user in users:
                    # clock user in
                    year = 2023
                    h = random.choice([8, 7])
                    m = random.choice(range(1, 59))
                    s = random.choice(range(1, 59))
                    timestamp1 = datetime.strptime(f'{day} {h}:{m}:{s}', "%Y-%m-%d %H:%M:%S")
                    self.log_attendance(user['id'], timestamp1)

                    # clock user out
                    h = random.choice([8, 7])
                    h += 9
                    m = random.choice(range(1, 59))
                    s = random.choice(range(1, 59))
                    timestamp2 = datetime.strptime(f'{day} {h}:{m}:{s}', "%Y-%m-%d %H:%M:%S")
                    self.log_attendance(user['id'], timestamp2)
                    print(f'user: {user["full_name"]}, time_in: {timestamp1}, time_out: {timestamp2}')
            month += 1
        self.root.after(1000 * 60 * 3, self.create_attendance_instance, month + 1)
        return

    def get_working_days(self, month):
        import datetime
        year = 2023
        working_days = []
        # Get the total number of days in the month
        num_days_in_month = (datetime.date(year, month + 1, 1) - datetime.date(year, month, 1)).days

        # Iterate through each day of the month
        for day in range(1, num_days_in_month + 1):
            date = datetime.date(year, month, day)
            # Check if the day is a weekday (0: Monday, 1: Tuesday, ..., 5: Saturday, 6: Sunday)
            if date.weekday() < 5:
                working_days.append(date)

        return working_days

    def create_attendance_history(self):
        """creates widgets for viewing attendance history"""
        # remove all existing widgets within the display frame
        self.remove_all_widgets(self.display_frame)

        # fetch useful data
        users = self.users
        attendance_data = self.attendance_data

        # create a label to hold the widgets
        self.root.update()
        h = int(self.display_frame.cget('height')) - 10
        text_w = w = (int(self.display_frame.winfo_width()) - 10) // 2
        base_label = ctk.CTkLabel(self.display_frame, text="", bg_color="#F0F0F0", fg_color="#ffffff",
                                  width=w, height=h, text_color="#000000")
        base_label.pack(anchor=tk.NW, padx=5, pady=5)

        # create a frame to hold the select fields
        h = 80
        x, y = 0, 0
        select_frame = ctk.CTkFrame(base_label, width=w, height=h, border_width=2, border_color="#f0f0f0",
                                    bg_color="#ffffff", fg_color="#f0f0f0", corner_radius=8)
        select_frame.place(x=x, y=y)

        # create a frame to hold the history data
        text_y = y = y + h + 5
        h = 620

        def display_data(data_info):
            data_window = ctk.CTkTextbox(base_label)
            data_window.insert("1.0", "ATTENDANCE HISTORY")
            data_window.configure(width=text_w, bg_color="#e0e0e0", height=620, fg_color="#ffffff",
                                  text_color="#333333",
                                  border_spacing=5, border_color="black", wrap="word", font=("Segoe UI", 16, "normal"))

            data_window.place(x=0, y=text_y)

            text = ""
            for item in data_info:
                text += f"{item['date']}        {item['full_name']}        {item['company_id']}        TIME IN: {item['time_in']}        TIME OUT: {item['time_out']}\n\n"

            data_window.insert("3.0", f'\n\n{text}')
            data_window.configure(state="disabled")

            return

        # add user select button
        w = 200
        h = 40
        x = 35
        y = 20
        name_values = [user['full_name'] for user in users]
        name_values.insert(0, "All")
        user_entry = ctk.CTkComboBox(select_frame, width=w, height=h, corner_radius=8, bg_color="#f0f0f0",
                                     dropdown_fg_color="#ffffff", dropdown_text_color="#333333", button_color="#28A745",
                                     text_color="#333333", values=name_values,
                                     border_color="#28A745")
        user_entry.pack(side=tk.LEFT, pady=y, padx=x)

        # add year select button
        w = 150
        year_vals = [x for x in self.list_of_years]
        year_vals.insert(0, "Select Year")
        year_entry = ctk.CTkComboBox(select_frame, width=w, height=h, corner_radius=8, bg_color="#f0f0f0",
                                     dropdown_fg_color="#ffffff", dropdown_text_color="#333333", button_color="#28A745",
                                     text_color="#333333", values=year_vals,
                                     border_color="#28A745")
        year_entry.pack(side=tk.LEFT, pady=y, padx=x)

        # add month select button
        w = 150
        month_vals = [x for x in self.list_of_months]
        month_vals.insert(0, "Select Month")
        month_entry = ctk.CTkComboBox(select_frame, width=w, height=h, corner_radius=8, bg_color="#f0f0f0",
                                      dropdown_fg_color="#ffffff", dropdown_text_color="#333333",
                                      button_color="#28A745",
                                      text_color="#333333", values=month_vals,
                                      border_color="#28A745")
        month_entry.pack(side=tk.LEFT, pady=y, padx=x)

        # add day select button
        w = 150
        day_entry = ctk.CTkComboBox(select_frame, width=w, height=h, corner_radius=8, bg_color="#f0f0f0",
                                    dropdown_fg_color="#ffffff", dropdown_text_color="#333333",
                                    button_color="#28A745",
                                    text_color="#333333", values=[],
                                    border_color="#28A745")
        day_entry.pack(side=tk.LEFT, pady=y, padx=x)
        day_entry.set('Select Day')

        # day callback function
        def day_callback(choice):
            """function executed when user selects day option"""
            month_data = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                          "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}

            # get other selected values
            year = year_entry.get()
            month = month_data.get(month_entry.get())
            user = user_entry.get()

            if user == "All":
                data = self.attendance_data
                if year != "Select Year" and month_entry.get() != "Select Month" and choice != "Select Day":
                    data = self.filter_data(self.attendance_data, year=year, month=month, day=choice)
                elif year != "Select Year" and month_entry.get() != "Select Month" and choice == "Select Day":
                    data = self.filter_data(self.attendance_data, year=year, month=month)
                elif year != "Select Year" and month_entry.get() == "Select Month" and choice == "Select Day":
                    data = self.filter_data(self.attendance_data, year=year)
            else:
                if year != "Select Year" and month_entry.get() != "Select Month" and choice != "Select Day":
                    data = self.filter_data(self.attendance_data, user=user, year=year, month=month, day=choice)
                elif year != "Select Year" and month_entry.get() != "Select Month" and choice == "Select Day":
                    data = self.filter_data(self.attendance_data, user=user, year=year, month=month)
                elif year != "Select Year" and month_entry.get() == "Select Month" and choice == "Select Day":
                    data = self.filter_data(self.attendance_data, user=user, year=year)
                else:
                    data = self.filter_data(self.attendance_data, user=user)
            self.thread_request(display_data, data)

            return

        day_entry.configure(command=day_callback)

        # Month callback functon
        def month_callback(choice):
            """function executed when user selects month option"""
            month_data = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                          "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
            # configure all selects after it
            day_entry.configure(values=["Select Day"])
            day_entry.set("Select Day")

            year = year_entry.get()
            user = user_entry.get()
            if year != "Select Year":
                if choice != "Select Month":
                    # populate day entry
                    day_values = self.get_days_in_month(choice, year)
                    day_values.insert(0, "Select Day")
                    day_entry.configure(values=day_values)
            else:
                self.thread_request(self.show_user, "Please select Year")
                return

            if user == "All":
                data = self.attendance_data
                if year != "Select Year" and choice != "Select Month":
                    data = self.filter_data(self.attendance_data, year=year, month=month_data.get(choice))
                elif year != "Select Year" and choice == "Select Month":
                    data = self.filter_data(self.attendance_data, year=year)

            else:
                if year != "Select Year" and choice != "Select Month":
                    data = self.filter_data(self.attendance_data, user=user, year=year, month=month_data.get(choice))
                elif year != "Select Year" and choice == "Select Month":
                    data = self.filter_data(self.attendance_data, user=user, year=year)
                else:
                    data = self.filter_data(self.attendance_data, user=user)

            self.thread_request(display_data, data)

        month_entry.configure(command=month_callback)

        # year callback function
        def year_callback(choice):
            """function executed when user selects month option"""
            # configure all selects after it
            day_entry.configure(values=["Select Day"])
            day_entry.set("Select Day")
            month_entry.set("Select Month")

            user = user_entry.get()

            if user == "All":
                data = self.attendance_data
                if choice != "Select Year":
                    data = self.filter_data(self.attendance_data, year=choice)

            else:
                data = self.filter_data(self.attendance_data, user=user)
                if choice != "Select Year":
                    data = self.filter_data(self.attendance_data, user=user, year=choice)

            self.thread_request(display_data, data)

        year_entry.configure(command=year_callback)

        # user callback function
        def user_callback(choice):
            """function executed when user selects month option"""
            month_data = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                          "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
            # get other values
            year = year_entry.get()
            month = month_data.get(month_entry.get())
            day = day_entry.get()

            if choice == "All":
                data = self.attendance_data
                if year != "Select Year" and month_entry.get() != "Select Month" and day != "Select Day":
                    data = self.filter_data(self.attendance_data, year=year, month=month, day=day)
                elif year != "Select Year" and month_entry.get() != "Select Month" and day == "Select Day":
                    data = self.filter_data(self.attendance_data, year=year, month=month)
                elif year != "Select Year" and month_entry.get() == "Select Month" and day == "Select Day":
                    data = self.filter_data(self.attendance_data, year=year)
            else:
                data = self.filter_data(self.attendance_data, user=choice)
                if year != "Select Year" and month_entry.get() != "Select Month" and day != "Select Day":
                    data = self.filter_data(self.attendance_data, user=choice, year=year, month=month, day=day)
                elif year != "Select Year" and month_entry.get() != "Select Month" and day == "Select Day":
                    data = self.filter_data(self.attendance_data, user=choice, year=year, month=month)
                elif year != "Select Year" and month_entry.get() == "Select Month" and day == "Select Day":
                    data = self.filter_data(self.attendance_data, user=choice, year=year)
            display_data(data)

        user_entry.configure(command=user_callback)

        # Displaying initial set of data
        display_data(attendance_data)

        return

    def filter_data(self, data, user=None, year=None, month=None, day=None):
        """filters data by the provided parameters"""
        filtered_data = []
        if year and user is None:
            for item in data:
                date = datetime.strptime(item['date'], "%Y-%m-%d")
                if date.year == int(year):
                    filtered_data.append(item)
            if month:
                new_list = []
                for item in filtered_data:
                    date = datetime.strptime(item['date'], "%Y-%m-%d")
                    if date.month == int(month):
                        new_list.append(item)
                filtered_data = new_list
                if day:
                    new_list_2 = []
                    for item in filtered_data:
                        date = datetime.strptime(item['date'], "%Y-%m-%d")
                        if date.day == int(day):
                            new_list_2.append(item)
                    filtered_data = new_list_2

        elif user:
            new_list = [x for x in data if x["full_name"] == user]
            filtered_data = new_list
            if year:
                new_list_1 = []
                for item in new_list:
                    date = datetime.strptime(item['date'], "%Y-%m-%d")
                    if date.year == int(year):
                        new_list_1.append(item)
                filtered_data = new_list_1
                if month:
                    new_list_2 = []
                    for item in new_list_1:
                        date = datetime.strptime(item['date'], "%Y-%m-%d")
                        if date.month == int(month):
                            new_list_2.append(item)
                    filtered_data = new_list_2
                    if day:
                        new_list_3 = []
                        for item in new_list_2:
                            date = datetime.strptime(item['date'], "%Y-%m-%d")
                            if date.day == int(day):
                                new_list_3.append(item)
                        filtered_data = new_list_3

        else:
            filtered_data = data

        return filtered_data

    def get_days_in_month(self, month_name, year):
        # Get the index of the month name (1 for January, 2 for February, etc.)
        month_number = list(calendar.month_name).index(month_name.title())

        # Get the calendar for the specified month and year
        month_calendar = calendar.monthcalendar(int(year), month_number)

        # Flatten the calendar into a list of day numbers
        days_in_month = [str(day) for week in month_calendar for day in week if day != 0]

        return days_in_month

    def get_all_attendance_records(self):
        conn = sqlite3.connect(self.database_url)
        cursor = conn.cursor()

        cursor.execute("SELECT attendance_id, user_id, time_in, time_out FROM Attendance ORDER BY time_in DESC")
        records = cursor.fetchall()
        attendance_list = []
        for record in records:
            attendance_dict = {}
            attendance_dict['attendance_id'] = record[0]
            attendance_dict['user_id'] = record[1]
            attendance_dict['date'] = datetime.strptime(record[2], '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d")
            attendance_dict['time_in'] = datetime.strptime(record[2], '%Y-%m-%d %H:%M:%S').strftime("%I:%M:%S %p")
            date_in = datetime.strptime(record[2], '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d")
            date_out = datetime.strptime(record[3], '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d")
            if date_in == date_out:
                attendance_dict['time_out'] = datetime.strptime(record[3], '%Y-%m-%d %H:%M:%S').strftime("%I:%M:%S %p")
            else:
                attendance_dict['time_out'] = datetime.strptime(record[3], '%Y-%m-%d %H:%M:%S').strftime(
                    "%Y-%m-%d %I:%M:%S %p")
            user = self.get_user_info(user_id=int(record[1]))
            attendance_dict['full_name'] = user['full_name']
            attendance_dict['company_id'] = user['company_id']

            attendance_list.append(attendance_dict)

        conn.close()
        return attendance_list

    def get_listofyears(self):
        """extracts the list of unique years covered in the attendance data"""
        # get the data
        data = self.attendance_data

        # isolate the years from the date attribute of the list
        date_list = [x['date'].split('-')[0] for x in data]

        return [x for x in set(date_list)]

    def thread_request(self, func, *args, **kwargs):
        """Starts a thread that invokes functions for specific actions"""
        # Start a thread to handle the database operation
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True  # Daemonize the thread to avoid issues on application exit
        thread.start()

    def run_attendance_trend(self, scope):
        """creates widgets for viewing attendance trend graph"""
        # remove all existing widgets within the display frame
        self.remove_all_widgets(self.display_frame)

        # fetch useful data
        users = self.users

        # create a label to hold the widgets
        self.root.update()
        h = int(self.display_frame.cget('height')) - 10
        w = (int(self.display_frame.winfo_width()) - 10) // 2
        base_label = ctk.CTkLabel(self.display_frame, text="", bg_color="#F0F0F0", fg_color="#ffffff",
                                  width=w, height=h, text_color="#000000")
        base_label.pack(anchor=tk.NW, padx=5, pady=5)

        # create a frame to hold the select fields
        h = 80
        x, y = 0, 0
        select_frame = ctk.CTkFrame(base_label, width=w, height=h, border_width=2, border_color="#f0f0f0",
                                    bg_color="#ffffff", fg_color="#f0f0f0", corner_radius=8)
        select_frame.place(x=x, y=y)

        # create a frame to hold the history graph
        w = w - 30
        y = y + h + 5
        h = 620
        data_frame = ctk.CTkScrollableFrame(base_label, width=w, height=h, border_width=2, border_color="#f0f0f0",
                                            bg_color="#ffffff", fg_color="#ffffff", corner_radius=8,
                                            scrollbar_button_color="#e0e0e0")
        data_frame.place(x=x, y=y)

        # add time threshold select button
        def create_thresh_vals():
            data = {}
            for i in range(24):
                if i == 0:
                    data[f'{i}:00'] = 24
                else:
                    data[f'{i}:00'] = i
            return data

        h = 40
        x = 30
        if scope == "monthly":
            x = 70
        y = 20
        w = 150
        thresh_vals = list(create_thresh_vals().keys())
        thresh_entry = ctk.CTkComboBox(select_frame, width=w, height=h, corner_radius=8, bg_color="#f0f0f0",
                                       dropdown_fg_color="#ffffff", dropdown_text_color="#333333",
                                       button_color="#28A745",
                                       text_color="#333333", values=thresh_vals,
                                       border_color="#28A745")
        thresh_entry.pack(side=tk.LEFT, pady=y, padx=x)
        thresh_entry.set('Select Threshold')

        # add user select button
        w = 200
        name_values = [user['full_name'] for user in users]
        name_values.insert(0, "Select User")
        user_entry = ctk.CTkComboBox(select_frame, width=w, height=h, corner_radius=8, bg_color="#f0f0f0",
                                     dropdown_fg_color="#ffffff", dropdown_text_color="#333333", button_color="#28A745",
                                     text_color="#333333", values=name_values,
                                     border_color="#28A745")
        user_entry.pack(side=tk.LEFT, pady=y, padx=x)

        # add year select button
        w = 150
        year_vals = [x for x in self.list_of_years]
        year_vals.insert(0, "Select Year")
        year_entry = ctk.CTkComboBox(select_frame, width=w, height=h, corner_radius=8, bg_color="#f0f0f0",
                                     dropdown_fg_color="#ffffff", dropdown_text_color="#333333", button_color="#28A745",
                                     text_color="#333333", values=year_vals,
                                     border_color="#28A745")
        year_entry.pack(side=tk.LEFT, pady=y, padx=x)

        # add month select button
        # w = 150
        month_vals = [x for x in self.list_of_months]
        month_vals.insert(0, "Select Month")
        month_entry = ctk.CTkComboBox(select_frame, width=w, height=h, corner_radius=8, bg_color="#f0f0f0",
                                      dropdown_fg_color="#ffffff", dropdown_text_color="#333333",
                                      button_color="#28A745",
                                      text_color="#333333", values=month_vals,
                                      border_color="#28A745")
        if scope == "daily":
            month_entry.pack(side=tk.LEFT, pady=y, padx=x)

        # day callback function
        def thresh_callback(choice):
            """function executed when user selects day option"""
            data = create_thresh_vals()

            if isinstance(data.get(choice), int):
                self.expected_time_of_arrival = data.get(choice)
            return

        thresh_entry.configure(command=thresh_callback)

        # Month callback functon
        def month_callback(choice):
            """function executed when user selects month option"""
            month_data = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                          "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}

            year = year_entry.get()
            user = user_entry.get()

            if choice == "Select Month":
                self.remove_all_widgets(data_frame)
                return

            if year == "Select Year":
                year = datetime.now().year

            if user == "Select User":
                self.thread_request(self.show_user, "Please select a user")

            else:
                data = self.filter_data(self.attendance_data, user=user, year=year, month=month_data.get(choice))
                if data:
                    time_list = []
                    for item in data:
                        tyme = f'{item["date"]} {item["time_in"]}'
                        time_list.append(tyme)
                    self.generate_attendance_graph(time_list, data_frame, user, year, choice)
                else:
                    self.thread_request(self.show_user, "No records found!")

        month_entry.configure(command=month_callback)

        # year callback function
        def year_callback(choice):
            """function executed when user selects month option"""
            # configure all selects after it
            month_entry.set("Select Month")

            user = user_entry.get()

            if scope == "monthly":
                if choice != "Select Year" and user != "Select User":
                    data = self.filter_data(self.attendance_data, user=user, year=choice)
                    if data:
                        # group attendance datetime into their respective months
                        group = {}
                        for month in self.list_of_months:
                            time_list = []
                            for item in data:
                                tyme = f'{item["date"]} {item["time_in"]}'
                                obj = datetime.strptime(tyme, '%Y-%m-%d %I:%M:%S %p')
                                if obj.strftime("%B") == month:
                                    time_list.append(obj)
                            group[month] = time_list
                        # use group to plot graph here
                        self.plot_monthly_lateness(group, user, choice, data_frame)
                    else:
                        self.thread_request(self.show_user, "No records found!")
                elif choice == "Select Year":
                    self.remove_all_widgets(data_frame)
            return

        year_entry.configure(command=year_callback)

        # user callback function
        def user_callback(choice):
            """function executed when user selects month option"""
            month_data = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                          "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
            # get other values
            year = year_entry.get()
            month = month_data.get(month_entry.get())
            if year == "Select Year":
                year = datetime.now().year

            if scope == "monthly":
                if choice != "Select User":
                    data = self.filter_data(self.attendance_data, user=choice, year=year)
                    if data:
                        # group attendance datetime into their respective months
                        group = {}
                        for month in self.list_of_months:
                            time_list = []
                            for item in data:
                                tyme = f'{item["date"]} {item["time_in"]}'
                                obj = datetime.strptime(tyme, '%Y-%m-%d %I:%M:%S %p')
                                if obj.strftime("%B") == month:
                                    time_list.append(obj)
                            group[month] = time_list
                        # use group to plot graph here
                        self.plot_monthly_lateness(group, choice, year, data_frame)
                    else:
                        self.thread_request(self.show_user, "No records found!")
                elif choice == "Select User":
                    self.remove_all_widgets(data_frame)
            else:
                if choice == "Select User":
                    self.remove_all_widgets(data_frame)
                    return
                if month in month_data.values():
                    data = self.filter_data(self.attendance_data, user=choice, year=year, month=month)
                    if data:
                        time_list = []
                        for item in data:
                            tyme = f'{item["date"]} {item["time_in"]}'
                            time_list.append(tyme)
                        self.generate_attendance_graph(time_list, data_frame, choice, year, month)
                    else:
                        self.thread_request(self.show_user, "No records found.")

        user_entry.configure(command=user_callback)

        return

    def generate_attendance_graph(self, attendance_times, display_window, user, year, month_name):
        # first close the current plot if open in memory
        self.close_plot()

        # Convert attendance times to datetime objects
        attendance_times = [datetime.strptime(tyme, '%Y-%m-%d %I:%M:%S %p') for tyme in attendance_times]

        # Extract day of the month and hour of attendance
        days = np.array([tyme.day for tyme in attendance_times])
        hours = np.array([tyme.hour + tyme.minute / 60 for tyme in attendance_times])

        # Calculate the daily expected time of arrival (8am by default)
        expected_arrival = np.arange(days.min(), days.max() + 1)
        expected_arrival = np.repeat(self.expected_time_of_arrival, len(expected_arrival))

        # Create a new figure
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(days, hours, 'go-', label='Attendance Graph')

        # Draw the straight red line for the expected time of arrival
        ax.axhline(y=self.expected_time_of_arrival, color='r', linestyle='-', label=f'Expected Time of Arrival')

        # Calculate the number of times the employee crossed the expected arrival line
        crossed_line = sum(hours > self.expected_time_of_arrival)

        # Show label for the number of times employee crossed the line versus total attendance
        ax.text(0.5, 0.95, f'Number of Late Arrival: {crossed_line}/{len(attendance_times)}',
                horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=13)

        ax.set_xlabel('Day of the Month', fontsize=16)
        ax.set_ylabel('Arrival Time', fontsize=16)
        ax.set_title(f"{user}'s  Attendance Trend in the month of {month_name}, {year}", fontsize=18)
        ax.legend(fontsize=16)
        ax.grid(True)

        # Set custom ticks and labels for the x-axis
        ax.set_xticks(days)
        ax.set_xticklabels(days, fontsize=16)

        # Set font size for y-axis ticks
        ax.tick_params(axis='y', labelsize=16)

        self.current_plot = plt
        self.display_graph(display_window, fig)
        return

    def plot_monthly_lateness(self, monthly_data, employee, year, display_window):
        """
        Generate a bar chart showing the number of times each employee was late to work for each month.

        Args:
        monthly_data (dict): A dictionary where keys are month names and values are lists of arrival times (datetime strings).
        """
        # first close the current plot if open in memory
        self.close_plot()

        if not monthly_data:
            self.thread_request(self.show_user, "No data provided to plot.")
            return

        lateness_count = []  # List to store lateness count for each month

        for month, arrival_times in monthly_data.items():
            late_count = 0
            for tyme in arrival_times:
                expected_tyme_obj = datetime.strptime(f'{tyme.date()} {self.expected_time_of_arrival}:00:00',
                                                      '%Y-%m-%d %H:%M:%S')
                if tyme.time() > expected_tyme_obj.time():
                    late_count += 1
            lateness_count.append(late_count)

        months = list(monthly_data.keys())

        fig, ax = plt.subplots(figsize=(18, 8))
        ax.bar(months, lateness_count, color='coral')
        ax.set_xlabel(f'Months of the year', fontsize=18)
        ax.set_ylabel('Number of Times Late', fontsize=18)
        ax.set_title(f'Monthly Lateness Report for {employee} in {year}', fontsize=20)
        ax.tick_params(axis='both', which='major', labelsize=18)  # Increase fontsize of ticks

        # Annotate each bar with its value
        for i, late_count in enumerate(lateness_count):
            ax.text(i, late_count + 0.1, str(late_count), ha='center', va='bottom', fontsize=14)

        plt.xticks(rotation=45, ha='right')
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        self.current_plot = plt
        self.display_graph(display_window, fig)

        return

    def display_graph(self, window, fig, expand_command=None):
        self.remove_all_widgets(window)

        if expand_command is None:
            expand_command = self.show_current_plot  # self.current_plot.show

        def exit_command():
            self.current_plot = None
            self.remove_all_widgets(window)
            return

        # Convert Matplotlib figure to Tkinter-compatible format
        canvas = FigureCanvasTkAgg(fig, master=window)

        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        w = 1700
        h = 1080
        canvas_widget.config(width=w, height=h)
        canvas_widget.pack(pady=10, padx=10)

        # create action buttons frame
        h = 50
        action_frame = ctk.CTkFrame(window, fg_color="#ffffff", height=h)
        action_frame.pack(pady=10, padx=20)

        # create buttons inside the action label
        w = 100
        h = 24

        expand_btn = ctk.CTkButton(action_frame, text='expand', bg_color='#ffffff', fg_color="#28A745",
                                   text_color="#333333", corner_radius=8, height=h, width=w,
                                   command=expand_command)
        expand_btn.pack(side=tk.LEFT, padx=10)

        # exit btn
        exit_btn = ctk.CTkButton(action_frame, text='exit', bg_color='#ffffff', fg_color="#28A745",
                                 text_color="#333333", corner_radius=8, height=h, width=50,
                                 command=exit_command)
        exit_btn.pack(side=tk.LEFT, padx=10)

    def show_current_plot(self):
        """shows the current plot outside the app"""

        # Display the modified plot
        self.current_plot.show()

        return

    def close_plot(self):
        """closes plot assigned to current_plot"""
        if self.current_plot is not None:
            self.current_plot.close()
            self.current_plot = None

        return

    def create_settings_form(self):
        """creates a form for app configuration settings"""
        # remove all existing widgets within the display frame
        self.remove_all_widgets(self.display_frame)

        # read the previous settings if exists
        data = self.read_app_settings()['data']

        # create a label to hold the settings form fields
        self.root.update()
        h = int(self.display_frame.cget('height')) - 10
        w = int(self.display_frame.winfo_width()) - 10
        base_label = ctk.CTkLabel(self.display_frame, text="", bg_color="#F0F0F0", fg_color="#e0e0e0",
                                  width=w, height=h, text_color="#000000")
        base_label.pack(anchor=tk.NW, padx=5, pady=5)

        self.root.update()
        h = (int(base_label.cget('height')) // 2) + 100
        w = (int(base_label.cget("width")) // 2) - 80
        y = (int(base_label.cget('height')) - h) // 2
        x = ((int(base_label.cget("width")) // 2) - w) // 2
        signup_label = ctk.CTkLabel(base_label, text="", bg_color="#F0F0F0", fg_color="#F0F0F0",
                                    width=w, height=h, text_color="#000000")
        signup_label.place(x=x, y=y)

        # create title
        w = int(12.5 * 20)  # 5 is the number of char
        h = 40
        y = 0
        x = (int(signup_label.cget('width')) - w) // 2
        title_label = ctk.CTkLabel(signup_label, text="App Settings", bg_color="#F0F0F0",
                                   font=("Trebuchet Ms", 22, "bold"),
                                   text_color="#000000", fg_color="#F0F0F0", width=w, height=h)
        title_label.place(x=x, y=y)

        # create the form fields
        w = int(12.5 * 9)
        x = 25
        y = y + int(title_label.cget('height')) + 10
        port_label = ctk.CTkLabel(signup_label, text="Port:", bg_color="#f0f0f0",
                                  text_color="#000000",
                                  fg_color="#e0e0e0", width=w, height=h)
        port_label.place(x=x, y=y)

        x = x + int(port_label.cget('width')) + 20
        port_entry = ctk.CTkEntry(signup_label, fg_color="transparent", width=350, height=h,
                                  text_color="#000000")
        port_entry.place(x=x, y=y)

        w = int(12.5 * 9)
        x = 25
        y = y + int(port_entry.cget('height')) + 10
        password_label = ctk.CTkLabel(signup_label, text="Module Password:", bg_color="#f0f0f0",
                                      text_color="#000000",
                                      fg_color="#e0e0e0", width=w, height=h)
        password_label.place(x=x, y=y)

        x = x + int(password_label.cget('width')) + 20
        password_entry = ctk.CTkEntry(signup_label, fg_color="transparent", width=350, height=h,
                                      text_color="#000000")
        password_entry.place(x=x, y=y)

        w = int(12.5 * 9)
        x = 25
        y = y + int(password_entry.cget('height')) + 10
        baudrate_label = ctk.CTkLabel(signup_label, text="BaudRate:", bg_color="#f0f0f0",
                                      text_color="#000000",
                                      fg_color="#e0e0e0", width=w, height=h)
        baudrate_label.place(x=x, y=y)

        x = x + int(baudrate_label.cget('width')) + 20
        baudrate_entry = ctk.CTkEntry(signup_label, fg_color="transparent", width=350, height=h,
                                      text_color="#000000")
        baudrate_entry.place(x=x, y=y)

        w = int(12.5 * 9)
        x = 25
        y = y + int(baudrate_entry.cget('height')) + 10
        address_label = ctk.CTkLabel(signup_label, text="Module Address:", bg_color="#f0f0f0",
                                     text_color="#000000",
                                     fg_color="#e0e0e0", width=w, height=h)
        address_label.place(x=x, y=y)

        x = x + int(address_label.cget('width')) + 20
        address_entry = ctk.CTkEntry(signup_label, fg_color="transparent", width=350, height=h,
                                     text_color="#000000")
        address_entry.place(x=x, y=y)

        # fill the entry fields with previous data
        port_entry.insert(0, self.module_port)
        password_entry.insert(0, self.module_password)
        baudrate_entry.insert(0, self.baud_rate)
        address_entry.insert(0, self.module_address)

        w = 100
        x = x + int(address_entry.cget('width'))//2
        y = y + int(address_entry.cget('height')) + 15
        submit_btn = ctk.CTkButton(signup_label, text="Save", font=("Trebuchet Ms", 14, "normal"),
                                   text_color="#000000", bg_color="#f0f0f0", fg_color="#28A745", height=h, width=w)
        submit_btn.place(x=x, y=y)

        def save_data():
            """saves the settings data"""
            port = port_entry.get() if port_entry.get() else self.module_port
            address = address_entry.get() if address_entry.get() else self.module_address
            baudrate = int(baudrate_entry.get()) if baudrate_entry.get() else self.baud_rate
            password = password_entry.get() if password_entry.get() else self.module_password

            data = {}
            data['port'] = port
            data['password'] = password
            data['address'] = address
            data['baud_rate'] = baudrate

            self.store_app_settings(data)
            self.thread_request(self.notify_user, "Settings saved successfully")
            self.remove_all_widgets(self.display_frame)

            return

        submit_btn.configure(command=save_data)

        return

    def store_app_settings(self, settings):
        file_path = "files/app_settings.json"

        try:
            with open(file_path, 'w') as file:
                json.dump(settings, file, indent=4)

            self.module_port = settings['port']
            self.module_password = settings['password']
            self.module_address = settings['address']
            self.baud_rate = settings['baud_rate']

            message = f"Settings saved to '{file_path}'"
            status = 1
        except Exception as e:
            message = f"Error writing settings to '{file_path}': {e}"
            status = 2

        return {'status': status, 'message': message, 'data': None}

    def read_app_settings(self):
        file_path = "files/app_settings.json"
        try:
            with open(file_path, 'r') as file:
                settings = json.load(file)

            self.module_port = settings['port']
            self.module_password = settings['password']
            self.module_address = settings['address']
            self.baud_rate = settings['baud_rate']

            data = settings
            status = 1
            message = "success"
        except FileNotFoundError:
            data = None
            status = 2
            message = f"File '{file_path}' not found."
        except json.JSONDecodeError:
            data = None
            status = 2
            message = f"Error decoding JSON from '{file_path}'. Check if the file contains valid JSON."

        return {'status': status, 'message': message, 'data': data}


class AdminUser:
    """Representing an admin user when they are logged in"""

    def __init__(self, user_info):
        self.first_name = user_info['first_name']
        self.last_name = user_info['last_name']
        self.id = user_info['id']
        self.company_id = user_info['company_id']
        self.email = user_info['email']
        self.admin_type = user_info['admin_type']


def main():
    root = ctk.CTk()
    app = EmployeeAttendanceSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()
