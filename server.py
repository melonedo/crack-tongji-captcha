from fastapi import FastAPI
from pydantic import BaseModel
from crack_captcha import crack, read_base64
from find_chars import CharacterTooComplicated

app = FastAPI()

class CrackQuery(BaseModel):
    data_url: str

@app.post('/crack')
def crack_handler(query: CrackQuery):
    ans = crack(read_base64(query.data_url))
    print(ans)
    try:
        return {"success": True, "ans": ans}
    except CharacterTooComplicated:
        return {"success": False}
