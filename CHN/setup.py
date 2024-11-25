from setuptools import setup, find_packages

setup(
    name='CHN',
    version='1.0',
    description='Métodos útiles y recurrentes en roles desempeñados en el CHN.',
    author='Diego Sarceño',
    author_email='dsarceno68@gmail.com',
    packages=find_packages(),
    install_requires=[
        'pyodbc==5.2.0',
        'pandas==2.2.3',
        'SQLAlchemy==2.0.36'
    ],
    include_package_data=True,
    package_data={
        'metodosINE' : ['metodosINE/credenciales.json']
    }
)
