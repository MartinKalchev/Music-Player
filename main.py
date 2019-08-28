from pygame import mixer   # for audio playing
from tkinter import *      # for gui
import os
from mutagen.mp3 import MP3    # extracting metadata from file
import tkinter.messagebox      # for messages showing error for example
from tkinter import filedialog
from tkinter import ttk
from ttkthemes import themed_tk as tk
import time
import threading


# create a window for the mp3 player
root = tk.ThemedTk()
root.get_themes()
root.set_theme("keramik")

status_bar = ttk.Label(root, text="Welcome to Acoustic!", relief=SUNKEN, anchor=W, font='Arial 10 bold')
status_bar.pack(side=BOTTOM, fill=X)

# Create the menu bar
menu_bar = Menu(root)
subMenu = Menu(menu_bar, tearoff=0)
root.config(menu=menu_bar)
root.title("Acoustic")                           # change the title displayed on top of the window
root.iconbitmap(r'images/acoustic_logo.ico')     # change the logo

mixer.init()                                     # initiate the mixer module

# Root Window contains the status bar, left frame and right frame
# Left frame contains the list box
# Right frame contains the top, middle and bottom frames

left_frame = ttk.Frame(root)
left_frame.pack(side=LEFT, padx=30)

right_frame = ttk.Frame(root)
right_frame.pack()

top_frame = ttk.Frame(right_frame)
top_frame.pack()

length_label = ttk.Label(top_frame, text='Total Length: --:--', font='Arial 10 bold')
length_label.pack(pady=10)

current_duration_label = ttk.Label(top_frame, text='Current Duration: --:--', font='Arial 10 bold')
current_duration_label.pack()

# Playlist contains the full path + filename
# Playlist box contains just the filename
# Full path + filename is required to play music inside play_music function
playlist = []


# function to choose file from directory and adding functionality to the 'open' cascade
def browse_file():
    global song_path
    song_path = filedialog.askopenfilename()
    add_to_playlist(song_path)


def add_to_playlist(song_name):
    song_name = os.path.basename(song_name)
    index = 0
    playlist_box.insert(index, song_name)
    playlist.insert(index, song_path)
    index += 1


def about_us():
    tkinter.messagebox.showinfo('About Acoustic', 'This is a music player build using tkinter on Python')


def show_details(play_song):
    file_data = os.path.splitext(play_song)

    if file_data[1] == '.mp3':
        audio = MP3(play_song)
        total_length = audio.info.length
    else:
        a = mixer.Sound(play_song)
        total_length = a.get_length()

    # div - total_length/60, mod - total_length%60
    mins, secs = divmod(total_length, 60)
    mins = round(mins)
    secs = round(secs)
    # proper format to display the length
    time_format = '{:02d}:{:02d}'.format(mins, secs)
    length_label['text'] = "Total Length: " + ' - ' + time_format

    # Threading is necessary because the while loop in start_count will stop the other parts of the program until it is finished
    t1 = threading.Thread(target=start_count, args=(total_length,))
    t1.start()


def start_count(t):
    global paused
    # mixer.music.get_busy() stops the duration count when we press the stop button
    # continue - ignores all of the statements below it and we check if the music is paused or not
    current_time = 0
    while current_time <= t and mixer.music.get_busy():
        if paused:
            continue
        else:
            mins, secs = divmod(current_time, 60)
            mins = round(mins)
            secs = round(secs)
            time_format = '{:02d}:{:02d}'.format(mins, secs)
            current_duration_label['text'] = "Current Duration: " + ' - ' + time_format
            time.sleep(1)
            current_time += 1


def play_music(event):
    global paused
    if paused:
        mixer.music.unpause()
        status_bar['text'] = "Music resumed."
        paused = FALSE
    else:
        try:
            # when switching the song in the playlist we need to stop the song that is already playing because
            # if it is not stopped another thread will be started and the duration label will not display
            # the time correctly
            stop_music()
            time.sleep(1)
            selected_song = playlist_box.curselection()
            selected_song = int(selected_song[0])
            play_song = playlist[selected_song]
            mixer.music.load(play_song)
            mixer.music.play()
            status_bar['text'] = "Playing music " + ' ' + os.path.basename(play_song)
            show_details(play_song)
        except:
            tkinter.messagebox.showerror("File not found", "Acoustic could not find the file, please check again.")


def stop_music():
    mixer.music.stop()
    status_bar['text'] = "Music stopped."


paused = FALSE


# function that pauses the music
def pause_music(event):
    global paused
    paused = TRUE
    mixer.music.pause()
    status_bar['text'] = "Music paused."


def rewind_music(event):
    play_music(event)
    status_bar['text'] = "Music rewound."


muted = FALSE


# function for the mute and unmute functionality
def mute_music(event):
    global muted
    if muted:  # Unmute the music
        mixer.music.set_volume(0.5)
        volume_btn.configure(image=volume_photo)
        scale_vol.set(50)
        muted = FALSE
    else:  # Mute the music
        mixer.music.set_volume(0)
        volume_btn.configure(image=mute_photo)
        scale_vol.set(0)
        muted = TRUE


# set_volume function of mixer takes value only from 0 to 1 exp: 0.1, 0.25
def set_vol(val):
    volume = float(val) / 100
    mixer.music.set_volume(volume)


def del_song():
    selected_song = playlist_box.curselection()
    selected_song = int(selected_song[0])
    playlist_box.delete(selected_song)
    playlist.pop(selected_song)


# center frame for play,stop,pause buttons and status bar
center_frame = ttk.Frame(right_frame)
center_frame.pack(pady=30, padx=30)

# Create the sub-menu
menu_bar.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Open", command=browse_file)
subMenu.add_command(label="Exit", command=root.destroy)

subMenu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=subMenu)
subMenu.add_command(label="About us", command=about_us)

playlist_box = Listbox(left_frame)
playlist_box.pack()

add_photo = PhotoImage(file='images/add_button.png')
add_btn = ttk.Button(left_frame, image=add_photo, command=browse_file)
add_btn.pack(side=LEFT)

del_photo = PhotoImage(file='images/remove_button.png')
del_btn = ttk.Button(left_frame, image=del_photo, command=del_song)
del_btn.pack(side=RIGHT)

play_photo = PhotoImage(file='images/play_button.png')          # specify what is the image to be inserted
play_btn = ttk.Button(center_frame, image=play_photo)               # convert the image into a button
play_btn.bind("<Button-1>", play_music)
play_btn.grid(row=0, column=0, padx=10)

stop_photo = PhotoImage(file='images/stop_button.png')          # specify what is the image to be inserted
stop_btn = ttk.Button(center_frame, image=stop_photo, command=stop_music)               # convert the image into a button
stop_btn.grid(row=0, column=1, padx=10)

pause_photo = PhotoImage(file='images/pause_button.png')
pause_btn = ttk.Button(center_frame, image=pause_photo)
pause_btn.bind("<Button-1>", pause_music)
pause_btn.grid(row=0, column=2, padx=10)

# bottom frame for mute,rewind,scale of volume
bottom_frame = ttk.Frame(right_frame)
bottom_frame.pack()

rewind_photo = PhotoImage(file='images/rewind_button.png')
rewind_btn = ttk.Button(bottom_frame, image=rewind_photo)
rewind_btn.bind("<Button-1>", rewind_music)
rewind_btn.grid(row=0, column=0)

mute_photo = PhotoImage(file='images/mute_btn.png')
volume_photo = PhotoImage(file='images/sound_btn.png')
volume_btn = ttk.Button(bottom_frame, image=volume_photo)
volume_btn.bind("<Button-1>", mute_music)
volume_btn.grid(row=0, column=1, padx=10, pady=10)

# adding a scale for the sound level
scale_vol = ttk.Scale(bottom_frame, from_=0, to=100, orient=HORIZONTAL, command=set_vol)
scale_vol.set(50)   # implement the default value of scale when music player starts
mixer.music.set_volume(0.5)
scale_vol.grid(row=0, column=2, pady=15, padx=30)


def on_close():
    stop_music()
    root.destroy()


# makes sure that when you exit the program while
# it is playing music it doesnt display an error relating the thread function
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
