#!/usr/bin/env python3
"""
PlanMySky Weather API - FastAPI Backend
Provides endpoints for historical weather predictions

Author: PlanMySky Team
NASA Space Apps Challenge
"""

from fastapi import FastAPI, HTTPException, Query, Path as PathParam
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import sys
from pathlib import Path

# Add src/modeling to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src" / "modeling"))
from historical_pattern_predictor import HistoricalWeatherPredictor

# Initialize FastAPI
app = FastAPI(
    title="PlanMySky Weather API",
    description="Historical weather pattern analysis for any date",
    version="1.0.0"
)

# Import Google Calendar router (after app initialization)
try:
    from google_calendar import router as calendar_router
    app.include_router(calendar_router)
    print("✓ Google Calendar integration loaded")
except Exception as e:
    print(f"⚠ Google Calendar integration not available: {e}")
    print("  Calendar features will be disabled.")

# Add Auth Router
try:
    from auth_routes import auth_router
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    print("✓ Auth Router loaded")
except Exception as e:
    print(f"⚠ Auth Router not available: {e}")
    print("  Authentication features will not be avaialable.")

# CORS middleware (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global predictors (one per location, loaded on-demand)
predictors = {}  # {location_name: predictor_instance}
available_locations = []
predictor_status = {
    "loaded": False,
    "error": None,
    "locations_available": []
}


# ============================================================
# MODELS (Request/Response schemas)
# ============================================================

class WeatherRequest(BaseModel):
    """Request model for weather prediction"""
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    day: int = Field(..., ge=1, le=31, description="Day (1-31)")
    location: str = Field(..., description="Location identifier")
    window_days: int = Field(7, ge=0, le=14, description="Include dates within ±N days")

    class Config:
        json_schema_extra = {
            "example": {
                "month": 7,
                "day": 15,
                "location": "kathmandu_nepal",
                "window_days": 7
            }
        }


class MonthlyStatsRequest(BaseModel):
    """Request model for monthly statistics"""
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    location: str = Field(..., description="Location identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "month": 7,
                "location": "kathmandu_nepal"
            }
        }


class StatusResponse(BaseModel):
    """API status response"""
    status: str
    locations_available: list
    total_locations: int
    features_available: Dict[str, bool]


# ============================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================

def get_available_locations():
    """Scan for available locations in processed data directory"""
    from pathlib import Path

    data_dir = Path(__file__).parent.parent.parent / "data" / "processed"

    if not data_dir.exists():
        return []

    locations = []
    for item in data_dir.iterdir():
        if item.is_dir():
            # Check if location has processed data
            has_data = bool(list(item.glob("*.parquet")) or list(item.glob("*.csv")))
            if has_data:
                locations.append(item.name)

    return sorted(locations)


def load_predictor(location_name: str):
    """Load predictor for a specific location"""
    global predictors

    if location_name in predictors:
        return predictors[location_name]

    try:
        predictor = HistoricalWeatherPredictor(location_name=location_name)

        if predictor.load_historical_data():
            predictors[location_name] = predictor
            print(f"✓ Loaded predictor for {location_name}")
            return predictor
        else:
            print(f"✗ Failed to load data for {location_name}")
            return None

    except Exception as e:
        print(f"✗ Error loading predictor for {location_name}: {e}")
        return None


@app.on_event("startup")
async def startup_event():
    """Discover available locations and pre-load data on startup"""
    global available_locations, predictor_status

    try:
        print("Discovering available locations...")
        available_locations = get_available_locations()

        if available_locations:
            predictor_status["loaded"] = True
            predictor_status["locations_available"] = available_locations
            print(f"✓ Found {len(available_locations)} location(s): {', '.join(available_locations)}")

            # Skip pre-loading for faster startup - data will be loaded on-demand
            print("⚡ Fast startup mode: Data will be loaded on first request")
            print(f"✓ Ready! {len(available_locations)} location(s) available")
        else:
            predictor_status["error"] = "No processed data found"
            print(f"✗ No processed data locations found")

    except Exception as e:
        predictor_status["error"] = str(e)
        print(f"✗ Error discovering locations: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down weather API...")


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "message": "PlanMySky Weather API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "/api/status"
    }


@app.get("/api/status", response_model=StatusResponse, tags=["Status"])
async def get_status():
    """
    Get API status and availability

    Returns information about available locations and features.
    """
    return {
        "status": "online" if predictor_status["loaded"] else "error",
        "locations_available": predictor_status["locations_available"],
        "total_locations": len(predictor_status["locations_available"]),
        "features_available": {
            "historical_prediction": predictor_status["loaded"],
            "monthly_statistics": predictor_status["loaded"],
            "multi_location": predictor_status["loaded"],
            "json_download": predictor_status["loaded"],
            "ml_forecast": False  # Future feature
        }
    }


@app.get("/api/locations", tags=["Locations"])
async def get_locations():
    """
    Get list of available locations with metadata

    Returns all locations that have processed weather data available,
    including coverage area information.

    **Returns:**
    - List of location identifiers with metadata
    - Coverage area details (lat/lon bounds)
    - Each location can be used in prediction endpoints

    **Example:**
    ```
    GET /api/locations
    ```
    """
    from pathlib import Path
    import json

    locations_detail = []

    raw_data_dir = Path(__file__).parent.parent.parent / "data" / "raw"

    for location in available_locations:
        # Try to read metadata file
        metadata_path = raw_data_dir / location / "metadata.json"

        location_info = {"name": location}

        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)

                location_info.update({
                    "display_name": metadata.get('location_name', location),
                    "latitude": metadata.get('latitude'),
                    "longitude": metadata.get('longitude'),
                    "coverage_km": metadata.get('coverage_km', 55),
                    "coverage_area": metadata.get('coverage_area'),
                    "data_start": metadata.get('start_date'),
                    "data_end": metadata.get('end_date')
                })
            except Exception as e:
                print(f"Error reading metadata for {location}: {e}")

        locations_detail.append(location_info)

    return {
        "locations": locations_detail,
        "total": len(available_locations)
    }


@app.get("/api/predict/{month}/{day}", tags=["Weather Prediction"])
async def predict_weather(
    month: int = PathParam(..., ge=1, le=12, description="Month (1-12)"),
    day: int = PathParam(..., ge=1, le=31, description="Day (1-31)"),
    location: str = Query(..., description="Location identifier"),
    window_days: int = Query(7, ge=0, le=14, description="Include dates within ±N days")
):
    """
    Get weather prediction for a specific date

    Analyzes historical weather patterns for the specified date across all available years.

    **Parameters:**
    - **month**: Month (1-12)
    - **day**: Day (1-31)
    - **window_days**: Include dates within ±N days (default: 7)

    **Returns:**
    - Comprehensive weather statistics including:
      - Rainfall probability and expected amount
      - Temperature range and averages
      - Wind speed statistics
      - Cloud cover percentages
      - Extreme weather probabilities
      - Recent years breakdown

    **Example:**
    ```
    GET /api/predict/7/15?location=kathmandu_nepal&window_days=7
    ```
    """
    if not predictor_status["loaded"]:
        raise HTTPException(
            status_code=503,
            detail=f"Predictor not available: {predictor_status.get('error', 'Unknown error')}"
        )

    # Validate location
    if location not in available_locations:
        raise HTTPException(
            status_code=404,
            detail=f"Location '{location}' not found. Available: {', '.join(available_locations)}"
        )

    try:
        # Validate date
        try:
            datetime(2000, month, day)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date: month={month}, day={day}"
            )

        # Load predictor for location
        predictor = load_predictor(location)
        if not predictor:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load predictor for location: {location}"
            )

        # Get prediction
        result = predictor.predict_for_date(month, day, window_days)

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/api/predict", tags=["Weather Prediction"])
async def predict_weather_post(request: WeatherRequest):
    """
    Get weather prediction (POST version)

    Same as GET /api/predict/{month}/{day} but accepts JSON body.

    **Example request:**
    ```json
    {
      "month": 7,
      "day": 15,
      "location": "kathmandu_nepal",
      "window_days": 7
    }
    ```
    """
    if not predictor_status["loaded"]:
        raise HTTPException(
            status_code=503,
            detail=f"Predictor not available: {predictor_status.get('error', 'Unknown error')}"
        )

    # Validate location
    if request.location not in available_locations:
        raise HTTPException(
            status_code=404,
            detail=f"Location '{request.location}' not found. Available: {', '.join(available_locations)}"
        )

    try:
        # Validate date
        try:
            datetime(2000, request.month, request.day)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date: month={request.month}, day={request.day}"
            )

        # Load predictor for location
        predictor = load_predictor(request.location)
        if not predictor:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load predictor for location: {request.location}"
            )

        # Get prediction
        result = predictor.predict_for_date(
            request.month,
            request.day,
            request.window_days
        )

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/api/monthly/{month}", tags=["Statistics"])
async def get_monthly_stats(
    month: int = PathParam(..., ge=1, le=12, description="Month (1-12)"),
    location: str = Query(..., description="Location identifier")
):
    """
    Get overall statistics for a specific month

    Returns aggregated statistics for all days in the specified month.

    **Parameters:**
    - **month**: Month (1-12)
    - **location**: Location identifier

    **Example:**
    ```
    GET /api/monthly/7?location=kathmandu_nepal
    ```
    """
    if not predictor_status["loaded"]:
        raise HTTPException(
            status_code=503,
            detail=f"Predictor not available: {predictor_status.get('error', 'Unknown error')}"
        )

    # Validate location
    if location not in available_locations:
        raise HTTPException(
            status_code=404,
            detail=f"Location '{location}' not found. Available: {', '.join(available_locations)}"
        )

    try:
        # Load predictor for location
        predictor = load_predictor(location)
        if not predictor:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load predictor for location: {location}"
            )

        result = predictor.get_monthly_statistics(month)

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/api/monthly", tags=["Statistics"])
async def get_monthly_stats_post(request: MonthlyStatsRequest):
    """
    Get monthly statistics (POST version)

    **Example request:**
    ```json
    {
      "month": 7,
      "location": "kathmandu_nepal"
    }
    ```
    """
    if not predictor_status["loaded"]:
        raise HTTPException(
            status_code=503,
            detail=f"Predictor not available: {predictor_status.get('error', 'Unknown error')}"
        )

    # Validate location
    if request.location not in available_locations:
        raise HTTPException(
            status_code=404,
            detail=f"Location '{request.location}' not found. Available: {', '.join(available_locations)}"
        )

    try:
        # Load predictor for location
        predictor = load_predictor(request.location)
        if not predictor:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load predictor for location: {request.location}"
            )

        result = predictor.get_monthly_statistics(request.month)

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/calendar", tags=["Statistics"])
async def get_annual_calendar(
    location: str = Query(..., description="Location identifier"),
    dates_per_month: int = Query(2, ge=1, le=4, description="Predictions per month (1-4)")
):
    """
    Get predictions for entire year calendar

    Generates predictions for multiple dates across all 12 months.

    **Parameters:**
    - **location**: Location identifier
    - **dates_per_month**: Number of predictions per month (default: 2 = 1st and 15th)

    **Returns:**
    - Dictionary with date keys (MM-DD format) and prediction values

    **Example:**
    ```
    GET /api/calendar?location=kathmandu_nepal&dates_per_month=2
    ```

    Returns predictions for 1st and 15th of each month (24 dates total)
    """
    if not predictor_status["loaded"]:
        raise HTTPException(
            status_code=503,
            detail=f"Predictor not available: {predictor_status.get('error', 'Unknown error')}"
        )

    # Validate location
    if location not in available_locations:
        raise HTTPException(
            status_code=404,
            detail=f"Location '{location}' not found. Available: {', '.join(available_locations)}"
        )

    try:
        # Load predictor for location
        predictor = load_predictor(location)
        if not predictor:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load predictor for location: {location}"
            )

        calendar_predictions = {}

        # Determine which days to sample
        if dates_per_month == 1:
            days = [15]  # Middle of month
        elif dates_per_month == 2:
            days = [1, 15]  # Start and middle
        elif dates_per_month == 3:
            days = [1, 15, 28]  # Start, middle, end
        else:  # 4
            days = [1, 10, 20, 28]  # Distributed

        for month in range(1, 13):
            for day in days:
                try:
                    # Validate date
                    datetime(2000, month, day)

                    pred = predictor.predict_for_date(month, day)
                    calendar_predictions[f"{month:02d}-{day:02d}"] = pred
                except ValueError:
                    # Skip invalid dates (e.g., Feb 30)
                    continue
                except Exception as e:
                    # Log error but continue
                    print(f"Error predicting {month:02d}-{day:02d}: {e}")
                    continue

        return {
            "calendar": calendar_predictions,
            "total_predictions": len(calendar_predictions),
            "dates_per_month": dates_per_month
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/download/predictions", tags=["Download"])
async def download_predictions(
    location: str = Query(..., description="Location identifier"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    save_to_file: bool = Query(True, description="Save to output folder as well")
):
    """
    Download weather predictions as JSON file

    Generates predictions for a date range and returns as downloadable JSON.
    Optionally saves to output/{location}/ folder.

    **Parameters:**
    - **location**: Location identifier
    - **start_date**: Start date (YYYY-MM-DD)
    - **end_date**: End date (YYYY-MM-DD)
    - **save_to_file**: Save to output folder (default: true)

    **Example:**
    ```
    GET /api/download/predictions?location=kathmandu_nepal&start_date=2024-01-01&end_date=2024-12-31
    ```

    **Returns:**
    - JSON file download with all predictions
    """
    from fastapi.responses import StreamingResponse
    import io
    import json
    from pathlib import Path

    if not predictor_status["loaded"]:
        raise HTTPException(
            status_code=503,
            detail=f"Predictor not available: {predictor_status.get('error', 'Unknown error')}"
        )

    # Validate location
    if location not in available_locations:
        raise HTTPException(
            status_code=404,
            detail=f"Location '{location}' not found. Available: {', '.join(available_locations)}"
        )

    try:
        # Parse dates
        import pandas as pd
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')

        # Load predictor for location
        predictor = load_predictor(location)
        if not predictor:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load predictor for location: {location}"
            )

        # Generate predictions
        predictions = {}
        for date in date_range:
            month = date.month
            day = date.day
            date_str = date.strftime('%Y-%m-%d')

            try:
                pred = predictor.predict_for_date(month, day)
                # The predictor already returns the correct future date
                # But we'll use the user-requested date for consistency
                pred['requested_date'] = date_str
                predictions[date_str] = pred
            except Exception as e:
                print(f"Error predicting {date_str}: {e}")
                continue

        # Prepare JSON response
        response_data = {
            "location": location,
            "start_date": start_date,
            "end_date": end_date,
            "total_predictions": len(predictions),
            "generated_at": datetime.now().isoformat(),
            "predictions": predictions
        }

        # Optionally save to file
        if save_to_file:
            output_dir = Path(__file__).parent.parent.parent / "output" / location
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"predictions_{start_date}_to_{end_date}.json"

            with open(output_file, 'w') as f:
                json.dump(response_data, f, indent=2)

            print(f"✓ Saved predictions to {output_file}")

        # Return as downloadable file
        json_str = json.dumps(response_data, indent=2)
        filename = f"weather_predictions_{location}_{start_date}_to_{end_date}.json"

        return StreamingResponse(
            io.BytesIO(json_str.encode()),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating predictions: {str(e)}")


@app.get("/api/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint

    Returns 200 OK if API is running and predictor is loaded.
    """
    if not predictor_status["loaded"]:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": "Predictor not loaded",
                "error": predictor_status.get("error")
            }
        )

    return {
        "status": "healthy",
        "message": "API is running",
        "locations_available": len(available_locations)
    }


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("PlanMySky Weather API")
    print("=" * 60)
    print("\nStarting server...")
    print("API Documentation: http://localhost:8000/docs")
    print("API Status: http://localhost:8000/api/status")
    print("\n" + "=" * 60)

    uvicorn.run(
        "weather_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
