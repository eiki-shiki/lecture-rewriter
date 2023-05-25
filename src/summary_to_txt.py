import json
import os

from .util import TryToCreateFolder
from .util import GetFolderPath

from .config import CFG

def SummaryToTxt(path):
    # TODO: add to result_json "vid_seq_indexes": [0, 1, ...] : vid_seq indexes
    print("summary")
    folder = GetFolderPath(path)
    TryToCreateFolder(folder)
    if (os.path.isfile(os.path.join(folder, CFG.summary_json_file + ".done"))):
        print(folder, "is ready. Delete", os.path.join(folder, CFG.summary_json_file + ".done"), "to try again. Ignoring...")
        return
    if not (os.path.isfile(os.path.join(folder, CFG.voice_to_txt_json_file)) and os.path.isfile(os.path.join(folder, CFG.vid_seq_to_txt_json_file))):
        print(os.path.join(folder, CFG.voice_to_txt_json_file), "or", os.path.join(folder, CFG.vid_seq_to_txt_json_file), "not found. Can't create summary.")
        return
    json_cfg = {}
    if (os.path.isfile(os.path.join(folder, CFG.summary_cfg_json_file))):
        with open(os.path.join(folder, CFG.summary_cfg_json_file), "r") as cfg_f:
            json_cfg = json.load(cfg_f)
    voice_json = None
    vid_json = None
    with open(os.path.join(folder, CFG.voice_to_txt_json_file), "r") as voice_f:
        with open(os.path.join(folder, CFG.vid_seq_to_txt_json_file), "r") as vid_f:
            voice_json = json.load(voice_f)
            vid_json = json.load(vid_f)
    json_result = {
        "title": json_cfg.get("title", os.path.split(folder)[-1]),
        "desc": json_cfg.get("desc", ""),
        "data": [],
        #"vid_seq_indexes": [],
    }
    voice_i = 0
    vid_i = 0
    i = 0
    voice_len = len(voice_json)
    vid_len = len(vid_json)
    while (voice_i < voice_len):
        if (vid_i < vid_len and voice_json[voice_i]["timeMs"][1] >= vid_json[vid_i]["timeMs"]):
            json_result["data"].append({"type": "vid_seq"} | vid_json[vid_i])
            #result_json["vid_seq_indexes"].append(i)
            vid_i += 1
            i += 1
        json_result["data"].append({"type": "voice_txt"} | voice_json[voice_i])
        voice_i += 1
        i += 1
            
    while (vid_i < vid_len):
        json_result["data"].append({"type": "vid_seq"} | vid_json[vid_i])
        #result_json["vid_seq_indexes"].append(i)
        vid_i += 1
        i += 1
    with open(os.path.join(folder, CFG.summary_json_file), "w") as f:
        json.dump(json_result, f, ensure_ascii=False, indent=4)

    with open(os.path.join(folder, CFG.summary_json_file + ".done"), "w") as f:
        pass
