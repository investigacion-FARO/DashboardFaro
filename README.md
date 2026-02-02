# 📊 Herramienta de Seguimiento Estratégico - FARO

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dashboardfaroie.streamlit.app/)

Este repositorio aloja el código y los datos del **Dashboard de Seguimiento de Indicadores Estratégicos** de Grupo FARO. Es una aplicación interactiva diseñada para visualizar el desempeño institucional en tiempo real.

## 🔗 Enlaces Rápidos

* **🚀 Ver Aplicación Desplegada:** [https://dashboardfaroie.streamlit.app/](https://dashboardfaroie.streamlit.app/)
* **💻 Repositorio en GitHub:** [https://github.com/investigacion-FARO/DashboardFaro](https://github.com/investigacion-FARO/DashboardFaro)

## 🚀 Características Principales

* **Nivel 1 – Resumen Ejecutivo:** Vistazo rápido a las métricas clave (Proyectos, Sostenibilidad, Beneficiarios) y visualización jerárquica (Treemap) del desempeño por áreas.
* **Nivel 2 – Comparativo:** Análisis de mapas de calor (Heatmaps) y rankings de desempeño entre diferentes áreas y ejes estratégicos.
* **Nivel 3 – Detalle y Reportes:** Tabla detallada de indicadores con opción de **descarga en Excel (.xlsx)** con formato estilizado y profesional.
* **🤖 Asistente IA Integrado:** Chatbot capaz de responder preguntas sobre los datos en tiempo real, impulsado por modelos de Inteligencia Artificial.

---

## ⚠️ Actualización de Datos (IMPORTANTE)

La aplicación está configurada para leer los datos **directamente desde este repositorio**. Para actualizar la información que se muestra en el tablero, **no es necesario tocar el código**, simplemente debes reemplazar los archivos de Excel.

### Pasos para actualizar la información:

1.  **Prepara tus archivos:** Asegúrate de que tus archivos de Excel actualizados tengan **exactamente** los siguientes nombres (respetando mayúsculas y minúsculas):
    * `1.BaseIncadoresAgregados.xlsx`
    * `2.BaseIncadoresDetalle.xlsx`

2.  **Sube los archivos a GitHub:**
    * Entra a la carpeta **`BasesDatos`** de este repositorio.
    * Haz clic en el botón **"Add file"** ↗️ **"Upload files"**.
    * Arrastra tus archivos nuevos. GitHub te avisará que estás reemplazando los archivos existentes.

3.  **Guarda los cambios:**
    * Haz clic en el botón verde **"Commit changes"**.

4.  **Refresca la App:**
    * Los cambios suelen reflejarse automáticamente tras unos minutos. Si no lo hacen, entra a tu panel de Streamlit Cloud y selecciona **"Reboot App"** o **"Clear Cache"** para forzar la actualización.

---

## 🛠️ Requisitos e Instalación

Si deseas ejecutar este proyecto en tu máquina local o entender qué librerías necesita el servidor:

### 1. Archivo `requirements.txt`
Para que la aplicación funcione correctamente (especialmente la descarga de Excel con formato), el archivo `requirements.txt` debe contener:

```text
streamlit
pandas
numpy
altair
plotly
openai
openpyxl
xlsxwriter

```

### 2. Ejecución Local

1. Clona el repositorio:
```bash
git clone [https://github.com/investigacion-FARO/DashboardFaro.git](https://github.com/investigacion-FARO/DashboardFaro.git)

```


2. Instala las dependencias:
```bash
pip install -r requirements.txt

```


3. Configura las claves (Secrets):
* Crea un archivo `.streamlit/secrets.toml` para tu `OPENROUTER_API_KEY` si deseas usar la funcionalidad de IA.


4. Ejecuta la app:
```bash
streamlit run dashboardFARO.py

```



## 📂 Estructura del Proyecto

* `dashboardFARO.py`: El script principal de la aplicación.
* `BasesDatos/`: Carpeta contenedora de los archivos Excel fuente.
* `requirements.txt`: Lista de dependencias para el despliegue.

---

*Desarrollado para el seguimiento estratégico de Grupo FARO.*
