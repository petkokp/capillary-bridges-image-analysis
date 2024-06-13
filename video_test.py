import pypylon.pylon as pylon
from imageio import get_writer

fps = 100  # Hz
time_to_record = 20  # seconds
images_to_grab = fps * time_to_record

tlf = pylon.TlFactory.GetInstance()
devices = tlf.EnumerateDevices()

cam = pylon.InstantCamera(tlf.CreateDevice(devices[0]))
cam.Open()
print("Using device ", cam.GetDeviceInfo().GetModelName())
cam.AcquisitionFrameRate.SetValue(fps)

writer = get_writer(
       'output-filename.mkv',  # mkv players often support H.264
        fps=fps,  # FPS is in units Hz; should be real-time.
        codec='libx264',  # When used properly, this is basically "PNG for video" (i.e. lossless)
        quality=None,  # disables variable compression
        ffmpeg_params=[  # compatibility with older library versions
            '-preset',   # set to fast, faster, veryfast, superfast, ultrafast
            'fast',      # for higher speed but worse compression
            '-crf',      # quality; set to 0 for lossless, but keep in mind
            '24'         # that the camera probably adds static anyway
        ]
)

print(f"Recording...") #{time_to_record} second video at {fps} fps")

cam.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
#cam.StartGrabbingMax(images_to_grab, pylon.GrabStrategy_OneByOne)
while cam.IsGrabbing():
    with cam.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException) as res:
        if res.GrabSucceeded():
            img = res.Array
            writer.append_data(img)
            print(res.BlockID, end='\r')
            res.Release()
        else:
            print("Grab failed")
            # raise RuntimeError("Grab failed")

print("Saving...", end=' ')
cam.StopGrabbing()
cam.Close()
print("Done")