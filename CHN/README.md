# DOCUMENTACIÓN DEL PAQUETE 'CHN'

### Instalación del Paquete

1. Se recomienda estar en un entorno virtual, ya sea creado con _pip_ o _conda_:
   - En el caso de pip: `$ python -m venv <nombre_del_entorno>`; y se activa de la siguiente forma: `$ <nombre_del_entorno>\Scripts\activate`.
   - En el caso de conda se puede tener un archivo yaml con ciertos paquetes para luego agregar el nuestro, o solo habilitar un entorno vacío. Colocaré ambas formas:
     i. Usando un .yaml: `conda env create -f <nombre_del_archivo>.yaml>`
     ii. Entorno vacío: `conda create -n <nombre_del_entorno> python=3.13.0 -y`
     Y se activa de una forma aun mas simple: `conda activate <nombre_del_entorno>`
2. Empaquetamos la librería usando _setuptools_ para generar los archivos de distribución: `python setup.py sdist bdist_wheel`.
3. Instalamos el paquete usando conda y pip, en ambos casos la sintaxis es la misma, unicamente cambia el comando inicial: `conda/pip install dist/<nombre_de_la_libreria>-<version>-py3-none.any.whl` (En caso de ya tener las librerías adicionales en el entorno virtual, se puede hacer que la nueva librería las utlice en lugar de descargar otras, esto puede ser muy util por los problemas que generan los **proxies** en entornos corporativos, solo se agrega el _flag_: `--no-deps`). En mi caso, el comando es: `conda install dist\CHN-1.0.1-py3-none-any.whl --no-deps` o `pip install dist\CHN-1.0.2-py3-none-any.whl`.
4. Puedes probar la instalación importando el paquete en un proyecto o usando lesta linea: `python -c "import nueva_libreria; print('Instalado correctamente')"`
