import os
import subprocess
import cv2
import json
import random
import argparse
import logging
import coloredlogs

# Logging Configuration
LOG_FORMAT = "{asctime} [{levelname[0]}] {name} : {message}"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_STYLE = "{"

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
logger.info("Required files: dovi_tool.exe, mkvmerge.exe, ffmpeg.exe, hdr10plus_tool.exe")

current_file = __file__
real_path = os.path.realpath(current_file)
dir_path = os.path.dirname(real_path)

# Tool paths definition
dvexe = os.path.join(dir_path, 'dovi_tool.exe')
ffmpegexe = os.path.join(dir_path, 'ffmpeg.exe')
mkvmergeexe = os.path.join(dir_path, 'mkvmerge.exe')
hdrplusexe = os.path.join(dir_path, 'hdr10plus_tool.exe')

# Command-line argument parsing
parser = argparse.ArgumentParser(description="Process HDR10+ and Dolby Vision video")
parser.add_argument("-o", '--output', dest="output", help="Specify output file name with no extension", required=True)
parser.add_argument("-hdr10plus_file", help="Path to the input HDR10+ file")
parser.add_argument("-rpu", help="RPU generation mode (options: hdr, hlg)")
parser.add_argument("-no_muxing", action="store_true", help="Skip the muxing process")
args = parser.parse_args()
output = str(args.output)

if args.hdr10plus_file:
    logger.info("Processing HDR10+...")

    # Extract HDR10+ video and determine FPS
    hdr10plus_extraction_command = [
        ffmpegexe,
        '-nostdin',
        '-loglevel', 'error',
        '-stats',
        '-i', args.hdr10plus_file,
        '-c:v', 'copy',
        'hdr10plus.hevc'
    ]
    subprocess.run(hdr10plus_extraction_command)
    logger.info("Extraction complete.")

    # Extract HDR10+ JSON metadata
    hdr10plus_extraction_json_command = [
        hdrplusexe, 'extract', 'hdr10plus.hevc', '-o', 'hdr10plus_manifest.json'
    ]
    subprocess.run(hdr10plus_extraction_json_command)

    # Generate RPU.bin from HDR10+ JSON
    dv_fromhdr10plus_command = [
        dvexe, 'generate', '-j', 'cmv40.json', '--hdr10plus-json', 'hdr10plus_manifest.json', '-o', 'RPU.bin'
    ]
    subprocess.run(dv_fromhdr10plus_command)

if args.rpu == "hdr" or args.rpu is None:
    filename = 'L6_8.1.json'
    json_data = {
        "length": 0,
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
    logger.info(f"JSON file '{filename}' successfully generated for {mode_description}.")

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

# Open the video file using OpenCV
video_path = args.hdr10plus_file
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    logger.error("Error: Failed to open the video file.")
else:
    # Get the video FPS
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Determine description based on frame rate
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
logger.info("Combining DV Profile 8 and HDR...")
if os.path.isfile("RPU-edited.bin"):
    logger.info("RPU edited successfully. Using RPU-edited.bin for injection.")
    dv_hdr_command = [
        dvexe,
        'inject-rpu',
        '-i', 'hdr10plus.hevc',
        '--rpu-in', 'RPU-edited.bin',
        '-o', 'dvhdr.hevc'
    ]
else:
    logger.info("RPU was not edited successfully. Using RPU.bin for injection.")
    dv_hdr_command = [
        dvexe,
        'inject-rpu',
        '-i', 'hdr10plus.hevc',
        '--rpu-in', 'RPU.bin',
        '-o', 'dvhdr.hevc'
    ]
subprocess.run(dv_hdr_command, shell=True)

os.remove("hdr10plus.hevc")

if not args.no_muxing:
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
        args.hdr10plus_file
    ]
    subprocess.run(muxing_command)
    os.remove("dvhdr.hevc")
    logger.info("Muxing complete.")
else:
    logger.info("Muxing skipped.")
