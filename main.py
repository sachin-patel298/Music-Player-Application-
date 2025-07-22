import os
from tkinter import *
from tkinter import filedialog, messagebox
from pygame import mixer  # type: ignore
from mutagen.mp3 import MP3  # type: ignore
import time
import threading

# Initialize mixer
mixer.init()

root = Tk()
root.title("🎵 Python MP3 Music Player")
root.geometry("600x480")
root.config(bg="#f0f0f0")

# Global Variables
song_name = StringVar()
status = StringVar(value="Stopped")
song_paths = {}
current_song_path = None
current_position = 0
duration = 0
paused = False

def update_time():
    global current_position
    while True:
        time.sleep(1)
        if mixer.music.get_busy() and not paused:
            current_position += 1
            mins = current_position // 60
            secs = current_position % 60
            time_display.set(f"{mins:02}:{secs:02} / {int(duration)//60:02}:{int(duration)%60:02}")

def add_songs():
    files = filedialog.askopenfilenames(filetypes=[("MP3 Files", "*.mp3")])
    for file in files:
        try:
            audio = MP3(file)
            display_name = os.path.basename(file)
            if display_name not in song_paths:
                song_paths[display_name] = file
                song_list.insert(END, display_name)
        except Exception as e:
            print(f"Invalid MP3: {file}\n{e}")
    if song_list.size() > 0 and not song_list.curselection():
        song_list.select_set(0)

def play_song(from_pos=0):
    global current_song_path, duration, current_position, paused
    try:
        selected_index = song_list.curselection()
        if not selected_index and not current_song_path:
            messagebox.showinfo("No selection", "Please select a song to play.")
            return
        display_name = song_list.get(selected_index) if selected_index else os.path.basename(current_song_path)
        path = song_paths[display_name]
        current_song_path = path
        duration = MP3(path).info.length
        current_position = int(from_pos)
        song_name.set(display_name)
        status.set("Playing")
        paused = False
        mixer.music.load(path)
        mixer.music.play(start=from_pos)
    except Exception as e:
        status.set("Error")
        messagebox.showerror("Playback Error", str(e))

def toggle_play_pause():
    global paused
    if status.get() == "Playing":
        mixer.music.pause()
        status.set("Paused")
        paused = True
    elif status.get() in ["Paused", "Stopped"]:
        if current_song_path:
            mixer.music.unpause()
            status.set("Playing")
            paused = False
        else:
            play_song()

def skip_forward():
    global current_position
    if current_song_path:
        new_pos = current_position + 10
        if new_pos < duration:
            play_song(from_pos=new_pos)

def skip_backward():
    global current_position
    if current_song_path:
        new_pos = max(current_position - 10, 0)
        play_song(from_pos=new_pos)

def set_volume(val):
    mixer.music.set_volume(float(val))

# 🆕 NEW FUNCTION: Play song when selected
def on_song_select(event):
    global current_song_path
    selected_index = song_list.curselection()
    if selected_index:
        selected_song = song_list.get(selected_index)
        if song_paths.get(selected_song) != current_song_path:
            play_song(from_pos=0)
        else:
            play_song(from_pos=0)  # Restart if same song clicked

# UI
Label(root, text="Python Music Player", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)
Label(root, textvariable=song_name, font=("Arial", 12), fg="blue", bg="#f0f0f0").pack()

# Time Display
time_display = StringVar(value="00:00 / 00:00")
Label(root, textvariable=time_display, font=("Arial", 11), bg="#f0f0f0").pack()

# Song list
frame = Frame(root)
frame.pack(pady=10)

scrollbar = Scrollbar(frame, orient=VERTICAL)
song_list = Listbox(frame, yscrollcommand=scrollbar.set, width=60, height=10)
scrollbar.config(command=song_list.yview)
scrollbar.pack(side=RIGHT, fill=Y)
song_list.pack(side=LEFT, fill=BOTH)
song_list.bind("<<ListboxSelect>>", on_song_select)  # 🆕 Bind list click to play

# Music Controls
button_frame = Frame(root, bg="#f0f0f0")
button_frame.pack(pady=5)

Button(button_frame, text="⏮️ Back 10s", command=skip_backward, width=17).grid(row=0, column=0, padx=5, pady=5)
Button(button_frame, text="▶️/⏸️ Play/Pause", command=toggle_play_pause, width=17).grid(row=0, column=1, padx=5, pady=5)
Button(button_frame, text="⏭️ Forward 10s", command=skip_forward, width=17).grid(row=0, column=2, padx=5, pady=5)

# Volume slider
Label(root, text="Volume", bg="#f0f0f0").pack()
volume_slider = Scale(root, from_=0, to=1, resolution=0.1, orient=HORIZONTAL, command=set_volume, length=300)
volume_slider.set(0.7)
volume_slider.pack()

# Add Songs Button (Bottom Center)
Button(root, text="➕ Add Songs", command=add_songs, width=20).pack(pady=15)

# Status bar
Label(root, textvariable=status, bd=1, relief=SUNKEN, anchor=W, bg="#e0e0e0").pack(side=BOTTOM, fill=X)

# Start time tracking thread
threading.Thread(target=update_time, daemon=True).start()

# Start GUI
root.mainloop()
