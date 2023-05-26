import json
import os

from .util import TryToCreateFolder
from .util import GetFolderPath
from .util import GetSortedFoldersFromDir

from .config import CFG

from fpdf import FPDF
import datetime

# TODO: refactor + add link to latest screenshot on footer on every page.

def WriteEmptyLine(pdf, h=5):
    #pdf.cell(0, ln=h)
    pdf.ln(h)

def WriteParagraph(pdf, text, h=5, align='J'):
    # https://pyfpdf.readthedocs.io/en/latest/reference/cell/index.html#example
    #pdf.multi_cell(CFG.to_pdf_padding, 10)
    #pdf.multi_cell(210 - 2*CFG.to_pdf_padding, 10, txt=text, align=align, ln=1, link=link)
    pdf.multi_cell(0, h, txt=text, align=align)
    #WriteEmptyLine(pdf)

def WriteLine(pdf, text, h=5, align='', link='', ln=1):
    pdf.cell(0, h=h, txt=text, align=align, link=link, ln=ln)

def SetFont(pdf, format):
    pdf.set_font(*format)

class CustomPDF(FPDF):
    title_for_header = ""
    def header(self):
        # Title
        #self.set_font('FreeMono', '', 12)
        SetFont(self, CFG.to_pdf_small_format)
        self.cell(30, h=10, txt=self.title_for_header, align='L')
        #self.set_font('FreeMono', '', 12)
        # Line break
        self.ln(15)
    
    def footer(self):
        self.set_y(-15)
        #self.set_font('FreeMono', 'I', 8)
        SetFont(self, CFG.to_pdf_page_format)
        self.cell(0, h=10, txt="Страница " + str(self.page_no()) + "/{nb}", align='C')
        #self.set_font('FreeMono', '', 12)
    
    def _putinfo(self):
        # yes im evil
        #self._out('/Producer '+self._textstring('PyFPDF '+FPDF_VERSION+' http://pyfpdf.googlecode.com/'))
        if hasattr(self,'title'):
            self._out('/Title '+self._textstring(self.title))
        if hasattr(self,'subject'):
            self._out('/Subject '+self._textstring(self.subject))
        if hasattr(self,'author'):
            self._out('/Author '+self._textstring(self.author))
        if hasattr (self,'keywords'):
            self._out('/Keywords '+self._textstring(self.keywords))
        if hasattr(self,'creator'):
            self._out('/Creator '+self._textstring(self.creator))
        self._out('/CreationDate '+self._textstring('D:'+datetime.datetime.now().strftime('%Y%m%d%H%M%S')))

def ToPdf(path):
    print("to_pdf")
    if (not os.path.isdir(path)):
        print(path, "is not a directory. Can't create pdf.")
        return
    paths = GetSortedFoldersFromDir(path)
    # Checks
    for p in paths:
        folder = GetFolderPath(os.path.join(path, p))
        TryToCreateFolder(folder)
        if (not os.path.isfile(os.path.join(folder, CFG.summary_json_file))):
            print(os.path.join(folder, CFG.summary_json_file), "not found.", "Skipping...")
            paths.remove(p)
    
    if (len(p) == 0):
        print("All", CFG.summary_json_file, "are not found. Can't create pdf.")
        return
    
    pdf = CustomPDF()

    #pdf.add_font("FreeMono", '', CFG.PATH.free_mono_font, True)
    #pdf.add_font("FreeMono", 'B', CFG.PATH.free_mono_bold_font, True)
    #pdf.add_font("FreeMono", 'I', CFG.PATH.free_mono_italic_font, True)

    pdf.add_font("FreeSans", '', CFG.PATH.free_sans_font, True)
    pdf.add_font("FreeSans", 'B', CFG.PATH.free_sans_bold_font, True)
    pdf.add_font("FreeSans", 'I', CFG.PATH.free_sans_italic_font, True)

    #pdf.add_font("FreeSerif", '', CFG.PATH.free_serif_font, True)
    #pdf.add_font("FreeSerif", 'B', CFG.PATH.free_serif_bold_font, True)
    #pdf.add_font("FreeSerif", 'I', CFG.PATH.free_serif_italic_font, True)

    screens_links = [] # store screen's page, folder, screen file name, text. Put it on the end of the pdf
    table_of_content = [] # store folder and page
    pdf.add_page()
    for p in paths:
        folder = GetFolderPath(os.path.join(path, p))
        summ_json = None
        with open(os.path.join(folder, CFG.summary_json_file), "r") as f:
            summ_json = json.load(f)
        summ_arr = summ_json["data"]
        screens_links.append({"title": summ_json["title"], "data": []})
        pdf.title_for_header = summ_json["title"]
        SetFont(pdf, CFG.to_pdf_title_format)
        pdf.cell(0, 5, txt=summ_json["title"], align='C', ln=1)
        pdf.cell(0, 5, ln=1)
        SetFont(pdf, CFG.to_pdf_text_format)
        table_of_content.append({"title": summ_json["title"], "page": pdf.page_no()})
        if (summ_json["desc"] != ""):
            WriteParagraph(pdf, summ_json["desc"])
        #WriteEmptyLine(pdf, 2)
        for sum_arr_e in summ_arr:
            if (sum_arr_e["type"] == "vid_seq"):
                screens_links[-1]["data"].append({"page": pdf.page_no(), "file": os.path.split(sum_arr_e["file"])[-1], "text": sum_arr_e["text"], "path": os.path.join(folder, sum_arr_e["file"]), "timeMs": str(sum_arr_e["timeMs"]), "time": str(sum_arr_e["time"])})
                pdf.image(os.path.join(folder, sum_arr_e["file"]), w=CFG.to_pdf_image_width)
                SetFont(pdf, CFG.to_pdf_small_format)
                pdf.cell(0, 5, txt='[' + summ_json["title"] + '/' + os.path.split(sum_arr_e["file"])[-1] + ' | ' + str(sum_arr_e["timeMs"]) + ' | ' + str(sum_arr_e["time"]) + ']', align='C', ln=1)
                SetFont(pdf, CFG.to_pdf_text_format)
                pdf.cell(0, 5, ln=1)
                #WriteEmptyLine(pdf)
            elif (sum_arr_e["type"] == "voice_txt"):
                SetFont(pdf, CFG.to_pdf_small_format)
                pdf.cell(0, 5, txt='[' + str(sum_arr_e["index"]) + ' | ' + str(sum_arr_e["timeMs"][0]) + '-' + str(sum_arr_e["timeMs"][1]) + ' | ' + str(sum_arr_e["time"][0]) + '-' + str(sum_arr_e["time"][1]) + ']', align='C', ln=1)
                SetFont(pdf, CFG.to_pdf_text_format)
                WriteParagraph(pdf, sum_arr_e["text"])
                WriteEmptyLine(pdf)
        pdf.title_for_header = ""
        pdf.add_page()
    table_of_content.append({"title": "Текста из скриншотов", "page": pdf.page_no()})
    SetFont(pdf, CFG.to_pdf_title_format)
    pdf.cell(0, 5, txt=table_of_content[-1]["title"], align='C', ln=1)
    SetFont(pdf, CFG.to_pdf_text_format)
    WriteEmptyLine(pdf)
    for screens_link in screens_links:
        SetFont(pdf, CFG.to_pdf_title_format)
        pdf.cell(0, 5, txt=screens_link["title"], align='C', ln=1)
        SetFont(pdf, CFG.to_pdf_text_format)
        WriteEmptyLine(pdf)
        pdf.title_for_header = "Текста из скриншотов: " + screens_link["title"]
        table_of_content.append({"title": pdf.title_for_header, "page": pdf.page_no()})
        screens_data = screens_link["data"]
        for screens_data_e in screens_data:
            link = pdf.add_link()
            pdf.set_link(link, page=screens_data_e["page"])
            pdf.image(screens_data_e["path"], link=link, w=CFG.to_pdf_image_width)
            SetFont(pdf, CFG.to_pdf_small_format)
            pdf.cell(0, 5, txt='[' + screens_link["title"] + '/' + screens_data_e["file"] + ' | ' + screens_data_e["timeMs"] + ' | ' + screens_data_e["time"] + ']', align='', ln=1, link=link)
            SetFont(pdf, CFG.to_pdf_text_format)
            WriteParagraph(pdf, screens_data_e["text"])
            WriteEmptyLine(pdf)
        if (not screens_link is screens_links[-1]):
            pdf.title_for_header = "Текста из скриншотов"
        else:
            pdf.title_for_header = ""
        pdf.add_page()
    SetFont(pdf, CFG.to_pdf_title_format)
    pdf.cell(0, 5, txt="Содержание", align='C', ln=1)
    SetFont(pdf, CFG.to_pdf_text_format)
    WriteEmptyLine(pdf)
    pdf.title_for_header = "Содержание"
    table_of_content.append({"title": pdf.title_for_header, "page": pdf.page_no()})
    for table_of_content_e in table_of_content:
        link = pdf.add_link()
        pdf.set_link(link, page=table_of_content_e["page"])
        SetFont(pdf, CFG.to_pdf_text_format)
        pdf.cell(0, 5, txt=table_of_content_e["title"] + " [" + str(table_of_content_e["page"]) + ']', link=link, ln=1)
        WriteEmptyLine(pdf)
    pdf.alias_nb_pages()
    pdf.output(os.path.join(path, CFG.to_pdf_file_name), 'F')
