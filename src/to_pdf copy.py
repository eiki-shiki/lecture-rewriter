import json

from .util import TryToCreateFolder
from .util import GetFolderPath
from .util import GetSortedFoldersFromDir

from .config import CFG

from fpdf import FPDF

def WriteEmptyLine(pdf):
    pdf.cell(0, ln=1)

def WriteParagraph(pdf, text, align='J'):
    # https://pyfpdf.readthedocs.io/en/latest/reference/cell/index.html#example
    #pdf.multi_cell(CFG.to_pdf_padding, 10)
    #pdf.multi_cell(210 - 2*CFG.to_pdf_padding, 10, txt=text, align=align, ln=1, link=link)
    pdf.multi_cell(0, 10, txt=text, align=align)
    #WriteEmptyLine(pdf)

def SetFont(pdf, format):
    pdf.set_font(*format)

class CustomPDF(FPDF):
    title_for_header = "Sample Title"
    def header(self):
        # Title
        self.set_font('Arial', '', 12)
        self.cell(30, h=10, txt=self.title_for_header, align='R')
        #self.set_font('Arial', '', 12)
        # Line break
        self.ln(20)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, h=10, txt='Page ' + str(self.page_no()) + '/{nb}', align='C')
        #self.set_font('Arial', '', 12)

def ToPdf(path):
    if (not os.path.isdir(path)):
        print(path, "is not a directory. Can't create pdf.")
        return
    paths = GetSortedFoldersFromDir(path)
    # Checks
    for p in paths:
        folder = GetFolderPath(p)
        TryToCreateFolder(folder)
        if not (os.path.isfile(os.path.join(folder, CFG.summary_json_file))):
            print(os.path.join(folder, CFG.summary_json_file), "not found. Can't create pdf.")
            return
    pdf = CustomPDF()
    screens_links = [] # store screen's page, folder, screen file name, text. Put it on the end of the pdf
    table_of_content = [] # store folder and page
    pdf.add_page()
    for p in paths:
        folder = GetFolderPath(p)
        summ_json = None
        with open(os.path.join(folder, CFG.summary_json_file), "r") as f:
            summ_json = json.load(f)
        summ_arr = summ_json["data"]
        screens_links.append({"title": summ_json["title"], "data": []})
        pdf.title_for_header = summ_json["title"]
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, txt=summ_json["title"], align='C', ln=1)
        pdf.set_font('Arial', '', 12)
        table_of_content.append({"title": summ_json["title"], "page": pdf.page_no()})
        if (summ_json["desc"] != ""):
            pdf.cell(0, txt=summ_json["desc"], ln=1)
            pdf.cell(0, ln=1)
            pdf.cell(0, ln=1)
        for sum_arr_e in summ_arr:
            if (sum_arr_e["type"] == "vid_seq"):
                screens_links[-1]["data"].append({"page": pdf.page_no(), "file": os.path.split(sum_arr_e["file"])[-1], "text": sum_arr_e["text"], "path": sum_arr_e["file"], "timeMs": sum_arr_e["timeMs"], "time": str(sum_arr_e["time"])})
                pdf.image(sum_arr_e["file"])
                pdf.set_font('Arial', 'I', 11)
                pdf.cell(0, txt=summ_json["title"] + ' ' + os.path.split(sum_arr_e["file"])[-1] + sum_arr_e["timeMs"] + ' | ' + str(sum_arr_e["time"]), align='', ln=1)
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, ln=1)
            elif (sum_arr_e["type"] == "voice_txt"):
                pdf.cell(0, txt=sum_arr_e["timeMs"][0] + '-' + sum_arr_e["timeMs"][0] + ' | ' + str(sum_arr_e["time"][0]) + '-' + str(sum_arr_e["time"][1]), ln=1)
                pdf.cell(0, txt=sum_arr_e["text"], ln=1)
                pdf.cell(0, ln=1)
        pdf.add_page()
    table_of_content.append({"title": "Текста из скриншотов", "page": pdf.page_no()})
    for screens_link in screens_links:
        #pdf.set_font('Arial', 'B', 16)
        SetFont(pdf, CFG.to_pdf_title_format)
        pdf.cell(0, txt=screens_link["title"], align='C', ln=1)
        #pdf.set_font('Arial', '', 12)
        SetFont(pdf, CFG.to_pdf_text_format)
        pdf.cell(0, ln=1)
        screens_data = screens_link["data"]
        for screens_data_e in screens_data:
            link = pdf.add_link()
            pdf.set_link(link, page=screens_data_e["page"])
            pdf.image(screens_data_e["path"], link=link)
            pdf.set_font('Arial', 'I', 11)
            pdf.cell(0, txt=screens_link["title"] + ' ' + screens_data_e["file"] + screens_data_e["timeMs"] + ' | ' + screens_data_e["time"], align='', ln=1, link=link)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, txt=screens_data_e["text"], ln=1)
            pdf.cell(0, ln=1)
        pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, txt="Содержание", align='C', ln=1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, ln=1)
    for table_of_content_e in table_of_content:
        link = pdf.add_link()
        pdf.set_link(link, page=table_of_content_e["page"])
        pdf.cell(0, txt=table_of_content_e["title"] + " [" + str(table_of_content_e["page"]) + ']', link=link, ln=1)
    pdf.output(os.path.join(path, CFG.to_pdf_file_name), 'F')
