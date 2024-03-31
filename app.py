from openpyxl import Workbook
from tkinter import *
import cv2
from os.path import join, exists, expanduser
from os import makedirs
from PIL import Image, ImageTk
from tkinter import filedialog
from processing.process_image_basic import process_image_basic

# from processing.process_image import process_image

from pypylon import pylon
from datetime import datetime

width, height = 1300, 700

app = Tk()
app.title("Capillary bridges image processing")

app.bind('<Escape>', lambda e: app.quit())

label_widget = Label(app, width=width, height=height)
label_widget.pack()

empty_image = ImageTk.PhotoImage(Image.new("RGB", (width, height), "white"))
label_widget.configure(image=empty_image)
label_widget.photo_image = empty_image

values_label = Label(app, text="", font=("Helvetica", 10), wraplength=1200, anchor='w')
values_label.pack(pady=10)

running_camera = False
is_recording = False
is_grabbing = False
should_process_image = True

STANDARD_CAMERA = "Standard"
BASLER_CAMERA = "Basler"

RECORDINGS_FOLDER = "recordings"

base_dir = join(expanduser("~"), "Desktop", "Capillary bridges image analysis")
current_folder_path = None
workbook = None
worksheet = None
image_count = 0
values = None

def create_images_folder_structure():
    global current_folder_path, workbook, worksheet

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    current_folder_path = join(base_dir, timestamp)
    makedirs(current_folder_path)

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["Image", "Neck", "Down", "Up", "Left", "Right", "Left major", "Left minor", "Right major", "Right minor", "Left average", "Right average", "Base", "Height", "x", "1/x", "y"])

    workbook.save(join(current_folder_path, "measured_values.xlsx"))
    
def create_recordings_folder_structure():
    RECORDINGS_PATH = join(base_dir, RECORDINGS_FOLDER)
    
    recordings_folder_exists = exists(RECORDINGS_PATH)
    
    if not recordings_folder_exists: makedirs(RECORDINGS_PATH)

def copy_to_clipboard():
    values_text = values_label.cget("text")
    app.clipboard_clear()
    app.clipboard_append(values_text)
    app.update()

def show_cam_frame(frame):
    if frame is None: return
    
    opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    img = Image.fromarray(opencv_image)
    
    wpercent = (width/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    resized_image = img.resize((width,hsize), Image.Resampling.LANCZOS)
    
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
        
        processed_image, _, values = process_image_basic(image, 0) # process_image(image, 0, './temp', MODEL)
        
        update_values_label(values)

        if processed_image is not None:
            show_cam_frame(processed_image)

def start_recording(selected_camera_index: str):
    global is_recording, out, running_camera
    
    create_recordings_folder_structure()
    
    save_button.config(state="disabled")
    
    stop_button.config(state="normal")
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    out = cv2.VideoWriter(join(base_dir, join(RECORDINGS_FOLDER, f"{timestamp}.avi")), fourcc, 20.0, (640,  480))
    
    is_recording = True
    
    if not running_camera:
        open_camera(selected_camera_index)
    
def stop_recording(selected_camera_index: str):
    global running_camera, is_recording
    
    if not is_recording: return
    
    out.release()
    is_recording = False
    
    stop_button.config(state="disabled")
    
    if running_camera:
        reset_label()
        
        if selected_camera_index == STANDARD_CAMERA:
            standard_camera.release()
        elif selected_camera_index == BASLER_CAMERA:
            basler_camera.StopGrabbing()
        
        running_camera = False

def open_camera(selected_camera_index: str):
    global running_camera, standard_camera, basler_camera, is_grabbing, converter, image_count
    is_grabbing = False
    image_count = 0
    
    if not is_recording: create_images_folder_structure()
    
    if not running_camera:
        running_camera = True
        
        if selected_camera_index == STANDARD_CAMERA:
            standard_camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        elif selected_camera_index == BASLER_CAMERA:
            basler_camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
            basler_camera.ExposureTime.SetValue(basler_camera.ExposureTime.Min)
            
        capture_camera(selected_camera_index)
        if not is_recording: save_button.config(state="normal")
        
def save_frame(frame, processed_frame, values):
    global workbook, worksheet, image_count
    
    image_count += 1
    raw_image_filename = f"raw_{image_count}.jpg"
    processed_image_filename = f"processed_{image_count}.jpg"

    cv2.imwrite(join(current_folder_path, raw_image_filename), frame)
    cv2.imwrite(join(current_folder_path, processed_image_filename), processed_frame)
    
    values_list = [values[key] for key in ["neck", "down", "up", "left", "right", "left major", "left minor", "right major", "right minor", "left average", "right average", "base", "height", "x", "1/x", "y"]]

    worksheet.append([worksheet.max_row, *values_list])
    workbook.save(join(current_folder_path, "measured_values.xlsx"))
    
def save_current_frame():
    global frame, processed_frame, values
    if frame is not None and processed_frame is not None and values is not None:
        save_frame(frame, processed_frame, values)

def capture_standard():
    global frame, processed_frame, values, should_process_image
    _, frame = standard_camera.read()
        
    if frame is not None and is_recording:
        out.write(frame)
        show_cam_frame(frame)

    if frame is not None and not is_recording:
        processed_frame, _, values = process_image_basic(frame, 0)
        
        update_values_label(values)

        show_cam_frame(processed_frame if should_process_image else frame)

    label_widget.after(10, lambda: capture_camera(selected_camera_index))
            
def capture_basler():
        global is_grabbing, converter, frame, processed_frame, values, should_process_image
        if not is_grabbing:
            basler_camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            is_grabbing = True
            converter = pylon.ImageFormatConverter()
            converter.OutputPixelFormat = pylon.PixelType_BGR8packed
            converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        
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

                show_cam_frame(processed_frame if should_process_image else frame)

            label_widget.after(10, lambda: capture_camera(selected_camera_index))

        grabResult.Release()

def capture_camera(selected_camera_index: str):
    global is_grabbing
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
        
def toggle_processing():
    global should_process_image
    should_process_image = not should_process_image

def reset_label():
    label_widget.configure(image=empty_image)
    label_widget.photo_image = empty_image
    save_button.config(state="disabled")

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

save_button = Button(app, text="Save image", command=lambda: save_current_frame(), state="disabled")
save_button.pack(side="left", padx=10, pady=10)

start_button = Button(app, text="Start recording", command=lambda: start_recording(selected_camera_index))
start_button.pack(side="left", padx=10, pady=10)

stop_button = Button(app, text="Stop recording", command=lambda: stop_recording(selected_camera_index), state="disabled")
stop_button.pack(side="left", padx=10, pady=10)

camera_menu = OptionMenu(app, StringVar(app, camera_options[1]), *camera_options, command=lambda index: select_camera(index))
camera_menu.pack(side="right", padx=10, pady=10)

image_button_basic = Button(app, text="Process an image (basic)", command=lambda: open_image("NAIVE", selected_camera_index))
image_button_basic.pack(side="right", padx=10, pady=10)

toggle_button = Button(app, text="Toggle processing", command=toggle_processing)
toggle_button.pack(side="right", padx=10, pady=10)

# image_button_basic = Button(app, text="Process an image (neural network)", command=lambda: open_image("SAM", selected_camera_index))
# image_button_basic.pack(side="right", padx=10, pady=10)

copy_button = Button(app, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.pack(side="bottom", padx=10, pady=10)

app.mainloop()
