import os
import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json

CONFIG_FILE = 'config.json'

class YouTubeAudioDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('YouTube Audio Downloader')
        self.geometry('500x250')
        
        self.link_var = tk.StringVar()
        self.destination_var = tk.StringVar()
        
        self.load_config()
        
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text='YouTube Link:').pack(pady=10)
        tk.Entry(self, textvariable=self.link_var, width=50).pack(pady=5)
        
        tk.Button(self, text='Choose Destination Folder', command=self.choose_folder).pack(pady=5)
        tk.Entry(self, textvariable=self.destination_var, width=50, state='readonly').pack(pady=5)
        
        self.progress = ttk.Progressbar(self, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(pady=10)
        
        self.status_label = tk.Label(self, text='')
        self.status_label.pack(pady=5)
        
        tk.Button(self, text='Download', command=self.download_audio).pack(pady=5)
    
    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.destination_var.set(folder)
            self.save_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as file:
                config = json.load(file)
                self.destination_var.set(config.get('last_folder', ''))
    
    def save_config(self):
        with open(CONFIG_FILE, 'w') as file:
            config = {'last_folder': self.destination_var.get()}
            json.dump(config, file)
    
    def update_progress(self, d):
        if d['status'] == 'finished':
            self.progress['value'] = 100
            self.status_label.config(text='Download complete')
        elif d['status'] == 'downloading':
            percentage_str = d.get('_percent_str', '0.0%').replace('\x1b[0;94m', '').replace('\x1b[0m', '').strip('%')
            try:
                percentage = float(percentage_str)
                self.progress['value'] = percentage
                self.status_label.config(text=f"Downloading: {d['_percent_str']} of {d['_total_bytes_str']}")
            except ValueError:
                self.status_label.config(text='Error in progress update')

    def download_audio(self):
        url = self.link_var.get()
        if not url:
            self.status_label.config(text='Please enter a YouTube link')
            return
        
        folder = self.destination_var.get()
        if not folder:
            self.status_label.config(text='Please choose a destination folder')
            return
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
            'progress_hooks': [self.update_progress],
        }
        
        self.progress['value'] = 0
        self.status_label.config(text='Downloading...')
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                self.status_label.config(text='Download complete')
        except Exception as e:
            self.status_label.config(text='Failed to download audio')

if __name__ == '__main__':
    app = YouTubeAudioDownloader()
    app.mainloop()
