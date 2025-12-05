"""
@file __init__.py
@brief Inicialización del paquete de Conversor de Audio con Cifrado.
@version 1.0.0
@author Eddy De Oleo

Este archivo expone las clases principales del paquete para que puedan ser 
importadas de forma directa. También define metadatos del paquete.
"""

__version__ = '1.0.0'
__author__ = '[Eddy De Oleo]'

# Importar módulos principales para facilitar el uso
from .encriptacion import EncriptadorFernet
from .audio_converter import AudioConverter
from .storage import StorageManager

__all__ = [
    'EncriptadorFernet',
    'AudioConverter',
    'StorageManager'
]