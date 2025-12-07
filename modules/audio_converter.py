##
# @file audio_converter.py
# @brief Contiene la clase encargada de convertir audios y extraer texto mediante reconocimiento de voz.
#
# Esta clase encapsula:
# - Validación de archivos de audio
# - Conversión a WAV estándar (16kHz, mono)
# - Procesamiento con Google Speech Recognition
# - Obtención de metadatos del archivo
# - Lectura de bytes para mostrar contenido RAW (código máquina)
##

import speech_recognition as sr
from pydub import AudioSegment
import os
import logging
from config import (
    IDIOMA_RECONOCIMIENTO,
    FORMATOS_PERMITIDOS,
    TAMANO_MAX_MB,
    AUDIOS_DIR
)

logger = logging.getLogger(__name__)

# ==============================================================================
# DIAGRAMA DE ACTIVIDAD PLANTUML (CORREGIDO)
# Este bloque se coloca fuera de la docstring para asegurar el renderizado
# ==============================================================================

## Diagrama de Flujo (Método extraer_texto_de_audio)
#
# Este diagrama de actividad representa el flujo de ejecución completo
# del proceso de extracción de texto, incluyendo validación y manejo de errores.
# @startuml
# title Flujo: Extraer Texto de Audio
# 
# start
# 
# :Validar Archivo (validar_archivo);
# 
# if (Archivo es válido?) is (No)
#   :Lanzar Excepción (ValueError);
#   stop
# endif
# 
# partition Conversión {
#   if (Formato es WAV?) is (No)
#     :Convertir a WAV (16kHz, mono);
#     :Obtener ruta_wav y duración;
#   else (Sí)
#     :Obtener duración de WAV;
#   endif
# }
# 
# #LightBlue:Ajustar a ruido ambiente;
# :Procesar Audio;
# #LightBlue:Transcribir usando Google Speech Recognition;
# 
# if (Reconocimiento fue exitoso?) is (Sí)
#   :Limpieza (Eliminar WAV temporal);
#   :Retornar (Texto, Duración);
#   stop
# else (No/Error)
#   :Limpieza (Eliminar WAV temporal);
#   if (Error es de Conexión/Servicio?) is (Sí)
#     :Lanzar Excepción (sr.RequestError);
#   else (No se entendió el audio)
#     :Lanzar Excepción (sr.UnknownValueError);
#   endif
#   stop
# endif
# @enduml

class AudioConverter:
    """
    @class AudioConverter
    @brief Convierte audios a texto utilizando Google Speech Recognition.

    Esta clase centraliza toda la lógica relacionada con:
    - Validación de formato y tamaño
    - Conversión a WAV para reconocimiento
    - Reconocimiento de voz (speech-to-text)
    - Obtención de fragmentos RAW del archivo (bytes)
    """

    def __init__(self):
        """
        @brief Constructor: inicializa el reconocedor de voz.

        Configura parámetros como:
        - Umbral de energía
        - Detección dinámica de ruido
        """
        self.recognizer = sr.Recognizer()

        # Ajustes recomendados para reducir ruido y falsos positivos
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True

        logger.info("✅ AudioConverter inicializado correctamente")

    # ------------------------------------------------------------------

    def validar_archivo(self, ruta_archivo):
        """
        @brief Valida la existencia, extensión y tamaño del archivo.

        @param ruta_archivo Ruta absoluta al archivo de audio.
        @return (bool, str) - Es válido, mensaje.

        Validaciones realizadas:
        - El archivo existe
        - Extensión permitida
        - No excede el tamaño máximo configurado
        """
        if not os.path.exists(ruta_archivo):
            return False, "El archivo no existe"

        _, extension = os.path.splitext(ruta_archivo)
        extension = extension.lower()

        if extension not in FORMATOS_PERMITIDOS:
            formatos = ', '.join(FORMATOS_PERMITIDOS)
            return False, f"Formato no permitido. Formatos aceptados: {formatos}"

        tamano_mb = os.path.getsize(ruta_archivo) / (1024 * 1024)
        if tamano_mb > TAMANO_MAX_MB:
            return False, f"El archivo excede el tamaño máximo de {TAMANO_MAX_MB}MB (actual: {tamano_mb:.2f}MB)"

        return True, "Archivo válido"

    # ------------------------------------------------------------------

    def convertir_a_wav(self, ruta_audio):
        """
        @brief Convierte un archivo de audio a formato WAV 16kHz mono.

        @param ruta_audio Ruta original del audio.
        @return (str, float) - Ruta del WAV generado, duración en segundos.
        @throws Exception si ocurre un error en la conversión.

        El archivo WAV se guarda temporalmente dentro de AUDIOS_DIR.
        """
        try:
            nombre_archivo = os.path.basename(ruta_audio)
            nombre_sin_ext, _ = os.path.splitext(nombre_archivo)

            extension = os.path.splitext(ruta_audio)[1].lower().replace('.', '')
            logger.info(f"🔄 Convirtiendo {extension.upper()} a WAV...")

            audio = AudioSegment.from_file(ruta_audio, format=extension)

            # Configuración recomendada para reconocimiento
            audio = audio.set_channels(1)       # Mono
            audio = audio.set_frame_rate(16000) # 16kHz

            ruta_wav = os.path.join(AUDIOS_DIR, f"{nombre_sin_ext}_temp.wav")
            audio.export(ruta_wav, format='wav')

            duracion_segundos = len(audio) / 1000.0

            logger.info(f"✅ Audio convertido a WAV: {ruta_wav}")
            logger.info(f"   Duración: {duracion_segundos:.2f} segundos")

            return ruta_wav, duracion_segundos

        except Exception as e:
            logger.error(f"❌ Error al convertir audio: {e}")
            raise Exception(f"No se pudo convertir el audio: {str(e)}")

    # ------------------------------------------------------------------

    def extraer_texto_de_audio(self, ruta_audio):
        """
        @brief Extrae texto hablado desde un archivo de audio.

        @param ruta_audio Ruta del archivo a transcribir.
        @return (str, float) - Texto reconocido, duración.
        @throws Exception cuando el reconocimiento no puede realizarse.

        Flujo:
        1. Validación del archivo
        2. Conversión a WAV (si aplica)
        3. Ajuste al ruido
        4. Reconocimiento con Google Speech Recognition
        """
        ruta_wav = None

        try:
            es_valido, mensaje = self.validar_archivo(ruta_audio)
            if not es_valido:
                raise ValueError(mensaje)

            extension = os.path.splitext(ruta_audio)[1].lower()
            if extension != '.wav':
                ruta_wav, duracion = self.convertir_a_wav(ruta_audio)
                archivo_para_reconocer = ruta_wav
            else:
                archivo_para_reconocer = ruta_audio
                audio = AudioSegment.from_wav(ruta_audio)
                duracion = len(audio) / 1000.0

            logger.info("🎤 Iniciando reconocimiento de voz...")

            with sr.AudioFile(archivo_para_reconocer) as source:
                logger.info("   Ajustando al ruido ambiente...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                logger.info("   Procesando audio...")
                audio_data = self.recognizer.record(source)

            logger.info("   Reconociendo texto...")
            texto = self.recognizer.recognize_google(
                audio_data,
                language=IDIOMA_RECONOCIMIENTO
            )

            logger.info(f"✅ Texto reconocido exitosamente ({len(texto)} caracteres)")

            if ruta_wav and os.path.exists(ruta_wav):
                os.remove(ruta_wav)

            return texto, duracion

        except sr.UnknownValueError:
            logger.warning("⚠️ No se pudo entender el audio")
            if ruta_wav and os.path.exists(ruta_wav):
                os.remove(ruta_wav)
            raise Exception("No se pudo entender el audio. Usa voz clara.")

        except sr.RequestError as e:
            logger.error(f"❌ Error en el servicio de reconocimiento: {e}")
            if ruta_wav and os.path.exists(ruta_wav):
                os.remove(ruta_wav)
            raise Exception(f"Servicio de reconocimiento no disponible: {str(e)}")

        except Exception as e:
            logger.error(f"❌ Error al procesar audio: {e}")
            if ruta_wav and os.path.exists(ruta_wav):
                os.remove(ruta_wav)
            raise

    # ------------------------------------------------------------------

    def obtener_bytes_audio(self, ruta_audio, max_bytes=1000):
        """
        @brief Obtiene los primeros bytes del archivo (código máquina RAW).

        @param ruta_audio Ruta al archivo.
        @param max_bytes Cantidad máxima de bytes a leer.
        @return bytes - Fragmento del archivo en crudo.
        """
        try:
            with open(ruta_audio, 'rb') as f:
                return f.read(max_bytes)
        except Exception as e:
            logger.error(f"❌ Error al leer bytes del audio: {e}")
            raise

    # ------------------------------------------------------------------

    def obtener_info_audio(self, ruta_audio):
        """
        @brief Retorna metadatos del archivo de audio.

        @param ruta_audio Ruta al archivo.
        @return dict con formato, tamaño, duración, canales, etc.
        """
        try:
            nombre = os.path.basename(ruta_audio)
            tamano_bytes = os.path.getsize(ruta_audio)
            tamano_kb = tamano_bytes / 1024
            extension = os.path.splitext(ruta_audio)[1].lower()

            formato = extension.replace('.', '')
            audio = AudioSegment.from_file(ruta_audio, format=formato)

            info = {
                'nombre_archivo': nombre,
                'formato': extension,
                'tamano_bytes': tamano_bytes,
                'tamano_kb': round(tamano_kb, 2),
                'duracion_segundos': round(len(audio) / 1000.0, 2),
                'canales': audio.channels,
                'frecuencia_muestreo': audio.frame_rate,
                'bits_por_muestra': audio.sample_width * 8
            }
            return info

        except Exception as e:
            logger.error(f"❌ Error al obtener info del audio: {e}")
            return {
                'nombre_archivo': nombre,
                'formato': extension,
                'error': str(e)
            }