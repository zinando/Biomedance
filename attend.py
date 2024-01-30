import time
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime
from time import strftime
from pyfingerprint.pyfingerprint import PyFingerprint
import cv2
import sqlite3
from PIL import Image, ImageTk
import numpy as np
import os


class EmployeeAttendanceSystem:
    """Class representing the Employee Attendance System GUI."""

    def __init__(self, root):
        """Initialize the EmployeeAttendanceSystem instance.

        Parameters:
            root (tk.Tk): The root Tkinter window.
        """
        self.root = root
        self.root.title("Employee Attendance System")
        self.frames = {}
        self.repeat_password_entry = None
        self.bg_label = None
        self.motion = "forward"
        self.display_frame = None
        self.signup_form = None
        self.login_form = None
        self.password_entry = None
        self.email_entry = None
        self.first_name_entry = None
        self.last_name_entry = None
        self.userid_entry = None
        self.submit_btn = None
        self.finger_print_data = None
        self.animator = None

        # Set window geometry and center it on the screen
        self.root.geometry("1200x760")
        self.center_window()

        self.root.update()
        # create a background label with a solid color
        self.bg_label = ctk.CTkLabel(self.root, text="", height=self.root.winfo_height(),
                                     width=self.root.winfo_width(), bg_color="#F0F0F0", fg_color="#f0f0f0")
        self.bg_label.place(relx=0, rely=0)

        # Create login frame
        # self.create_login_frame()

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
        self.submit_btn = submit_btn

        w = int(12.5 * 7)
        x = x + int(submit_btn.cget('width')) + 10
        signup_btn = ctk.CTkLabel(signup_label, text="Login here.", bg_color="#f0f0f0",
                                  font=("Trebuchet Ms", 13, "normal"), text_color="#000000",
                                  fg_color="#f0f0f0", width=w, height=h, cursor="hand2")
        signup_btn.place(x=x, y=y)
        # bind a click event to the text
        signup_btn.bind("<Button-1>", self.create_login_form)

        return

    def remove_all_widgets(self, container):
        for widget in container.winfo_children():
            widget.pack_forget()

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
        self.display_clock(clock_label)

    def display_clock(self, window):
        """displays clock at the center of the given window"""
        string = strftime('%H:%M:%S %p')
        window.configure(text=string)
        window.after(1000, lambda: self.display_clock(window))

    def animate_button(self, canvas, button, end):
        if self.finger_print_data:
            return
        if button.position_x == 0:
            self.motion = "forward"
        elif button.position_x == end-20:
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
        end = w//2
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
                fingerprint_sensor = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

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
                #print(error)
                self.notify_user(error)
                #time.sleep(5)
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

    def display_tif(self, window):
        """displays tif fingerprint images"""
        image_path = "tif/100__M_Left_index_finger.tif"

        #fingerprint_test = cv2.imread(image_path)
        #cv2.imshow("Original", cv2.resize(fingerprint_test, None, fx=1, fy=1))
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        # process with PIL
        image = Image.open(image_path)

        # Convert the PIL Image to a Tkinter PhotoImage
        photo = ImageTk.PhotoImage(image)

        # Create a Label widget to display the image
        window.configure(image=photo)
        # Keep a reference to the image to prevent it from being garbage collected
        window.image = photo


def main():
    root = ctk.CTk()
    app = EmployeeAttendanceSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()
