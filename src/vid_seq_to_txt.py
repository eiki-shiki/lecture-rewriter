import cv2
import pytesseract
import json
import os
import difflib
import numpy as np

from .util import Clamp
from .util import TryToCreateFolder
from .util import GetFolderPath
from .util import GetTimeFromMs
from .util import SafeDeepCopy
from .util import DictGetAliases
from .util import SortCFGJSONByTime
from .util import ManageConfigs

from .config import CFG

def VidSeqToTxt(path):
    def ManageCrop(cap, crop, max_x = None, max_y = None):
        _max_x = max_x if max_x != None else int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        _max_y = max_y if max_y != None else int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        crop[0] = Clamp(crop[0], 0, _max_x) # x1
        crop[1] = Clamp(crop[1], 0, _max_y) # y1
        crop[2] = Clamp(crop[2], 0, _max_x) # x2
        crop[3] = Clamp(crop[3], 0, _max_y) # y2
        if (crop[2] == 0):
            crop[2] = _max_x
        if (crop[3] == 0):
            crop[3] = _max_y
        return crop

    def Iterate(i):
        nonlocal cap, prev_text, file_index, json_result, folder_screens, current_cfg, prev_tess_img
        cap.set(cv2.CAP_PROP_POS_MSEC, i)
        succ, frame = cap.read()
        if (not succ):
            print(i, "succ is False. Something bad happened.")
            return
        do_crop = current_cfg["crop"] != [0, 0, 0, 0]
        crop = ManageCrop(cap, current_cfg["crop"])
        crop_rel = ManageCrop(cap, current_cfg["crop_rel"], max_x=crop[2]-crop[0], max_y=crop[3]-crop[1])
        crop_tess = ManageCrop(cap, current_cfg["crop_tess"])
        crop_tess_rel = ManageCrop(cap, current_cfg["crop_tess_rel"], max_x=crop_tess[2]-crop_tess[0], max_y=crop_tess[3]-crop_tess[1])
        crop_scrn = ManageCrop(cap, current_cfg["crop_scrn"])
        crop_scrn_rel = ManageCrop(cap, current_cfg["crop_scrn_rel"], max_x=crop_scrn[2]-crop_scrn[0], max_y=crop_scrn[3]-crop_scrn[1])
        #if (do_crop):
        frame = frame[crop[1]:crop[3], crop[0]:crop[2]]
        #if (crop != crop_rel):
        frame = frame[crop_rel[1]:crop_rel[3], crop_rel[0]:crop_rel[2]]
        tess_img = frame
        #if (crop != crop_tess):
        tess_img = tess_img[crop_tess[1]:crop_tess[3], crop_tess[0]:crop_tess[2]]
        #if (crop_tess != crop_tess_rel):
        tess_img = tess_img[crop_tess_rel[1]:crop_tess_rel[3], crop_tess_rel[0]:crop_tess_rel[2]]
        tess_img = cv2.cvtColor(tess_img, cv2.COLOR_BGR2GRAY)
        ret, tess_img = cv2.threshold(tess_img, 110, 255, cv2.THRESH_TOZERO)
        text_comp = ""
        if (not current_cfg["force"]):
            text_comp = pytesseract.image_to_string(tess_img, config=current_cfg["tesseract_args"])
        #text_comp = text_comp.replace("\nо ", "\n").replace("\nо_", "\n").replace("\nэ ", "\n").replace("\nэ_", "\n")
        if (prev_text != text_comp or current_cfg["force"]):
            s = difflib.SequenceMatcher(None, prev_text, text_comp)
            if (current_cfg["force"] or s.ratio() < current_cfg["max_text_difference_ratio"]):
                # TODO: also check images similarities because this isn't perfect
                haveto = True
                if (haveto or current_cfg["force"]):
                    time = GetTimeFromMs(i)
                    file_name = str(file_index) + '_' + time.replace(':', '-') + '.' + CFG.vid_seq_to_txt_screens_format
                    file_path = os.path.join(folder_screens, file_name)
                    scrn = frame
                    #if (crop != crop_scrn):
                    scrn = scrn[crop_scrn[1]:crop_scrn[3], crop_scrn[0]:crop_scrn[2]]
                    #if (crop != crop_rel):
                    scrn = scrn[crop_scrn_rel[1]:crop_scrn_rel[3], crop_scrn_rel[0]:crop_scrn_rel[2]]
                    cv2.imwrite(file_path, scrn)
                    text = pytesseract.image_to_string(scrn, config=current_cfg["tesseract_args"])
                    # cv2.imwrite(os.path.join(folder_screens, file_name.replace('.', ".test.")), tess_img) # Debug?
                    json_result.append({
                        "timeMs": i, "time": time, "file": os.path.join(CFG.vid_seq_to_txt_screens_dir, file_name), "dim": [scrn.shape[1], scrn.shape[0]],
                    })
                    print(json_result[-1])
                    print("-"*75)
                    print(text)
                    print("-"*75)
                    json_result[-1]["text"] = text
                    file_index += 1
        #prev_tess_img = tess_img
        prev_text = text_comp
        return
    
    print("vid_seq_to_txt")
    folder = GetFolderPath(path)
    if (os.path.isfile(os.path.join(folder, CFG.vid_seq_to_txt_done_file))):
        print(folder, "is ready. Delete", os.path.join(folder, CFG.vid_seq_to_txt_done_file), "to try again. Ignoring...")
        return
    try:
        pytesseract.get_tesseract_version()
    except pytesseract.TesseractNotFoundError:
        print("Tesseract not found in PATH. / Tesseract не найден в PATH.")
        return
    if not "rus" in pytesseract.get_languages():
        print("Russian language is not installed. / Русский язык не установлен.")
        return
    if not "eng" in pytesseract.get_languages(): # how?
        print("English language is not installed. / Английский язык не установлен.")
        return
    
    json_cfg = []
    if (os.path.isfile(os.path.join(folder, CFG.vid_seq_to_txt_cfg_json_file))):
        with open(os.path.join(folder, CFG.vid_seq_to_txt_cfg_json_file), "r") as cfg_f:
            #json_cfg = SortCFGJSONByTime(json.load(cfg_f)) # Is this really necessary?
            json_cfg = json.load(cfg_f)
    current_cfg = SafeDeepCopy(CFG.DEFAULT.vid_seq_to_txt_cfg_json)
    json_cfg_i = 0
    
    folder_screens = os.path.join(folder, CFG.vid_seq_to_txt_screens_dir)
    TryToCreateFolder(folder)
    TryToCreateFolder(folder_screens)
    json_result = []
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps * 1000)
    succ = True
    i = 0
    prev_text = ""
    prev_tess_img = None
    cap.set(cv2.CAP_PROP_POS_MSEC, i)
    file_index = 1
    if (os.path.isfile(os.path.join(folder, CFG.vid_seq_to_txt_save_file))):
        with open(os.path.join(folder, CFG.vid_seq_to_txt_save_file), 'r') as f_save:
            json_save = json.load(f_save)
            i = json_save["i"]
            json_cfg_i = json_save["json_cfg_i"]
            current_cfg = json_save["current_cfg"]
            json_result = json_save["json_result"]
            prev_text = json_save["prev_text"]
            file_index = json_save["file_index"]
    do_stop = False
    while (i < duration and i >= 0):
        iterated_once = False
        cfg_done_once = False
        while (json_cfg_i < len(json_cfg) and DictGetAliases(json_cfg[json_cfg_i], *CFG.time_dict_key_aliases, default=0) <= i):
            cfg_done_once = True
            current_cfg = current_cfg | json_cfg[json_cfg_i]
            current_cfg = ManageConfigs(CFG.DEFAULT.vid_seq_to_txt_cfg_json, current_cfg, CFG.vid_seq_to_txt_cfg_json_file, i)
            i_temp = DictGetAliases(json_cfg[json_cfg_i], *CFG.time_dict_key_aliases, default=0)
            do_stop = current_cfg["stop"]
            if (do_stop):
                break
            if (current_cfg["jump"] != 0):
                i_temp += current_cfg["jump"]
                i = i_temp
            if (current_cfg["jump_to"] >= 0):
                i_temp = current_cfg["jump_to"]
                i = i_temp
            json_cfg_i += 1
            if ((not current_cfg["ignore"] or current_cfg["force"]) and i_temp < duration and i_temp >= 0):
                Iterate(i_temp)
                iterated_once = True
            current_cfg = current_cfg | SafeDeepCopy(CFG.DEFAULT.vid_seq_to_txt_cfg_json_reset)
        if (do_stop):
            break
        if (not iterated_once and (not current_cfg["ignore"] or current_cfg["force"]) and i < duration and i >= 0):
            Iterate(i)
        if (not cfg_done_once):
            current_cfg = current_cfg | SafeDeepCopy(CFG.DEFAULT.vid_seq_to_txt_cfg_json_reset)
        i += current_cfg["step"]
        with open(os.path.join(folder, CFG.vid_seq_to_txt_save_file), "w") as f_save:
            json.dump({
                "i": i,
                "json_cfg_i": json_cfg_i,
                "current_cfg": current_cfg,
                "json_result": json_result,
                "prev_text": prev_text,
                "file_index": file_index,
            }, f_save, ensure_ascii=False, indent=4)
    
    with open(os.path.join(folder, CFG.vid_seq_to_txt_json_file), "w") as f:
        json.dump(json_result, f, ensure_ascii=False, indent=4)
    with open(os.path.join(folder, CFG.vid_seq_to_txt_done_file), "w") as f:
        pass
    if (os.path.isfile(os.path.join(folder, CFG.vid_seq_to_txt_save_file))):
        os.remove(os.path.join(folder, CFG.vid_seq_to_txt_save_file))
    if (CFG.vid_seq_to_txt_delete_screens_dir):
        for e in [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]:
            os.remove(e)
        try:
            os.rmdir(folder_screens)
        except OSError as err:
            pass
