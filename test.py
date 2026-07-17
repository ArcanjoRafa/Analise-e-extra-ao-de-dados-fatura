import fitz
import pdfplumber
import re


pdf_fatura = r"C:\Users\rafae\Downloads\Energisa_2026-05_1.955.050.017-62.pdf"
pdf_fatura1 = r"C:\Users\rafae\Downloads\Energisa_2026-05_1.045.938.017-10.pdf"
pdf_fatura2 = r"C:\Users\rafae\Downloads\Energisa_2026-05_1.769.293.017-27.pdf"
pdf_fatura3 = r"\Users\rafae\Downloads\Energisa_2026-05_692.976.017-87.pdf"
pdf_fatura4 = r"\Users\rafae\Downloads\2026-06_1.086.801.017-46_28939221.pdf"
pdf_fatura5 = r"\Users\rafae\Downloads\2026-05_372.847.017-05_28562256.pdf"

        #Dados da UC
        # 'text': '1.955.050.017-62'
        # 'x0': 244.08, 'x1': 305.0399725254
        # 'top': 196.50056610599995

class_UC = {}
class_CLIENTE = {}

with pdfplumber.open(pdf_fatura5) as pdf:
    first_page = pdf.pages[0]
    texto = first_page.extract_text()
    words = first_page.extract_words()

    #Econtrando UC:
    match = re.search(r"\d+\.\d+\.\d+(?:\.\d+)?-\d{2}", texto)
    if match:
        UC = match.group(0)
        dados_UC = next(w for w in words if w['text'] == UC)
        class_UC['UC'] = dados_UC['text']

    #Encontrando Endereço:
    # primeiro_end = [w['text'] for w in words if abs(w['top'] - dados_UC['top']) < 3 and w['x1'] < dados_UC['x0']]
    segundo_end = [w['text'] for w in words if dados_UC['top'] < w['top']
                   <= dados_UC['top'] + 8 and w['x1'] < dados_UC['x0']]
    endereco = ' '.join(segundo_end)
    class_UC['END'] = endereco


    #encontrando CPF/CNPJ:
    # match = re.search(r"CNPJ/CPF(/RANI)?:\s*[\dX]{2}\.[\dX]{3}\.[\dX]{3}/[\dX]{4}-\d{2}",texto)
    match = re.search(r"CNPJ/CPF(/RANI)?:\s*([0-9X./-]+)", texto)
    if match:
        cpf_cnpj = match.group(0)
        class_CLIENTE['CNPJ_CPF'] = cpf_cnpj

    #Econtrando CEP:
    possiveis_ceps = []
    for w in words:
        if  len(w['text']) == 8 and 178 <= w['top'] <= 186:
         possiveis_ceps.append(w)
         cep = possiveis_ceps[-1]['text']


    #Econtrando as leituras:
    match = re.search(r"\d{2}/\d{2}/\d{4}\s+\d{2}/\d{2}/\d{4}\s+\d+\s+\d{2}/\d{2}/\d{4}", texto)
    ordem = 0
    nomes_leituras = ['leitura anterior:', 'leitura atual:', 'n dias:', 'proxima leitura:']
    leituras = {}
    if match:
        leituras_dados = match.group(0).split()
        for _ in leituras_dados:
            leituras[nomes_leituras[ordem]] = _
            ordem += 1
    ##localizacao das leituras[top]:
    for w in words:
        if w['text'] == leituras_dados[-1]:
            leituras_loc = w['top']


    #Econtrando nome cliente:
    nome1 = []
    nome2 = []
    for w in words:
        if leituras_loc - 8 <= w['top'] < leituras_loc:
            nome1.append(w['text'])
        if leituras_loc < w['top'] <= leituras_loc + 8:
            nome2.append(w['text'])
    nome2.pop(0)
    nome_completo = nome1 + nome2
    cliente = ''
    for nome in nome_completo:
        if nome == nome_completo[0]:
            cliente = nome
        else:
            cliente += ' ' + nome
    class_CLIENTE['CLIENTE'] = cliente

    #Encontrando valor fatura:
    match = re.search(r'([A-Za-zÀ-ÿ]+\s*/\s*\d{4})\s+(\d{2}/\d{2}/\d{4})\s+R\$\s*([\d.]+,\d{2})', texto)
    if match:
        valores_fat = {
            "MES_REF": match.group(1),
            "VENCIMENTO": match.group(2),
            "PAGAR": match.group(3)
        }

    #Encontrando quadro tributos:
    pdf_2 = fitz.open(pdf_fatura)
    page = pdf_2[0]
    palavras = page.get_text('words', sort = 'true')

    for p in palavras:
        if p[4] == 'PIS':
            pis_loc = p

    tributos_pis = [p[4] for p in palavras if abs(p[1] - pis_loc[1]) <= 3 and p[0] > pis_loc[2]]

    for p in palavras:
        if p[4] == 'COFINS':
            confis_loc = p

    tributos_cofins = [p[4] for p in palavras if abs(p[1] - confis_loc[1]) <= 3 and p[0] > confis_loc[2]]

    for p in palavras:
        if p[4] == 'ICMS':
            icms_loc = p

    tributos_icms = [p[4] for p in palavras if abs(p[1] - icms_loc[1]) <= 3 and p[0] > icms_loc[2]]

    #Econtrando Valores Totais:
    for p in palavras:
        if p[4] == 'TOTAL:':
            loc_total = p

    valores_totais = [p[4] for p in palavras if abs(p[1] - loc_total[1]) <= 3]

    #Econtrando Itens da fatura:
    for p in palavras:
        if p[4] == 'Itens':
            itens_fatura_loc = p

    colunas = {
        'Itens da fatura': (0, 135),
        'Unid.': (135, 180),
        'Quant.': (180, 214),
        'Preço unit c tributo': (214, 250),
        'Valor': (250, 282),
        'PIS/COFINS': (282, 318),
        'Base calc ICMS': (318, 352),
        'Aliq ICMS': (352, 380),
        'ICMS': (380, 410),
        'Tarifa unit': (410, 433)
    }

    linhas = {}
    for p in palavras:
        if itens_fatura_loc[1] + 3 < p[1] < loc_total[1] and p[0] < 433:
            y = round(p[1], 1)
            if y not in linhas:
                linhas[y] = []
            linhas[y].append(p)

    for y in linhas:
        linhas[y].sort(key=lambda p: p[0])

    ordem_colunas = [
        'Itens da fatura',
        'Unid.',
        'Quant.',
        'Preço unit c tributo',
        'Valor',
        'PIS/COFINS',
        'Base calc ICMS',
        'Aliq ICMS',
        'ICMS',
        'Tarifa unit'
    ]

    dados_fatura = []
    for y, palavras_linha in linhas.items():
        linha = {coluna: "" for coluna in colunas}

        for p in palavras_linha:
            x_meio = (p[0] + p[2]) / 2

            for coluna, (inicio, fim) in colunas.items():
                if inicio <= x_meio < fim:
                    linha[coluna] += p[4] + " "
                    break
        dados_fatura.append( [linha[coluna].strip() for coluna in ordem_colunas])

    linhas_corrigidas = []
    i = 0
    while i < len(dados_fatura):
        linha_atual = dados_fatura[i]

        # verifica se só tem descrição preenchida
        valores = [x for x in linha_atual[1:] if x != ""]
        if len(valores) == 0 and linha_atual[0] != "" and i + 1 < len(dados_fatura):
            proxima = dados_fatura[i + 1]
            nova_linha = [
                linha_atual[j] if linha_atual[j] else proxima[j]
                for j in range(len(linha_atual))
            ]
            linhas_corrigidas.append(nova_linha)
            i += 2
        else:
            linhas_corrigidas.append(linha_atual)
            i += 1

    linhas_finais = []
    for linha in linhas_corrigidas:
        if linha[0] == "":
            if linhas_finais:
                linha_anterior = linhas_finais[-1]
                for i in range(len(linha)):
                    if linha[i] != "":
                        if linha_anterior[i] == "":
                            linha_anterior[i] = linha[i]
                        else:
                            linha_anterior[i] += " " + linha[i]
            else:
                linhas_finais.append(linha)
        else:
            linhas_finais.append(linha)


    #Encontrando Medidor:
    loc_medidor = (39.0, 579.5043334960938, 69.36003112792969, 584.4683227539062)
    medidor_val = []
    medidor_group = ''
    medidor = ''
    for p in palavras:
        if abs(p[1] - loc_medidor[1]) <= 3 and p[0] == loc_medidor[0]:
           medidor_group = p[5]
           medidor = p[4]
    ##Encontrando todos os valores do medidor:
    for p in palavras:
        if p[5] == medidor_group:
            if p[6] != 7:
                if p[7] != 0:
                    medidor_val[-1] += ' ' + p[4]
                else:
                    medidor_val.append(p[4])

    print(medidor_val)



