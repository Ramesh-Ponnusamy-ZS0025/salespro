"""
SalesPro API Server - Main Entry Point
Imports and combines all module routers
"""
import asyncio
import platform

# Fix for Windows - Set event loop policy to support Playwright subprocesses
import httpx

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from groq import Groq
import os
import logging
from pathlib import Path

from config.tone_config import get_system_prompt, get_email_structure_validation, format_email_output
from config.case_study_manager import CaseStudyManager

# Import all route modules
import login
import agent_builder
import campaign
import gtm
import personalize
import thread_intelligence
import documents
import document_management
import zuci_news
import content_management
import microsite

# Import new Chrome extension modules
from modules.content_generation import routes as content_generation
from modules.case_studies import routes as case_studies
from modules.custom_instructions import routes as custom_instructions
from modules.content_generation.ai_service import AIContentGenerator

# ============== LOGGING SETUP (Must be early) ==============

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Setup
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# LLM Config
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY, http_client=httpx.Client(verify=False))

# Initialize FastAPI app
app = FastAPI(title="SalesPro API", version="2.0")

# Initialize Case Study Manager
case_study_manager = None

# ============== LLM SYSTEM PROMPT ==============

SALES_AGENT_SYSTEM_PROMPT = """You are SalesAI, a highly skilled B2B Sales Agent trained to convert leads into meetings.

CORE SALES PERSONALITY:
- Warm, confident, simple English
- Deep understanding of prospect pain points and business goals
- Position our solution as the clear value choice
- Professional SDR/BDR communication style

MANDATORY OUTPUT STRUCTURE (every response must include):
1. **Prospect Insight**: Brief summary of prospect's needs/pain points (max 2 sentences)
2. **Sales Message**: Your recommended reply/outreach copy/script (ready to send)
3. **Soft CTA**: Always include a next step like "Would you be open for a quick 10-minute call?"

QUALITY STANDARDS:
- Persuasive, value-driven, outcome-focused messaging
- Personalized to prospect's role and industry context
- Clear value proposition highlighting business impact
- Short, crisp copy with natural conversational flow
- NO generic long explanations or robotic AI tone
- NO disclaimers like "As an AI..."
- Every message feels human and aligned with revenue generation

BEHAVIOR BY MODULE:
- **Thread Intelligence**: Identify buying signals, objections, urgency, stakeholder role → Provide polished sales reply
- **Campaign Builder**: Generate personalized outreach sequences (emails, LinkedIn, WhatsApp scripts) with clear CTAs
- **Personalize**: Hyper-personalized messaging tailored to role, pain points, and business impact
- **All Responses**: Sales-first mindset, focusing on moving the lead forward
"""

# ============== LLM HELPER ==============

async def generate_llm_response(prompt: str, system_message: str = None, module: str = None) -> str:
    """Generate LLM response with module-specific system prompt"""
    from fastapi import HTTPException

    try:
        if system_message is None:
            if module:
                system_message = get_system_prompt(module)
            else:
                system_message = SALES_AGENT_SYSTEM_PROMPT

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        response = chat_completion.choices[0].message.content

        return response
    except Exception as e:
        logging.error(f"LLM Error: {str(e)}")
        raise e
        raise HTTPException(status_code=500, detail="Error generating AI response")

# ============== STARTUP EVENT ==============

@app.on_event("startup")
async def startup_event():
    global case_study_manager

    # Initialize Case Study Manager with LLM for intelligent matching
    case_study_manager = CaseStudyManager(db, llm_function=generate_llm_response)

    # Set database reference for all modules
    login.set_db(db)
    agent_builder.set_db(db)
    campaign.set_db(db)
    gtm.set_db(db)
    personalize.set_db(db)
    thread_intelligence.set_db(db)
    documents.set_db(db)
    document_management.set_db(db)
    zuci_news.set_db(db)
    content_management.set_db(db)
    microsite.set_db(db)

    # Set LLM helper for modules that need it
    agent_builder.set_llm_helper(generate_llm_response)
    campaign.set_llm_helper(generate_llm_response)
    gtm.set_llm_helper(generate_llm_response)
    personalize.set_llm_helper(generate_llm_response)
    thread_intelligence.set_llm_helper(generate_llm_response)
    document_management.set_llm_helper(generate_llm_response)
    microsite.set_llm_helper(generate_llm_response)

    # Set case study manager for campaign, thread intelligence, personalize, and document_management modules
    campaign.set_case_study_manager(case_study_manager)
    thread_intelligence.set_case_study_manager(case_study_manager)
    personalize.set_case_study_manager(case_study_manager)
    document_management.set_case_study_manager(case_study_manager)
    microsite.set_case_study_manager(case_study_manager)

    # Sync documents missing from vector database on startup
    try:
        logger.info("Syncing documents to vector database...")
        synced_count = await case_study_manager.sync_missing_documents()
        if synced_count > 0:
            logger.info(f"✓ Added {synced_count} missing documents to vector DB")
        else:
            logger.info("✓ All existing documents already in vector DB")
    except Exception as e:
        logger.error(f"Error during vector DB sync: {e}")

    # Set ROOT_DIR for documents module
    documents.set_root_dir(ROOT_DIR)

    # Set groq client for GTM module
    gtm.set_groq_client(groq_client)

    # Set case study manager for GTM module
    gtm.set_case_study_manager(case_study_manager)

    # Initialize AI Content Generator for Chrome extension
    ai_generator = AIContentGenerator()

    # Set database and dependencies for new Chrome extension modules
    content_generation.set_db(db)
    content_generation.set_ai_generator(ai_generator)
    case_studies.set_db(db)
    case_studies.set_case_study_manager(case_study_manager)
    custom_instructions.set_db(db)

    logging.info("SalesPro API started successfully")

# ============== SHUTDOWN EVENT ==============

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# ============== INCLUDE ALL ROUTERS ==============

app.include_router(login.router)
app.include_router(agent_builder.router)
app.include_router(campaign.router)
app.include_router(gtm.router)
app.include_router(personalize.router)
app.include_router(thread_intelligence.router)
app.include_router(documents.router)
app.include_router(document_management.router)
app.include_router(zuci_news.router)
app.include_router(content_management.router)
app.include_router(microsite.router)

# Include Chrome extension routers
app.include_router(content_generation.router)
app.include_router(case_studies.router)
app.include_router(custom_instructions.router)

# ============== CORS MIDDLEWARE ==============

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== HEALTH CHECK ==============

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0"}

@app.get("/")
async def root():
    return {
        "message": "SalesPro API v2.0",
        "docs": "/docs",
        "modules": [
            "login",
            "agent_builder",
            "campaign",
            "gtm",
            "personalize",
            "thread_intelligence",
            "documents",
            "document_management",
            "microsite"
        ]
    }
