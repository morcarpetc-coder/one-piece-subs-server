from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import re

app = FastAPI()

# הגדרת CORS מלאה ותקנית עבור סטרמיו בכל הפלטפורמות
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("output_subs", exist_ok=True)

# מנגנון הגנה גלובלי שמדפיס כל פנייה ומנטרל לחלוטין זיכרון מטמון ב-Edge
@app.middleware("http")
async def host_interceptor(request: Request, call_next):
    print(f"📡 [NET INCOMING] Path accessed: {request.url.path}", flush=True)
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/manifest.json")
def get_manifest():
    return {
        "id": "com.mor.onepiece.ai.subs.official.v1", # מזהה ייחודי חדש ונקי
        "version": "2.0.0",
        "name": "One Piece AI Subs 👑", # סימן של כתר לזיהוי הגרסה הסופית
        "description": "Hebrew subtitles translated by AI for One Piece",
        "resources": ["subtitles"],
        "types": ["series", "anime"],
        "catalogs": [],
        "idPrefixes": ["tt", "kitsu", "anilist", "mal"] # קריטי! בלעדי זה סטרמיו לא תשלח בקשות
    }

@app.get("/subtitles/{type}/{video_id}.json")
async def get_subtitles(type: str, video_id: str, request: Request):
    print(f"🎯 [ADDON TRIGGERED] Video ID requested: {video_id}", flush=True)
    
    clean_id = video_id.replace(".json", "")
    parts = clean_id.split(":")
    
    if not parts or len(parts) < 2:
        print("⚠️ [WARN] Request format not recognized.", flush=True)
        return {"subtitles": []}
        
    # חילוץ אגרסיבי של מספר הפרק (האיבר האחרון במערך התשובה של סטרמיו)
    episode = parts[-1]
    
    expected_filename = f"one_piece_S01E{episode}.srt"
    file_path = os.path.join("output_subs", expected_filename)
    
    print(f"🔍 [FILE SEARCH] Searching for file at: {file_path}", flush=True)
    
    if os.path.exists(file_path):
        base_url = str(request.base_url).rstrip("/")
        # אבטחת פרוטוקול HTTPS עבור אפליקציות סטרמיו בטלוויזיה/וב
        if "onrender.com" in base_url and not base_url.startswith("https://"):
            base_url = base_url.replace("http://", "https://")
            
        print(f"✅ [FOUND] Sending subtitle payload for episode {episode} to Stremio", flush=True)
        return {
            "subtitles": [
                {
                    "id": f"ai-heb-op-{episode}",
                    "url": f"{base_url}/subs/{expected_filename}",
                    "lang": "heb",
                    "title": f"עברית AI - פרק {episode} 🇮🇱"
                }
            ]
        }
        
    print(f"❌ [NOT FOUND] Missing SRT file for episode {episode}", flush=True)
    return {"subtitles": []}

@app.get("/subs/{filename}")
def serve_subtitle_file(filename: str):
    file_path = os.path.join("output_subs", filename)
    if os.path.exists(file_path):
        # הגשת הקובץ עם מזהה המדיה הרשמי של כתוביות כדי למנוע חסימת נגן
        return FileResponse(file_path, media_type="application/x-subrip", filename=filename)
    return JSONResponse(status_code=404, content={"error": "Subtitle file not found"})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)