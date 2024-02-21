from tkinter import *
import cv2
from os.path import join
from PIL import Image, ImageTk
from tkinter import filedialog
from processing.process_image_basic import process_image_basic
from pypylon import pylon
from pathlib import Path

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
is_recording = False
is_grabbing = False

STANDARD_CAMERA = "Standard"
BASLER_CAMERA = "Basler"

def copy_to_clipboard():
    values_text = values_label.cget("text")
    app.clipboard_clear()
    app.clipboard_append(values_text)
    app.update()

def show_cam_frame(frame):
    if frame is None: return
    
    opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resized_image = Image.fromarray(opencv_image).resize((width, height))
    img = ImageTk.PhotoImage(image=resized_image)
    label_widget.photo_image = img
    label_widget.configure(image=img)

def open_image(MODEL, selected_camera_index: str):
    global running_camera
    if running_camera:
        running_camera = False
        
        if selected_camera_index == STANDARD_CAMERA:
            standard_camera.release()
        elif selected_camera_index == BASLER_CAMERA:
            basler_camera.StopGrabbing()
        
        reset_label()

    file_path = filedialog.askopenfilename(title="Select an image file",
                                           filetypes=[("Image files", "*.png;*.jpg;*.jpeg;")])
    if file_path:
        image = cv2.imread(file_path)
        
        processed_image, _, values = process_image_basic(image, 0)
        
        update_values_label(values)

        if processed_image is not None:
            show_cam_frame(processed_image)

def start_recording(selected_camera_index: str):
    global is_recording, out, running_camera
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    
    DOWNLOADS_PATH = str(Path.home() / "Downloads")
    
    out = cv2.VideoWriter(join(DOWNLOADS_PATH, "output.avi"), fourcc, 20.0, (640,  480))
    
    is_recording = True
    
    if not running_camera:
        open_camera(selected_camera_index)
    
def stop_recording(selected_camera_index: str):
    global running_camera, is_recording
    
    if not is_recording: return
    
    out.release()
    is_recording = False
    if running_camera:
        reset_label()
        
        if selected_camera_index == STANDARD_CAMERA:
            standard_camera.release()
        elif selected_camera_index == BASLER_CAMERA:
            basler_camera.StopGrabbing()
        
        running_camera = False

def open_camera(selected_camera_index: str):
    global running_camera, standard_camera, basler_camera, is_grabbing, converter
    is_grabbing = False
    if not running_camera:
        running_camera = True
        
        if selected_camera_index == STANDARD_CAMERA:
            standard_camera = cv2.VideoCapture(0, cv2.CAP_DSHOW) # TO DO - CHANGE INDEX TO 1
        elif selected_camera_index == BASLER_CAMERA:
            basler_camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
            
        capture_camera(selected_camera_index)

def capture_standard():
    _, frame = standard_camera.read()
        
    if frame is not None and is_recording:
        out.write(frame)
        show_cam_frame(frame)

    if frame is not None and not is_recording:
        processed_frame, _, values = process_image_basic(frame, 0)
        
        update_values_label(values)

        show_cam_frame(processed_frame)

    label_widget.after(10, lambda: capture_camera(selected_camera_index))
            
def capture_basler():
        global is_grabbing, converter
        if not is_grabbing:
            basler_camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            is_grabbing = True
            converter = pylon.ImageFormatConverter()
            converter.OutputPixelFormat = pylon.PixelType_BGR8packed
            converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        
    # while basler_camera.IsGrabbing():
        grabResult = basler_camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        if grabResult.GrabSucceeded():
            image = converter.Convert(grabResult)
            frame = image.GetArray()

            if frame is not None and is_recording:
                out.write(frame)
                show_cam_frame(frame)
                
            if frame is not None and not is_recording:
                processed_frame, _, values = process_image_basic(frame, 0)
                
                update_values_label(values)

                show_cam_frame(processed_frame)

            label_widget.after(10, lambda: capture_camera(selected_camera_index))

        grabResult.Release()

def capture_camera(selected_camera_index: str):
    if running_camera:
        if selected_camera_index == STANDARD_CAMERA:
            capture_standard()
        elif selected_camera_index == BASLER_CAMERA:
            capture_basler()
    else:
        if selected_camera_index == STANDARD_CAMERA:
            standard_camera.release()
        elif selected_camera_index == BASLER_CAMERA:
            basler_camera.StopGrabbing()
            is_grabbing = False
        reset_label()

def reset_label():
    label_widget.configure(image=empty_image)
    label_widget.photo_image = empty_image

def update_values_label(values):
    if values is None: return

    formatted_values = {key.capitalize(): f'{value:.2f} um' for key, value in values.items()}
    values_text = ", ".join([f"{key}: {value}" for key, value in formatted_values.items()])
    values_label.config(text=values_text)
    
def select_camera(camera_index):
    global selected_camera_index
    selected_camera_index = camera_index

camera_options = [
    STANDARD_CAMERA,
    BASLER_CAMERA
]
selected_camera_index = BASLER_CAMERA 

realtime_button = Button(app, text="Process realtime", command=lambda: open_camera(selected_camera_index))
realtime_button.pack(side="left", padx=10, pady=10)

start_button = Button(app, text="Start recording", command=lambda: start_recording(selected_camera_index))
start_button.pack(side="left", padx=10, pady=10)

stop_button = Button(app, text="Stop recording", command=lambda: stop_recording(selected_camera_index))
stop_button.pack(side="left", padx=10, pady=10)

camera_menu = OptionMenu(app, StringVar(app, camera_options[1]), *camera_options, command=lambda index: select_camera(index))
camera_menu.pack(side="right", padx=10, pady=10)

image_button_basic = Button(app, text="Process an image (basic)", command=lambda: open_image("NAIVE", selected_camera_index))
image_button_basic.pack(side="right", padx=10, pady=10)

# image_button_basic = Button(app, text="Process an image (neural network)", command=lambda: open_image("SAM"))
# image_button_basic.pack(side="right", padx=10, pady=10)

copy_button = Button(app, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.pack(side="bottom", padx=10, pady=10)

app.mainloop()
