from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd

app = FastAPI()


@app.get("/")
async def root():
    return {
        "Mensaje": "Bienvenido a la API de Juegos de Steam",
        "Autor" : "Alexis Yglesias"
        }

@app.get("/genero/{genero}")
async def PlayTimeGenre(genero: str):
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
        return JSONResponse(content={"Error": f"Ocurrió un error al procesar la solicitud.{e}"}, status_code=500)



