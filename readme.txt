A quick bodge to take some video recorded looking at the Stryde app
while doing a freeride to dump the stats of the video to a csv.

Useful for calculating your average wattage or FTP, as the default
Stryde freeride app doesn't do this for some reason.

Requires ffmpeg to be installed and easyocr (https://github.com/JaidedAI/EasyOCR)
to be set up.

Call as:
ocr.py (video_name)

and it'll use ffmpeg to grab one frame per second, run the frame through OCR,
search for output wattage, cadence, and resistance, and dump these values to a
CSV.

known issues:
easyocr will sometimes put random gibberish into the numbers.  i've tried to
put some handling for this in the script, but it doesn't handle all cases.
