Image analysis of capillary bridges images. It supports both real-time processing and processing of a single image. The measured values are "neck" (shortest distance), "up", "bottom", "left", "right", "left ellipse" and "right ellipse" (+ major and minor axis of the ellipses). There are additional ratio parameters that are calculated based on those values (base, height, etc.).

There can be used two different models for the image segmentation part:

- NAIVE (Satoshi Suzuki and Keiichi Abe. Topological structural analysis of digitized binary images by border following. Computer Vision, Graphics, and Image Processing, 30(1):32–46, 1985.)
- SAM (Fast segment anything https://arxiv.org/pdf/2306.12156.pdf that is based on Segment anything https://arxiv.org/pdf/2304.02643.pdf) 

![image](https://github.com/petkokp/capillary-bridges-image-analysis/assets/61232356/c1f33ff0-3790-4a2b-ad94-a08325a82737)

# Run GUI app:

`python app.py`

# Run against test data:

MODEL = { "NAIVE", "SAM", "MOBILE_SAM" }

`python process_test_data.py NAIVE`

# Run realtime

Realtime works only with NAIVE model.

`python process_realtime.py`

# Create executable

`pyinstaller --onefile --paths env/Lib/site-packages --hidden-import='PIL._tkinter_finder' --hidden-import=appdirs --hidden-import=numpy --hidden-import=pyparsing --hidden-import=opencv --hidden-import=numpy.core._multiarray_tests --hidden-import=numpy.core._multiarray_umath --add-binary "env/Lib/site-packages/numpy.libs/libopenblas64__v0.3.23-293-gc2f4bdbb-gcc_10_3_0-2bde3a66a51006b2b53eb373ff767a3f.dll:." app.py`
