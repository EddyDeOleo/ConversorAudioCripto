"""
@file encriptacion.py
@brief Módulo encargado de manejar encriptación y desencriptación con Fernet.
@author Eddy De Oleo
@version 1.0.0

Este módulo contiene la clase `EncriptadorFernet`, la cual simplifica el uso de
Fernet para encriptación simétrica. Maneja:
- Encriptar texto → token en Base64 (bytes)
- Desencriptar token → texto original
- Obtener información del proceso de encriptación
"""

from cryptography.fernet import Fernet
from config import FERNET_KEY
import logging

logger = logging.getLogger(__name__)

# ==============================================================================
# DIAGRAMA DE ACTIVIDAD PLANTUML
# Bloque de diagrama colocado fuera de la docstring para asegurar el renderizado.
# ==============================================================================

## Diagrama de Flujo (Métodos encriptar_texto y desencriptar_texto)
#
# Este diagrama de actividad representa los dos flujos principales
# dentro del EncriptadorFernet: encriptación y desencriptación.
# @startuml
# title Flujo de Encriptación/Desencriptación Fernet
# 
# start
# 
# partition Encriptar Texto {
#   :Entrada (Texto Plano);
#   if (Texto es vacío?) is (Sí)
#     :Lanzar ValueError;
#     stop
#   endif
#   :Codificar a UTF-8;
#   #LightBlue:Fernet.encrypt();
#   :Salida (Token Base64 bytes);
# }
# 
# partition Desencriptar Token {
#   :Entrada (Token Fernet bytes);
#   if (Token es vacío?) is (Sí)
#     :Lanzar ValueError;
#     stop
#   endif
#   #LightBlue:Fernet.decrypt();
#   :Decodificar a UTF-8;
#   :Salida (Texto Plano);
# }
# 
# stop
# @enduml

class EncriptadorFernet:
    """
    @class EncriptadorFernet
    @brief Clase para manejar encriptación/descencriptación usando Fernet.

    Implementa una interfaz simple para:
    - Encriptar texto como tokens Fernet Base64
    - Desencriptarlos de vuelta a texto plano
    - Consultar metadatos de encriptación

    No utiliza formatos intermedios (Hex, binario), solo Fernet puro.
    """

    def __init__(self):
        """
        @brief Constructor: inicializa el cifrador Fernet.
        @exception Exception Error si la clave Fernet no es válida.
        """
        try:
            self.cipher = Fernet(FERNET_KEY)
            logger.info("Cipher Fernet inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar Fernet: {e}")
            raise

    def encriptar_texto(self, texto: str) -> bytes:
        """
        @brief Encripta un texto y retorna el token Fernet.

        @param texto Texto plano a encriptar.
        @return bytes Token seguro en Base64 (url-safe).
        @exception ValueError Si el texto está vacío.

        @note Devuelve bytes, no string.
        """
        if not texto or texto.strip() == "":
            raise ValueError("El texto no puede estar vacío")

        texto_bytes = texto.encode("utf-8")
        token = self.cipher.encrypt(texto_bytes)

        logger.info(f"Texto encriptado: {len(texto)} chars → {len(token)} bytes")

        return token

    def desencriptar_texto(self, token: bytes) -> str:
        """
        @brief Desencripta un token Fernet y retorna texto plano.

        @param token Token generado por Fernet.
        @return str Texto original desencriptado.
        @exception ValueError Si el token está vacío.
        """
        if not token:
            raise ValueError("El token no puede estar vacío")

        try:
            texto_bytes = self.cipher.decrypt(token)
            texto = texto_bytes.decode("utf-8")

            logger.info(f"Texto desencriptado: {len(token)} bytes → {len(texto)} chars")

            return texto
        except Exception as e:
            logger.error(f"Error de desencriptación (token inválido o clave incorrecta): {e}")
            raise ValueError("Token inválido o clave Fernet incorrecta.") # Manejo de excepción más específica

    def obtener_info_encriptacion(self, texto_original: str, token: bytes):
        """
        @brief Retorna metadatos sobre la encriptación ejecutada.

        @param texto_original Texto original previo a encriptación.
        @param token Token Fernet generado.
        @return dict Información del proceso:
                - longitud_original
                - longitud_encriptada
                - algoritmo
                - formato
        """
        return {
            "longitud_original": len(texto_original),
            "longitud_encriptada": len(token),
            "algoritmo": "Fernet (AES-128 CBC + HMAC)",
            "formato": "Base64 URL-safe",
        }


def generar_nueva_clave():
    """
    @brief Genera y muestra por consola una nueva clave Fernet.
    @return bytes Nueva clave generada.
    @warning Guardar la clave en un entorno seguro.
    """
    nueva = Fernet.generate_key()
    print("=" * 70)
    print("🔑 NUEVA CLAVE FERNET GENERADA")
    print("=" * 70)
    print(f"FERNET_KEY = {nueva}")
    print("=" * 70)
    return nueva