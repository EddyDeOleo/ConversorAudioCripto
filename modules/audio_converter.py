
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

# Configurar logger para este módulo
logger = logging.getLogger(__name__)


class AudioConverter:
    """
    Clase para convertir archivos de audio a texto
    Utiliza Google Speech Recognition para el reconocimiento de voz
    """
    
    def __init__(self):
        """
        Constructor: Inicializa el reconocedor de voz
        """
        # Crear instancia del reconocedor de Google Speech Recognition
        self.recognizer = sr.Recognizer()
        
        # Configurar parámetros del reconocedor
        # energy_threshold: Umbral de energía para detectar voz (valores más altos = menos sensible a ruido)
        self.recognizer.energy_threshold = 4000
        
        # dynamic_energy_threshold: Ajusta automáticamente el umbral según el ruido ambiente
        self.recognizer.dynamic_energy_threshold = True
        
        logger.info("✅ AudioConverter inicializado correctamente")
    
    def validar_archivo(self, ruta_archivo):
        """
        Valida que el archivo de audio sea correcto
        
        Parámetros:
            ruta_archivo (str): Ruta completa al archivo de audio
            
        Retorna:
            tuple: (bool, str) - (es_válido, mensaje_error)
            
        Validaciones:
            - El archivo existe
            - Tiene una extensión permitida
            - No excede el tamaño máximo
        """
        # Verificar que el archivo existe
        if not os.path.exists(ruta_archivo):
            return False, "El archivo no existe"
        
        # Obtener la extensión del archivo
        _, extension = os.path.splitext(ruta_archivo)
        extension = extension.lower()
        
        # Verificar que la extensión esté permitida
        if extension not in FORMATOS_PERMITIDOS:
            formatos = ', '.join(FORMATOS_PERMITIDOS)
            return False, f"Formato no permitido. Formatos aceptados: {formatos}"
        
        # Verificar el tamaño del archivo
        tamano_mb = os.path.getsize(ruta_archivo) / (1024 * 1024)  # Convertir bytes a MB
        if tamano_mb > TAMANO_MAX_MB:
            return False, f"El archivo excede el tamaño máximo de {TAMANO_MAX_MB}MB (tamaño actual: {tamano_mb:.2f}MB)"
        
        return True, "Archivo válido"
    
    def convertir_a_wav(self, ruta_audio):
        """
        Convierte un archivo de audio a formato WAV
        (necesario para speech_recognition)
        
        Parámetros:
            ruta_audio (str): Ruta al archivo de audio original
            
        Retorna:
            str: Ruta al archivo WAV generado
            
        Lanza:
            Exception: Si hay error en la conversión
            
        Nota:
            El archivo WAV se guarda temporalmente en la carpeta AUDIOS_DIR
            con el mismo nombre del original pero extensión .wav
        """
        try:
            # Obtener información del archivo
            nombre_archivo = os.path.basename(ruta_audio)
            nombre_sin_ext, _ = os.path.splitext(nombre_archivo)
            
            # Detectar el formato del archivo de audio
            extension = os.path.splitext(ruta_audio)[1].lower().replace('.', '')
            
            logger.info(f"🔄 Convirtiendo {extension.upper()} a WAV...")
            
            # Cargar el archivo de audio usando pydub
            # pydub soporta múltiples formatos: mp3, wav, ogg, flac, etc.
            audio = AudioSegment.from_file(ruta_audio, format=extension)
            
            # Configurar parámetros del WAV para mejor reconocimiento
            # Mono (1 canal): El reconocimiento funciona mejor con un solo canal
            # 16000 Hz: Frecuencia de muestreo óptima para voz humana
            audio = audio.set_channels(1)  # Convertir a mono
            audio = audio.set_frame_rate(16000)  # Frecuencia de muestreo
            
            # Ruta donde se guardará el archivo WAV temporal
            ruta_wav = os.path.join(AUDIOS_DIR, f"{nombre_sin_ext}_temp.wav")
            
            # Exportar a formato WAV
            audio.export(ruta_wav, format='wav')
            
            logger.info(f"✅ Audio convertido a WAV: {ruta_wav}")
            
            # Obtener información del audio
            duracion_segundos = len(audio) / 1000.0  # pydub mide en milisegundos
            logger.info(f"   Duración: {duracion_segundos:.2f} segundos")
            
            return ruta_wav, duracion_segundos
            
        except Exception as e:
            logger.error(f"❌ Error al convertir audio: {e}")
            raise Exception(f"No se pudo convertir el audio: {str(e)}")
    
    def extraer_texto_de_audio(self, ruta_audio):
        """
        Extrae el texto hablado de un archivo de audio
        
        Parámetros:
            ruta_audio (str): Ruta al archivo de audio
            
        Retorna:
            str: Texto extraído del audio
            
        Lanza:
            Exception: Si no se puede reconocer el audio
            
        Proceso:
            1. Convierte el audio a WAV si es necesario
            2. Carga el audio en el reconocedor
            3. Utiliza Google Speech Recognition para transcribir
            4. Retorna el texto reconocido
        """
        ruta_wav = None
        
        try:
            # Validar el archivo antes de procesarlo
            es_valido, mensaje = self.validar_archivo(ruta_audio)
            if not es_valido:
                raise ValueError(mensaje)
            
            # Convertir a WAV si no lo es ya
            extension = os.path.splitext(ruta_audio)[1].lower()
            if extension != '.wav':
                ruta_wav, duracion = self.convertir_a_wav(ruta_audio)
                archivo_para_reconocer = ruta_wav
            else:
                archivo_para_reconocer = ruta_audio
                # Obtener duración del WAV
                audio = AudioSegment.from_wav(ruta_audio)
                duracion = len(audio) / 1000.0
            
            logger.info(f"🎤 Iniciando reconocimiento de voz...")
            
            # Cargar el archivo de audio en el reconocedor
            with sr.AudioFile(archivo_para_reconocer) as source:
                # Ajustar al ruido ambiente
                # Esto mejora el reconocimiento eliminando ruido de fondo
                logger.info("   Ajustando al ruido ambiente...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Grabar el audio desde el archivo
                logger.info("   Procesando audio...")
                audio_data = self.recognizer.record(source)
            
            # Realizar el reconocimiento de voz usando Google Speech Recognition
            logger.info("   Reconociendo texto...")
            texto = self.recognizer.recognize_google(
                audio_data,
                language=IDIOMA_RECONOCIMIENTO
            )
            
            logger.info(f"✅ Texto reconocido exitosamente ({len(texto)} caracteres)")
            
            # Limpiar archivo temporal WAV si se creó
            if ruta_wav and os.path.exists(ruta_wav):
                os.remove(ruta_wav)
                logger.info("   Archivo temporal eliminado")
            
            return texto, duracion
            
        except sr.UnknownValueError:
            # El audio no contiene voz reconocible
            logger.warning("⚠️  No se pudo entender el audio")
            if ruta_wav and os.path.exists(ruta_wav):
                os.remove(ruta_wav)
            raise Exception("No se pudo entender el audio. Asegúrate de que contenga voz clara.")
            
        except sr.RequestError as e:
            # Error en el servicio de Google (sin internet, API caída, etc.)
            logger.error(f"❌ Error en el servicio de reconocimiento: {e}")
            if ruta_wav and os.path.exists(ruta_wav):
                os.remove(ruta_wav)
            raise Exception(f"Error en el servicio de reconocimiento: {str(e)}")
            
        except Exception as e:
            # Cualquier otro error
            logger.error(f"❌ Error al procesar audio: {e}")
            if ruta_wav and os.path.exists(ruta_wav):
                os.remove(ruta_wav)
            raise
    
    def obtener_bytes_audio(self, ruta_audio, max_bytes=1000):
        """
        Obtiene los bytes del archivo de audio
        (para mostrar la representación en código de máquina)
        
        Parámetros:
            ruta_audio (str): Ruta al archivo de audio
            max_bytes (int): Cantidad máxima de bytes a leer
            
        Retorna:
            bytes: Primeros bytes del archivo
        """
        try:
            with open(ruta_audio, 'rb') as f:
                audio_bytes = f.read(max_bytes)
            return audio_bytes
        except Exception as e:
            logger.error(f"❌ Error al leer bytes del audio: {e}")
            raise
    
    def obtener_info_audio(self, ruta_audio):
        """
        Obtiene información detallada del archivo de audio
        
        Parámetros:
            ruta_audio (str): Ruta al archivo de audio
            
        Retorna:
            dict: Información del audio (formato, tamaño, duración, etc.)
        """
        try:
            # Información básica del archivo
            nombre_archivo = os.path.basename(ruta_audio)
            tamano_bytes = os.path.getsize(ruta_audio)
            tamano_kb = tamano_bytes / 1024
            extension = os.path.splitext(ruta_audio)[1].lower()
            
            # Cargar audio con pydub para obtener metadatos
            formato = extension.replace('.', '')
            audio = AudioSegment.from_file(ruta_audio, format=formato)
            
            info = {
                'nombre_archivo': nombre_archivo,
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
                'nombre_archivo': os.path.basename(ruta_audio),
                'formato': os.path.splitext(ruta_audio)[1],
                'error': str(e)
            }

