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
from src.solver.diamond_solver import DiamondSolver

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
    # Read seed.txt file from current working directory or directory above,
    # and fall back to the hardcoded addendum 2 blueprints if not found.
    seed_paths = [
        "seed.txt",
        os.path.join(os.path.dirname(__file__), "..", "..", "seed.txt")
    ]
    content = None
    for path in seed_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                break
            except Exception:
                pass
                
    if not content:
        content = (
            "Blueprint 1: Each ore robot costs 4 ore. Each clay robot costs 2 ore. Each obsidian robot costs 3 ore and 14 clay. Each geode robot costs 2 ore and 7 obsidian. Each diamond robot costs 1 geode, 8 clay and 7 obsidian.\n"
            "Blueprint 2: Each ore robot costs 2 ore. Each clay robot costs 3 ore. Each obsidian robot costs 3 ore and 8 clay. Each geode robot costs 3 ore and 12 obsidian. Each diamond robot costs 3 geode, 2 clay and 3 obsidian."
        )

    try:
        lines = content.splitlines()
        blueprints = []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            try:
                blueprints.append(Blueprint.parse(line))
            except ValueError as e:
                raise ValueError(f"Error parsing blueprint line {i + 1}: {str(e)}")
        
        if not blueprints:
            raise ValueError("No valid blueprints found to analyze.")

        # Solve each blueprint at 24 minutes to get quality (quality = id * max_diamonds)
        results = []
        best_bp_id = None
        max_quality = -1
        
        for bp in blueprints:
            max_diamonds = DiamondSolver(bp, 24).solve()
            quality = bp.id * max_diamonds
            results.append((bp.id, quality))
            if quality > max_quality:
                max_quality = quality
                best_bp_id = bp.id
        
        if not results:
            raise ValueError("Evaluation produced no results.")

        # Construct textual report exactly as in Addendum 3 specifications
        report_lines = []
        for bp_id, quality in results:
            report_lines.append(f"Blueprint {bp_id}: {quality}")
        
        report_content = "\n".join(report_lines) + f"\n\nBest blueprint is the blueprint {best_bp_id}.\n"
        
        # 1. Output to standard output
        print(report_content, end="", flush=True)
        
        # 2. Write to ./analysis.txt
        analysis_path = "analysis.txt"
        with open(analysis_path, "w", encoding="utf-8") as f:
            f.write(report_content)
            
        # 3. Return response in specified format (Addendum 4)
        return AnalyzeResponse(
            bestBlueprint=str(best_bp_id),
            blueprints=[BlueprintQuality(id=str(bp_id), quality=q) for bp_id, q in results]
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
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

