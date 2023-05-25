import json

import speech_recognition as sr
import os 
from pydub import AudioSegment
#from pydub.silence import split_on_silence

from .util import TryToCreateFolder
from .util import GetFolderPath
from .util import GetTimeFromMs
from .util import AlwaysReplaceVoice
from .util import SafeDeepCopy
from .util import DictGetAliases
from .util import SortCFGJSONByTime
from .util import ManageConfigs

from .config import CFG

# split_on_silence dependencies
import itertools
from pydub.silence import detect_nonsilent

def split_on_silence_edited(audio_segment, min_silence_len=1000, silence_thresh=-16, keep_silence=100,
                     seek_step=1):
    """
    # https://github.com/jiaaro/pydub/blob/master/pydub/silence.py#L112
    # Modification: also return timecodes
    Returns list of audio segments from splitting audio_segment on silent sections (and timecodes)
    audio_segment - original pydub.AudioSegment() object
    min_silence_len - (in ms) minimum length of a silence to be used for
        a split. default: 1000ms
    silence_thresh - (in dBFS) anything quieter than this will be
        considered silence. default: -16dBFS
    keep_silence - (in ms or True/False) leave some silence at the beginning
        and end of the chunks. Keeps the sound from sounding like it
        is abruptly cut off.
        When the length of the silence is less than the keep_silence duration
        it is split evenly between the preceding and following non-silent
        segments.
        If True is specified, all the silence is kept, if False none is kept.
        default: 100ms
    seek_step - step size for interating over the segment in ms
    """

    # from the itertools documentation
    def pairwise(iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = itertools.tee(iterable)
        next(b, None)
        return zip(a, b)

    if isinstance(keep_silence, bool):
        keep_silence = len(audio_segment) if keep_silence else 0

    detect_nonsilent_result = detect_nonsilent(audio_segment, min_silence_len, silence_thresh, seek_step)

    output_ranges = [
        [ start - keep_silence, end + keep_silence ]
        for (start,end)
            in detect_nonsilent_result
    ]

    for range_i, range_ii in pairwise(output_ranges):
        last_end = range_i[1]
        next_start = range_ii[0]
        if next_start < last_end:
            range_i[1] = (last_end+next_start)//2
            range_ii[0] = range_i[1]

    return ([
        audio_segment[ max(start,0) : min(end,len(audio_segment)) ]
        for start,end in output_ranges
    ], detect_nonsilent_result)


def VoiceToTxt(path):

    def Iterate(i):
        # TODO: create all chunks before starting iteration (right after split_on_silence)
        nonlocal chunks_dir_name, json_result, recogn, timecodes
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(chunks_dir_name, f"{CFG.voice_to_txt_chunk_filename}{i}.{CFG.voice_to_txt_sound_format}")
        audio_chunk = AudioSegment.from_file(chunk_filename, CFG.voice_to_txt_sound_format)
        if (current_cfg["add_volume"] != 0):
            audio_chunk = audio_chunk + current_cfg["add_volume"]
        if (current_cfg["add_volume_rel"] != 0):
            audio_chunk = audio_chunk + current_cfg["add_volume_rel"]
        audio_chunk.export(chunk_filename, format=CFG.voice_to_txt_sound_format)
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = recogn.record(source)
            # try converting it to text
            try:
                text = recogn.recognize_google(audio_listened, language=current_cfg["language"])
                #text = recogn.recognize_sphinx(audio_listened, language=current_cfg["language"])
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = f"{text.capitalize()}. "
                text = AlwaysReplaceVoice(text)
                print(chunk_filename, ":", text)
                # timecodes_normal = [str(timecodes[i][0])] # what is this for???
                json_result.append({
                    "timeMs": timecodes[i], "time": [GetTimeFromMs(timecodes[i][0]), GetTimeFromMs(timecodes[i][1])], "text": text, "index": i,
                })
        return
    print("voice_to_txt")
    folder = GetFolderPath(path)
    TryToCreateFolder(folder)
    if (os.path.isfile(os.path.join(folder, CFG.voice_to_txt_done_file))):
        print(folder, "is ready. Delete", os.path.join(folder, CFG.voice_to_txt_done_file), "to try again. Ignoring...")
        return
    json_cfg = []
    recogn = sr.Recognizer()
    json_result = []
    folder = GetFolderPath(path)
    current_cfg = None
    chunks_dir_name = os.path.join(folder, CFG.voice_to_txt_chunks_dir)
    timecodes = None
    chunks_len = 0
    i = 0
    json_cfg_i = 0
    if (os.path.isfile(os.path.join(folder, CFG.voice_to_txt_cfg_json_file))):
        with open(os.path.join(folder, CFG.voice_to_txt_cfg_json_file), "r") as cfg_f:
            #json_cfg = SortCFGJSONByTime(json.load(cfg_f)) # Is this really necessary?
            json_cfg = json.load(cfg_f)
    if (os.path.isfile(os.path.join(folder, CFG.voice_to_txt_save_file))):
        with open(os.path.isfile(os.path.join(folder, CFG.voice_to_txt_save_file)), 'r') as f_save:
            json_save = json.load(f_save)
            timecodes = json_save["timecodes"]
            i = json_save["i"]
            json_cfg_i = json_save["json_cfg_i"]
            current_cfg = json_save["current_cfg"]
            json_result = json_save["json_result"]
            chunks_len = json_save["chunks_len"]
    else:
        current_cfg = SafeDeepCopy(CFG.DEFAULT.voice_to_txt_cfg_json)
        while (json_cfg_i < len(json_cfg) and not DictGetAliases(json_cfg[json_cfg_i], *CFG.time_dict_key_aliases, default=0)):
            current_cfg = current_cfg | json_cfg[json_cfg_i]
            current_cfg = ManageConfigs(CFG.DEFAULT.voice_to_txt_cfg_json, current_cfg, CFG.voice_to_txt_cfg_json_file, 0)
            json_cfg_i += 1
        json_cfg_i = 0
        sound = AudioSegment.from_file(path)
        if (current_cfg["add_volume_before"]):
            sound = sound + current_cfg["add_volume_before"]
        # split audio sound where silence is 700 miliseconds or more and get chunks
        chunks, timecodes = split_on_silence_edited(sound,
            # experiment with this value for your target audio file
            min_silence_len = current_cfg["min_silence_len"],
            # adjust this per requirement
            silence_thresh = sound.dBFS + current_cfg["silence_thresh"],
            # keep the silence for 1 second, adjustable as well
            keep_silence = current_cfg["keep_silence"],
        )
        chunks_len = len(chunks)
        # reset current_cfg
        current_cfg = SafeDeepCopy(CFG.DEFAULT.voice_to_txt_cfg_json)
        # create a directory to store the audio chunks
        TryToCreateFolder(chunks_dir_name)
        for j in range(chunks_len):
            chunk_filename = os.path.join(chunks_dir_name, f"{CFG.voice_to_txt_chunk_filename}{j}.{CFG.voice_to_txt_sound_format}")
            chunks[j].export(chunk_filename, format=CFG.voice_to_txt_sound_format)
    do_stop = False
    # process each chunk 
    #for i, audio_chunk in enumerate(chunks, start=0):
    while (i < chunks_len and i >= 0):
        iterated_once = False
        cfg_done_once = False
        while (json_cfg_i < len(json_cfg) and DictGetAliases(json_cfg[json_cfg_i], *CFG.time_dict_key_aliases, default=0) <= timecodes[i][1]):
            cfg_done_once = True
            current_cfg = current_cfg | json_cfg[json_cfg_i]
            current_cfg = ManageConfigs(CFG.DEFAULT.voice_to_txt_cfg_json, current_cfg, CFG.voice_to_txt_cfg_json_file, timecodes[i][1])
            do_stop = current_cfg["stop"]
            if (do_stop):
                break
            if (current_cfg["jump_to"] >= 0):
                jump_i_offset = 0
                if (current_cfg["jump_to"] > timecodes[i][1]):
                    jump_i_offset = 1
                if (current_cfg["jump_to"] < timecodes[i][0]):
                    jump_i_offset = -1
                while ((current_cfg["jump_to"] > timecodes[i][1] or current_cfg["jump_to"] < timecodes[i][0]) and i >= 0 and i < chunks_len):
                    i += jump_i_offset
            json_cfg_i += 1
            if (not current_cfg["ignore"] and i < chunks_len and i >= 0):
                Iterate(i)
                iterated_once = True
            current_cfg = current_cfg | SafeDeepCopy(CFG.DEFAULT.voice_to_txt_cfg_json_reset)
        if (do_stop):
            break
        if (not iterated_once and not current_cfg["ignore"] and i < chunks_len and i >= 0):
            Iterate(i)
        if (not cfg_done_once):
            current_cfg = current_cfg | SafeDeepCopy(CFG.DEFAULT.voice_to_txt_cfg_json_reset)
        i += current_cfg["step"]
        if (i % CFG.voice_to_txt_save_after_i == CFG.voice_to_txt_save_after_i-1):
            with open(os.path.join(folder, CFG.voice_to_txt_save_file), "w") as f_save:
                json.dump({
                    "timecodes": timecodes,
                    "i": i,
                    "json_cfg_i": json_cfg_i,
                    "current_cfg": current_cfg,
                    "json_result": json_result,
                    "chunks_len": chunks_len,
                }, f_save, ensure_ascii=False, indent=4)
    with open(os.path.join(folder, CFG.voice_to_txt_json_file), "w") as f:
        json.dump(json_result, f, ensure_ascii=False, indent=4)
    with open(os.path.join(folder, CFG.voice_to_txt_done_file), "w") as f:
        pass
    if (os.path.isfile(os.path.join(folder, CFG.voice_to_txt_save_file))):
        os.remove(os.path.join(folder, CFG.voice_to_txt_save_file))
    if (CFG.voice_to_txt_delete_chunks_dir):
        for j in range(chunks_len):
            chunk_filename = os.path.join(chunks_dir_name, f"{CFG.voice_to_txt_chunk_filename}{j}.{CFG.voice_to_txt_sound_format}")
            if (os.path.isfile(chunk_filename)):
                os.remove(chunk_filename)
        try:
            os.rmdir(chunks_dir_name)
        except OSError as err:
            pass
