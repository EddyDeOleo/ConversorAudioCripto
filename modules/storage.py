# modules/storage.py
import json
import os
from datetime import datetime
import logging
from config import ARCHIVO_CONVERSIONES, DATOS_DIR
import base64  

logger = logging.getLogger(__name__)

class StorageManager:
    """
    Manejo simple de archivos JSON para guardar conversiones.
    Cada registro:
    {
      "id": 1,
      "archivo_origen": "nombre.mp3",
      "ruta": "/ruta/..",
      "texto": "texto claro",
      "texto_encriptado": "gAAAAABpMMK0...",
      "codigo_maquina": "UklGR... (Base64)",
      "duracion_segundos": 12.34,
      "info_audio": {...},
      "fecha": "2025-12-02T14:00:00Z"
    }
    """
    def __init__(self, archivo=ARCHIVO_CONVERSIONES):
        self.archivo = archivo
        os.makedirs(DATOS_DIR, exist_ok=True)
        if not os.path.exists(self.archivo):
            self._inicializar_archivo()

    def _inicializar_archivo(self):
        logger.info("Inicializando archivo de conversiones JSON")
        with open(self.archivo, 'w', encoding='utf-8') as f:
            json.dump({"conversiones": []}, f, ensure_ascii=False, indent=2)

    def _leer_todo(self):
        try:
            with open(self.archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo JSON: {e}")
            self._inicializar_archivo()
            return {"conversiones": []}

    def _escribir_todo(self, data):
        try:
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error escribiendo JSON: {e}")
            return False

    def agregar_conversion(self, registro: dict):
        """
        Agrega un registro. El parámetro registro debe contener al menos:
        'archivo_origen', 'ruta', 'texto', 'texto_encriptado', 'codigo_maquina', 'duracion_segundos', 'info_audio'
        """
        data = self._leer_todo()
        conversiones = data.get("conversiones", [])
        next_id = (conversiones[-1]['id'] + 1) if conversiones else 1

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
        data = self._leer_todo()
        return data.get("conversiones", [])

    def obtener_por_id(self, id_):
        for r in self.listar_conversiones():
            if r.get("id") == id_:
                return r
        return None