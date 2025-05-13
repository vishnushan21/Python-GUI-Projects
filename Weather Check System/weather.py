from tkinter import *
import tkinter as tk
from datetime import datetime
from PIL import ImageTk, Image
import requests
from tkinter import messagebox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import schedule
import time


class Weather:
    def weather_report(self):
        self.url = "http://api.openweathermap.org/data/2.5/weather?q="
        self.cityname = self.loc.get(1.0, END).strip()  
        self.api_key = '21721e5127f4c7cd81e2beadf5acdafd'
        
        try:
            response = requests.get(self.url + self.cityname + '&appid=' + self.api_key)
            self.data = response.json()

            if response.status_code != 200 or self.data.get('cod') != 200:
                error_message = self.data.get('message', 'Unknown Error')
                messagebox.showerror('Error', f'City Not Found or API Error: {error_message}')
            else:
                self.location['text'] = f"{self.data['name']}, {self.data['sys']['country']}"
                self.c = int(self.data['main']['temp'] - 273.15)  # Temperature in Celsius
                self.f = round(self.c * 9/5 + 32, 2)  # Temperature in Fahrenheit
                self.weather['text'] = self.data['weather'][0]['main']
                self.weather['font'] = ('verdana', 20, 'bold')
                self.temperature['text'] = f'{self.c} °C \n {self.f} °F'
                self.temperature['font'] = ('verdana', 15, 'bold')
                self.humidity['text'] = f"Humidity: {self.data['main']['humidity']}%"
                self.humidity['font'] = ('verdana', 15, 'bold')
                self.pressure['text'] = f"Pressure: {self.data['main']['pressure']} hPa"
                self.pressure['font'] = ('verdana', 15, 'bold')

        except requests.exceptions.RequestException as e:
            messagebox.showerror('Error', f"Network Error: {e}")
        except KeyError as e:
            messagebox.showerror('Error', f"Unexpected Response Structure: Missing {e}")

    def send_email(self):
        sender_email = self.sender_email_entry.get().strip()
        app_password = self.sender_password_entry.get().strip()
        recipient_email = self.email_entry.get().strip()

        # Save credentials for future use
        if sender_email and app_password and recipient_email:
            with open('email_credentials.txt', 'w') as f:
                f.write(f"{sender_email}\n{app_password}\n{recipient_email}")

        if not sender_email or not app_password or not recipient_email:
            messagebox.showerror("Error", "Please fill in all email fields.")
            return

        def send_email_in_background():
            try:
                # Email content
                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = recipient_email
                message["Subject"] = "Daily Weather Report"
                email_content = (
                    f"City: {self.cityname}\n"
                    f"Temperature: {self.c} °C / {self.f} °F\n"
                    f"Weather: {self.weather['text']}\n"
                    f"Humidity: {self.humidity['text']}\n"
                    f"Pressure: {self.pressure['text']}\n"
                )
                message.attach(MIMEText(email_content, "plain"))

                # Sending the email
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, app_password)
                    server.send_message(message)

                messagebox.showinfo("Success", "Email sent successfully!")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to send email: {e}")

        # Start a new thread to send the email
        threading.Thread(target=send_email_in_background).start()

    def schedule_daily_email(self):
        # This function will send an email every day at a specific time (e.g., 8:00 AM)
        schedule.every().day.at("08:00").do(self.send_scheduled_email)

    def send_scheduled_email(self):
        # Read saved credentials and send the email
        try:
            with open('email_credentials.txt', 'r') as f:
                lines = f.readlines()
                sender_email = lines[0].strip()
                app_password = lines[1].strip()
                recipient_email = lines[2].strip()

                if sender_email and app_password and recipient_email:
                    # Use the credentials and send the email
                    self.cityname = 'London'  # Default city or fetch dynamically
                    self.weather_report()  # Get weather data for the email content
                    self.send_email()

        except FileNotFoundError:
            messagebox.showerror("Error", "Email credentials file not found. Please enter credentials.")

    def run_schedule(self):
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute if there is a scheduled task

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('500x500')
        self.root.title("Weather Application")
        self.root.maxsize(500, 500)
        self.root.minsize(500, 500)

        self.header = Label(self.root, width=100, height=2, bg="#00274c")
        self.header.place(x=0, y=0)

        self.font = ('verdana', 10, 'bold')

        self.date = Label(self.root, text=datetime.now().date(), bg="#00274c", fg="white", font=self.font)
        self.date.place(x=400, y=5)

        self.heading = Label(self.root, text="Weather Report", bg="#00274c", fg="white", font=self.font)
        self.heading.place(x=180, y=5)

        self.location = Label(self.root, text="NA/-", bg="#00274c", fg="white", font=self.font)
        self.location.place(x=10, y=5)

        self.name = Label(self.root, text="City or Country Name", fg="#00274c", font=self.font)
        self.name.place(x=140, y=45)

        self.loc = Text(self.root, width=18, height=2)
        self.loc.place(x=140, y=70)
        self.loc.configure(font=('verdana', 13))

        self.button = Button(self.root, text="Search", bg="#00274c", fg="white", font=self.font, relief=RAISED, borderwidth=3, command=self.weather_report)
        self.button.place(x=350, y=73)

        # Email credentials input
        self.sender_email_label = Label(self.root, text="Your Email Address", fg="#00274c", font=self.font)
        self.sender_email_label.place(x=140, y=170)

        self.sender_email_entry = Entry(self.root, width=30)
        self.sender_email_entry.place(x=140, y=190)

        self.sender_password_label = Label(self.root, text="Your Email Password", fg="#00274c", font=self.font)
        self.sender_password_label.place(x=140, y=220)

        self.sender_password_entry = Entry(self.root, width=30, show="*")  # Masking password input
        self.sender_password_entry.place(x=140, y=240)

        self.email_label = Label(self.root, text="Recipient Email Address", fg="#00274c", font=self.font)
        self.email_label.place(x=140, y=270)

        self.email_entry = Entry(self.root, width=30)
        self.email_entry.place(x=140, y=290)

        self.send_button = Button(self.root, text="Send", bg="#00274c", fg="white", font=self.font, command=self.send_email)
        self.send_button.place(x=350, y=285)

        # Weather output
        self.weather = Label(self.root, text="Weather: NA/-", fg="#00274c", font=self.font)
        self.weather.place(x=140, y=320)
        self.temperature = Label(self.root, text="Temperature: NA/-", fg="#00274c", font=self.font)
        self.temperature.place(x=140, y=350)
        self.humidity = Label(self.root, text="Humidity: NA/-", fg="#00274c", font=self.font)
        self.humidity.place(x=140, y=380)
        self.pressure = Label(self.root, text="Pressure: NA/-", fg="#00274c", font=self.font)
        self.pressure.place(x=140, y=420)

        # Start scheduling the daily email
        self.schedule_daily_email()

        # Run the scheduled email task in a background thread
        threading.Thread(target=self.run_schedule, daemon=True).start()

        self.root.mainloop()


if __name__ == '__main__':
    Weather()
