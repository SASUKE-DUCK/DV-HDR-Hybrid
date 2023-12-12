import os
import subprocess
import argparse
import pyfiglet
import cv2
import logging
import coloredlogs
import random
import json

LOG_FORMAT = "{asctime} [{levelname[0]}] {name} : {message}"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_STYLE = "{"

# Configure the custom logger
class Logger():
    def __init__(self, service, log_level):
        self.service = service
        self.log_level = log_level

    def set_logger(self):
        logger1 = logging.getLogger(self.service)
        coloredlogs.install(level=self.log_level, fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT, style=LOG_STYLE)
        return logger1

logger = Logger("HYBRiD", "INFO").set_logger()
logger.info("by -∞WKS∞-#3982")
logger.info("Required files: dovi_tool.exe, mkvmerge.exe, ffmpeg.exe")

arguments = argparse.ArgumentParser()
arguments.add_argument("-o", '--output', dest="output", help="Specify output file name with no extension", required=True)
arguments.add_argument("-dv", '--dolbyvision', dest="dv_file", help="Specify Dolby Vision input file (e.g., dv.mkv , dv.xml or hdr10plus.json)", required=True)
arguments.add_argument("-hdr", '--hdr10', dest="hdr_file", help="Specify HDR10 input file (e.g., hdr10.mkv)", required=True)
arguments.add_argument("-nm", '--no-muxing', dest="no_muxing", action="store_true", help="Omit muxing")
arguments.add_argument("-rpu", choices=["hdr", "hlg"], help="Specify the mode (hdr or hlg)")
arguments.add_argument("-m", "--mode", type=int, choices=[2, 3], help="Specify the DV extraction mode (2 or 3)")
args = arguments.parse_args()

current_file = __file__
real_path = os.path.realpath(current_file)
dir_path = os.path.dirname(real_path)

dvexe = os.path.join(dir_path, 'dovi_tool.exe')
ffmpegexe = os.path.join(dir_path, 'ffmpeg.exe')
mkvmergeexe = os.path.join(dir_path, 'mkvmerge.exe')

output = str(args.output)
dv_file = args.dv_file
hdr_file = args.hdr_file
no_muxing = args.no_muxing

logger.info("Extracting Dolby Vision video and generating BIN DV Profile 8...")

# Determine the file extension of the -dv input file
dv_file_extension = os.path.splitext(dv_file)[1].lower()

if dv_file_extension == '.xml':
    logger.info("Using XML-based Dolby Vision extraction...")
    # Modify the command to use the XML-based extraction
    dv_extraction_rpu_command = [
        dvexe, "generate", "--xml", dv_file, "-o", "RPU.bin"
    ]
elif dv_file_extension == '.json':
    logger.info("Using JSON-based Dolby Vision extraction...")
    # Modify the command to use the JSON-based extraction
    dv_extraction_rpu_command = [
        dvexe, "generate", "--json", dv_file, "--hdr10plus-json", "file_json", "-o", "RPU.bin"
    ]
else:
    if not args.mode:
        logger.error("You must specify a mode using -m or --mode (2 or 3).")
        exit(1)
    logger.info("Using default Dolby Vision extraction...")
    # Use the default extraction method
    dv_extraction_command = [
        ffmpegexe,
        '-nostdin',
        '-loglevel', 'error',
        '-stats',
        '-i', dv_file,
        '-an',
        '-c:v', 'copy',
        '-f', 'hevc',
        'dv.hevc'
    ]
    subprocess.run(dv_extraction_command)
    logger.info("Converting P5 RPU to P8...")
    dv_extraction_rpu_command = [
        dvexe,
        '-m', str(args.mode),
        'extract-rpu',
        'dv.hevc'
    ]

# Continue with the extraction based on the determined method
subprocess.run(dv_extraction_rpu_command)
if dv_file_extension not in ['.xml', '.json']:
    os.remove("dv.hevc")

logger.info("Extraction complete.")

if args.rpu == "hdr" or args.rpu is None:
    filename = 'L6_8.1.json'
    json_data = {
        "level6": {
            "max_display_mastering_luminance": 1000,
            "min_display_mastering_luminance": 1,
            "max_content_light_level": 1000,
            "max_frame_average_light_level": 400
        }
    }
    mode_description = "HDR Mode"
elif args.rpu == "hlg":
    filename = 'L6_8.4.json'
    random_maxcll = random.randint(1, 1000)
    random_maxfall = random.randint(1, 1000)
    json_data = {
        "mode": 4,
        "level6": {
            "max_display_mastering_luminance": 1000,
            "min_display_mastering_luminance": 1,
            "max_content_light_level": random_maxcll,
            "max_frame_average_light_level": random_maxfall
        }
    }
    mode_description = "HLG Mode"
else:
    logger.error("Unrecognized mode.")
    exit(1)

with open(filename, 'w') as json_file:
    json.dump(json_data, json_file, indent=4)
    logger.info(f"JSON file '{filename}' generated successfully for {mode_description}.")

dovi_tool_editor_command = [
    dvexe,
    'editor',
    '-i', 'RPU.bin',
    '-j', filename,
    '--rpu-out', 'RPU-edited.bin'
]
subprocess.run(dovi_tool_editor_command, shell=True)

# Check if RPU-edited.bin exists
if not os.path.isfile("RPU-edited.bin"):
    logger.warning("Warning: RPU was not edited successfully!")

# Continue with the rest of the script
logger.info("Extracting HDR10 video and determining FPS...")
hdr_extraction_command = [
    ffmpegexe,
    '-nostdin',
    '-loglevel', 'error',
    '-stats',
    '-i', hdr_file,
    '-c:v', 'copy',
    'hdr10.hevc'
]
subprocess.run(hdr_extraction_command)
logger.info("Extraction complete.")

# Open the video file using OpenCV
video_path = hdr_file
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    logger.error("Error: Failed to open the video file.")
else:
    # Get the video's FPS
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Determine the description based on the frame rate
    if fps == 23:
        description = "24000/1001p"
    elif fps == 24:
        description = "24p"
    elif fps == 25:
        description = "25p"
    else:
        description = f"{fps} FPS"
    logger.info(f"Video FPS: {description}")

# Decide which command to use for dv_hdr_command based on the existence of RPU-edited.bin
logger.info("Merging DV Profile 8 and HDR...")
if os.path.isfile("RPU-edited.bin"):
    logger.info("RPU edited successfully. Using RPU-edited.bin for injection.")
    dv_hdr_command = [
        dvexe,
        'inject-rpu',
        '-i', 'hdr10.hevc',
        '--rpu-in', 'RPU-edited.bin',
        '-o', 'dvhdr.hevc'
    ]
else:
    logger.info("RPU was not edited successfully. Using RPU.bin for injection.")
    dv_hdr_command = [
        dvexe,
        'inject-rpu',
        '-i', 'hdr10.hevc',
        '--rpu-in', 'RPU.bin',
        '-o', 'dvhdr.hevc'
    ]
subprocess.run(dv_hdr_command, shell=True)

os.remove("hdr10.hevc")

if not no_muxing:
    logger.info("Muxing...")
    muxing_command = [
        mkvmergeexe,
        '--ui-language',
        'en',
        '--output',
        f'{output}.DV.HDR.H.265-GRP.mkv',
        "--default-duration",
        f"0:{description}",
        'dvhdr.hevc',
        '--no-video',
        hdr_file
    ]
    subprocess.run(muxing_command)
    os.remove("dvhdr.hevc")
    logger.info("Muxing complete.")
else:
    logger.info("Muxing omitted.")
