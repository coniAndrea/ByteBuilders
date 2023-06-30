# ByteBuilders

¡Bienvenido a ByteBuilders! Este es un proyecto basado en Flask para construir una aplicación web. A continuación, encontrarás las instrucciones para configurar y ejecutar el proyecto en tu entorno local.

## Instrucciones de configuración

### 1. Clonar el repositorio

Para comenzar, clona el repositorio de ByteBuilders en tu entorno de desarrollo local. Puedes hacerlo ejecutando el siguiente comando en tu terminal:

```
git clone https://github.com/coniAndrea/ByteBuilders.git
```

### 2. Instalar las dependencias

Asegúrate de tener Python y pip instalados en tu sistema. Luego, en tu terminal, navega hasta la carpeta raíz del proyecto y ejecuta el siguiente comando para instalar las dependencias necesarias:

```
pip install -r requirements.txt
```

Este comando instalará Flask y otras dependencias requeridas para el proyecto.


### 3. Configurar la base de datos

Antes de ejecutar el proyecto, asegúrate de tener una base de datos llamada "bytebuilders" creada en tu entorno de MySQL. Puedes utilizar las herramientas de administración de MySQL, como phpMyAdmin o la línea de comandos, para crear la base de datos.

**Importar la base de datos**

Si necesitas importar la base de datos proporcionada en el archivo SQL, puedes utilizar el comando `flask import_db`. Asegúrate de haber configurado correctamente la conexión a tu base de datos en el archivo `app.py` antes de ejecutar este comando.

```
flask import_db
```
### 4. Ejecutar el proyecto

Una vez instaladas las dependencias, estás listo para ejecutar el proyecto. En tu terminal, dentro de la carpeta raíz del proyecto, ejecuta el siguiente comando:

```
python app.py
```

Esto iniciará la aplicación Flask y estará disponible en tu navegador en la dirección `http://localhost:5000`.




## Instrucciones adicionales

### Agregar nuevos requerimientos

Si necesitas agregar nuevos paquetes o bibliotecas a tu proyecto, asegúrate de agregarlos al archivo `requirements.txt`. Puedes hacerlo ejecutando el siguiente comando:

```
pip freeze > requirements.txt
```

Esto guardará todas las dependencias actuales en el archivo `requirements.txt`. Asegúrate de compartir el archivo actualizado junto con tu código.



---

¡Eso es todo! Con estas instrucciones, deberías poder configurar y ejecutar el proyecto ByteBuilders en tu entorno local. Si tienes alguna pregunta o enfrentas algún problema, no dudes en consultarnos. ¡Disfruta construyendo con ByteBuilders!
