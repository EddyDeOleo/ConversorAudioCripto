
from cryptography.fernet import Fernet
from config import FERNET_KEY
import logging

logger = logging.getLogger(__name__)

class EncriptadorFernet:
    """
    Manejo limpio de encriptación Fernet:
    - Encripta texto → token base64 (bytes)
    - Desencripta token → texto original (str)
    Sin conversiones HEX ni binario.
    """

    def __init__(self):
        try:
            self.cipher = Fernet(FERNET_KEY)
            logger.info("Cipher Fernet inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar Fernet: {e}")
            raise

    def encriptar_texto(self, texto: str) -> bytes:
        """Encripta texto y retorna token Fernet puro."""
        if not texto or texto.strip() == "":
            raise ValueError("El texto no puede estar vacío")

        texto_bytes = texto.encode("utf-8")
        token = self.cipher.encrypt(texto_bytes)

        logger.info(f"Texto encriptado: {len(texto)} chars → {len(token)} bytes")

        return token

    def desencriptar_texto(self, token: bytes) -> str:
        """Desencripta token Fernet puro."""
        if not token:
            raise ValueError("El token no puede estar vacío")

        texto_bytes = self.cipher.decrypt(token)
        texto = texto_bytes.decode("utf-8")

        logger.info(f"Texto desencriptado: {len(token)} bytes → {len(texto)} chars")

        return texto

    def obtener_info_encriptacion(self, texto_original: str, token: bytes):
        """Información sobre la encriptación."""
        return {
            "longitud_original": len(texto_original),
            "longitud_encriptada": len(token),
            "algoritmo": "Fernet (AES-128 CBC + HMAC)",
            "formato": "Base64 URL-safe",
        }


def generar_nueva_clave():
    """Genera una nueva clave Fernet."""
    nueva = Fernet.generate_key()
    print("=" * 70)
    print("🔑 NUEVA CLAVE FERNET GENERADA")
    print("=" * 70)
    print(f"FERNET_KEY = {nueva}")
    print("=" * 70)
    return nueva
