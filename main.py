from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import scipy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity


app = FastAPI()


@app.get("/")
async def root():
    return {
        "Mensaje": "Bienvenido a la API de Juegos de Steam",
        "Autor" : "Alexis Yglesias"
        }

@app.get("/horas_jugadas/{genero}")
async def PlayTimeGenre(genero: str):
    """Encuentra el año de lanzamiento con mas horas jugadas para el genero especificado 

    Args:
    - genero (str): Género específico para el cual se desea encontrar el año con mas horas jugadas.

    Returns:
    - dict: Diccionario que contiene el año de lanzamiento con mas horas jugadas para el genero especifico. Ejemplo de retorno: {"Año de lanzamiento con más horas jugadas para Género X" : 2013}

    """
    try:
        # Leer el dataframe desde el archivo parquet
        df = pd.read_parquet('generos.parquet')

        # Obtener la lista de géneros válidos
        generos_validos = list(df['genres'].drop_duplicates())

        # Validar si el género proporcionado está en la lista de géneros válidos
        if genero.capitalize() not in generos_validos:
            raise HTTPException(status_code=400, detail=f"El género '{genero}' no es válido.")
        
        # Filtrar el dataframe por el género especificado
        df = df[df['genres'] == genero.capitalize()]

        # Calcular la suma de horas jugadas por año para el género especificado
        df_agrupado = df.groupby('release_year')['playtime_forever'].sum().reset_index()

        # Encontrar el año con más horas jugadas para el género especificado
        año_mas_horas = df_agrupado.loc[df_agrupado['playtime_forever'].idxmax()]['release_year']

        # Construir la respuesta JSON con el año de lanzamiento con más horas jugadas
        content = { f"Año de lanzamiento con más horas jugadas para Género {genero.capitalize()}" : f"{año_mas_horas}" }

        return  JSONResponse(content=content)

    except HTTPException as e:
        # Capturar y retornar el detalle del error HTTPException
        content = {"Error": e.detail}
        return JSONResponse(content=content, status_code=e.status_code)
    
    except Exception as e:
        # Capturar y retornar un mensaje genérico en caso de otros errores
        return JSONResponse(content={"Error": f"Ocurrió un error al procesar la solicitud"}, status_code=500)


@app.get('/horas_jugadas_usuario/{genero}')
async def UserForGenre(genero: str):
    """
    Encuentra el usuario con más horas jugadas para un género específico.

    Args:
    - genero: Género específico para el cual se desea encontrar al usuario con más horas jugadas.

    Returns:
    - Diccionario que contiene el usuario con más horas jugadas para el genero dado y las horas jugadas por año para ese género.
    """
    try:
        # Leemos el dataframe
        df = pd.read_parquet('users_generos.parquet')
        
        # Convertir el género a minúsculas para realizar la búsqueda sin distinción entre mayúsculas y minúsculas
        genero_minuscula = genero.lower()

        # Filtrar el DataFrame para el género especificado (ignorando mayúsculas y minúsculas)
        df_filtered = df[df['genres'].str.lower().str.contains(genero_minuscula, na=False)]

        if df_filtered.empty:
            raise HTTPException(status_code=400, detail=f"No se encontraron datos para el género '{genero}'.")
        
        # Agrupar por 'user_id' y 'year', sumar las horas jugadas
        df_grouped = df_filtered.groupby(['user_id', 'release_year'])['playtime_forever'].sum().reset_index()

        if df_grouped.empty:
            raise HTTPException(status_code=400, detail=f"No se encontraron datos de horas jugadas para el género '{genero}'.")
        
        # Encontrar el usuario con la máxima suma de horas jugadas
        max_playtime_user = df_grouped.loc[df_grouped['playtime_forever'].idxmax(), 'user_id']

        # Filtrar el DataFrame para el usuario con máxima suma de horas jugadas
        df_user_max_playtime = df_grouped[df_grouped['user_id'] == max_playtime_user]

        # Crear la lista de horas jugadas por año en el formato esperado
        horas_jugadas = []
        for index, row in df_user_max_playtime.iterrows():
            horas_jugadas.append({
                'Año': int(row['release_year']),  # Convertir el año a entero
                'Horas': int(row['playtime_forever'])  # Convertir las horas a entero
            })

        content = {
            f"Usuario con más horas jugadas para '{genero}'": max_playtime_user,
            "Horas jugadas": horas_jugadas
        }

        return  JSONResponse(content=content)

    except HTTPException as e:
        # Capturar y retornar el detalle del error HTTPException
        content = {"Error": e.detail}
        return JSONResponse(content=content, status_code=e.status_code)

    except Exception as e:
        # Capturar y retornar un mensaje genérico en caso de otros errores
        return JSONResponse(content={"Error": f"Ocurrió un error al procesar la solicitud{e}"}, status_code=500)

@app.get('/recomendacion_juego/{item_id}')
async def recomendacion_juego(item_id: int):
    """
    Función para obtener juegos recomendados para un juego específico en una muestra aleatoria del dataframe.
    
    Args:
    - item_id: Id del juego para el cual se desean obtener recomendaciones.
    
    Returns:
    - Lista de 5 nombres de juegos recomendados únicos (sin repeticiones) que no incluye el juego dado como argumento.
    """
    try:
        df = pd.read_parquet('modelo.parquet')

        # Obtener la lista de géneros válidos
        items_validos = list(df['item_id'].drop_duplicates())

        # Validar si el género proporcionado está en la lista de géneros válidos
        if item_id not in items_validos:
            raise HTTPException(status_code=400, detail=f"El id '{item_id}' no es válido.")
        
        #Inicializar CountVectorizer para convertir texto en una matriz de recuentos de términos
        count_vectorizer = CountVectorizer()
        text_matrix = count_vectorizer.fit_transform(df['combined_text'])

        #Normalizar características numéricas
        numeric_features = ['negative_reviews', 'neutral_reviews', 'positive_reviews','no_recommend_count','recommend_count'] 
        scaler = StandardScaler()
        numeric_matrix = scaler.fit_transform(df[numeric_features])

        # Combinar matrices de características de texto y numéricas. Usamos el modulo scipy.sparse que optimiza los calculos para matrices que tienen en su mayoria ceros.
        combined_matrix = scipy.sparse.hstack((text_matrix, numeric_matrix))

        # Calcula la matriz de similitud de coseno
        cosine_sim = cosine_similarity(combined_matrix, combined_matrix)

        # Obtener el índice del juego correspondiente al nombre dado
        idx = df[df['item_id'] == item_id].index[0]
        # Calcular la similitud del juego con todos los demás juegos en la muestra
        sim_scores = list(enumerate(cosine_sim[idx]))

        # Ordenar los juegos según las puntuaciones de similitud
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Obtener los índices de los juegos más similares (excluyendo el juego dado)
        sim_scores = [score for score in sim_scores if df.iloc[score[0]]['item_id'] != item_id][:5]

        # Obtener los nombres de los juegos recomendados (excluyendo repeticiones)
        recommended_games = []
        seen_games = set()
        for score in sim_scores:
            game_name = df.iloc[score[0]]['title']
            if game_name not in seen_games:
                recommended_games.append(game_name)
                seen_games.add(game_name)

        return  JSONResponse(content=recommended_games)


    except HTTPException as e:
        # Capturar y retornar el detalle del error HTTPException
        content = {"Error": e.detail}
        return JSONResponse(content=content, status_code=e.status_code)

    except Exception as e:
        # Capturar y retornar un mensaje genérico en caso de otros errores
        return JSONResponse(content={"Error": f"Ocurrió un error al procesar la solicitud{e}"}, status_code=500)

