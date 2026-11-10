"""Regras de classificação das respostas de objetivo (onboarding) usadas nas personas da S5.

Fonte única das regras; não lê dados. Recebe texto e devolve classificação.

Definições (para reprodução):
- Normalização: sem acentos, minúsculas, espaços colapsados (`norm`).
- Estado da resposta (`estado_objetivo`):
    "nulo"          campo vazio ou só espaços;
    "sem conteúdo"  resposta normalizada na lista SEM_CONTEUDO, ou com menos de 3 caracteres alfanuméricos;
    "com conteúdo"  qualquer outra.
  Denominador dos percentuais de tema = respostas "com conteúdo" (nulos e "sem conteúdo" ficam de fora).
- Tema principal (`tema_principal`): UM tema por resposta, o primeiro que casar na ordem de TEMAS
  (companhia/social > mente/bem-estar > saúde clínica > desempenho > estética/peso).
  Sem casamento: "não classificado" (em geral erros de digitação, como "secar ab arriga").
  Como o tema é único, os percentuais por segmento somam 100% entre as respostas com conteúdo.
- Meta com data (`meta_com_data`): SINALIZADOR À PARTE, que pode coexistir com qualquer tema
  (verão, casamento, formatura, viagem, meses, "daqui N meses", data dd/mm, prova, apresentação).
  Os percentuais de meta com data NÃO somam com os de tema.
- As respostas seguem cerca de 35 frases-modelo (mais variações com data, quilos e erros de digitação).
  As regras foram montadas a partir das respostas distintas mais frequentes de onboarding.csv.

Diferença conhecida: a lista de "sem conteúdo" daqui também descarta respostas com menos de 3 caracteres
alfanuméricos e não inclui o emoji; a de preparar_diagnostico_s5.py usa só a lista fixa (inclui "😂" e "não sei").
"""
import re
import unicodedata

SEM_CONTEUDO = {"nada", ".", "x", "ok", "-", "sla", "kkkk", "asdf", "nao sei", "ñ sei", "..."}

# a ordem é a prioridade
TEMAS = {
    "companhia / social": r"galera|pessoal do trabalho|grupo|namorad|amiga me chamou|companhia",
    "mente / bem-estar": r"momento so meu|celular|dormir|dorimr|desligar a cabeca|ansiedade|saude mental|feel better",
    "saúde clínica": r"colesterol|coletserol|saude, to sed|sedentario|dor nas costas|disposicao|pressao|prsesao|medico|stay healthy",
    "desempenho": r"correr mais|pedal|evoluir na corrida|pace|planilha|10k|5k|meia maratona|half marathon|prova de",
    "estética / peso": r"peso|barriga|forma de novo|emagrec|definir o corpo|defniir|perder|lose weight|get fit|verao|espelho|kg",
}
META_DATA = r"verao|casamento|formatura|viagem|dezembro|janeiro|fevereiro|daqui|fim do ano|\d/\d|prova de|investidores|apresentacao"
NAO_CLASSIFICADO = "não classificado"


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().strip()
    return re.sub(r"\s+", " ", s)


def estado_objetivo(x):
    if x is None or (isinstance(x, float) and x != x) or not str(x).strip() or str(x).strip().lower() == "nan":
        return "nulo"
    t = norm(x)
    if t in SEM_CONTEUDO or len(re.sub(r"[^a-z0-9]", "", t)) < 3:
        return "sem conteúdo"
    return "com conteúdo"


def tema_principal(texto_normalizado):
    for tema, rx in TEMAS.items():
        if re.search(rx, texto_normalizado):
            return tema
    return NAO_CLASSIFICADO


def meta_com_data(texto_normalizado):
    return bool(re.search(META_DATA, texto_normalizado))
