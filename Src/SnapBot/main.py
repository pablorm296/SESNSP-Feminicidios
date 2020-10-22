from SnapBot.Bot import SnapBot

import logging

logging.basicConfig(level = logging.INFO)

# Define snapbot
myBot = SnapBot("https://www.gob.mx/sesnsp/articulos/informacion-sobre-violencia-contra-las-mujeres-incidencia-delictiva-y-llamadas-de-emergencia-9-1-1-febrero-2019", "/srv/SESNSP/Data")

# Get fullpage
myBot.getFullPage()

# Get document
myBot.getDocument()