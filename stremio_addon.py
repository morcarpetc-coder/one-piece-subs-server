from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

# נתיבים חדשים לחלוטין (/v5/) שעוקפים את זיכרון הרפאים של השרת
@app.get("/v5/manifest.json")
def get_manifest(response: Response):
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return {
        "id": "com.mor.ops.v5",
        "version": "1.0.4",
        "name": "One Piece AI Subs 🚀", # סמל של טיל שנדע שהתקנו נכון
        "description": "Hebrew subtitles translated by AI",
        "resources": ["subtitles"],
        "types": ["series", "anime", "movie"],
        "catalogs": [],
        "idPrefixes": ["tt", "kitsu", "anilist", "tmdb"]
    }

@app.get("/v5/subtitles/{type}/{video_id}.json")
def get_subtitles(request: Request, type: str, video_id: str, response: Response):
    response.headers["Cache-Control"] = "no-store, max-age=0"
    print(f"🚀 STREMIO REQUEST REACHED PYTHON: {type} | {video_id}", flush=True)
    
    parts = video_id.split(":")
    episode = None
    
    if len(parts) >= 3:
        episode = parts[-1]
        
    if episode:
        expected_filename = f"one_piece_S01E{episode}.srt"
        file_path = os.path.join("output_subs", expected_filename)
        
        if os.path.exists(file_path):
            base_url = str(request.base_url).rstrip("/").replace("http://", "https://")
            print("✅ SUBTITLE FOUND! Sending to Stremio.", flush=True)
            
            # שולחים לסטרמיו שתי תוויות כדי להבטיח זיהוי של השפה
            return {
                "subtitles": [
                    {
                        "id": f"heb-op-{episode}",
                        "url": f"{base_url}/subs/{expected_filename}",
                        "lang": "heb",
                        "title": f"AI Translated - Ep {episode} 🇮🇱"
                    },
                    {
                        "id": f"he-op-{episode}",
                        "url": f"{base_url}/subs/{expected_filename}",
                        "lang": "he",
                        "title": f"AI Translated (HE) - Ep {episode} 🇮🇱"
                    }
                ]
            }
            
    print("❌ SUBTITLE NOT FOUND IN FOLDER.", flush=True)
    return {"subtitles": []}

@app.get("/subs/{filename}")
def serve_sub_file(filename: str, response: Response):
    response.headers["Cache-Control"] = "no-store, max-age=0"
    file_path = os.path.join("output_subs", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/plain")
    return {"error": "Not found"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)