import sys
from subprocess import call, check_output
import re
from tempfile import TemporaryDirectory
import random


def get_video_duration(input_file):
    """
    This function get the duration of the video file
    :param input_file: input_file is the targeted video
    :return: duration of the video
    """
    info = check_output(["ffprobe", "-i", input_file, "-show_format"])
    info_text = str(info, "UTF-8")
    m = re.search("duration=(.+?)\\n", info_text)
    return float(m.group(1))


def extract_frames(input, tmp_dir):
    """
    This function extract the frames from the video
    :param input: targeted video
    :param tmp_dir: directory for storing frames
    :return: nothing
    """
    print('Process: Extracting frames...')
    total_duration = get_video_duration(input)
    ts = str(total_duration * 2 / 3)
    td = str(random.randint(6, 11))
    c = call(['ffmpeg', '-ss', ts, '-t', td, '-i', input, '-r', '10', "{}/ffout%03d.png".format(tmp_dir)])
    if c == 0:
        print('Completed extracting frames.')
    else:
        print('Unexpected error occurred.')
    return


def convert_to_gif(output_file, tmp_dir):
    """
    This function covert the frames to gif file
    :param output_file: name of the output file
    :param tmp_dir: directory that stored the frames
    :return: nothing
    """
    print('Process:Start converting frames...')
    c = call(['convert', '-loop', '0', "{}/ffout*.png".format(tmp_dir), output_file])
    if c == 0:
        print("Completed Converting")
    else:
        print('Unexpected error occurred.')
    return


def converter(input, output):
    """
    This function combined all required functions for converting video
    :param input: targeted video file
    :param output: name of that output
    :return:  nothing
    """
    with TemporaryDirectory() as tmp_dir:
        extract_frames(input, tmp_dir)
        convert_to_gif(output, tmp_dir)
    print('Done')
    return


def main():
    """
    Main function
    :return: nothing
    """
    print(sys.argv)
    if len(sys.argv) != 3:
        print("Invalid Number of arguments")
        return
    # =============================
    # Get the arguments (optional
    input = sys.argv[1]
    output = sys.argv[2]
    # =============================
    converter(input, output)


if __name__ == '__main__':
    main()
