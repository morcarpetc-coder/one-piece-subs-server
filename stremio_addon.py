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

ONE_PIECE_IMDB_ID = "tt0388629"

@app.get("/manifest.json")
def get_manifest():
    return {
        "id": "com.mor.onepiecesubs",
        "version": "1.0.1", # עלינו גרסה כדי שסטרמיו תתאפס
        "name": "One Piece AI Subs",
        "description": "Hebrew subtitles translated by AI for One Piece.",
        "resources": ["subtitles"],
        "types": ["series", "anime", "movie"], # פתחנו את התוסף לכל סוגי התוכן
        "catalogs": [],
        "idPrefixes": ["tt", "kitsu"] # הוספנו תמיכה במזהי אנימה
    }

@app.get("/subtitles/{type}/{video_id}.json")
def get_subtitles(request: Request, type: str, video_id: str):
    # שורת איתור באגים - תדפיס ב-Render כל פנייה של סטרמיו לשרת
    print(f"🔥 STREMIO ASKED FOR: type={type}, video_id={video_id}")
    
    parts = video_id.split(":")
    
    # בודקים אם המזהה תואם לוואן פיס
    if len(parts) >= 3 and parts[0] == ONE_PIECE_IMDB_ID:
        season = parts[1]
        episode = parts[2]
        
        expected_filename = f"one_piece_S{season.zfill(2)}E{episode}.srt"
        file_path = os.path.join("output_subs", expected_filename)
        
        if os.path.exists(file_path):
            base_url = str(request.base_url).rstrip("/")
            return {
                "subtitles": [
                    {
                        "id": f"heb-op-{episode}",
                        "url": f"{base_url}/subs/{expected_filename}",
                        "lang": "heb",
                        "title": f"AI Translated - Ep {episode}"
                    }
                ]
            }
            
    return {"subtitles": []}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)