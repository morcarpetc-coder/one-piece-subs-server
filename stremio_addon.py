from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

app = FastAPI()

# פתיחת כל שערי האבטחה (CORS) לסטרמיו
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("output_subs", exist_ok=True)

@app.get("/manifest.json")
def get_manifest(response: Response):
    # אוסר על הדפדפן וסטרמיו לשמור את התוסף בזיכרון
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return {
        "id": "com.mor.ops.v4", # שינינו תעודת זהות לחלוטין
        "version": "1.0.3",
        "name": "One Piece AI Subs ⚓", # סמל העוגן החדש
        "description": "Hebrew subtitles translated by AI for One Piece.",
        "resources": ["subtitles"],
        "types": ["series", "anime", "movie"],
        "catalogs": [],
        "idPrefixes": ["tt", "kitsu", "anilist", "myanimelist"]
    }

@app.get("/subtitles/{type}/{video_id}.json")
def get_subtitles(request: Request, type: str, video_id: str, response: Response):
    # הפקודה הקריטית: אוסרת על רנדר (הענן) לשמור תשובות ריקות ישנות!
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    
    print(f"⚓ STREMIO ASKED FOR: type={type}, video_id={video_id}", flush=True)
    
    parts = video_id.split(":")
    episode = None
    
    if len(parts) >= 3:
        episode = parts[-1]
    
    if episode:
        expected_filename = f"one_piece_S01E{episode}.srt"
        file_path = os.path.join("output_subs", expected_filename)
        
        if os.path.exists(file_path):
            base_url = str(request.base_url).rstrip("/").replace("http://", "https://")
            print(f"✅ FOUND SUBTITLE: Sending to Stremio", flush=True)
            return {
                "subtitles": [
                    {
                        "id": f"heb-op-{episode}",
                        "url": f"{base_url}/subs/{expected_filename}",
                        "lang": "heb",
                        "title": f"AI Translated - Ep {episode} 🇮🇱"
                    }
                ]
            }
            
    print(f"❌ NOT FOUND for episode {episode}", flush=True)
    return {"subtitles": []}

# נתיב חכם להורדת הקובץ שפותר בעיות חסימה של נגנים
@app.get("/subs/{filename}")
def serve_sub_file(filename: str, response: Response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    file_path = os.path.join("output_subs", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/plain")
    return {"error": "Subtitle not found"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)