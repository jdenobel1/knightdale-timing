import cv2
import time
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
import pyautogui
import threading

# Global variables for the timer
start_time = None
running = False

# Function to start the stopwatch
def start_timer():
    global start_time, running
    if not running:
        start_time = time.time()
        running = True
        update_timer()

# Function to stop the stopwatch
def stop_timer():
    global running
    running = False

# Function to update the stopwatch display
def update_timer():
    if running:
        elapsed_time = time.time() - start_time
        timer_label.config(text=f"Elapsed time: {elapsed_time:.2f} seconds")
        timer_label.after(50, update_timer)  # Update every 50 ms

# Function to capture a screenshot
def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save(f"screenshot_{time.time():.0f}.png")

# Function to handle key press events (e.g., spacebar for screenshot)
def key_press(event):
    if event.keysym == 'space':
        capture_screenshot()

# Function to handle the webcam feed and overlay the timer
def video_stream():
    cap = cv2.VideoCapture(0)  # Open the webcam
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to ImageTk for embedding in Tkinter
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img_tk = ImageTk.PhotoImage(image=img)

        # Update the webcam label with the new frame
        webcam_label.imgtk = img_tk
        webcam_label.config(image=img_tk)

        # Overlay the timer on the webcam feed
        elapsed_time = 0 if not running else time.time() - start_time
        cv2.putText(frame, f"Elapsed Time: {elapsed_time:.2f}s", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Continue displaying the video feed
        webcam_label.after(10, video_stream)

    cap.release()

# GUI setup
root = tk.Tk()
root.title("Stopwatch with Webcam and Timer Overlay")

# Webcam display label
webcam_label = Label(root)
webcam_label.pack()

# Timer display label
timer_label = Label(root, text="Elapsed time: 0.00 seconds", font=("Arial", 24))
timer_label.pack()

# Start and stop buttons
start_button = tk.Button(root, text="Start Timer", command=start_timer)
start_button.pack(side="left", padx=20)

stop_button = tk.Button(root, text="Stop Timer", command=stop_timer)
stop_button.pack(side="right", padx=20)

# Bind spacebar to screenshot capture
root.bind('<KeyPress>', key_press)

# Start the video stream in a separate thread
threading.Thread(target=video_stream, daemon=True).start()

# Run the GUI loop
root.mainloop()
