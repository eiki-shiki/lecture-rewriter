import os

src_abs_path = os.path.dirname(os.path.abspath(__file__))

class CFG:
    #special_seq_at_txt = "<-!->"
    voice_to_txt_save_after_i = 6
    time_dict_key_aliases = ["t", "time"]
    voice_to_txt_json_file = "voice_to_txt.json"
    voice_to_txt_done_file = "voice_to_txt.json.done"
    voice_to_txt_cfg_json_file = "voice_to_txt.cfg.json"
    voice_to_txt_save_file = "voice_to_txt.save.json"
    vid_seq_to_txt_json_file = "vid_seq_to_txt.json"
    vid_seq_to_txt_done_file = "vid_seq_to_txt.json.done"
    vid_seq_to_txt_cfg_json_file = "vid_seq_to_txt.cfg.json"
    vid_seq_to_txt_save_file = "vid_seq_to_txt.save.json"
    summary_json_file = "summary.json"
    summary_done_file = "summary.json.done"
    summary_cfg_json_file = "summary.cfg.json" # TODO: Implement
    to_pdf_cfg_json_file = "to_pdf.cfg.json" # TODO: Implement
    to_pdf_done_file = "Document.pdf.done" # TODO: Implement
    vid_seq_to_txt_screens_dir = "screens"
    vid_seq_to_txt_screens_format = "jpg"
    vid_seq_to_txt_delete_screens_dir = False
    voice_to_txt_sound_format = "wav"
    voice_to_txt_chunks_dir = "audio-chunks"
    voice_to_txt_chunk_filename = "chunk"
    voice_to_txt_delete_chunks_dir = True
    to_pdf_file_name = "Document.pdf"
    to_pdf_padding = 0
    to_pdf_text_format = ['FreeSans', '', 12]
    to_pdf_title_format = ['FreeSans', 'B', 16]
    to_pdf_small_format = ['FreeSans', 'I', 8]
    to_pdf_page_format = ['FreeSans', 'I', 8]
    to_pdf_image_width = 175
    to_pdf_text_height = 5

    class DEFAULT:
        vid_seq_to_txt_cfg_json = {
            "//": "", # Reserved for comments ; Does nothing
            "configs": [], # Default, should be reseted. Order matters
            "force": False, # Default, should be reseted
            "jump": 0, # Default, should be reseted ; takes priority over jump_to
            "jump_to": -1, # Default, should be reseted ; if jump_to < 0: ignore
            "ignore": False, # Default, should be reseted ; affects jump and jump_to and affects everything. If False and jump (jump_to), on jump iteration will do job
            "tesseract_args": "-l rus+eng", # Default
            "crop": [0, 0, 0, 0], # if crop[2] is 0 then video.width, if crop[3] is 0 then video.height
            "crop_tess": [0, 0, 0, 0], # crop -> crop_rel -> crop_tess
            "crop_scrn": [0, 0, 0, 0], # crop -> crop_rel -> crop_scrn
            "crop_rel": [0, 0, 0, 0], # crop -> crop_rel
            "crop_tess_rel": [0, 0, 0, 0], # crop -> crop_rel -> crop_tess -> crop_tess_rel
            "crop_scrn_rel": [0, 0, 0, 0], # crop -> crop_rel -> crop_scrn -> crop_scrn_rel
            "max_text_difference_ratio": 0.85, # 0.0 < x < 1.0
            "step": 3000, # ms, int ; if step <= 0: unexpected results
            "stop": False, # The name says everything. If True then finishes.
        }
        vid_seq_to_txt_cfg_json_reset = { # resets after each step
            "configs": [],
            "force": False,
            "jump": 0,
            "jump_to": -1,
            "ignore": False,
        }
        voice_to_txt_cfg_json = {
            "//": "", # Reserved for comments ; Does nothing
            "min_silence_len": 1500, # Uses only once at time = 0. After time > 0 is ignored. Affects split_on_silence()!
            "silence_thresh": -16, # Uses only once at time = 0. After time > 0 is ignored. Affects split_on_silence()!
            "keep_silence": 200, # Uses only once at time = 0. After time > 0 is ignored. Affects split_on_silence()!
            "add_volume_before": 0, # Relative to the existing volume. Uses only once at time = 0. After time > 0 is ignored. Affects split_on_silence()!
            "add_volume": 0, # Relative to add_volume_before. Doesn't stack with others add_volume. DOESN'T affect split_on_silence()!
            "add_volume_rel": 0, # Relative to add_volume. Doesn't stack with others add_volume_rel. DOESN'T affect split_on_silence()!
            "language": "ru-RU", # Default
            # "jump": 0, # Not supported
            "jump_to": -1, # Default, should be reseted ; if jump_to < 0: ignore
            "ignore": False, # Default, should be reseted ; if jump (jump_to), after jump will be ignored
            "configs": [], # Default, should be reseted. Order matters
            "step": 1, # Default ; Only use 1 (to go from start to end) or -1 with jump_to to the end (so it will go from end to start), otherwise don't change it because step is not about the time but chunks index.
            "stop": False, # The name says everything. If True then finishes.
        }
        voice_to_txt_cfg_json_reset = { # resets after each step
            "configs": [],
            # "jump": 0, # Not supported
            "jump_to": -1,
            "ignore": False,
        }
        summary_cfg_json = { # Don't use time, use only once
            "//": "", # Reserved for comments ; Does nothing
            "configs": [],
            "title": None,
            "desc": "",
        }
    class PATH:
        free_mono_font = os.path.join(src_abs_path, "assets", "fonts", "FreeFont", "FreeMono.ttf")
        free_mono_bold_font = os.path.join(src_abs_path, "assets", "fonts", "FreeFont", "FreeMonoBold.ttf")
        free_mono_italic_font = os.path.join(src_abs_path, "assets", "fonts", "FreeFont", "FreeMonoOblique.ttf")

        free_sans_font = os.path.join(src_abs_path, "assets", "fonts", "FreeFont", "FreeSans.ttf")
        free_sans_bold_font = os.path.join(src_abs_path, "assets", "fonts", "FreeFont", "FreeSansBold.ttf")
        free_sans_italic_font = os.path.join(src_abs_path, "assets", "fonts", "FreeFont", "FreeSansOblique.ttf")

        free_serif_font = os.path.join(src_abs_path, "assets", "fonts", "FreeFont", "FreeSerif.ttf")
        free_serif_bold_font = os.path.join(src_abs_path, "assets", "fonts", "FreeFont", "FreeSerifBold.ttf")
        free_serif_italic_font = os.path.join(src_abs_path, "assets", "fonts", "FreeFont", "FreeSerifItalic.ttf")

always_replace_voice_dict = {
    "с++": "C++",
    "с+": "C++",
    "c+": "C++",
    "c++": "C++",
    " э ": " ",
    " эм ": " ",
    "=": "равно",
    " +": " плюс",
    # " - ": " минус ", # Bad idea
    "*": "умножить",
    "/": "делить",
    " алу ": " ALU ",
}
