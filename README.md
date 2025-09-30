
# Proyecto de Pipeline ETL para Limpieza de Datos

Este proyecto implementa un pipeline de ETL (Extract, Transform, Load) en Python para consumir datos de una API REST, aplicar una serie de reglas de limpieza y validación, y finalmente guardar los resultados en archivos JSON y CSV.

## Características

- **Extracción de Datos**: Consume datos de dos endpoints de una API (`/users` y `/todos`).
- **Transformación y Limpieza**:
  - Parsea y estructura los datos de entrada a un esquema definido.
  - Valida y estandariza números de teléfono a un formato E.164.
  - Valida el formato de emails.
  - Realiza deduplicación de usuarios basada en email, teléfono o nombre, conservando el registro con el ID más bajo.
- **Validación Cruzada**: Valida que las tareas (`todos`) pertenezcan a usuarios válidos y existentes.
- **Carga de Datos**: Guarda los datos procesados (aceptados y rechazados) en archivos `.json` y `.csv` en el directorio `data/`.
- **Testing**: Incluye una suite de tests unitarios para validar la lógica de procesamiento.

## Estructura del Proyecto

```
.
├── data/                 # Directorio de salida para los archivos generados
├── src/                  # Código fuente del pipeline
│   ├── __init__.py
│   ├── api_client.py     # Cliente para realizar peticiones a la API
│   ├── file_writer.py    # Utilidad para escribir archivos JSON y CSV
│   └── main.py           # Lógica principal del ETL y orquestación
├── tests/                # Suite de tests unitarios
│   ├── __init__.py
│   └── test_processors.py
├── main.py               # Punto de entrada para ejecutar el pipeline
├── requirements.txt      # Dependencias de Python
└── README.md             # Este archivo
```

## Configuración e Instalación

Para ejecutar este proyecto, necesitas tener Python 3 instalado. Se recomienda encarecidamente utilizar un entorno virtual.

1. **Clona el repositorio (si aplica)**:
   ```bash
   git clone <url-del-repositorio>
   cd <nombre-del-directorio>
   ```

2. **Crea un entorno virtual**:
   ```bash
   python3 -m venv venv
   ```

3. **Activa el entorno virtual**:
   - En macOS y Linux:
     ```bash
     source venv/bin/activate
     ```
   - En Windows:
     ```bash
     .\venv\Scripts\activate
     ```

4. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## Cómo Usar

### Ejecutar el Pipeline ETL

Para ejecutar el proceso completo de extracción, transformación y carga, simplemente ejecuta el script `main.py` desde la raíz del proyecto:

```bash
python3 main.py
```

Los archivos de salida se generarán en el directorio `data/`.

### Ejecutar los Tests

Para verificar que toda la lógica de negocio funciona como se espera, puedes ejecutar la suite de tests unitarios:

```bash
python3 -m unittest discover -s tests -t .
```

## Resumen del Código

- **`src/main.py`**: Es el corazón del proyecto. Contiene:
  - Las clases `UserProcessor` y `TodoProcessor`, donde reside toda la lógica de transformación, validación y deduplicación.
  - La función `run_processing_pipeline`, que orquesta la ejecución de los procesadores y sus dependencias.
  - La función `save_pipeline_results`, que se encarga de la fase de carga (Load) y guarda los archivos.
- **`src/api_client.py`**: Abstrae la comunicación con la API REST.
- **`src/file_writer.py`**: Maneja la escritura de los datos procesados en diferentes formatos de archivo.
- **`tests/test_processors.py`**: Contiene tests unitarios que simulan la API y validan el comportamiento de los procesadores ante diferentes escenarios (datos válidos, duplicados, inválidos, etc.).
