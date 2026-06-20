from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("output_subs", exist_ok=True)
app.mount("/subs", StaticFiles(directory="output_subs"), name="subs")

@app.get("/manifest.json")
def get_manifest():
    return {
        "id": "com.mor.ops.v3", # מזהה חדש לחלוטין! סטרמיו תחשוב שזה תוסף אחר לגמרי
        "version": "1.0.2",
        "name": "One Piece AI Subs 🔥", # הוספנו סמיילי כדי שנדע בוודאות שהתקנו את החדש
        "description": "Hebrew subtitles translated by AI for One Piece.",
        "resources": ["subtitles"],
        "types": ["series", "anime", "movie"],
        "catalogs": [],
        "idPrefixes": ["tt", "kitsu", "anilist", "myanimelist"] # עונים לכל שפות האנימה שקיימות
    }

@app.get("/subtitles/{type}/{video_id}.json")
def get_subtitles(request: Request, type: str, video_id: str):
    # flush=True - פקודה שמכריחה את פייתון לזרוק את ההדפסה ל-Render באותה שנייה!
    print(f"🔥 STREMIO ASKED FOR: type={type}, video_id={video_id}", flush=True)
    
    parts = video_id.split(":")
    episode = None
    
    # שליפה אגרסיבית של מספר הפרק מתוך הבקשה של סטרמיו
    if len(parts) >= 3:
        episode = parts[-1]
    
    if episode:
        expected_filename = f"one_piece_S01E{episode}.srt"
        file_path = os.path.join("output_subs", expected_filename)
        
        print(f"🔍 Searching for file: {file_path}", flush=True)
        
        if os.path.exists(file_path):
            base_url = str(request.base_url).rstrip("/").replace("http://", "https://")
            print(f"✅ File found! Sending to Stremio.", flush=True)
            
            return {
                "subtitles": [
                    {
                        "id": f"heb-op-{episode}",
                        "url": f"{base_url}/subs/{expected_filename}",
                        "lang": "heb",
                        "title": f"AI Translated - Ep {episode} 🇮🇱" # הוספנו דגל לזיהוי קל
                    }
                ]
            }
        else:
            print(f"❌ File not found.", flush=True)
            
    return {"subtitles": []}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)