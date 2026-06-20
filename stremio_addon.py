from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("output_subs", exist_ok=True)

# 1. הראדאר האולטימטיבי: מדפיס ללוג כל נשימה של סטרמיו
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    print(f"🌍 INCOMING: {request.method} {request.url.path}", flush=True)
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    print(f"✅ OUTGOING: {response.status_code}", flush=True)
    return response

# 2. תעודת זהות חדשה ללא שום מגבלות סינון לסטרמיו
@app.get("/manifest.json")
@app.get("/{any_prefix}/manifest.json")
def get_manifest():
    return {
        "id": "com.mor.ops.ultimate",
        "version": "1.0.6",
        "name": "One Piece AI Subs 🌟", # סמל כוכב
        "description": "Hebrew subtitles translated by AI",
        "resources": ["subtitles"],
        "types": ["series", "anime", "movie", "tv", "other"], # פתוח להכל
        "catalogs": [] # מחקנו את ה-idPrefixes לגמרי!
    }

# 3. נתיב "חסין כדורים" - בולע כל בקשה ושולף ממנה את המספר בסוף
@app.get("/subtitles/{type}/{video_id:path}")
@app.get("/{any_prefix}/subtitles/{type}/{video_id:path}")
def get_subtitles(request: Request, type: str, video_id: str):
    print(f"🌟 ADDON TRIGGERED: type={type}, video_id={video_id}", flush=True)
    
    clean_id = video_id.replace(".json", "")
    # שולף רק את המספרים מתוך תעודת הזהות של הפרק
    numbers = re.findall(r'\d+', clean_id)
    
    if numbers:
        ep_num = numbers[-1] # לוקח את המספר האחרון (עוקף את כל הפורמטים המוזרים של Kitsu ו-Torrentio)
        expected_filename = f"one_piece_S01E{ep_num}.srt"
        file_path = os.path.join("output_subs", expected_filename)
        
        if os.path.exists(file_path):
            base_url = str(request.base_url).rstrip("/").replace("http://", "https://")
            return {
                "subtitles": [
                    {
                        "id": f"heb-op-{ep_num}",
                        "url": f"{base_url}/subs/{expected_filename}",
                        "lang": "heb",
                        "title": f"AI Translated - Ep {ep_num} 🇮🇱"
                    }
                ]
            }
            
    return {"subtitles": []}

@app.get("/subs/{filename}")
@app.get("/{any_prefix}/subs/{filename}")
def serve_sub_file(filename: str):
    file_path = os.path.join("output_subs", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/x-subrip")
    return JSONResponse(status_code=404, content={"error": "Not found"})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)