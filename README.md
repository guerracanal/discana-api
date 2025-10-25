# Discana API

Discana API es un servicio web construido con Flask, diseñado para actuar como un intermediario entre Google Sheets y una base de datos MongoDB. Su función principal es extraer datos de inventario desde una hoja de cálculo, procesarlos y cargarlos en una base de datos para su uso en otras aplicaciones.

---

## ✨ Características

- **Extracción de Datos desde Google Sheets**: Se conecta de forma segura a la API de Google Sheets para leer y procesar datos.
- **Integración con MongoDB**: Inserta los datos directamente en una colección de MongoDB, utilizando `pymongo` para una operación eficiente.
- **Endpoint de Administración**: Proporciona un endpoint seguro para iniciar el proceso de sincronización de datos bajo demanda.
- **Optimizado para Despliegue**: Configurado con Gunicorn para un rendimiento robusto y listo para ser desplegado en plataformas en la nube.
- **Manejo Seguro de Credenciales**: Utiliza variables de entorno para gestionar las credenciales de servicio, evitando ficheros sensibles en producción.

---

## 🚀 Primeros Pasos

Sigue estas instrucciones para configurar y ejecutar el proyecto.

### 1. Prerrequisitos

- Python 3.11 o superior.
- Git.
- Una cuenta de Google con la API de Google Sheets habilitada.
- Un cluster de MongoDB (local o en la nube, como MongoDB Atlas).

### 2. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/discana-api.git
cd discana-api
```

### 3. Configurar el Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
```

### 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar Variables de Entorno y Credenciales

El proyecto utiliza un sistema flexible para manejar las credenciales, ideal tanto para desarrollo como para producción.

#### A) Para Desarrollo Local (Recomendado)

1.  **Fichero de Credenciales de Google**: Sigue la [guía de autenticación de `gspread`](https://gspread.readthedocs.io/en/latest/oauth2.html) para crear una cuenta de servicio. Descarga el fichero de credenciales JSON y guárdalo en la raíz del proyecto con el nombre `credenciales.json`. **Este fichero está incluido en `.gitignore` y nunca debe ser subido a tu repositorio.**

2.  **Fichero `.env`**: Crea un fichero llamado `.env` en la raíz para la conexión a MongoDB. Usa `.env.example` como plantilla.

    ```env
    # .env
    MONGO_SRV="mongodb+srv://user:password@host/database?retryWrites=true&w=majority"
    ```

Cuando ejecutes la aplicación, la lógica detectará que la variable de entorno `GOOGLE_CREDENTIALS_JSON` no está definida y usará automáticamente el fichero `credenciales.json`.

#### B) Para Producción (Obligatorio)

En un entorno de producción (como Cloud Run, Heroku, etc.), nunca debes usar ficheros de credenciales. En su lugar, el contenido del fichero JSON se pasa como una variable de entorno.

1.  **Transforma tus credenciales JSON**: Convierte el contenido de tu fichero `credenciales.json` en un string de una sola línea. Puedes usar un comando como este en tu terminal:

    ```bash
    cat credenciales.json | jq -c .
    ```

    El resultado será algo parecido a esto (un JSON compacto en una sola línea):
    `{"type": "service_account", "project_id": "...", ...}`

2.  **Configura las Variables de Entorno en tu Plataforma**: En el panel de configuración de tu proveedor de hosting, define las siguientes variables de entorno (o "secrets"):

    -   `GOOGLE_CREDENTIALS_JSON`: Pega aquí el string JSON de un solo renglón que generaste en el paso anterior.
    -   `MONGO_SRV`: La cadena de conexión a tu base de datos de producción.

La aplicación detectará automáticamente `GOOGLE_CREDENTIALS_JSON` y la usará para autenticarse, ignorando por completo la necesidad del fichero físico.

### 6. Ejecutar la Aplicación Localmente

```bash
# Gunicorn leerá MONGO_SRV desde el fichero .env
gunicorn --env-file .env -c gunicorn.conf.py app:app
```

La API estará disponible en `http://127.0.0.1:8080`.

---

## 🔌 Uso de la API

El endpoint principal para la sincronización de datos.

### `POST /admin/dump-google-sheet-data-to-db`

Lee datos de una hoja de cálculo y los carga en una colección de MongoDB. El endpoint primero borra los datos existentes en la colección antes de insertar los nuevos.

#### Petición
- **URL**: `/admin/dump-google-sheet-data-to-db`
- **Método**: `POST`
- **Headers**: `Content-Type: application/json`
- **Cuerpo**: `{"spreadsheet": "NombreSpreadsheet", "sheet": "NombreHoja", "collection": "nombreColeccion"}`

---

## 🛠️ Tecnologías Utilizadas

- **Framework**: Flask
- **Servidor WSGI**: Gunicorn
- **Base de Datos**: MongoDB (`pymongo`)
- **API de Google**: `gspread`, `oauth2client`
