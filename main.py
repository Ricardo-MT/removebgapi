from fastapi import FastAPI, File, UploadFile, Response, HTTPException, Header
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 
import uvicorn
from rembg import remove
from PIL import Image
import io
import os
from dotenv import load_dotenv

app = FastAPI(title='Remove Background', description='Introducing our powerful image background removal API! 🔥🖼️ that streamlines the background removal process for professionals across a wide range of industries! Our API leverages advanced machine learning algorithms to quickly and accurately remove the background from any image, making it perfect for graphic designers, photographers, social media managers, and more. With features like support for a variety of image formats, our API is designed to save you time and streamline your workflow. Plus, with 24/7 uptime and fast response times, you can count on our API to be there when you need it. Try it today and experience the power of advanced background removal at your fingertips! 🚀💻📷')
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

@app.get("/")
async def docs_redirect():
    return RedirectResponse(url='/docs')

@app.put('/remove_background/')
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

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv('HOST', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))