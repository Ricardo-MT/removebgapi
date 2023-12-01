from fastapi import FastAPI, File, UploadFile, Response, HTTPException, Header
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 
from rembg import remove
from PIL import Image
import io
import os
from dotenv import load_dotenv

app = FastAPI(title='Remove Background', description='Introducing our powerful image background removal API', docs_url=None)
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

@app.post('/')
async def remove_background(X_API_Key: str | None = Header(default=None), input_file: UploadFile = File(...)):
    # Check if request has API key
    api_key = os.getenv('API_KEY')
    if api_key != X_API_Key:
        print('API key is invalid ', X_API_Key, api_key)
        raise HTTPException(status_code=404, detail='Not found')
    try:
        input_image = Image.open(io.BytesIO(await input_file.read()))
    except Exception as e:
        raise HTTPException(status_code=400, detail='Failed to read input image')

    try:
        output_image = remove(input_image)
    except Exception as e:
        raise HTTPException(status_code=500, detail='Failed to process input image')

    output_file = io.BytesIO()
    try:
        output_image.save(output_file, format='PNG')
    except Exception as e:
        raise HTTPException(status_code=500, detail='Failed to save output image')

    response = Response(content=output_file.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=output.png'
    response.headers['Content-Type'] = 'image/png'

    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )

app.mount("/static", StaticFiles(directory="static"), name="static")
