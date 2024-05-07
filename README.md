# Proyecto de API para Recomendación de Juegos de Steam

Este proyecto consiste en una API que permite acceder a información específica sobre juegos de la plataforma Steam a través de 5 endpoints diferentes. Los datos están distribuidos en tres conjuntos (datasets) que contienen información detallada sobre usuarios, horas jugadas, nombres de juegos, reseñas, recomendaciones y más.

El proyecto incluye un sexto endpoint que utiliza un algoritmo de similitud de cosenos implementado con Scikit-Learn para generar recomendaciones personalizadas basadas en un nombre de juego dado.

## Instalación

Para utilizar esta API, sigue estos pasos:

1. Clona el repositorio desde GitHub:

   ```bash
   git clone https://github.com/alexis4320/Sistema_Recomendacion_Steam_Games.git
   ```

2. Accede al directorio del proyecto:

   ```bash
   cd Sistema_Recomendacion_Steam_Game
   ```


3. Instala las dependencias necesarias utilizando pip:
   
   ```bash
   pip install -r requirements.txt
   ```

## Uso

Una vez instaladas las dependencias, puedes ejecutar la API de la siguiente manera:

   ```bash
   uvicorn main:app --reload
   ```

La API estará disponible en `http://localhost:8000`.

## Endpoints

La API consta de los siguientes endpoints:

`/PlayTimeGenre/{genero}`: Devuelve el año con mas horas jugadas para dicho género.

`/UserForGenre/{genero}`: Devuelve el usuario que acumula más horas jugadas para el género dado y una lista de la acumulación de horas jugadas por año.

`/UsersRecommend/{ano}`: Devuelve el top 3 de juegos MÁS recomendados por usuarios para el año dado. (reviews.recommend = True y comentarios positivos/neutrales).

`/UsersNotRecommend/{ano}`: Devuelve el top 3 de juegos MENOS recomendados por usuarios para el año dado. (reviews.recommend = False y comentarios negativos).

`/sentiment_analysis{ano}`: Según el año de lanzamiento, se devuelve una lista con la cantidad de registros de reseñas de usuarios que se encuentren categorizados con un análisis de sentimiento.

Además, existe un endpoint especial para obtener recomendaciones personalizadas basadas en un nombre de juego dado:

`/recomendacion_juego/{item_id}`: Ingresando el id de producto, deberíamos recibir una lista con 5 juegos recomendados similares al ingresado.

## Estructura del Proyecto

La estructura del proyecto es la siguiente:

+ Data/: Directorio que contiene los conjuntos de datos utilizados.
+ Notebooks/: Directorio que contiene cuadernos Jupyter utilizados para análisis exploratorio y desarrollo.
+ main.py: Archivo principal que se utiliza para el despliegue de la API con FastAPI.

## Tecnologías Utilizadas

Este proyecto utiliza las siguientes tecnologías y librerías:

+ Python: Lenguaje de programación principal.
+ Pandas: Para manipulación y análisis de datos.
+ Numpy: Para calculos con matrices y algunos calculo estadisticos
+ Scikit-Learn: Para implementar el algoritmo de similitud del coseno y generar recomendaciones.
+ FastAPI: Framework utilizado para desarrollar la API web.
+ Uvicorn: Servidor ASGI utilizado para ejecutar la API.
+ seaborn: Calulos estadisticos
+ scipy: Calculos con grandes arreglos
+ pyarrow: Para manipulación de archivo parquet

## Desarrollo y Licencia

Este proyecto es desarrollado por un individuo y se distribuye bajo una licencia pública, lo que significa que cualquiera puede utilizar y modificar el código según sus necesidades.


## Recursos Adicionales

Se ha creado un video explicativo que muestra el funcionamiento de la API y cómo utilizarla. Puedes acceder al video en enlace al video explicativo.








