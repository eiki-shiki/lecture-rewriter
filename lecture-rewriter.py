import sys
import json
import os
import cv2
from multiprocessing import Process

from src.util import GetSortedFilesFromDir
from src.voice_to_txt import VoiceToTxt
from src.vid_seq_to_txt import VidSeqToTxt
from src.summary_to_txt import SummaryToTxt
from src.to_pdf import ToPdf

def ManageFile(file, act_arr, task_args):
    print("[ManageFile]", file)
    try:
        extension = os.path.splitext(file)[1]
        if (extension == ".pdf" or extension == ".json"):
            raise -1
        else:
            vid = cv2.VideoCapture(file)
            if not vid.isOpened():
                raise -1
    except:
        print(file, "is not a video.")
    else:
        if (0 in act_arr and 1 in act_arr and task_args.get("01async", True)):
            proc1 = Process(target=VoiceToTxt, args=(file, ))
            proc2 = Process(target=VidSeqToTxt, args=(file, ))
            proc1.start()
            proc2.start()
            proc1.join()
            proc2.join()
        else:
            if (0 in act_arr):
                VoiceToTxt(file)
            if (1 in act_arr):
                VidSeqToTxt(file)
        if (2 in act_arr):
            SummaryToTxt(file)

def Main(path):
    tasks = None
    if (os.path.isfile(path)):
        with open(path, 'r') as f:
            tasks = json.load(f)
    if (os.path.isdir(path)):
        tasks = [
            {
                "task": path,
                "act": [0, 1, 2, 3],
                "args": {},
            },
        ]
    if (tasks is None):
        print("Path", path, "not found.")
        return
    for e in tasks:
        task_arr = e["task"]
        if (not isinstance(task_arr, list)):
            task_arr = [e["task"]]
        act_arr = e["act"]
        task_args = e.get("args", {})
        if (not isinstance(act_arr, list)):
            act_arr = [e["act"]]
        for e_arr in task_arr:
            if (os.path.isdir(e_arr)):
                if (0 in act_arr or 1 in act_arr or 2 in act_arr):
                    dirs_e_arr = GetSortedFilesFromDir(e_arr)
                    for ee in dirs_e_arr:
                        ManageFile(os.path.join(e_arr, ee), act_arr, task_args)
                if (3 in act_arr):
                    ToPdf(e_arr)
            elif (os.path.isfile(e_arr)):
                ManageFile(e_arr, act_arr, task_args)
            else:
                print("Path", path, "not found.")


if (__name__ == "__main__"):
    if (len(sys.argv) > 1):
        Main(sys.argv[1])
    else:
        print("Not enough args.")
