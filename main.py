import os
from scripts.parser import parser

"""
Este el archivo principal en el que se genera el archivo html a partir
de la función de parser que contiene toda la lógica necesaria para 
leer el input (txt), 'interpretar', y generar el output (html).
"""

ruta_html = os.path.join(os.getcwd())

# Solamente por debug: ruta objetivo en donde se guardará el html.
print(f"RUTA HTML OBJETIVO: {ruta_html}")

# Emplea el programa.
parser(ruta_html=ruta_html, nombre_html="resalta_sintaxis")
