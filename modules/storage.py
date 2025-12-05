"""
@file storage.py
@brief Módulo encargado de persistir datos de conversiones en un archivo JSON.
@version 1.0.0
@author Eddy

Este módulo maneja operaciones CRUD básicas sobre un archivo JSON que almacena
registro de conversiones de audio → texto.

Cada conversión incluye:
- Texto claro
- Texto encriptado
- Bytes iniciales del archivo en Base64 ("código máquina")
- Datos del audio procesado
- Timestamp
"""

import json
import os
from datetime import datetime
import logging
from config import ARCHIVO_CONVERSIONES, DATOS_DIR
import base64

logger = logging.getLogger(__name__)


class StorageManager:
    """
    @class StorageManager
    @brief Clase para gestionar almacenamiento persistente en archivos JSON.

    Permite:
    - Agregar conversiones
    - Listar conversiones
    - Buscar conversiones por ID
    """

    def __init__(self, archivo=ARCHIVO_CONVERSIONES):
        """
        @brief Constructor: asegura que el archivo JSON exista.
        @param archivo Ruta completa al archivo de conversiones.
        """
        self.archivo = archivo
        os.makedirs(DATOS_DIR, exist_ok=True)

        if not os.path.exists(self.archivo):
            self._inicializar_archivo()

    def _inicializar_archivo(self):
        """
        @brief Inicializa el archivo JSON con la estructura base.
        """
        logger.info("Inicializando archivo de conversiones JSON")
        with open(self.archivo, 'w', encoding='utf-8') as f:
            json.dump({"conversiones": []}, f, ensure_ascii=False, indent=2)

    def _leer_todo(self):
        """
        @brief Lee el archivo JSON completo.
        @return dict Contenido del archivo.
        """
        try:
            with open(self.archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo JSON: {e}")
            self._inicializar_archivo()
            return {"conversiones": []}

    def _escribir_todo(self, data):
        """
        @brief Escribe el archivo JSON con los datos completos.
        @param data Diccionario a escribir.
        @return bool True si se guardó correctamente.
        """
        try:
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error escribiendo JSON: {e}")
            return False

    def agregar_conversion(self, registro: dict):
        """
        @brief Agrega un registro de conversión al archivo.

        @param registro Dict con campos obligatorios:
               - archivo_origen
               - ruta
               - texto
               - texto_encriptado (bytes o str)
               - codigo_maquina (bytes o str)
               - duracion_segundos
               - info_audio

        @return dict Registro final guardado.
        @exception Exception Si ocurre un error al escribir el archivo.
        """
        data = self._leer_todo()
        conversiones = data.get("conversiones", [])
        next_id = (conversiones[-1]['id'] + 1) if conversiones else 1

        # Normalizar campos que pueden venir en bytes
        registro_final = {
            "id": next_id,
            "archivo_origen": registro.get("archivo_origen"),
            "ruta": registro.get("ruta"),
            "texto": registro.get("texto"),
            "texto_encriptado": (
                registro.get("texto_encriptado").decode('utf-8')
                if isinstance(registro.get("texto_encriptado"), (bytes, bytearray))
                else registro.get("texto_encriptado")
            ),
            "codigo_maquina": (
                registro.get("codigo_maquina").decode('utf-8')
                if isinstance(registro.get("codigo_maquina"), (bytes, bytearray))
                else registro.get("codigo_maquina")
            ),
            "duracion_segundos": registro.get("duracion_segundos"),
            "info_audio": registro.get("info_audio"),
            "fecha": datetime.utcnow().isoformat() + "Z"
        }

        conversiones.append(registro_final)
        data["conversiones"] = conversiones

        exito = self._escribir_todo(data)
        if exito:
            logger.info(f"Registro agregado con id {next_id}")
            return registro_final
        else:
            raise Exception("No se pudo guardar la conversión en JSON")

    def listar_conversiones(self):
        """
        @brief Obtiene la lista completa de conversiones almacenadas.
        @return list Lista de conversiones.
        """
        data = self._leer_todo()
        return data.get("conversiones", [])

    def obtener_por_id(self, id_):
        """
        @brief Busca y retorna un registro por su ID.
        @param id_ Identificador de la conversión.
        @return dict|None Registro encontrado o None.
        """
        for r in self.listar_conversiones():
            if r.get("id") == id_:
                return r
        return None