import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk
import threading
import shutil
from facerec import *
from register import *
import time
import pyttsx3
import csv
import numpy as np
import ntpath
import os
import cv2
import requests
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 
from email.utils import formataddr
import csv
import pywintypes

import smtplib
current_hour = time.localtime().tm_hour


active_page = 0
thread_event = None
left_frame = None

right_frame = None
heading = None
webcam = None
img_label = None
img_read = None
img_list = []
slide_caption = None
slide_control_panel = None
current_slide = -1
global back_im
root = tk.Tk()
root.geometry('1366x768+0+10')
back_im = tk.PhotoImage(file= r"img\wheelerrr.png")

root.title('Two wheeler theft prediction')

root.state('zoomed')

pages = []
for i in range(5):
    pages.append(tk.Frame(root, bg="grey"))
    pages[i].pack(side="top", fill="both", expand=True)
    pages[i].place(x=0, y=0, relwidth=1, relheight=1)
    label = tk.Label(pages[i], image=back_im)
    label.place(relx=0, rely=0, relwidth=1, relheight=1)


def goBack():
    global active_page, thread_event, webcam

    if (active_page==4 and not thread_event.is_set()):
        thread_event.set()
        webcam.release()

    for widget in pages[active_page].winfo_children():
        widget.destroy()

    pages[0].lift()
    active_page = 0

import csv


def insertData(data):
    field=['Name', "Mobile number","Email"]
    x=[data['Name'], data["Mobile number"],data['Email']]
    filen = "file.csv"
    with open(filen, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(field)
        csvwriter.writerow(x)
        
def basicPageSetup(pageNo):
    global left_frame, right_frame, heading

    back_img = tk.PhotoImage(file= r"img\back.png")
    back_button = tk.Button(pages[pageNo], image=back_img, bg="grey", bd=0, highlightthickness=0,
           activebackground="grey", command=goBack)
    back_button.image = back_img
    back_button.place(x=10, y=10)

    heading = tk.Label(pages[pageNo], fg="white", bg="grey", font="Arial 20 bold", pady=10)
    heading.pack()

    content = tk.Frame(pages[pageNo], bg="grey", pady=20)
    content.pack(expand="true", fill="both")

    left_frame = tk.Frame(content, bg="grey")
    left_frame.grid(row=0, column=0, sticky="nsew")

    right_frame = tk.LabelFrame(content, text="Detected Person", bg="grey", font="Arial 20 bold", bd=4,
                             foreground="#2ea3ef", labelanchor="n")
    right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    content.grid_columnconfigure(0, weight=1, uniform="group1")
    content.grid_columnconfigure(1, weight=1, uniform="group1")
    content.grid_rowconfigure(0, weight=1)


def showImage(frame, img_size):
    global img_label, left_frame

    img = cv2.resize(frame, (img_size, img_size))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)
    if (img_label == None):
        img_label = tk.Label(left_frame, image=img, bg="#202d42")
        img_label.image = img
        img_label.pack(padx=20)
    else:
        img_label.configure(image=img)
        img_label.image = img


def getNewSlide(control):
    global img_list, current_slide

    if(len(img_list) > 1):
        if(control == "prev"):
            current_slide = (current_slide-1) % len(img_list)
        else:
            current_slide = (current_slide+1) % len(img_list)

        img_size = left_frame.winfo_height() - 200
        showImage(img_list[current_slide], img_size)

        slide_caption.configure(text = "Image {} of {}".format(current_slide+1, len(img_list)))


def selectMultiImage(opt_menu, menu_var):
    global img_list, current_slide, slide_caption, slide_control_panel

    filetype = [("images", "*.jpg *.jpeg *.png")]
    path_list = filedialog.askopenfilenames(title="Choose atleast 5 images", filetypes=filetype)

    if(len(path_list) < 5):
        messagebox.showerror("Error", "Choose atleast 5 images.")
    else:
        img_list = []
        current_slide = -1

        
        if (slide_control_panel != None):
            slide_control_panel.destroy()

       
        for path in path_list:
            img_list.append(cv2.imread(path))

       

       
        img_size =  left_frame.winfo_height() - 200
        current_slide += 1
        showImage(img_list[current_slide], img_size)

        slide_control_panel = tk.Frame(left_frame, bg="#202d42", pady=20)
        slide_control_panel.pack()

        back_img = tk.PhotoImage(file="previous.png")
        next_img = tk.PhotoImage(file="next_image.png")

        prev_slide = tk.Button(slide_control_panel, image=back_img, bg="#202d42", bd=0, highlightthickness=0,
                            activebackground="#202d42", command=lambda : getNewSlide("prev"))
        prev_slide.image = back_img
        prev_slide.grid(row=0, column=0, padx=60)

        slide_caption = tk.Label(slide_control_panel, text="Image 1 of {}".format(len(img_list)), fg="#ff9800",
                              bg="#202d42", font="Arial 15 bold")
        slide_caption.grid(row=0, column=1)

        next_slide = tk.Button(slide_control_panel, image=next_img, bg="#202d42", bd=0, highlightthickness=0,
                            activebackground="#202d42", command=lambda : getNewSlide("next"))
        next_slide.image = next_img
        next_slide.grid(row=0, column=2, padx=60)


def register(entries, required, menu_var):
    global img_list

    if(len(img_list) == 0):
        messagebox.showerror("Error", "Select Images first.")
        return

    entry_data = {}
    for i, entry in enumerate(entries):
        val = entry[1].get()
        
        if (len(val) == 0 and required[i] == 1):
            messagebox.showerror("Field Error", "Required field missing :\n\n%s" % (entry[0]))
            return
        else:
            entry_data[entry[0]] = val.lower()


    
    path = os.path.join('face_samples', "temp_file")
    if not os.path.isdir(path):
        os.mkdir(path)

    no_face = []
    for i, img in enumerate(img_list):
        
        id = Register(img, path, i + 1)
        if(id != None):
            no_face.append(id)

    
    if(len(no_face) > 0):
        no_face_st = ""
        for i in no_face:
            no_face_st += "Image " + str(i) + ", "
        messagebox.showerror("Registration Error", "Registration failed!\n\nFollowing images doesn't contain"
                        " face or Face is too small:\n\n%s"%(no_face_st))
        shutil.rmtree(path, ignore_errors=True)
    else:
        insertData(entry_data)
        rowId=1
        if(rowId >= 0):
            messagebox.showinfo("Success","Registered Successfully.")
            shutil.move(path, os.path.join('face_samples', entry_data["Name"]))

            

            goBack()
        else:
            shutil.rmtree(path, ignore_errors=True)
            messagebox.showerror("Database Error", "Some error occured while storing data.")


def on_configure(event, canvas, win):
    canvas.configure(scrollregion=canvas.bbox('all'))
    canvas.itemconfig(win, width=event.width)


def getPage1():
    global active_page, left_frame, right_frame, heading, img_label
    active_page = 1
    img_label = None
    opt_menu = None
    menu_var = tk.StringVar(root)
    pages[1].lift()

    basicPageSetup(1)
    heading.configure(text="Two Wheeler Theft Prediction", bg="grey")
    right_frame.configure(text="Vehicle Owner Details", fg="white", bg="grey")

    btn_grid = tk.Frame(left_frame, bg="grey")
    btn_grid.pack()

    tk.Button(btn_grid, text="Select Images", command=lambda: selectMultiImage(opt_menu, menu_var), font="Arial 15 bold", bg="black",
           fg="white", pady=10, bd=0, highlightthickness=0, activebackground="grey",
           activeforeground="white").grid(row=0, column=0, padx=25, pady=25)


   
    canvas = tk.Canvas(right_frame, bg="grey", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand="true", padx=30)
    scrollbar = tk.Scrollbar(right_frame, command=canvas.yview, width=20, troughcolor="#3E3B3C", bd=0,
                          activebackground="grey", bg="grey", relief="raised")
    scrollbar.pack(side="left", fill="y")

    scroll_frame = tk.Frame(canvas, bg="grey", pady=20)
    scroll_win = canvas.create_window((0, 0), window=scroll_frame, anchor='nw')

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda event, canvas=canvas, win=scroll_win: on_configure(event, canvas, win))


    tk.Label(scroll_frame, text="* Required Fields", bg="grey", fg="yellow", font="Arial 13 bold").pack()
   
    input_fields = ("Name", "Mobile number","Email")
    ip_len = len(input_fields)
    required = [1, 1, 1, 1]

    entries = []
    for i, field in enumerate(input_fields):
        print()
        row = tk.Frame(scroll_frame, bg="grey")
        row.pack(side="top", fill="x", pady=15)

        label = tk.Text(row, width=20, height=1, bg="#3E3B3C", fg="#ffffff", font="Arial 13", highlightthickness=0, bd=0)
        label.insert("insert", field)
        label.pack(side="left")

        if(required[i] == 1):
            label.tag_configure("star", foreground="yellow", font="Arial 13 bold")
            label.insert("end", "  *", "star")
            label.configure(state="disabled")

        #if(i != ip_len):
            ent = tk.Entry(row, font="Arial 13", selectbackground="#90ceff")
            ent.pack(side="right", expand="true", fill="x", padx=10)
            entries.append((field, ent))
        

    

    tk.Button(scroll_frame, text="Register", command=lambda: register(entries, required, menu_var), font="Arial 15 bold",
           bg="black", fg="white", pady=10, padx=30, bd=0, highlightthickness=0, activebackground="#3E3B3C",
           activeforeground="white").pack(pady=25)




def startRecognition():
    global img_read, img_label

    if(img_label == None):
        messagebox.showerror("Error", "No image selected. ")
        return

    crims_found_labels = []
    for wid in right_frame.winfo_children():
        wid.destroy()

    frame = cv2.flip(img_read, 1, 0)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    face_coords = detect_faces(gray_frame)

    if (len(face_coords) == 0):
        #messagebox.showinfo("Information", "Image doesn't contain any face or contains empty bike.")
        now2=tk.Label(root,text="Normal Mode",font="times 22 bold",width=100)
        now2.place(x=900,y=300,width=300,height=60)
        wrong2=tk.Label(root,text="Normal",font="times 22 bold",width=100)
        wrong2.place(x=800,y=400,width=500,height=60)
        wrong2.after(2000, wrong2.destroy)

        now2.after(2000,now2.destroy)
                
    else:
        (model, names) = train_model()
        print('Training Successful. Detecting Faces')
        (frame, recognized) = recognize_face(model, frame, gray_frame, face_coords, names)

        img_size = left_frame.winfo_height() - 40
        frame = cv2.flip(frame, 1, 0)
        showImage(frame, img_size)
        print("showImage")
        

        if (len(recognized) == 0):
            #messagebox.showwarning("Error", "UNKNOWN PERSON DETECTED.")
            if current_hour >= 18 or current_hour < 6:
                wrong=tk.Label(root,text="Unknown Person Detected",font="times 22 bold",width=100)
                wrong.place(x=800,y=400,width=500,height=60)
                now=tk.Label(root,text="Active Mode",font="times 22 bold",width=100)
                now.place(x=900,y=300,width=300,height=60)
                for i in range(1):
                    engine=pyttsx3.init()
                    engine.say("UNKNOWN PERSON DETECTED")
                    engine.runAndWait()
                    time.sleep(0.7)
                    print("fail")
                messagebox.showwarning("Information", "UNKNOWN PERSON DETECTED.")
                
                host = "smtp.gmail.com"
                mmail = "egowthamhari2019@gmail.com"        
                hmail = "harilingapradeep2001@gmail.com"
                receiver_name = "...."
                sender_name= "Security Officer"
                msg = MIMEMultipart()
                subject = '''Hello,
                       'Someone try to access your bike',
                       For further Details
                       Contant us- 1098
                       Email-id: egowthamhari2019@gmail.com'''
                text = '''Hello,
                       'Someone try to access your bike',
                       For further Details
                       Contant us- 1098
                       Email-id: egowthamhari2019@gmail.com'''
                msg = MIMEText(text, 'plain')
                msg['To'] = formataddr((receiver_name, hmail))
                msg['From'] = formataddr((sender_name, mmail))
                msg['Subject'] = 'Hello, my friend ' + receiver_name
                server = smtplib.SMTP(host, 587)
                server.ehlo()
                server.starttls()
                password = "kscbyldcbxtrvouz"
                server.login(mmail, password)
                server.sendmail(mmail, [hmail], msg.as_string())
                server.quit()
                print('send')
                messagebox.showinfo('Email Sent'," succesfully Sent")
                url='http://iotbegineer.com/api/sensors'
                myobj={'sensor1':'Unknown Person Detected','sensor2':'Chennai','sensor3':'Active Mode','sensor4':'Night','sms':'1'}
                r=requests.post(url,json=myobj,headers={'username':'iotbegin370','Content-Type':'application/json'})
                print(r.text)
                wrong.after(3000, wrong.destroy)
##                img_label.after(3000,img_label.destroy)
                now.after(3000,now.destroy)
                
                
            else:
                
                wrong=tk.Label(root,text="Unknown Person Detected",font="times 22 bold",width=100)
                wrong.place(x=800,y=400,width=500,height=60)
                now=tk.Label(root,text="Normal Mode",font="times 22 bold",width=100)
                now.place(x=900,y=300,width=300,height=60)
                for i in range(1):
                    engine=pyttsx3.init()
                    engine.say("UNKNOWN PERSON DETECTED")
                    engine.runAndWait()
                    time.sleep(0.7)
                    print("fail")
                messagebox.showwarning("Information", "UNKNOWN PERSON DETECTED.")
                host = "smtp.gmail.com"
                mmail = "egowthamhari2019@gmail.com"         
                hmail = "harilingapradeep2001@gmail.com"
                receiver_name = "...."
                sender_name= "Security Officer"
                msg = MIMEMultipart()
                subject = '''Hello,
                       'Someone try to access your bike',
                       For further Details
                       Contant us- 1098
                       Email-id: egowthamhari2019@gmail.com'''
                text = '''Hello,
                       'Someone try to access your bike',
                       For further Details
                       Contant us- 1098
                       Email-id: egowthamhari2019@gmail.com'''
                msg = MIMEText(text, 'plain')
                msg['To'] = formataddr((receiver_name, hmail))
                msg['From'] = formataddr((sender_name, mmail))
                msg['Subject'] = 'Hello, my friend ' + receiver_name
                server = smtplib.SMTP(host, 587)
                server.ehlo()
                server.starttls()
                password = "kscbyldcbxtrvouz"
                server.login(mmail, password)
                server.sendmail(mmail, hmail, msg.as_string())
                server.quit()
                print('send')
                messagebox.showinfo('Email Sent'," succesfully Sent")
                url='http://iotbegineer.com/api/sensors'
                myobj={'sensor1':'Unknown Person Detected','sensor2':'Chennai','sensor3':'Normal Mode','sensor4':'Morning','sms':'1'}
                r=requests.post(url,json=myobj,headers={'username':'iotbegin370','Content-Type':'application/json'})
                print(r.text)
                wrong.after(3000, wrong.destroy)
##                img_label.after(3000,img_label.destroy)
                now.after(3000,now.destroy)


                
                

        for i, crim in enumerate(recognized):
            crims_found_labels.append(tk.Label(right_frame, text=crim[0], bg="orange",
                                            font="Arial 15 bold", pady=20))
            crims_found_labels[i].pack(fill="x", padx=20, pady=10)
            #crims_found_labels[i].bind("<Button-1>", lambda e, name=crim[0]:showProfile(name))
            print("success")
            filen = "file.csv"

            # Open the CSV file in read mode
            with open(filen, 'r') as csvfile:
                # Create a CSV reader object
                csvreader = csv.reader(csvfile)
            
                # Skip the first two rows
                next(csvreader)
                next(csvreader)
            
                # Get the value of the 3rd column and 3rd row
                row = next(csvreader)
                value = row[2]
            
                # Print the value
                print(value)
                        


def selectImage():
    global left_frame, img_label, img_read
    
    for wid in right_frame.winfo_children():
        wid.destroy()

    filetype = [("images", "*.jpg *.jpeg *.png")]
    path = filedialog.askopenfilename(title="Choose a image", filetypes=filetype)

    if(len(path) > 0):
        img_read = cv2.imread(path)
        

        img_size =  left_frame.winfo_height() - 40
        
        showImage(img_read, img_size)
        startRecognition()
        


def getPage2():
    global active_page, left_frame, right_frame, img_label, heading
    img_label = None
    active_page = 2
    pages[2].lift()

    basicPageSetup(2)
    heading.configure(text="Detect Images")
    right_frame.configure(text="Detected Person", fg="white")

    btn_grid = tk.Frame(left_frame, bg="white")
    btn_grid.pack()

    tk.Button(btn_grid, text="Select Image", command=selectImage, font="Arial 15 bold", padx=20, bg="white",
            fg="black", pady=10, bd=0, highlightthickness=0, activebackground="white",
            activeforeground="white").grid(row=0, column=0, padx=25, pady=25)






def getPage3():
    root.destroy()
    

   




tk.Label(pages[0], text="TWO WHEELER THEFT PREDICTION", fg="black", activeforeground="#A0CFEC",bg="#A0CFEC",font="Arial 15 bold", pady=30).pack()

tk.Label(pages[0], bg="#A0CFEC").pack(side='left')

btn_frame = tk.Frame(pages[0], pady=30)
#btn_frame.pack(side='left', padx=100,pady=10)
btn_frame.place(x=170,y=150)

tk.Button(btn_frame, text="REGISTRATION", command=getPage1, highlightthickness=0, bd=0)
tk.Button(btn_frame, text="SURVEILLANCE", command=getPage2, highlightthickness=0, bd=0)
tk.Button(btn_frame, text="EXIT", command=getPage3, highlightthickness=0, bd=0)

for btn in btn_frame.winfo_children():
    btn.configure(font="Arial 12 bold", width=24, bg="#A0CFEC", fg="black", pady=1,
                  highlightthickness=0, bd=0,activebackground="#A0CFEC", activeforeground="black")
    btn.pack(pady=30)

pages[0].lift()
root.mainloop()
