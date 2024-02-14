# Run against test data:

MODEL = { "NAIVE", "SAM" }

`python process_test_data.py NAIVE`

# Run realtime

Realtime works only with NAIVE model.

`python process_realtime.py`

# Create executable

`pyinstaller --onefile --paths env/Lib/site-packages --hidden-import='PIL._tkinter_finder' --hidden-import=appdirs --hidden-import=numpy --hidden-import=pyparsing --hidden-import=opencv --hidden-import=numpy.core._multiarray_tests --hidden-import=numpy.core._multiarray_umath --add-binary "env/Lib/site-packages/numpy.libs/libopenblas64__v0.3.23-293-gc2f4bdbb-gcc_10_3_0-2bde3a66a51006b2b53eb373ff767a3f.dll:." app.py`
