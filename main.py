import pdfplumber
import re

n_line = 0
pdf_fatura = r"C:\Users\rafae\Downloads\Energisa_2026-05_1.955.050.017-62.pdf"
pdf_fatura2 = r"C:\Users\rafae\Downloads\Energisa_2026-05_1.769.293.017-27.pdf"


with pdfplumber.open(pdf_fatura) as pdf:
    first_page = pdf.pages[0]
    texto = first_page.extract_text(layout=True)
    words = first_page.extract_words()


    # for w in words:
    #     if  len(w['text']) == 8 and 178 <= w['top'] <= 186:
    #         cep = w['text']
    # print(cep)





