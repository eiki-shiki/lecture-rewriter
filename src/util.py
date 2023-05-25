import os
import json
# import pkgutil

from .config import always_replace_voice_dict
from .config import CFG

def Clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)

def TryCatchSafe(default, exception, func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except exception:
        return default

def TryToCreateFolder(path):
    if not os.path.isdir(path):
        os.mkdir(path)

def GetFolderPath(path):
    return os.path.splitext(path)[0]

def GetTimeFromMs(ms, add_ms = False):
    result = ""
    y = 60*60*1000
    h = int(ms/y)
    m = int((ms-(h*y))/(y/60))
    s = int((ms-(h*y)-(m*(y/60)))/1000)
    result += str(h) + ':'
    result += str(m) + ':'
    result += str(s)
    if (add_ms):
        result += ':' + str(int(ms-(h*y)-(m*(y/60))-(s*1000))) # ms
    return result


def AlwaysReplaceVoice(s):
        tmp = s.lower()
        for key, item in always_replace_voice_dict.items():
            tmp = tmp.replace(key, item)
            if key[-1] == ' ' and len(key) > 1:
                tmp2 = "."
                if (len(item) > 1):
                    tmp2 = item[:len(item) - 1] + '.'
                tmp = tmp.replace(key[:len(key) - 1] + '.', tmp2)
        return tmp.capitalize()

def SafeDeepCopy(d):
    return json.loads(json.dumps(d))

def GetSortedFoldersFromDir(path):
    #return sorted(sorted([name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]), key=lambda f: TryCatchSafe(0xFFFFFF, ValueError, int, ''.join(filter(str.isdigit, f))))
    return GetSortedSmhIn(path, os.path.isdir)

def GetSortedFilesFromDir(path):
    #return sorted(sorted([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]), key=lambda f: TryCatchSafe(0xFFFFFF, ValueError, int, ''.join(filter(str.isdigit, f))))
    return GetSortedSmhIn(path, os.path.isfile)

def GetSortedSmhIn(path, func):
    return sorted(sorted([name for name in os.listdir(path) if func(os.path.join(path, name))]), key=lambda f: TryCatchSafe(0xFFFFFF, ValueError, int, ''.join(filter(str.isdigit, f))))

def DictGetAliases(d, *aliases, default=None):
    for a in aliases:
        try:
            return d[a]
        except KeyError:
            pass
    return default

def SortCFGJSONByTime(d):
    return sorted(d, key= lambda f: DictGetAliases(f, *CFG.time_dict_key_aliases, default=0))

def ManageConfigs(default_cfg, current_cfg, cfg_json_file, timecode):
    config_e_i = 0
    for config_e in current_cfg["configs"]:
        config_e_path = None
        if (config_e == "default"):
            tmp = current_cfg["configs"]
            current_cfg = SafeDeepCopy(default_cfg)
            current_cfg["configs"] = tmp
            config_e_i += 1
            continue
        if (os.path.isdir(config_e)):
            config_e_path = config_e
        else:
            config_e_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs", config_e)
            #config_e_path = pkgutil.get_data(__name__, os.path.join("configs", config_e, cfg_json_file))
            #print(config_e_path)
            if (not os.path.isdir(config_e_path)):
                print(timecode, "config", config_e, "not found. Ignoring...")
                config_e_i += 1
                continue
        config_e_json = None
        if (os.path.isfile(os.path.join(config_e_path, cfg_json_file))):
            with open(os.path.join(config_e_path, cfg_json_file), "r") as config_e_f:
                config_e_json = json.load(config_e_f)
            config_e_json_configs = config_e_json.pop("configs", [])
            for config_e_json_configs_i in range(len(config_e_json_configs)):
                current_cfg["configs"].insert(config_e_i + config_e_json_configs_i + 1, config_e_json_configs[config_e_json_configs_i])
            current_cfg = current_cfg | config_e_json
        else:
            print(timecode, "config", config_e, ":",os.path.join(config_e_path, cfg_json_file), "not found. Ignoring...")
        config_e_i += 1
    return current_cfg
