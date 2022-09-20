# e-distribucion

## Distribución app

1. django-env: entorno virtual de la aplicación.

2. eDistribucion: carpeta donde está guardado la parte de django, son muy importante el settings.py (gestión de app)
, urls.py (rutas de la app).

3. queries: la app en si, es decir donde están las rutas, la lógica de la app y las plantillas (templates).

4. static: los archivos css y js.

## Ejecutar app

1. Activar entorno virtual (venv) en cmd: dentro del proyecto ejecutar (eDistribucion\django-env\Scripts\activate.bat)

2. Ejecutar python: en la ruta (e-distribucion\eDistribucion>) ejecutar (python manage.py runserver).

## instalar debug

1. Crear el launch.json para python en el proyecto.

2. instalar virtualenv (si no está instalado): pip install virtualenv (he tenido que ejecutarlo 2 veces para que se instalara)

3. crear entorno virtual dentro del proyecto: cd c:\ruta\proyecto y python -m venv nombre_entorno_virtual

4. Seleccionar interprete (si lo reconoce), el python.exe que está dentro de la carpeta nombre_entorno_virtual->Scripts->python.exe, si no introducir manualmente seleccionando esa opción (Python: Seleccionar Interprete) en ctl+shift+p. La ruta a introducir es absoluta.

5. Ejecutar el debugger.

## Por hacer

1. 1, 2 o 3 horas más baratas del día siguiente

2. Crear un logout

## Clonado

1. Crear un fichero .env en la ruta eDistribucion\eDistribucion, ahí poner el token de la api de esios (TOKEN_API_ESIOS=token), si queremos introducir un usuario y contraseña (USER=usuario)(PASSWORD=contraseña).

## urls

1. https://api.esios.ree.es/, api de esios.

2. url de esios para comparar los datos en la península: https://www.esios.ree.es/es/analisis/1001?vis=1&start_date=14-09-2022T01%3A00&end_date=14-09-2022T02%3A00&compare_start_date=13-09-2022T01%3A00&groupby=hour&compare_indicators=1739,1900&geoids=8741&zoom=6&latlng=40.01078714046552,-2.98828125
