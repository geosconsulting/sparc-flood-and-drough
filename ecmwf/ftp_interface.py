# Import the FTP object from ftplib
from ftplib import FTP
from Tkinter import *

app = Tk()
app.title("FTP")
app.geometry("300x500")

def handleDownload(block):
    file.write(block)
    print ".",

def login():
    ftp.login(username.get(),password.get())

    # This is where I am held up I tried ftp.retrlines('LIST') but it would
    # not be inserted into to the list box instead it inserted "Tranfer Complete" at the    end!
    # Any suggetion?
    # h = ?
    stuff = Listbox(app)
    stuff.insert(END, h)
    stuff.pack()

    filename = "Steam Engine Poster.pdf"

    Label(app, text ='Opening local file ' + filename).pack()
    file = open(filename, 'wb')

    Label(app, text = "Downloading Steam Engine Poster.pdf").pack()

    ftp.retrbinary('RETR ' + filename, handleDownload)

    Label(app, text = "Closing FTP connection!").pack()

    ftp.close()


ftp = FTP('ftp.wfp.org')
# ftp.login('WFP_GISviewer','FTPviewer')

print ftp.getwelcome()
ftp = FTP('ftp.wfp.org')
Label(app, text = "Login").pack()

username = StringVar(None)
username = Entry(app, text = "Username: ")
username.pack()

password = StringVar(None)
password = Entry(app, text = "Password: ")
password.pack()

zzoVuoi = StringVar(None)
zzoVuoi = Entry(app, text = "Dicevamo: ")
zzoVuoi.pack()

button = Button(app, text = "Login!", command = login)
button.pack()

app.mainloop()