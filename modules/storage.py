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

# ==============================================================================
# DIAGRAMA HIPO (HIERARCHY-INPUT-PROCESS-OUTPUT)
# Describe la función principal del módulo StorageManager.
# ==============================================================================

## Diagrama HIPO (StorageManager)
#
# Representa el flujo jerárquico del proceso de almacenamiento de conversiones.
# @startuml
# title Diagrama HIPO: StorageManager
# 
# rectangle "Registro de Conversión" as INPUT {
#     **INPUT:**
#     * Archivo Origen (ruta)
#     * Texto Claro
#     * Texto Encriptado (Token)
#     * Bytes RAW (Código Máquina)
#     * Metadatos de Audio (Duración, Info)
# }
# 
# rectangle "Gestión de Almacenamiento JSON" as PROCESS {
#     **PROCESS:**
#     -> 1. Leer archivo JSON (conversiones.json)
#     -> 2. Generar nuevo ID/Timestamp
#     -> 3. Normalizar datos (Bytes -> Base64/Str)
#     -> 4. Agregar nuevo registro
#     -> 5. Escribir/Guardar JSON
# }
# 
# rectangle "Archivo JSON Actualizado" as OUTPUT {
#     **OUTPUT:**
#     * Conversión persistida (ID, Datos)
#     * Lista completa de registros
#     * Estado (Éxito/Error)
# }
# 
# INPUT --> PROCESS
# PROCESS --> OUTPUT
# 
# @enduml

# ==============================================================================
# DIAGRAMA DE ACTIVIDAD PLANTUML
# Flujo del método agregar_conversion.
# ==============================================================================

## Diagrama de Flujo (Método agregar_conversion)
#
# Este diagrama de actividad representa el flujo completo para persistir
# un nuevo registro de conversión de audio a texto en el archivo JSON.
# @startuml
# title Flujo: Agregar Conversión (StorageManager)
# 
# start
# 
# :Llamar _leer_todo (Leer archivo JSON);
# 
# :Obtener lista de conversiones;
# 
# :Calcular próximo ID;
# 
# :Normalizar campos (bytes a Base64/str);
# 
# :Crear registro_final con timestamp UTC;
# 
# :Añadir registro_final a la lista de conversiones;
# 
# :Llamar _escribir_todo (Guardar archivo JSON);
# 
# if (Escritura exitosa?) is (Sí)
#   :Retornar registro guardado;
#   stop
# else (No/Error)
#   :Lanzar Excepción (Error al guardar);
#   stop
# endif
# 
# @enduml


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

        # Normalizar campos que pueden venir en bytes (Base64/UTF-8)
        texto_encriptado_norm = registro.get("texto_encriptado")
        if isinstance(texto_encriptado_norm, (bytes, bytearray)):
            texto_encriptado_norm = texto_encriptado_norm.decode('utf-8')

        codigo_maquina_norm = registro.get("codigo_maquina")
        if isinstance(codigo_maquina_norm, (bytes, bytearray)):
            # Asumo que el código máquina es Base64 para ser JSON-safe
            try:
                codigo_maquina_norm = base64.b64encode(codigo_maquina_norm).decode('utf-8')
            except Exception:
                # Si no es Base64, simplemente decodificar como UTF-8
                codigo_maquina_norm = codigo_maquina_norm.decode('utf-8', errors='ignore')


        registro_final = {
            "id": next_id,
            "archivo_origen": registro.get("archivo_origen"),
            "ruta": registro.get("ruta"),
            "texto": registro.get("texto"),
            "texto_encriptado": texto_encriptado_norm,
            "codigo_maquina": codigo_maquina_norm,
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