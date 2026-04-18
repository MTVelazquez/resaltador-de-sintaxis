# =============================================================================
# parser.py - Analizador Sintáctico (Parser)
# Implementación mediante Descenso Recursivo
# Reconoce programas del lenguaje tipo LISP/SCHEME usando la gramática:
#
#   <prog>      ::= <exp> <prog> | $
#   <exp>       ::= <atomo> | <lista>
#   <atomo>     ::= simbolo | <constante>
#   <constante> ::= numero | booleano | string
#   <lista>     ::= ( <elementos> )
#   <elementos> ::= <exp> <elementos> | vacio
#
# Los tokens son proporcionados por el scanner (obten_token.py).
# Al finalizar genera un archivo HTML con la sintaxis resaltada.
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
from . import obten_token as scanner

# Token actual
token = None

# Variable global para guardar la ruta destino del HTML
ruta_destino_html = "resalta_sintaxis.html"

# ===================== EMPATE DE TOKENS ======================================

def match(tokenEsperado):
    """Empata el token actual con el esperado y avanza al siguiente.
    Si no coincide, reporta error sintactico.
    Si el nuevo token es ERR, reporta error lexico."""
    global token
    if token == tokenEsperado:
        token = scanner.obten_token()
        if token == scanner.ERR:
            error_lexico()
    else:
        error_sintactico()

# ===================== REGLAS DE LA GRAMATICA ================================

# <prog> ::= <exp> <prog> | $
def prog():
    """Reconoce un programa: secuencia de expresiones terminada en $."""
    if token == scanner.END:
        return  # se alcanzo el fin de entrada $
    else:
        exp()
        prog()

# <exp> ::= <atomo> | <lista>
def exp():
    """Reconoce una expresion: atomo o lista."""
    if token in (scanner.SYM, scanner.NUM, scanner.BOOL, scanner.STR):
        atomo()
    elif token == scanner.LRP:
        lista()
    else:
        error_sintactico()

# <atomo> ::= simbolo | <constante>
def atomo():
    """Reconoce un atomo: simbolo o constante."""
    if token == scanner.SYM:
        match(scanner.SYM)
    else:
        constante()

# <constante> ::= numero | booleano | string
def constante():
    """Reconoce una constante: numero, booleano o string."""
    if token == scanner.NUM:
        match(scanner.NUM)
    elif token == scanner.BOOL:
        match(scanner.BOOL)
    elif token == scanner.STR:
        match(scanner.STR)
    else:
        error_sintactico()

# <lista> ::= ( <elementos> )
def lista():
    """Reconoce una lista: parentesis con elementos dentro."""
    match(scanner.LRP)
    elementos()
    match(scanner.RRP)

# <elementos> ::= <exp> <elementos> | vacio
def elementos():
    """Reconoce los elementos de una lista (0 o mas expresiones)."""
    if token in (scanner.SYM, scanner.NUM, scanner.BOOL, scanner.STR, scanner.LRP):
        exp()
        elementos()
    # si no, es la produccion vacia (epsilon)

# ===================== GENERACION DE HTML ====================================

def generar_html():
    """Escribe el archivo HTML completo con la sintaxis resaltada."""
    html = ('<!DOCTYPE html>\n<html lang="es">\n<head>\n'
            '    <meta charset="UTF-8">\n'
            '    <title>Resaltador de Sintaxis</title>\n'
            '    <link rel="stylesheet" href="resalta_sintaxis.css">\n'
            '</head>\n<body>\n<pre>' + scanner.get_html() + '</pre>\n'
            '</body>\n</html>\n')
    
    with open(ruta_destino_html, "w", encoding="utf-8") as f:
        f.write(html)

# ===================== MANEJO DE ERRORES =====================================

def error_lexico():
    # Agrega leyenda de error lexico al HTML, genera el archivo y aborta.
    info = scanner.escape_html(scanner.error_info.strip())
    scanner.add_html(' <span class="error-msg">==&gt; error de l\u00e9xico en ' + info + '</span>')
    generar_html()
    sys.exit(1)

def error_sintactico():
    # Agrega leyenda de error sintactico al HTML, genera el archivo y aborta.
    info = scanner.escape_html(scanner.lexema.strip())
    scanner.add_html(' <span class="error-msg">==&gt; error de sint\u00e1xis en ' + info + '</span>')
    generar_html()
    sys.exit(1)

# ===================== FUNCION PRINCIPAL =====================================

def parser(ruta_html: str = ".", nombre_html: str = "resalta_sintaxis"):
    global ruta_destino_html
    ruta_destino_html = os.path.join(ruta_html, f"{nombre_html}.html")

    nomb_documento = "documento.txt"
    ruta_documento = os.path.normpath(os.path.join(os.getcwd(), "docs", nomb_documento))
    scanner.set_documento_input(ruta_documento, True)

    """Funcion principal: inicia el analisis lexico-sintactico y genera HTML."""
    global token
    token = scanner.obten_token()   # obtener el primer token
    if token == scanner.ERR:
        error_lexico()
    prog()                          # iniciar reconocimiento del programa
    if token != scanner.END:
        error_sintactico()
    
    scanner.set_documento_input("", False)
    generar_html()                  # escribir el archivo HTML final

if __name__ == "__main__":
    parser()
