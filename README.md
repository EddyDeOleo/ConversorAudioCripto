📌 ConversorAudioCripto

Conversión de audio a texto con encriptación avanzada (Fernet AES-128)

📝 Descripción general

ConversorAudioCripto es una aplicación de escritorio desarrollada en Python, diseñada para:

✔ Convertir archivos de audio a texto
✔ Mostrar información técnica del archivo
✔ Visualizar el contenido RAW (código máquina) del audio
✔ Encriptar y desencriptar texto usando Fernet
✔ Guardar registros estructurados en JSON
✔ Mantener trazabilidad mediante un sistema de logging

El proyecto integra análisis de audio, procesamiento de texto, encriptación y almacenamiento seguro, todo dentro de una interfaz gráfica desarrollada con Tkinter.

🎯 Características principales
🔊 Conversión de audio a texto

Utiliza las librerías SpeechRecognition y pydub para extraer texto de archivos:

.mp3

.wav

.m4a

.ogg

.aac

.flac

.wma

🧪 Información técnica del audio

Muestra:

Nombre del archivo

Formato

Tamaño

Duración

Frecuencia de muestreo

Canales

Bits por muestra

🧬 Código RAW (código máquina)

Se extraen los bytes del archivo y se muestran de manera visual.

Se guardan en JSON como Base64 para garantizar compatibilidad y evitar corrupción.

🔐 Encriptación y desencriptación

Basado en Fernet, que utiliza:

AES-128 en modo CBC

HMAC-SHA256

Base64 seguro para URLs

🗄️ Gestión de almacenamiento

El módulo StorageManager permite:

Guardar conversiones en JSON

Manejar excepciones

Garantizar integridad de datos

Registrar errores mediante logging

🖥️ Interfaz gráfica moderna

Construida con Tkinter:

Tema “clam”

Botones personalizados

Campos ScrolledText optimizados

💻 Plataformas compatibles

El proyecto es multiplataforma, ya que el stack utilizado (Python + Tkinter + SpeechRecognition + cryptography) es portable.

Funciona en:

✔ Windows 10 / 11
✔ Linux (Ubuntu, Mint, Fedora, Arch, etc.)
✔ macOS (Intel y Apple Silicon)

Requisitos mínimos por plataforma:

🔹 Windows

Python 3.10+

Microsoft Visual C++ Build Tools (solo si usas PyAudio)

🔹 Linux

Python 3.10+

PortAudio (dependencia de PyAudio)

sudo apt install portaudio19-dev

🔹 macOS

Python 3.10+ (Homebrew recomendado)

PortAudio:

brew install portaudio

📂 Estructura del proyecto
ConversorAudioCripto/
│── main.py
│── config.py
│── requirements.txt
│── datos/
│   └── conversiones.json
│── modules/
│   ├── interfaz.py
│   ├── audio_converter.py
│   ├── encriptacion.py
│   ├── storage.py
│   └── __init__.py
│── audios/
│   └── (archivos de audio)

⚙️ Tecnologías utilizadas

Python 3.10.11

Tkinter

SpeechRecognition

pydub

cryptography (Fernet)

PyAudio

logging

Base64

📥 Instalación
1. Clonar el repositorio
git clone https://github.com/usuario/ConversorAudioCripto.git
cd ConversorAudioCripto

2. Crear entorno virtual (opcional)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

3. Instalar dependencias
pip install -r requirements.txt

▶️ Uso
python main.py

📦 Gestión de dependencias

Contenido de requirements.txt:

SpeechRecognition==3.10.0
pydub==0.25.1
PyAudio==0.2.14

cryptography==41.0.7

python-dotenv==1.0.0

🔐 Seguridad

El texto encriptado se almacena en Base64.

El código máquina también se guarda en Base64.

Los logs permiten trazabilidad sin exponer datos sensibles.

📚 Documentación interna

El proyecto está totalmente documentado con formato Doxygen, incluyendo:

@file

@brief

@class

@method

@param

@return

👨‍💻 Autor

Eddy De’Oleo
Desarrollador de software | República Dominicana

🏁 Licencia

Este proyecto se distribuye bajo licencia pública libre.