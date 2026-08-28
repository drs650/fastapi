from fastapi import Request, FastAPI
from fastapi.templating import Jinja2Templates

app = FastAPI() 

# Jinja2Templates: "templates" 폴더 안에서 템플릿 파일을 찾겠다는 설정
#               uvicorn을 실행하는 위치(현재 작업 폴더) 기준 상대경로
templates = Jinja2Templates(directory="templates")

@app.get("/hello/{name}")
async def hello(request: Request, name: str):
    return templates.TemplateResponse(
    request=request, name="hello.html", context={"name": name, "items": ["사과", "바나나", "오렌지"]}
    )

@app.get("/products")
async def product_list(request: Request):
    products = [
        {"id": 1, "name": "티셔츠", "price": 29000, "stock": 50},
        {"id": 2, "name": "청바지", "price": 59000, "stock": 30},
        {"id": 3, "name": "모자", "price": 15000, "stock": 0},
    ]
    return templates.TemplateResponse(
        request=request,
        name="products.html",
        context={"products": products},
    )