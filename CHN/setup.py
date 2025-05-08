from setuptools import setup, find_packages

setup(
    name='CHN',
    version='3.0.6',
    description='Colección de métodos y funciones útiles para análisis y ciencia de datos, web-scrapping y tareas comunes.',
    author='Diego Sarceño',
    author_email='dsarceno68@gmail.com',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'scikit-learn',
        'scipy',
        'seaborn',
        'selenium',
        'requests',
        'statsmodels',
        'sympy',
        'sqlalchemy',
        'pyodbc',
        'openpyxl',
        'ipykernel',
        'polars',
        'beautifulsoup4',
        'python-dotenv'
    ],
    include_package_data=True,
    package_data={
        'CHN': ['CHN/credenciales.json', 'CHN/.env'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='<=3.13.0',
)