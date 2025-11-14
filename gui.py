import requests
from tkinter import *
from PIL import Image, ImageTk
import threading
from io import BytesIO

API_URL = 'http://192.168.240.4:5000/controls'
STREAM_URL = 'http://192.168.240.16:5001/video_feed'

def send_command(direction):
    try:
        payload = {'direction': direction}
        response = requests.post(API_URL, json=payload, timeout=0.5)
        response.raise_for_status()
        
        log_message = f"Sent: {direction} | Status: {response.status_code} | Server State: {response.json().get('direction')}"
        login_console.insert(END, log_message + "\n")
        login_console.see(END)
        
    except requests.exceptions.RequestException as e:
        error_message = f"ERROR: Could not connect to API server at {API_URL}. Is the server running on the Pi?\nDetails: {e}"
        login_console.insert(END, error_message + "\n", 'error')
        login_console.see(END)

def forward():
    send_command('forward')

def left():
    send_command('left')

def right():
    send_command('right')

def backwards():
    send_command('backward')

def stop():
    send_command('stop')

class VideoStreamer(threading.Thread):
    def __init__(self, url, label1, label2):
        threading.Thread.__init__(self)
        self.url = url
        self.label1 = label1
        self.label2 = label2
        self.stop_event = threading.Event()

    def run(self):
        try:
            stream = requests.get(self.url, stream=True)
            boundary = stream.headers['content-type'].split('boundary=')[1].encode()
            
            data = b''
            for chunk in stream.iter_content(chunk_size=4096):
                if self.stop_event.is_set():
                    break
                
                data += chunk
                
                a = data.find(boundary)
                b = data.find(b'Content-Type: image/jpeg\r\n\r\n', a)
                c = data.find(boundary, b)
                
                if a != -1 and b != -1 and c != -1:
                    frame_bytes = data[b + len(b'Content-Type: image/jpeg\r\n\r\n'):c]
                    data = data[c:]
                    
                    self.label1.after(0, self.display_frame, frame_bytes)

        except Exception as e:
            print(f"Video Stream Error: {e}")

    def display_frame(self, frame_bytes):
        try:
            image = Image.open(BytesIO(frame_bytes))
            
            width = self.label1.winfo_width()
            height = self.label1.winfo_height()
            if width < 100 or height < 100:
                return

            image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            
            self.label1.config(image=photo)
            self.label1.image = photo
            self.label2.config(image=photo)
            self.label2.image = photo

        except Exception as e:
            pass

    def stop_stream(self):
        self.stop_event.set()

root = Tk()
root.title("4-Quadrant Robot Controller GUI")
root.geometry("1920x1080")

top_left = Frame(root, width=960, height=540, bg="#4f4f4f")
top_right = Frame(root, width=960, height=540, bg="#1a1a1a")
bottom_left = Frame(root, width=960, height=540, bg="#3b3b3b")
bottom_right = Frame(root, width=960, height=540, bg="#2d2d2d")

top_left.grid(row=0, column=0, sticky="nsew")
top_right.grid(row=0, column=1, sticky="nsew")
bottom_left.grid(row=1, column=0, sticky="nsew")
bottom_right.grid(row=1, column=1, sticky="nsew")

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

button_width = 15
button_height = 5
center_x = 960 // 2
center_y = 540 // 2
spacing = 5

btn_up = Button(top_right, text="↑ FORWARD", width=button_width, height=button_height, command=forward, font=('Arial', 14, 'bold'))
btn_up.place(x=center_x - button_width*5, y=center_y - 2*spacing - button_height*20)

btn_down = Button(top_right, text="↓ BACKWARD", width=button_width, height=button_height, command=backwards, font=('Arial', 14, 'bold'))
btn_down.place(x=center_x - button_width*5, y=center_y + 2*spacing)

btn_left = Button(top_right, text="← LEFT", width=button_width, height=button_height, command=left, font=('Arial', 14, 'bold'))
btn_left.place(x=center_x - 3*spacing - button_width*5, y=center_y)

btn_right = Button(top_right, text="→ RIGHT", width=button_width, height=button_height, command=right, font=('Arial', 14, 'bold'))
btn_right.place(x=center_x + 3*spacing - button_width*5, y=center_y)

btn_stop = Button(top_right, text="STOP", width=button_width, height=button_height, command=stop, bg='red', fg='white', font=('Arial', 14, 'bold'))
btn_stop.place(x=center_x - button_width*5, y=center_y)

video1_label = Label(top_left, bg="#4f4f4f")
video1_label.pack(expand=True, fill='both')

video2_label = Label(bottom_left, bg="#3b3b3b")
video2_label.pack(expand=True, fill='both')

console_title = Label(bottom_right, text="API Command Console", font=('Arial', 16, 'bold'), fg='white', bg="#2d2d2d")
console_title.pack(pady=5)
login_console = Text(bottom_right, wrap='word', height=20, width=50, bg="#121212", fg='lightgray', font=('Courier', 12))
login_console.tag_config('error', foreground='red')
login_console.pack(expand=True, fill='both', padx=10, pady=10)

video_thread = VideoStreamer(STREAM_URL, video1_label, video2_label)
video_thread.start()

def on_closing():
    video_thread.stop_stream()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
