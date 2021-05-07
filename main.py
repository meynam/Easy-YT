from pytube import YouTube
import tkinter
import tkinter.ttk
from tkinter.filedialog import askdirectory
import tkinter.messagebox
from threading import Thread
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Selenium Stuff
options = Options()
options.headless = True
try:
    driver = webdriver.Chrome("Tools\\chromedriver.exe", options=options)
except:
    tkinter.messagebox.showerror("Error","Chrome Driver Missing Download and install on Tools\\chromedriver.exe")
    exit()

running = False

class AppGUI(tkinter.Tk):
    # GUI of our Application
    def __init__(self):
        super().__init__()
        self.design_window()
        self.progress = tkinter.Label(self,font=("Times",12))
        self.progress.pack(side="bottom",fill="x")
    
    def design_window(self):
        # Designs basic window
        self.config(bg="grey")
        self.geometry("720x700")
        self.title("Easy YT")

        self.create_upper_part()
        self.create_mid_part()
        self.create_down_part()
    
    def create_upper_part(self):
        # Creates the upper part of the application
        self.upper = tkinter.LabelFrame(self,text="Video Details")
        self.upper.pack(fill=tkinter.X)

        # Different Frames for labels and textboxes
        qFrame = tkinter.Frame(self.upper)
        qFrame.pack(side=tkinter.LEFT)

        aFrame = tkinter.Frame(self.upper)
        aFrame.pack(side=tkinter.RIGHT)

        # Adding prompt labels
        tkinter.Label(qFrame,text="Save Path",font=("Times",15)).pack()
        tkinter.Label(qFrame,text="File Type",font=("Times",15)).pack()

        # Adding path selector button
        self.path_selector = tkinter.Button(aFrame,command=self.ask_folder,text="Click to Change the Path of saved Video",font=("Times",15))
        self.path_selector.pack(side=tkinter.TOP)

        # Adding file type selector combobox
        self.file_type = tkinter.ttk.Combobox(aFrame,values=[".mp4(Video Form)",".mp3(Audio Form)"],font=("Times",15))
        self.file_type.pack(side=tkinter.TOP,fill="x")
    
    def ask_folder(self):
        # Function of the button -> ask where to save the file
        folder_choosen = askdirectory()
        self.path_selector.config(text=folder_choosen) # Changing the text of the button

    def create_mid_part(self):
        # The mid Part where files cart is shown
        self.midFrame = tkinter.LabelFrame(self,text="Files Cart")
        self.midFrame.pack(fill='x',pady=10)

        self.files_cart = [] # Contains the files to download
        tkinter.Label(self.midFrame,text="Your Cart will start to fill from here -:").pack()

    def create_down_part(self):
        # The foot part 
        foot_frame = tkinter.LabelFrame(self,text="Enter the Name of the Video or link of the video  and press enter to add on the list")
        foot_frame.pack(fill="x")

        self.file_name_1 = tkinter.StringVar()
        self.file_name = tkinter.Entry(foot_frame,font=("Times",16),textvariable=self.file_name_1)
        self.file_name.pack(fill="x")

        # Pressing enter will also enter the details making that
        self.file_name.bind("<Return>",self.add_to_cart)
        self.file_name.bind("<Control-Key-V>",lambda e:self.file_name_1.set(self.clipboard_get()))

        # Adding Buttons
        tkinter.Button(foot_frame,text="Add to Cart",command=self.add_to_cart,font=("Elephant",11)).pack(side='left')
        self.toDisable = tkinter.Button(foot_frame,text="Start Downloading the List",command=self.start_download,font=("Elephant",11))
        self.toDisable.pack(side='right')
        tkinter.Button(foot_frame,command=self.delete,text="Delete last one",font=("Elephant",11)).pack(side='right')
    
    def delete(self):
        # Deletes the last entered video

        if len(self.files_cart) > 0:
            self.files_cart[len(self.files_cart)-1].destroy()
            self.files_cart.pop(len(self.files_cart)-1)

    def add_to_cart(self,e=None):
        # Adds the video to the cart
        if not self.file_name.get().lstrip() == "":
            tempLabel = tkinter.Label(self.midFrame,text=self.file_name.get(),font=("Times",7))
            tempLabel.pack(fill='x')
            self.files_cart.append(tempLabel)
            self.file_name_1.set("")
    
    def start_download(self):
        # Starts the download by creating a downloader object and verifying data
        # Verifying data
        global running
        if not running:
            error =None
            if len(self.files_cart) <1:
                error = "No Files to download"
            elif not os.path.isdir(self.path_selector['text']):
                error = "Please Select a correct Directory by clicking the button"
            elif not self.file_type.get() in [".mp4(Video Form)",".mp3(Audio Form)"]:
                error = "Please select a correct file format from the drop down menu"
            
            if not error == None:
                tkinter.messagebox.showerror("Error",error)
            else:
                downloader = Downloader(self.progress,self.files_cart,self.path_selector['text'],self.file_type.get())

                running = True
                Thread(target = downloader.download).start()
    
class Downloader:
    ''' Dowloader class'''
    def __init__(self,progressLabel,dList,location,format):
        self.progressLabel = progressLabel 
        self.dlist = dList
        self.format = format
        self.location = location
        self.links =[] # container for all the links
    
    def get_link(self,name):
        try:
            # Gets link by web-scraping
            if "www.youtube.com/watch" in name:
                driver.get(name)
                return(driver.title,name)

            else:   
                name = name.replace(" ","+")
                driver.get(f"https://www.youtube.com/results?search_query={name}")
                p_element = driver.find_element_by_id('video-title')
                return (p_element.get_attribute("title"),p_element.get_attribute("href"))
        except:
            tkinter.messagebox.showerror("Error","Couldn't connect to Youtube Probably internet issue. PLZ make sure you have chrome browser in your computer")
            quit()

    def download(self):
        global running
        # Downloads by getting the link
        for lists in self.dlist:
            self.progressLabel['text'] = "Getting link and title of the video -" +lists['text']
            self.links.append(self.get_link(lists['text']))
        
        for links in self.links:
            self.progressLabel['text'] = "Downloading " +links[0]+ " ,wait patiently"
            self.downloadByLink(links[1])
        
        self.progressLabel['text'] = "Downloaded all the files and saved Succesfully"
        running=False

    def downloadByLink(self,link):
        try:
            yt = YouTube(link)
            if self.format==".mp4(Video Form)":
                video = yt.streams[0]
            else:
                video = yt.streams.filter(only_audio=True).first()
            
            video.download(self.location)
        except:
            tkinter.messagebox.showerror("Error","Sorry, couldn't download videos")

if __name__ == "__main__":
    AppGUI().mainloop()
    try:
        driver.close()
    except:
        pass