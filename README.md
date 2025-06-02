# Sistema de Asistencia y Visitas del Barrio

Sistema web simple para registrar la asistencia a las reuniones dominicales y las visitas de hermanamiento realizadas en un barrio de La Iglesia de Jesucristo de los Santos de los Últimos Días.

## Pre-requisitos

- Python 3.8+
- Navegador web moderno (para el frontend)

## Configuración e Instalación

### Backend

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/tu_usuario/iglesia_asistencia_visitas.git](https://github.com/tu_usuario/iglesia_asistencia_visitas.git) # Reemplaza con tu URL
    cd iglesia_asistencia_visitas
    ```

2.  **Navegar a la carpeta backend y crear/activar entorno virtual:**
    ```bash
    cd backend
    python3 -m venv venv
    ```
    -   En Linux/Mac:
        ```bash
        source venv/bin/activate
        ```
    -   En Windows (cmd):
        ```bash
        venv\Scripts\activate
        ```
    -   En Windows (PowerShell):
        ```bash
        venv\Scripts\Activate.ps1
        ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r ../requirements.txt
    ```
    *(Nota: El archivo requirements.txt está en la raíz del proyecto, por eso `../requirements.txt` si estás dentro de `/backend`)*

4.  **Inicializar la base de datos:**
    (Asegúrate de estar en la carpeta `iglesia_asistencia_visitas/backend/`)
    ```bash
    python init_db.py
    ```
    Esto creará el archivo `instance/iglesia.db` con las tablas necesarias y algunos datos iniciales.

5.  **Ejecutar la aplicación Flask:**
    (Asegúrate de estar en la carpeta `iglesia_asistencia_visitas/backend/`)
    ```bash
    python app.py
    ```
    El backend estará corriendo en `http://127.0.0.1:5000` o `http://localhost:5000`.

### Frontend

1.  **Acceder a las páginas:**
    Simplemente abre los archivos HTML (`index.html`, `asistencia.html`, etc.) directamente en tu navegador desde la carpeta `iglesia_asistencia_visitas/frontend/`.
    -   `file:///ruta/a/tu/proyecto/iglesia_asistencia_visitas/frontend/index.html`

    Alternativamente, para una experiencia más similar a un servidor web y evitar posibles problemas con `fetch` debido a la política de origen del mismo archivo (file://), puedes servir la carpeta `frontend` usando Python:
    ```bash
    # Desde la carpeta raíz del proyecto (iglesia_asistencia_visitas)
    # o desde la carpeta frontend
    cd frontend
    python3 -m http.server 8080
    ```
    Luego abre `http://localhost:8080` en tu navegador.

## Cómo usar la Aplicación

1.  **Registrar Asistencia:**
    -   Navega a `asistencia.html`.
    -   La tabla mostrará los hermanos y los domingos del mes actual.
    -   Haz clic en el círculo de un hermano bajo un domingo específico para marcar su asistencia. El círculo se volverá verde.
    -   Los datos se guardan automáticamente.

2.  **Registrar Visitas:**
    -   Navega a `visitas.html`.
    -   Selecciona el "Hermano que visita" y el "Hermano que fue visitado" de las listas desplegables.
    -   Haz clic en el botón "LISTO".
    -   La visita se registrará con la fecha actual y se mostrará en la tabla de visitas del mes.

3.  **Consultar Base de Datos de Hermanos:**
    -   Navega a `base_datos.html`.
    -   Verás una lista de todos los hermanos registrados en la base de datos.

## Despliegue

### GitHub Pages (Solo Frontend)

Si solo deseas desplegar el frontend (sin backend funcional, solo la UI estática):
1.  Asegúrate que todas las rutas `fetch` en el JavaScript apunten a tu backend desplegado si lo tienes en otro servicio. Si no, solo será una demo visual.
2.  Ve a tu repositorio en GitHub `Settings > Pages`.
3.  En la sección "Build and deployment", bajo "Source", selecciona "Deploy from a branch".
4.  Elige la rama `main` (o la que uses) y la carpeta `/frontend` (o `/docs` si mueves el contenido allí, o la raíz `/ (root)` si el frontend está en la raíz).
5.  Guarda los cambios. GitHub Pages te proporcionará una URL.

### Despliegue Completo (Frontend + Backend) en Render/Heroku (Ejemplo Render)

Para desplegar la aplicación completa (backend y frontend):

1.  **Prepara tu aplicación para producción:**
    -   Asegúrate que tu `app.py` use `0.0.0.0` como host: `app.run(host='0.0.0.0', port=port)`
    -   Render (y otros) usualmente inyectan una variable de entorno `PORT`.

2.  **Crea un archivo `build.sh` en la raíz de tu repositorio (opcional, pero útil para Render):**
    ```bash
    #!/usr/bin/env bash
    # exit on error
    set -o errexit

    pip install -r requirements.txt
    # No es necesario ejecutar init_db.py aquí si la base de datos es persistente
    # o si la creas manualmente la primera vez.
    # Si SQLite se reinicia con cada despliegue, puedes añadir:
    # python backend/init_db.py
    ```
    Hazlo ejecutable: `chmod +x build.sh`

3.  **En Render.com:**
    -   Crea un nuevo "Web Service".
    -   Conecta tu repositorio GitHub.
    -   **Environment:** Python
    -   **Region:** Elige la más cercana.
    -   **Build Command:** `./build.sh` (o `pip install -r requirements.txt`)
    -   **Start Command:** `gunicorn backend.app:app` (necesitarás agregar `gunicorn` a `requirements.txt`) o `python backend/app.py`.
    -   **Variables de Entorno:**
        -   `PYTHON_VERSION`: `3.9.x` (o la que uses)
    -   **Disco Persistente (para SQLite):**
        -   Si usas SQLite y quieres que los datos persistan entre despliegues, necesitarás configurar un disco persistente en Render.
        -   **Mount Path:** `/opt/render/project/src/backend/instance` (o donde se guarde tu `iglesia.db`)
        -   Es **altamente recomendable** usar PostgreSQL o una base de datos similar para producción. Render ofrece instancias gratuitas de PostgreSQL. Si cambias a PostgreSQL, actualiza `init_db.py` y `app.py` para usar `psycopg2-binary` y las cadenas de conexión adecuadas.

4.  **Para servir el frontend desde Flask (si no usas un servicio de static hosting aparte):**
    En `backend/app.py`, configura Flask para servir archivos estáticos desde la carpeta `frontend`.
    ```python
    # backend/app.py
    app = Flask(__name__, static_folder='../frontend', static_url_path='/')

    @app.route('/')
    def serve_index():
        return app.send_static_file('index.html')

    # ... tus otras rutas API ...
    ```
    Asegúrate de que las rutas en tus HTMLs (para CSS, JS, y links entre páginas) sean relativas a la raíz (ej. `/css/styles.css`, `/asistencia.html`).

## Actualizar el Repositorio

Para guardar tus cambios y actualizar el repositorio en GitHub:
1.  **Verificar cambios:**
    ```bash
    git status
    ```
2.  **Agregar cambios al "staging area":**
    ```bash
    git add .  # Agrega todos los archivos modificados/nuevos
    # o git add nombre_del_archivo_especifico
    ```
3.  **Hacer commit de los cambios:**
    ```bash
    git commit -m "Descripción breve de los cambios, ej: Implementada API de visitas"
    ```
4.  **Subir los cambios al repositorio remoto (origin main):**
    ```bash
    git push origin main
    ```
5.  **Para obtener cambios de otros (si colaboras):**
    ```bash
    git pull origin main
    ```

## Estructura de la Base de Datos (SQLite)

-   **`hermanos`**:
    -   `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
    -   `nombre` (TEXT, NOT NULL)
    -   `sexo` (TEXT) - Ej: "M" (Masculino), "F" (Femenino)
    -   `otros_campos` (TEXT) - Opcional, para futura expansión

-   **`asistencias`**:
    -   `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
    -   `hermano_id` (INTEGER, FOREIGN KEY (`hermanos.id`))
    -   `fecha_sunday` (DATE, NOT NULL) - El domingo al que corresponde la asistencia.
    -   `creado_en` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
    -   UNIQUE (`hermano_id`, `fecha_sunday`) - Para evitar duplicados.

-   **`visitas`**:
    -   `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
    -   `visitante_id` (INTEGER, FOREIGN KEY (`hermanos.id`)) - Quien hizo la visita.
    -   `visitado_id` (INTEGER, FOREIGN KEY (`hermanos.id`)) - Quien recibió la visita.
    -   `fecha` (DATE, NOT NULL) - Fecha exacta de la visita.
    -   `mes` (TEXT, NOT NULL) - Mes de la visita (ej. "junio").
    -   `creado_en` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

---