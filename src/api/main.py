import os
import sys
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.models.blueprint import Blueprint
from src.services.runner import GameRunner
from src.services.analyzer import BlueprintAnalyzer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UploadResponse(BaseModel):
    part1: int
    part2: int

class BlueprintQuality(BaseModel):
    id: str
    quality: int

class AnalyzeResponse(BaseModel):
    bestBlueprint: str
    blueprints: List[BlueprintQuality]

@app.post("/upload", response_model=UploadResponse)
async def upload_seed_file(file: UploadFile = File(...)):
    if file.filename and not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .txt files are allowed.")
        
    try:
        content = await file.read()
        text = content.decode("utf-8").strip()
        if not text:
            raise ValueError("The uploaded file is empty.")
            
        lines = text.splitlines()
        blueprints = []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            try:
                blueprints.append(Blueprint.parse(line))
            except ValueError as e:
                raise ValueError(f"Error parsing line {i + 1}: {str(e)}")
        
        if not blueprints:
            raise ValueError("No valid blueprints found in the file.")
        
        part1 = GameRunner.solve_part_one(blueprints)
        part2 = GameRunner.solve_part_two(blueprints)
        
        return UploadResponse(part1=part1, part2=part2)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/blueprints/analyze", response_model=AnalyzeResponse)
def analyze_blueprints():
    filepath = "seed.txt"
    try:
        content = BlueprintAnalyzer.read_blueprint_file(filepath)
        blueprints = BlueprintAnalyzer.parse_blueprints(content)
        results, best_bp_id = BlueprintAnalyzer.evaluate_blueprints(blueprints, time_limit=24)
        report = BlueprintAnalyzer.generate_report(results, best_bp_id)
        BlueprintAnalyzer.save_and_print_report(report, output_path="analysis.txt")
        
        return AnalyzeResponse(
            bestBlueprint=str(best_bp_id),
            blueprints=[BlueprintQuality(id=str(bp_id), quality=q) for bp_id, q in results]
        )
    except (FileNotFoundError, ValueError) as err:
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
def serve_frontend():
    index_path = os.path.join(os.path.dirname(__file__), "..", "..", "index.html")
    try:
        with open(index_path, "r") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("index.html not found", status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=4000, reload=True)

