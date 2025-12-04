# main.py
import logging
import sys
from modules.interfaz import AppGUI
from config import LOG_FILE, LOG_LEVEL, TITULO_APP

def configurar_logging():
    numeric_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        filename=LOG_FILE,
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    # También mostrar por consola
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(numeric_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def main():
    configurar_logging()
    app = AppGUI(title=TITULO_APP)
    app.run()

if __name__ == "__main__":
    main()