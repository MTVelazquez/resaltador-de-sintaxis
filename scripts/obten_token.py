# =============================================================================
# obten_token.py - Analizador Léxico (Scanner)
# Implementación mediante AFD con Matriz de Transiciones
# Reconoce los elementos léxicos de un lenguaje tipo LISP/SCHEME:
#   numero, simbolo, booleano, string, parentesis y fin de entrada ($)
#
# Autores: Marcelo Treviño Velazquez  - A01286389
#          Ilan David Narváez Martínez - A01412672
#          Ringo Emiliano Garcia Gastelum - A01743951
#
# Materia: TC2037 Implementación de Métodos Computacionales
# Actividad 3.2 - Resaltador de Sintaxis
# =============================================================================

import os
import sys

# ---- Documento de entrada a Leer ----

# Placeholder para guardar el documento.
doc = None

"""
Esta función se encarga de cargar el documento "input" de la cual
se realizará el análisis léxico.
"""
def set_documento_input(doc_ruta: str = "", tener_abierto: bool = True):
    global doc
    if tener_abierto:
        try:
            doc = open(doc_ruta, 'r', encoding='utf-8')
            print(f"El archivo {os.path.split(doc_ruta)[1]} ha sido cargado!")
        except FileNotFoundError as fnfe:
            print(f"El documento no pudo ser leído, razón:\n{fnfe}")
            sys.exit(1)
    else:
        if doc is not None:
            doc.close()

# ---- Tipos de token (estados aceptores del AFD) ----
NUM  = 100   # numero: 1+ digitos
SYM  = 101   # simbolo: 1+ letras minusculas
BOOL = 102   # booleano: #t o #f
STR  = 103   # string: caracteres entre comillas dobles
LRP  = 104   # parentesis izquierdo (
RRP  = 105   # parentesis derecho )
END  = 106   # fin de entrada $
ERR  = 200   # error lexico

# ---- Variables globales del scanner ----
html_body  = ""    # contenido HTML acumulado
lexema     = ""    # lexema del token actual
c          = ""    # caracter leido
leer       = True  # True = leer nuevo caracter, False = reusar actual
error_info = ""    # texto que causo el error (para mensajes especificos)

# ---- Matriz de Transiciones del AFD ----
# Estados no finales:
#   0 = inicial
#   1 = leyendo digitos (numero)
#   2 = se leyo # (inicio de booleano)
#   3 = se leyo #t o #f (booleano completo)
#   4 = dentro de string (despues de " de apertura)
#   5 = leyendo letras minusculas (simbolo)
#
# Columnas (categorias de caracter):
#   0:dig  1:letra  2:t  3:f  4:#  5:"  6:(  7:)  8:$  9:espacio  10:newline  11:otro
MT = [
    [   1,    5,    5,    5,    2,    4, LRP,  RRP, END,    0,    0,  ERR],  # 0: inicial
    [   1,  NUM,  NUM,  NUM,  NUM,  NUM, NUM,  NUM, NUM,  NUM,  NUM,  ERR],  # 1: numero
    [ ERR,  ERR,    3,    3,  ERR,  ERR, ERR,  ERR, ERR,  ERR,  ERR,  ERR],  # 2: despues de #
    [BOOL, BOOL, BOOL, BOOL, BOOL, BOOL,BOOL, BOOL,BOOL, BOOL, BOOL,  ERR],  # 3: #t o #f
    [   4,    4,    4,    4,  ERR,  STR, ERR,  ERR, ERR,    4,  ERR,  ERR],  # 4: string
    [ SYM,    5,    5,    5,  SYM,  SYM, SYM,  SYM, SYM,  SYM,  SYM,  ERR],  # 5: simbolo
]

def filtro(c):
    """Clasifica un caracter en su columna de la matriz de transiciones."""
    if c.isdigit():                    return 0   # digito
    elif c == 't':                     return 2   # t (especial para booleano)
    elif c == 'f':                     return 3   # f (especial para booleano)
    elif c.islower():                  return 1   # otra letra minuscula
    elif c == '#':                     return 4   # inicio de booleano
    elif c == '"' or c == '\u201c' or c == '\u201d':  return 5   # comilla doble (recta o tipografica)
    elif c == '(':                     return 6   # parentesis izquierdo
    elif c == ')':                     return 7   # parentesis derecho
    elif c == '$':                     return 8   # fin de entrada
    elif c == ' ' or c == '\t':        return 9   # espacio o tabulador
    elif c == '\n' or c == '\r':       return 10  # salto de linea
    else:                              return 11  # caracter ilegal

def escape_html(text):
    # Escapa caracteres especiales para insertar en HTML.
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def obten_token():
    """Lee caracteres de la entrada estandar y retorna el siguiente token.
    Simultaneamente genera el HTML resaltado en html_body."""
    global html_body, lexema, c, leer, error_info

    edo = 0
    lexema = ""

    # Ciclo del AFD: avanzar mientras el estado no sea aceptor
    while edo < 100:
        if leer:
            c = doc.read(1)
            # c = sys.stdin.read(1)
            if not c:  # fin de archivo
                return END
        else:
            leer = True

        edo = MT[edo][filtro(c)]

        if edo == 0:
            # Estado inicial con espacio en blanco: preservar en HTML
            html_body += escape_html(c)
        elif edo < 100:
            # Estado intermedio: acumular caracter en el lexema
            lexema += c

    # Procesar token aceptado y generar su HTML con la clase CSS correspondiente
    if edo == NUM:
        leer = False  # el caracter que causo la aceptacion no es parte del numero
        html_body += '<span class="numero">' + escape_html(lexema) + '</span>'
    elif edo == SYM:
        leer = False  # el caracter que causo la aceptacion no es parte del simbolo
        html_body += '<span class="simbolo">' + escape_html(lexema) + '</span>'
    elif edo == BOOL:
        leer = False  # el delimitador no es parte del booleano
        html_body += '<span class="booleano">' + escape_html(lexema) + '</span>'
    elif edo == STR:
        lexema += c  # incluir la comilla de cierre en el lexema
        html_body += '<span class="string">' + escape_html(lexema) + '</span>'
    elif edo == LRP:
        lexema = c
        html_body += '<span class="parentesis">' + escape_html(c) + '</span>'
    elif edo == RRP:
        lexema = c
        html_body += '<span class="parentesis">' + escape_html(c) + '</span>'
    elif edo == END:
        lexema = c
        html_body += '<span class="fin">' + escape_html(c) + '</span>'
    elif edo == ERR:
        # Determinar que mostrar en el mensaje de error:
        # Si c es espacio/delimitador, el problema es el lexema incompleto (ej: # sin t/f)
        # Si c es otro caracter, ese caracter es el problema (ej: @ dentro de string)
        if c.strip() == '' or c in ('(', ')', '$'):
            error_info = lexema.strip()
        else:
            error_info = c
        html_body += '<span class="error">' + escape_html(lexema + c) + '</span>'

    return edo

def get_html():
    """Retorna el HTML acumulado durante el analisis lexico."""
    return html_body

def add_html(text):
    """Agrega texto al HTML (usado por el parser para mensajes de error)."""
    global html_body
    html_body += text