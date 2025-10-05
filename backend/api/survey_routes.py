from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from database import db
from datetime import datetime

survey_router = APIRouter()

# Survey collection
surveys_collection = db["surveys"]


class SurveyVote(BaseModel):
    location: str
    date: str
    question: str
    option: str


@survey_router.post("/vote")
async def submit_vote(vote: SurveyVote):
    """
    Submit a survey vote

    **Parameters:**
    - location: Location identifier
    - date: Date of the weather prediction
    - question: Survey question
    - option: Selected option

    **Returns:**
    - Success message
    """
    try:
        # Create a unique key for this survey
        survey_key = f"{vote.location}_{vote.date}_{vote.question}"

        # Find existing survey or create new one
        existing_survey = await surveys_collection.find_one({"survey_key": survey_key})

        if existing_survey:
            # Update vote count for the selected option
            vote_counts = existing_survey.get("vote_counts", {})
            vote_counts[vote.option] = vote_counts.get(vote.option, 0) + 1

            await surveys_collection.update_one(
                {"survey_key": survey_key},
                {
                    "$set": {
                        "vote_counts": vote_counts,
                        "total_votes": existing_survey.get("total_votes", 0) + 1,
                        "last_updated": datetime.now().isoformat()
                    }
                }
            )
        else:
            # Create new survey
            new_survey = {
                "survey_key": survey_key,
                "location": vote.location,
                "date": vote.date,
                "question": vote.question,
                "vote_counts": {vote.option: 1},
                "total_votes": 1,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            await surveys_collection.insert_one(new_survey)

        return {
            "success": True,
            "message": "Vote submitted successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting vote: {str(e)}")


@survey_router.get("/results")
async def get_results(location: str, date: str):
    """
    Get survey results for a specific location and date

    **Parameters:**
    - location: Location identifier
    - date: Date of the weather prediction

    **Returns:**
    - Survey results with vote counts
    """
    try:
        # Find all surveys matching location and date
        surveys = await surveys_collection.find(
            {
                "location": location,
                "date": date
            }
        ).to_list(length=100)

        if not surveys:
            return {
                "results": [],
                "total_votes": 0,
                "message": "No votes yet"
            }

        # Get the most recent survey (in case there are multiple)
        latest_survey = sorted(surveys, key=lambda x: x.get("last_updated", ""), reverse=True)[0]

        # Convert vote_counts to chart format
        results = [
            {"name": option, "value": count}
            for option, count in latest_survey.get("vote_counts", {}).items()
        ]

        return {
            "results": results,
            "total_votes": latest_survey.get("total_votes", 0),
            "question": latest_survey.get("question", "")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching results: {str(e)}")


@survey_router.get("/statistics")
async def get_statistics(location: str = None):
    """
    Get overall survey statistics

    **Parameters:**
    - location: Optional location filter

    **Returns:**
    - Overall statistics
    """
    try:
        query = {"location": location} if location else {}

        surveys = await surveys_collection.find(query).to_list(length=1000)

        total_surveys = len(surveys)
        total_votes = sum(s.get("total_votes", 0) for s in surveys)

        return {
            "total_surveys": total_surveys,
            "total_votes": total_votes,
            "locations": len(set(s.get("location") for s in surveys)),
            "message": "Statistics retrieved successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")
