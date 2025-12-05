##
# @file storage.py
# @brief Configuración central del proyecto: rutas, claves, parámetros y validaciones.
#
# Este módulo define toda la configuración global necesaria para el funcionamiento
# del Conversor de Audio a Texto con Encriptación.  
# Contiene:
# - Configuración de almacenamiento local (carpetas y JSON).
# - Clave Fernet para encriptación.
# - Parámetros de reconocimiento de voz.
# - Configuración de interfaz gráfica.
# - Mensajes estándar.
# - Parámetros de logging.
# - Función para validar que la configuración inicial esté correcta.
#
# @author Eddie
# @version 1.0
# @date 2025
##

import os
from cryptography.fernet import Fernet

# =====================================================================
# ALMACENAMIENTO: ARCHIVOS JSON
# =====================================================================

USAR_BASE_DATOS = False  
# Indica si el sistema usará base de datos en vez de archivos JSON.


# =====================================================================
# 🔐 CLAVE DE ENCRIPTACIÓN FERNET
# =====================================================================
# IMPORTANTE: Esta clave NO debe generarse automáticamente.  
# Debe ser fija y mantenerse privada.

# Clave Fernet utilizada para encriptar y desencriptar los textos y metadatos.
FERNET_KEY = b'Xq_q2WzLdBTIwyMGCxwZDLXDFPOqcLro5z4gaWn-0mk='


# =====================================================================
# RUTAS DEL PROYECTO
# =====================================================================

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Carpetas internas del sistema
AUDIOS_DIR = os.path.join(BASE_DIR, 'audios')
DATOS_DIR = os.path.join(BASE_DIR, 'datos')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Se crean automáticamente si no existen
os.makedirs(AUDIOS_DIR, exist_ok=True)
os.makedirs(DATOS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Archivo donde se registran las conversiones (encriptadas)
ARCHIVO_CONVERSIONES = os.path.join(DATOS_DIR, 'conversiones.json')


# =====================================================================
# CONFIGURACIÓN DE AUDIO
# =====================================================================

# Extensiones permitidas para conversión
FORMATOS_PERMITIDOS = ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.wma', '.aac']

# Tamaño máximo del audio aceptado
TAMANO_MAX_MB = 50


# =====================================================================
# SPEECH RECOGNITION
# =====================================================================

IDIOMA_RECONOCIMIENTO = 'es-ES'  # Idioma para Google Speech API
TIMEOUT_RECONOCIMIENTO = 10      # Tiempo máximo antes de cancelar
MOTOR_RECONOCIMIENTO = 'google'  # Motor utilizado


# =====================================================================
# INTERFAZ GRÁFICA
# =====================================================================

TITULO_APP = "Conversor de Audio a Texto con Encriptación"
ANCHO_VENTANA = 1100
ALTO_VENTANA = 800

# Paleta de colores de la interfaz
COLOR_PRIMARIO = "#2c3e50"
COLOR_SECUNDARIO = "#3498db"
COLOR_EXITO = "#27ae60"
COLOR_ERROR = "#e74c3c"
COLOR_WARNING = "#f39c12"
COLOR_FONDO = "#ecf0f1"
COLOR_TEXTO = "#2c3e50"
COLOR_BLANCO = "#ffffff"

# Fuentes estándar utilizadas en la UI
FUENTE_TITULO = ("Segoe UI", 16, "bold")
FUENTE_SUBTITULO = ("Segoe UI", 12, "bold")
FUENTE_NORMAL = ("Segoe UI", 10)
FUENTE_BOTON = ("Segoe UI", 11, "bold")
FUENTE_CODIGO = ("Consolas", 9)


# =====================================================================
# MENSAJES
# =====================================================================

# Diccionario para mantener todos los mensajes centralizados
MENSAJES = {
    'bienvenida': 'Bienvenido al Conversor de Audio a Texto con Encriptación',
    'instrucciones': 'Seleccione un archivo de audio para comenzar',
    'cargando': 'Procesando archivo...',
    'convirtiendo': 'Convirtiendo audio a texto...',
    'encriptando': 'Encriptando texto...',
    'guardando': 'Guardando datos...',
    'exito_conversion': '✅ Audio convertido exitosamente',
    'exito_encriptacion': '✅ Texto encriptado exitosamente',
    'exito_guardado': '✅ Datos guardados correctamente',
    'exito_desencriptacion': '✅ Texto desencriptado exitosamente',
    'error_formato': '❌ Formato de audio no permitido',
    'error_tamano': f'❌ El archivo excede el tamaño máximo de {TAMANO_MAX_MB}MB',
    'error_conversion': '❌ Error al convertir audio',
    'error_encriptacion': '❌ Error al encriptar',
    'error_guardado': '❌ Error al guardar datos',
    'error_archivo': '❌ No se pudo leer el archivo',
    'error_audio_vacio': '❌ No se detectó audio',
    'advertencia_sin_texto': '⚠️  No se pudo extraer texto',
}


# =====================================================================
# LOGGING
# =====================================================================

LOG_FILE = os.path.join(LOGS_DIR, 'app.log')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'


# =====================================================================
# VALIDACIÓN DE CONFIGURACIÓN
# =====================================================================

def validar_configuracion():
    ##
    # @brief Verifica que la configuración inicial del sistema sea válida.
    #
    # Examina la existencia de directorios, la presencia de la clave Fernet
    # y cualquier parámetro crítico necesario para que la aplicación funcione.
    #
    # @return (bool, str)  
    # - True, "Configuración válida" si todo está correcto.  
    # - False, mensaje con la lista de errores encontrados.
    ##
    errores = []
    
    if not FERNET_KEY:
        errores.append("Clave Fernet no configurada")
    
    if not os.path.exists(AUDIOS_DIR):
        errores.append(f"No existe directorio de audios: {AUDIOS_DIR}")
    
    if not os.path.exists(DATOS_DIR):
        errores.append(f"No existe directorio de datos: {DATOS_DIR}")
    
    if not os.path.exists(LOGS_DIR):
        errores.append(f"No existe directorio de logs: {LOGS_DIR}")
    
    if errores:
        return False, "; ".join(errores)

    return True, "Configuración válida"
