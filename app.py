from tkinter import *
import cv2
from PIL import Image, ImageTk
from tkinter import filedialog
# from processing.process_image import process_image
from processing.process_image_basic import process_image_basic

width, height = 800, 700

app = Tk()
app.title("Capillary bridges image processing")

app.bind('<Escape>', lambda e: app.quit())

label_widget = Label(app, width=width, height=height)
label_widget.pack()

empty_image = ImageTk.PhotoImage(Image.new("RGB", (width, height), "white"))
label_widget.configure(image=empty_image)
label_widget.photo_image = empty_image

values_label = Label(app, text="", font=("Helvetica", 14))
values_label.pack(pady=10)

running_camera = False

def copy_to_clipboard():
    values_text = values_label.cget("text")
    app.clipboard_clear()
    app.clipboard_append(values_text)
    app.update()
    print("Values copied to clipboard:", values_text)

def open_image(MODEL):
    global running_camera
    if running_camera:
        running_camera = False
        vid.release()
        reset_label()

    file_path = filedialog.askopenfilename(title="Select an image file",
                                           filetypes=[("Image files", "*.png;*.jpg;*.jpeg;")])
    if file_path:
        image = cv2.imread(file_path)
        
        processed_image, _, values = process_image_basic(image, 0)
        # processed_image, _, values = process_image(image, 0, 'single', MODEL)
        
        update_values_label(values)

        if processed_image is not None:
            opencv_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
            resized_image = Image.fromarray(opencv_image).resize((width, height))
            img = ImageTk.PhotoImage(image=resized_image)

            label_widget.photo_image = img
            label_widget.configure(image=img)

def open_camera():
    global running_camera, vid
    if not running_camera:
        running_camera = True
        vid = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        capture_camera()

def capture_camera():
    if running_camera:
        _, frame = vid.read()

        if frame is not None:
            processed_frame, _, values = process_image_basic(frame, 0)
            # processed_frame, _, values = process_image(frame, 0, 'realtime', 'NAIVE')
            
            update_values_label(values)

            if processed_frame is not None:
                opencv_image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                resized_image = Image.fromarray(opencv_image).resize((width, height))
                img = ImageTk.PhotoImage(image=resized_image)

                label_widget.photo_image = img
                label_widget.configure(image=img)

        label_widget.after(10, capture_camera)
    else:
        vid.release()
        reset_label()

def reset_label():
    label_widget.configure(image=empty_image)
    label_widget.photo_image = empty_image

def update_values_label(values):
    formatted_values = {key.capitalize(): f'{value:.2f} um' for key, value in values.items()}
    values_text = ", ".join([f"{key}: {value}" for key, value in formatted_values.items()])
    values_label.config(text=values_text)

realtime_button = Button(app, text="Process realtime", command=open_camera)
realtime_button.pack(side="left", padx=10, pady=10)

image_button_basic = Button(app, text="Process an image (basic)", command=lambda: open_image("NAIVE"))
image_button_basic.pack(side="right", padx=10, pady=10)

# image_button_basic = Button(app, text="Process an image (neural network)", command=lambda: open_image("SAM"))
# image_button_basic.pack(side="right", padx=10, pady=10)

copy_button = Button(app, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.pack(side="bottom", pady=10)

app.mainloop()
