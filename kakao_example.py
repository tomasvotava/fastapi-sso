import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request

from fastapi_sso.sso.kakao import KakaoSSO

load_dotenv(verbose=True)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


app = FastAPI()

google_sso = KakaoSSO(
    client_id=os.getenv("REST_API_KEY"),
    client_secret=os.getenv("REST_API_KEY"),
    redirect_uri=os.getenv("REDIRECT_URI"),
    use_state=False,
    allow_insecure_http=True,
)


@app.get("/kakao/login")
async def kakao():
    return await google_sso.get_login_redirect()


@app.get("/kakao/callback")
async def microsoft_callback(request: Request):
    user = await google_sso.verify_and_process(request)
    return user


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
