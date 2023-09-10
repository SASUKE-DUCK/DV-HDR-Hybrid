## DV-HDR-Hybrid
This script will make a hybrid between Dolby Vision (DV) and HDR videos

## Binaries

* [dovi_tool](https://github.com/quietvoid/dovi_tool)
* [hdr10plus_tool](https://github.com/quietvoid/hdr10plus_tool/)
* [FFmpeg](https://ffmpeg.org/ffmpeg.html)
* [MKVToolNix](https://www.videohelp.com/software/MKVToolNix)

## How to Use dv.py

The `dv.py` script is a powerful video processing tool that allows you to work with Dolby Vision and HDR10 video efficiently. Below, we'll detail how you can use this script to perform various tasks related to video manipulation.

### Prerequisites

Before getting started, ensure you have the following prerequisites in place:

1. **Python**: Make sure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

2. **Executable Files**: The `dv.py` script relies on several external executable files, including `dovi_tool.exe`, `ffmpeg.exe`, and `mkvmerge.exe`. Make sure these files are present in the same directory as `dv.py` before running the script.

### Basic Usage

To get started, you can use the `dv.py` script with the following basic commands:

```shell
python dv.py -o output_name -dv dolby_vision_file -hdr hdr10_file
```

- `-o output_name`: Specify the output file name without the extension. For example, if you want the output file to be named "my_video," provide `-o my_video`.

- `-dv dolby_vision_file`: Specify the input Dolby Vision file you want to process.

- `-hdr hdr10_file`: Define the input HDR10 file to be used in the process.

### Additional Options

The `dv.py` script offers several additional options to customize its behavior. Here are some of the most common options:

- `-nm` or `--no-muxing`: This option skips the multiplexing process, meaning the Dolby Vision and HDR10 videos will not be combined into a single MKV file.

- `-rpu hdr`: This option is used to generate an RPU (Raw Picture Unit) that is compatible with L6 8.1 mode. It ensures that the Dolby Vision video processed with this RPU will be in HDR (High Dynamic Range) mode.

- `-rpu hlg`: When you specify this option, it converts the RPU to L6 8.4 mode. This conversion makes the RPU compatible with HLG (Hybrid Log-Gamma) files, allowing you to work with videos in an HLG format.

- `-m` or `--mode`: Sets the Dolby Vision extraction mode, which can be 2 or 3.

Be sure to review the complete documentation of the `dv.py` script for detailed information on all available options.

### Usage Examples

Here are some usage examples demonstrating how to use the `dv.py` script:

```shell
# Example 1: Process a Dolby Vision and HDR10 video and perform multiplexing.
python dv.py -o my_final_video -dv dolby_vision_video.mkv -hdr hdr10_video.mkv

# Example 2: Extract Dolby Vision in HDR mode and generate a custom JSON file.
python dv.py -o my_video -dv dolby_vision.xml -hdr hdr10_video.mkv -rpu hdr -m 3
```

## How to Use hdr10plus.py

The `hdr10plus.py` script is a versatile tool for processing HDR10+ videos with ease. This script provides various features to handle HDR10+ video extraction, metadata manipulation, and more. In this guide, we'll explore how to use `hdr10plus.py` and its key functionalities.

### Prerequisites

Before you start using `hdr10plus.py`, make sure you have the following prerequisites in place:

1. **Python**: Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

2. **Required Files**: You'll need the `hdr10plus.py` script and associated executable files, such as `ffmpeg.exe`, in the same directory.

### Basic Usage

The `hdr10plus.py` script can be used with the following basic command:

```shell
python hdr10plus.py -o output_name -hdr10plus_file input_hdr10plus_video
```

- `-o output_name`: Specify the name of the output file without the extension.

- `-hdr10plus_file input_hdr10plus_video`: Provide the path to the input HDR10+ video you want to process.

### Features

#### HDR10+ Video Extraction

The script can extract the HDR10+ video stream from your input file. After extraction, the video stream can be further processed or analyzed.

#### Metadata Extraction

`hdr10plus.py` can also extract HDR10+ metadata from the video. This metadata includes information about luminance levels, content light levels, and more.

#### RPU Generation

You can generate an RPU (Raw Picture Unit) file from the HDR10+ metadata. This RPU can be used for further processing or integration into Dolby Vision workflows.

### Usage Examples

Here are some common usage examples of `hdr10plus.py`:

#### Extract HDR10+ Video and Metadata:

```shell
python hdr10plus.py -o my_output -hdr10plus_file input_video.mkv
```

#### Generate RPU from HDR10+ Metadata:

```shell
python hdr10plus.py -o my_rpu -hdr10plus_file input_video.mkv -rpu hdr
```

#### Skip Muxing (No Output File Creation):

```shell
python hdr10plus.py -o my_output -hdr10plus_file input_video.mkv -no_muxing
```

### Additional Options

- `-rpu`: Specifies the RPU generation mode (options: hdr, hlg).

- `-no_muxing`: Skips the multiplexing process, useful when you don't want to create an output file.
