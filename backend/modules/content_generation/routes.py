"""
Content Generation Module
Handles AI-powered content generation for Chrome extension
"""
from fastapi import APIRouter, HTTPException, Depends, status
from .models import ContentGenerationRequest, GeneratedContent, GeneratedContentResponse
from .ai_service import AIContentGenerator
from .writing_styles import get_all_writing_styles, get_all_message_lengths
from login import User, get_current_user
import logging

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api", tags=["content-generation"])

# Database reference
db = None
ai_generator = None

def set_db(database):
    global db
    db = database

def set_ai_generator(generator):
    global ai_generator
    ai_generator = generator

# Content generation endpoints
@router.post("/generate-content", response_model=GeneratedContentResponse)
async def generate_content(
    request: ContentGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate personalized content based on LinkedIn profile data"""
    try:
        # Get user
        user = await db.users.find_one({"email": current_user.email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Use writing_style instead of tone
        writing_style = request.writing_style or "data-driven"

        # Prepare selected insights for AI service
        selected_insights_dicts = [
            insight.dict() if hasattr(insight, 'dict') else insight
            for insight in request.selected_insights
        ] if request.selected_insights else []

        # Prepare case studies for AI service
        case_studies_list = []
        if request.case_studies:
            for cs in request.case_studies:
                if isinstance(cs, str):
                    case_studies_list.append({'title': cs})
                elif isinstance(cs, dict):
                    case_studies_list.append(cs)
                elif hasattr(cs, 'dict'):
                    case_studies_list.append(cs.dict())

        # Generate content using AI
        generated_text, insights, score = await ai_generator.generate_personalized_content(
            linkedin_data=request.linkedin_data.dict(),
            selected_insights=selected_insights_dicts,
            case_studies=case_studies_list,
            content_type=request.content_type,
            content_focus=request.content_focus,
            tone=writing_style,
            value_proposition=request.value_proposition,
            additional_context=request.additional_context,
            message_length=request.message_length
        )

        # Save to database
        generated_content = GeneratedContent(
            user_id=user['id'],
            linkedin_data=request.linkedin_data,
            generated_text=generated_text,
            content_type=request.content_type,
            tone=writing_style,
            insights_used=insights,
            score=score
        )

        await db.generated_content.insert_one(generated_content.dict())

        return GeneratedContentResponse(
            id=generated_content.id,
            generated_text=generated_content.generated_text,
            insights_used=generated_content.insights_used,
            score=generated_content.score,
            created_at=generated_content.created_at
        )

    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate content: {str(e)}"
        )

@router.get("/content-history")
async def get_content_history(
    current_user: User = Depends(get_current_user),
    limit: int = 20
):
    """Get user's content generation history"""
    user = await db.users.find_one({"email": current_user.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    content_list = await db.generated_content.find(
        {"user_id": user['id']}
    ).sort("created_at", -1).limit(limit).to_list(limit)

    return content_list

@router.get("/writing-styles")
async def get_writing_styles():
    """Get all available writing styles"""
    return {"styles": get_all_writing_styles()}

@router.get("/message-lengths")
async def get_message_lengths():
    """Get all available message length options"""
    return {"lengths": get_all_message_lengths()}
