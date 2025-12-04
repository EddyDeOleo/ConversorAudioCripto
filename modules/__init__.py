
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