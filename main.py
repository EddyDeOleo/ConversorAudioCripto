##
# @file main.py
# @brief Punto de entrada principal de la aplicación Conversor de Audio a Texto con Encriptación.
#
# Este módulo inicializa el sistema de logging, configura el registro tanto en
# archivo como en consola, y lanza la interfaz gráfica principal (AppGUI).
#
# @details
# - Configura el registro en `logs/app.log` usando los parámetros definidos en `config.py`.
# - Agrega un manejador adicional para mostrar los logs en la consola.
# - Crea y ejecuta la interfaz gráfica principal.
#
# @see AppGUI (modules/interfaz.py)
# @see config.py (parámetros globales)
#
# @date 2025
# @version 1.0
# @author Eddy
##

import logging
import sys
from modules.interfaz import AppGUI
from config import LOG_FILE, LOG_LEVEL, TITULO_APP

# =====================================================================
# CONFIGURACIÓN DE LOGGING
# =====================================================================

def configurar_logging():
    """
    @brief Configura el sistema de logging global de la aplicación.
    
    - Escribe logs en el archivo definido en LOG_FILE.
    - También envía los logs a la consola.
    - El nivel de log proviene de LOG_LEVEL.
    """
    # Obtener el nivel numérico (INFO, DEBUG, ERROR...) desde el texto
    numeric_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    # Configuración básica del logging (archivo)
    logging.basicConfig(
        filename=LOG_FILE,
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Crear un handler adicional para imprimir logs en consola
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(numeric_level)

    # Formato del mensaje en consola
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)

    # Añadir el handler de consola al logger raíz
    logging.getLogger('').addHandler(console)


# =====================================================================
# FUNCIÓN PRINCIPAL
# =====================================================================

def main():
    """!
    @brief Inicia la aplicación completa.
    
    A continuación, se presenta el Diagrama de Secuencia para el proceso clave de Conversión y Encriptación.
    
    @startuml
    title Escenario: Conversión y Encriptación de Audio
    
    actor Usuario
    participant AppGUI as "interfaz.py"
    participant AudioConverter as "audio_converter.py"
    participant CryptoEngine as "encriptacion.py"
    participant Storage as "storage.py"
    
    Usuario -> AppGUI : click_en_Convertir(ruta_audio)
    
    AppGUI -> AudioConverter : cargar_y_analizar(ruta_audio)
    activate AudioConverter
    AudioConverter -> AudioConverter : convertir_a_texto()
    return texto_plano, metadata_audio
    deactivate AudioConverter
    
    AppGUI -> CryptoEngine : encriptar_texto(texto_plano, CLAVE_FERNET)
    activate CryptoEngine
    return texto_encriptado
    deactivate CryptoEngine
    
    AppGUI -> Storage : guardar_registro(texto_encriptado, datos_raw, metadata_audio)
    activate Storage
    Storage -> Storage : escribir_en_json(conversiones.json)
    return Registro_Guardado
    deactivate Storage
    
    AppGUI -> Usuario : notificacion_Exito()
    @enduml
    
    - Configura logging.
    - Instancia la interfaz gráfica.
    - Ejecuta el loop principal de Tkinter.
    """
    configurar_logging()
    
    # Crear la interfaz gráfica principal
    app = AppGUI(title=TITULO_APP)

    # Lanzar la interfaz (mainloop)
    app.run()


# =====================================================================
# EJECUCIÓN DIRECTA
# =====================================================================

if __name__ == "__main__":
    main()