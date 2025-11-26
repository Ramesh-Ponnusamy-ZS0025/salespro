"""
Campaign Module
Contains: Campaign, Sequence, Sender Profile models and routes
Also includes: Feedback, Insights, Dashboard stats
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import logging

from login import User, get_current_user

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api", tags=["campaigns"])

# Database reference - will be set from server.py
db = None

# External references - will be set from server.py
generate_llm_response = None
case_study_manager = None

def set_db(database):
    global db
    db = database

def set_llm_helper(llm_func):
    global generate_llm_response
    generate_llm_response = llm_func

def set_case_study_manager(manager):
    global case_study_manager
    case_study_manager = manager

# ============== MODELS ==============

class Campaign(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_name: str
    agent_id: str
    service: str
    stage: str  # TOFU/MOFU/BOFU
    icp: List[str] = []
    methodologies: List[str] = []
    tone: str
    resources: List[str] = []
    custom_inputs: List[Dict[str, str]] = []
    selected_documents: List[str] = []
    auto_pick_documents: bool = False
    status: str = "draft"  # draft/review/published
    ai_content: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CampaignCreate(BaseModel):
    campaign_name: str
    agent_id: str
    service: str
    stage: str
    icp: List[str] = []
    methodologies: List[str] = []
    tone: str
    resources: List[str] = []
    custom_inputs: List[Dict[str, str]] = []
    selected_documents: List[str] = []
    auto_pick_documents: bool = False

class TouchpointConfig(BaseModel):
    total_touchpoints: int
    email_count: int
    linkedin_count: int
    voicemail_count: int

class SequenceStep(BaseModel):
    step_number: int
    day: int
    channel: str  # email, linkedin, voicemail
    content: Optional[str] = None
    status: str = "draft"  # draft, generating, ready

class CampaignSequence(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: str
    touchpoint_config: TouchpointConfig
    steps: List[SequenceStep] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SequenceCreate(BaseModel):
    campaign_id: str
    touchpoint_config: TouchpointConfig

class SequenceStepUpdate(BaseModel):
    content: Optional[str] = None
    day: Optional[int] = None

class SenderProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    position: str
    company: str
    email: EmailStr
    phone: Optional[str] = None
    signature_template: str
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SenderProfileCreate(BaseModel):
    name: str
    position: str
    company: str
    email: EmailStr
    phone: Optional[str] = None
    signature_template: str

class FeedbackCreate(BaseModel):
    campaign_id: Optional[str] = None
    agent_id: Optional[str] = None
    feedback_text: str
    rating: int
    tags: List[str] = []

class Feedback(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: Optional[str] = None
    agent_id: Optional[str] = None
    user_id: str
    feedback_text: str
    rating: int
    tags: List[str] = []
    status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InsightResponse(BaseModel):
    id: str
    campaign_id: Optional[str] = None
    metric: str
    observation: str
    suggested_action: str
    status: str
    created_at: datetime

# ============== CAMPAIGN UTILITY FUNCTIONS ==============

async def find_relevant_case_studies(docs: List[Dict], campaign_context: Dict, agent_context: Dict) -> List[str]:
    """Find relevant case studies using summaries and LLM"""
    relevant_doc_ids = []

    context_text = f"""
Campaign Service: {campaign_context.get('service', '')}
Campaign Stage: {campaign_context.get('stage', '')}
Target ICP: {', '.join(campaign_context.get('icp', []))}
Custom Inputs: {', '.join([ci.get('value', '') for ci in campaign_context.get('custom_inputs', [])])}
Agent Value Props: {', '.join(agent_context.get('value_props', []))}
"""

    for doc in docs:
        doc_summary = doc.get('summary', '')
        if not doc_summary:
            continue

        relevance_prompt = f"""Given this campaign context:
{context_text}

And this case study summary:
{doc_summary}

Is this case study relevant to the campaign? Respond ONLY with "yes" or "no".
"""

        try:
            response = await generate_llm_response(relevance_prompt)
            if 'yes' in response.lower():
                relevant_doc_ids.append(doc['id'])
        except Exception as e:
            logger.error(f"Error checking relevance for doc {doc.get('id')}: {e}")
            continue

    return relevant_doc_ids

# ============== CAMPAIGN ROUTES ==============

@router.post("/campaigns", response_model=Campaign)
async def create_campaign(campaign_data: CampaignCreate, current_user: User = Depends(get_current_user)):
    # Verify agent exists
    agent = await db.agents.find_one({"id": campaign_data.agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Handle auto-pick documents using CaseStudyManager
    selected_docs = campaign_data.selected_documents
    if campaign_data.auto_pick_documents and case_study_manager:
        selected_docs = await case_study_manager.auto_pick_case_studies(
            service=campaign_data.service,
            stage=campaign_data.stage,
            icp=campaign_data.icp,
            custom_inputs=campaign_data.custom_inputs,
            max_results=3
        )
        logger.info(f"Auto-picked {len(selected_docs)} case studies for campaign")

    campaign = Campaign(
        **campaign_data.model_dump(exclude={'selected_documents'}),
        selected_documents=selected_docs,
        created_by=current_user.id
    )
    doc = campaign.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()

    await db.campaigns.insert_one(doc)
    await db.agents.update_one({"id": campaign_data.agent_id}, {"$inc": {"usage_count": 1}})

    return campaign

@router.get("/campaigns", response_model=List[Campaign])
async def get_campaigns(current_user: User = Depends(get_current_user)):
    campaigns = await db.campaigns.find({"created_by": current_user.id}, {"_id": 0}).to_list(1000)
    for campaign in campaigns:
        if isinstance(campaign.get('created_at'), str):
            campaign['created_at'] = datetime.fromisoformat(campaign['created_at'])
        if isinstance(campaign.get('updated_at'), str):
            campaign['updated_at'] = datetime.fromisoformat(campaign['updated_at'])
    return campaigns

@router.get("/campaigns/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str, current_user: User = Depends(get_current_user)):
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if isinstance(campaign.get('created_at'), str):
        campaign['created_at'] = datetime.fromisoformat(campaign['created_at'])
    if isinstance(campaign.get('updated_at'), str):
        campaign['updated_at'] = datetime.fromisoformat(campaign['updated_at'])
    return Campaign(**campaign)

@router.post("/campaigns/{campaign_id}/generate")
async def generate_campaign_copy(campaign_id: str, current_user: User = Depends(get_current_user)):
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    agent = await db.agents.find_one({"id": campaign['agent_id']}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Build custom inputs text
    custom_inputs_text = "\n".join([
        f"- {ci['value']}"
        for ci in campaign.get('custom_inputs', [])
    ]) or "None"

    # Get selected case studies with full details
    case_study_references = []
    if campaign.get('selected_documents') and case_study_manager:
        case_studies = await case_study_manager.get_case_study_details(campaign['selected_documents'])

        for cs in case_studies:
            ref = case_study_manager.format_case_study_reference(cs, context='inline')
            title = cs.get('title', 'Case Study')
            source_url = cs.get('metadata', {}).get('source_url', '')
            summary = cs.get('summary', '')[:200]

            case_study_references.append({
                'title': title,
                'url': source_url,
                'summary': summary,
                'formatted_ref': ref
            })

    case_studies_text = "\n".join([
        f"- {cs['title']}: {cs['summary']}\n  Link: {cs['url']}"
        for cs in case_study_references
    ]) if case_study_references else "No case studies selected"

    methodology_text = ", ".join(campaign.get('methodologies', [])) or "Standard approach"

    prompt = f"""Generate EMAIL campaign content following PROFESSIONAL EMAIL-COPYWRITING STRUCTURE.

Campaign Context:
- Service: {campaign['service']}
- Funnel Stage: {campaign['stage']}
- Target ICP: {', '.join(campaign.get('icp', []))}
- Tone: {campaign['tone']} (but MUST follow data-driven, CXO-focused professional style)
- Methodologies: {methodology_text}

Custom Requirements:
{custom_inputs_text}

Agent Profile:
- Value Propositions: {', '.join(agent.get('value_props', []))}
- Pain Points to Address: {', '.join(agent.get('pain_points', []))}
- Target Personas: {', '.join(agent.get('personas', []))}

Available Case Studies (MUST reference with PDF link in the body):
{case_studies_text}

=== MANDATORY EMAIL-COPYWRITING STRUCTURE ===

1. SUBJECT LINE (5-8 words)
   - Create curiosity or urgency
   - Include a benefit or outcome
   - Avoid spam triggers

2. HOOK (1-2 sentences)
   - Personalize with recipient's industry/role/company
   - State a relevant observation or insight
   - Create immediate relevance

3. BODY (3 paragraphs, 200-250 words total)
   - Paragraph 1: Identify the PAIN/CHALLENGE your prospect faces
   - Paragraph 2: Present your SOLUTION with a CASE STUDY reference
     * MUST include the case study PDF link in markdown format: [Case Study Name](URL)
     * Example: "See how we helped [Company]: [Case Study Title](https://...pdf)"
   - Paragraph 3: Highlight measurable OUTCOMES/RESULTS with metrics (%, ROI, time saved)

4. CTA (Call-to-Action)
   - Single, clear next step
   - Low commitment (15-min call, quick chat)
   - Specific and actionable

5. SIGNATURE: ALWAYS end with this exact signature:
        Best regards,
        Tamil Bharathi
        Manager - Growth
        +1 647 404 2503
        Toronto, ON
        Zuci Systems

6. P.S. (Optional but recommended)
   - Additional case study link or compelling fact
   - Reinforce urgency or value

=== OUTPUT FORMAT ===
---
SUBJECT: [Compelling subject line]

Hi [Name],

[HOOK - 1-2 personalized sentences]

[BODY PARAGRAPH 1 - Pain/Challenge]

[BODY PARAGRAPH 2 - Solution + Case Study with PDF link]

[BODY PARAGRAPH 3 - Results/Outcomes with metrics]

[CTA - Clear call-to-action]

Best regards,
[Signature]

P.S. [Case study reference with link or compelling fact]
---
"""

    ai_content = await generate_llm_response(prompt, module='campaign')

    await db.campaigns.update_one(
        {"id": campaign_id},
        {"$set": {"ai_content": ai_content, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    return {"content": ai_content}

@router.put("/campaigns/{campaign_id}", response_model=Campaign)
async def update_campaign(campaign_id: str, campaign_data: CampaignCreate, current_user: User = Depends(get_current_user)):
    # Verify campaign exists and belongs to user
    existing = await db.campaigns.find_one({"id": campaign_id, "created_by": current_user.id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Verify agent exists
    agent = await db.agents.find_one({"id": campaign_data.agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    updated_data = campaign_data.model_dump()
    updated_data['updated_at'] = datetime.now(timezone.utc).isoformat()

    await db.campaigns.update_one({"id": campaign_id}, {"$set": updated_data})

    updated_campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if isinstance(updated_campaign.get('created_at'), str):
        updated_campaign['created_at'] = datetime.fromisoformat(updated_campaign['created_at'])
    if isinstance(updated_campaign.get('updated_at'), str):
        updated_campaign['updated_at'] = datetime.fromisoformat(updated_campaign['updated_at'])
    return Campaign(**updated_campaign)

@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str, current_user: User = Depends(get_current_user)):
    # Verify campaign exists and belongs to user
    campaign = await db.campaigns.find_one({"id": campaign_id, "created_by": current_user.id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Delete campaign sequence first
    await db.campaign_sequences.delete_many({"campaign_id": campaign_id})

    # Delete campaign
    result = await db.campaigns.delete_one({"id": campaign_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return {"message": "Campaign and associated sequences deleted successfully"}

@router.put("/campaigns/{campaign_id}/status")
async def update_campaign_status(campaign_id: str, status: str, current_user: User = Depends(get_current_user)):
    result = await db.campaigns.update_one(
        {"id": campaign_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "Status updated successfully"}

# ============== CAMPAIGN SEQUENCE ROUTES ==============

@router.post("/campaigns/{campaign_id}/sequence")
async def create_campaign_sequence(campaign_id: str, sequence_data: SequenceCreate, current_user: User = Depends(get_current_user)):
    # Verify campaign exists
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Generate initial sequence steps based on touchpoint config
    steps = []
    step_number = 1
    day_counter = 1

    # Distribute touchpoints
    for _ in range(sequence_data.touchpoint_config.email_count):
        steps.append({
            "step_number": step_number,
            "day": day_counter,
            "channel": "email",
            "content": None,
            "status": "draft"
        })
        step_number += 1
        day_counter += 1

    for _ in range(sequence_data.touchpoint_config.linkedin_count):
        steps.append({
            "step_number": step_number,
            "day": day_counter,
            "channel": "linkedin",
            "content": '',
            "status": "draft"
        })
        step_number += 1
        day_counter += 1

    for _ in range(sequence_data.touchpoint_config.voicemail_count):
        steps.append({
            "step_number": step_number,
            "day": day_counter,
            "channel": "voicemail",
            "content": '',
            "status": "draft"
        })
        step_number += 1
        day_counter += 1

    # Create sequence
    sequence = {
        "id": str(uuid.uuid4()),
        "campaign_id": campaign_id,
        "touchpoint_config": sequence_data.touchpoint_config.model_dump(),
        "steps": steps,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    await db.campaign_sequences.insert_one(sequence.copy())
    return sequence

@router.get("/campaigns/{campaign_id}/sequence")
async def get_campaign_sequence(campaign_id: str, current_user: User = Depends(get_current_user)):
    sequence = await db.campaign_sequences.find_one({"campaign_id": campaign_id}, {"_id": 0})
    if not sequence:
        raise HTTPException(status_code=404, detail="Sequence not found")
    return sequence

@router.post("/campaigns/{campaign_id}/sequence/steps/{step_number}/generate")
async def generate_step_content(campaign_id: str, step_number: int, current_user: User = Depends(get_current_user)):
    # Get campaign and agent details
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    agent = await db.agents.find_one({"id": campaign['agent_id']}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    sequence = await db.campaign_sequences.find_one({"campaign_id": campaign_id}, {"_id": 0})
    if not sequence:
        raise HTTPException(status_code=404, detail="Sequence not found")

    # Find the step
    step = next((s for s in sequence['steps'] if s['step_number'] == step_number), None)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")

    # Get case studies for this campaign
    case_study_references = []
    if campaign.get('selected_documents') and case_study_manager:
        case_studies = await case_study_manager.get_case_study_details(campaign['selected_documents'])
        for cs in case_studies[:2]:  # Get up to 2 case studies
            source_url = cs.get('metadata', {}).get('source_url', '')
            case_study_references.append({
                'title': cs.get('title', 'Case Study'),
                'url': source_url,
                'summary': cs.get('summary', '')[:200]
            })

    case_study_text = ""
    if case_study_references:
        case_study_text = "\n=== CASE STUDIES TO REFERENCE (MUST include PDF link) ==="
        for idx, cs in enumerate(case_study_references, 1):
            case_study_text += f"""
Case Study {idx}: {cs['title']}
Summary: {cs['summary']}
PDF Link: {cs['url']}
Markdown format: [{cs['title']}]({cs['url']})
"""
        case_study_text += "\nIMPORTANT: Include at least one case study link in your response!"

    # Generate content based on channel and campaign context
    channel = step['channel']

    if channel == 'email':
        prompt = f"""Generate EMAIL content for Step {step_number} of {len(sequence['steps'])} in this sequence.

Campaign: {campaign['campaign_name']}
Service: {campaign['service']}
Stage: {campaign['stage']}
Target ICP: {', '.join(campaign.get('icp', []))}

Agent Profile:
- Value Props: {', '.join(agent.get('value_props', []))}
- Pain Points: {', '.join(agent.get('pain_points', []))}
{case_study_text}

Sequence Context:
- This is Step {step_number} on Day {step['day']}
- Follow-up in multi-touch sequence

=== EMAIL-COPYWRITING STRUCTURE (MANDATORY) ===

1. SUBJECT LINE: Compelling, 5-8 words, create curiosity
2. HOOK: 1-2 sentences, personalized, create relevance
3. BODY: 150-200 words total
   - Challenge/Pain point acknowledgment
   - Solution with CASE STUDY reference and PDF LINK (if available)
   - Results/outcomes with metrics
4. CTA: Single, clear, low-commitment action
5. SIGNATURE: Professional closing

CRITICAL: If case study is provided above, MUST include the PDF link in this format:
[Case Study Title](URL)

=== OUTPUT FORMAT ===
---
SUBJECT: [Compelling subject 5-8 words]

Hi [Name],

[HOOK - Personalized opening]

[BODY - Pain → Solution with case study link → Results]

[CTA - Clear next step]

Best regards,
Tamil Bharathi
Manager - Growth
+1 647 404 2503
Toronto, ON
Zuci Systems

P.S. [Optional case study reference]
---
"""
    elif channel == 'linkedin':
        prompt = f"""Generate LINKEDIN message for Step {step_number}.

Campaign: {campaign['campaign_name']}
Service: {campaign['service']}
Stage: {campaign['stage']}
Target ICP: {', '.join(campaign.get('icp', []))}

Agent Profile:
- Value Props: {', '.join(agent.get('value_props', []))}
- Pain Points: {', '.join(agent.get('pain_points', []))}
{case_study_text}

=== LINKEDIN MESSAGE STRUCTURE ===

1. OPENER: Personalized, reference their role/company/recent activity
2. VALUE: Brief insight or observation relevant to them
3. PROOF: Reference case study with link (if available)
   - Format: "Here's a quick read: [Title](URL)"
4. CTA: Soft ask (coffee chat, quick call, connect)
5. CLOSE: Professional but friendly

REQUIREMENTS:
- Conversational, LinkedIn-appropriate tone
- 100-150 words max
- Include case study PDF link if provided above
- Low-pressure CTA
- Professional but friendly

=== OUTPUT FORMAT ===
Hi [Name],

[Personal observation about their role/company]

[Brief value prop + case study reference with link]

[Soft CTA]

Best Regards,
Tamil Bharathi
Manager - Growth
+1 647 404 2503
Toronto, ON
Zuci Systems
"""
    else:  # voicemail
        prompt = f"""Generate VOICEMAIL script for Step {step_number}.

Campaign: {campaign['campaign_name']}
Service: {campaign['service']}
Target ICP: {', '.join(campaign.get('icp', []))}

Agent Profile:
- Value Props: {', '.join(agent.get('value_props', []))}
{case_study_text}

=== VOICEMAIL STRUCTURE ===

1. INTRO: Name + Company (5 seconds)
2. REASON: Why you're calling - reference a specific insight or case study
3. VALUE: One clear benefit/outcome (mention case study results if available)
4. CTA: Clear callback with number
5. CLOSE: Name again + brief urgency

REQUIREMENTS:
- Natural speaking script (80-100 words, ~30 seconds)
- Reference case study success story if provided
- One specific, memorable outcome/metric
- Clear callback number and reason
- Professional, confident tone

=== OUTPUT FORMAT ===
[VOICEMAIL SCRIPT]

Hi [Name], this is [Your Name] from [Company].

[Reason for call + brief case study reference]

[One clear value/outcome with metric]

[Callback CTA with your number]

Again, this is [Your Name] at [number]. Looking forward to connecting.
"""

    content = await generate_llm_response(prompt, module='campaign')

    # Update step content
    for s in sequence['steps']:
        if s['step_number'] == step_number:
            s['content'] = content
            s['status'] = 'ready'
            break

    await db.campaign_sequences.update_one(
        {"campaign_id": campaign_id},
        {"$set": {"steps": sequence['steps'], "updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    return {"content": content, "step_number": step_number}

@router.put("/campaigns/{campaign_id}/sequence/steps/{step_number}")
async def update_step(campaign_id: str, step_number: int, step_update: SequenceStepUpdate, current_user: User = Depends(get_current_user)):
    sequence = await db.campaign_sequences.find_one({"campaign_id": campaign_id}, {"_id": 0})
    if not sequence:
        raise HTTPException(status_code=404, detail="Sequence not found")

    # Update the specific step
    for step in sequence['steps']:
        if step['step_number'] == step_number:
            if step_update.content is not None:
                step['content'] = step_update.content
            if step_update.day is not None:
                step['day'] = step_update.day
            break

    await db.campaign_sequences.update_one(
        {"campaign_id": campaign_id},
        {"$set": {"steps": sequence['steps'], "updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    return {"message": "Step updated successfully"}

@router.delete("/campaigns/{campaign_id}/sequence/steps/{step_number}")
async def delete_step(campaign_id: str, step_number: int, current_user: User = Depends(get_current_user)):
    sequence = await db.campaign_sequences.find_one({"campaign_id": campaign_id}, {"_id": 0})
    if not sequence:
        raise HTTPException(status_code=404, detail="Sequence not found")

    # Remove the step
    updated_steps = [step for step in sequence['steps'] if step['step_number'] != step_number]

    # Renumber remaining steps
    for idx, step in enumerate(updated_steps, 1):
        step['step_number'] = idx

    await db.campaign_sequences.update_one(
        {"campaign_id": campaign_id},
        {"$set": {"steps": updated_steps, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    return {"message": "Step deleted successfully", "steps": updated_steps}

class StepReorderRequest(BaseModel):
    step_order: List[Dict[str, Any]]

@router.put("/campaigns/{campaign_id}/sequence/reorder")
async def reorder_sequence(campaign_id: str, request: StepReorderRequest, current_user: User = Depends(get_current_user)):
    sequence = await db.campaign_sequences.find_one({"campaign_id": campaign_id}, {"_id": 0})
    if not sequence:
        raise HTTPException(status_code=404, detail="Sequence not found")

    logger.info(f"Reordering sequence for campaign {campaign_id}")
    logger.info(f"Received step_order: {request.step_order}")
    logger.info(f"Current sequence steps: {sequence.get('steps', [])}")

    # Create a mapping of old step numbers to full step data
    step_map = {step['step_number']: step for step in sequence['steps']}

    # Build reordered steps array
    reordered_steps = []
    for order_item in request.step_order:
        old_step_num = order_item.get('step_number')
        new_position = order_item.get('new_position')

        if old_step_num in step_map:
            # Get the existing step data
            step = step_map[old_step_num].copy()

            # Update with new position
            step['step_number'] = new_position

            # Preserve any updated content from frontend
            if 'content' in order_item and order_item['content']:
                step['content'] = order_item['content']

            # Preserve channel and day
            if 'channel' in order_item:
                step['channel'] = order_item['channel']
            if 'day' in order_item:
                step['day'] = order_item['day']

            reordered_steps.append(step)
        else:
            logger.warning(f"Step number {old_step_num} not found in existing steps")

    # Sort by new position to ensure correct order
    reordered_steps.sort(key=lambda x: x['step_number'])

    logger.info(f"Reordered steps: {reordered_steps}")

    # Update database
    result = await db.campaign_sequences.update_one(
        {"campaign_id": campaign_id},
        {"$set": {"steps": reordered_steps, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    logger.info(f"Database update result: matched={result.matched_count}, modified={result.modified_count}")

    # Verify the update
    updated_sequence = await db.campaign_sequences.find_one({"campaign_id": campaign_id}, {"_id": 0})
    logger.info(f"Verified updated sequence: {updated_sequence.get('steps', [])}")

    return {"message": "Sequence reordered successfully", "steps": reordered_steps}

# ============== SENDER PROFILE ROUTES ==============

@router.post("/sender-profiles", response_model=SenderProfile)
async def create_sender_profile(profile_data: SenderProfileCreate, current_user: User = Depends(get_current_user)):
    profile = SenderProfile(**profile_data.model_dump(), created_by=current_user.id)
    doc = profile.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.sender_profiles.insert_one(doc)
    return profile

@router.get("/sender-profiles", response_model=List[SenderProfile])
async def get_sender_profiles(current_user: User = Depends(get_current_user)):
    profiles = await db.sender_profiles.find({"created_by": current_user.id}, {"_id": 0}).to_list(1000)
    for profile in profiles:
        if isinstance(profile.get('created_at'), str):
            profile['created_at'] = datetime.fromisoformat(profile['created_at'])
    return profiles

# ============== FEEDBACK ROUTES ==============

@router.post("/feedback", response_model=Feedback)
async def submit_feedback(feedback_data: FeedbackCreate, current_user: User = Depends(get_current_user)):
    feedback = Feedback(**feedback_data.model_dump(), user_id=current_user.id)
    doc = feedback.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.feedback.insert_one(doc)
    return feedback

@router.get("/feedback", response_model=List[Feedback])
async def get_feedback(current_user: User = Depends(get_current_user)):
    feedback_list = await db.feedback.find({}, {"_id": 0}).to_list(1000)
    for fb in feedback_list:
        if isinstance(fb.get('created_at'), str):
            fb['created_at'] = datetime.fromisoformat(fb['created_at'])
    return feedback_list

# ============== INSIGHTS ROUTES ==============

@router.get("/insights", response_model=List[InsightResponse])
async def get_insights(current_user: User = Depends(get_current_user)):
    # Get feedback and campaigns for analysis
    feedback_list = await db.feedback.find({}, {"_id": 0}).to_list(1000)
    campaigns = await db.campaigns.find({}, {"_id": 0}).to_list(1000)

    insights = []

    # Generate insights based on feedback patterns
    if len(feedback_list) > 5:
        avg_rating = sum(f['rating'] for f in feedback_list) / len(feedback_list)

        insight_id = str(uuid.uuid4())
        insight = {
            "id": insight_id,
            "campaign_id": None,
            "metric": "average_rating",
            "observation": f"Average feedback rating is {avg_rating:.1f}/5 based on {len(feedback_list)} responses",
            "suggested_action": "Continue current approach" if avg_rating >= 4 else "Review and improve messaging strategies",
            "status": "active",
            "created_at": datetime.now(timezone.utc)
        }
        insights.append(InsightResponse(**insight))

    # Campaign performance insights
    if len(campaigns) > 0:
        published_count = len([c for c in campaigns if c.get('status') == 'published'])
        draft_count = len([c for c in campaigns if c.get('status') == 'draft'])

        insight_id = str(uuid.uuid4())
        insight = {
            "id": insight_id,
            "campaign_id": None,
            "metric": "campaign_status",
            "observation": f"{published_count} campaigns published, {draft_count} in draft",
            "suggested_action": "Review draft campaigns and move to production" if draft_count > published_count else "Great campaign momentum!",
            "status": "active",
            "created_at": datetime.now(timezone.utc)
        }
        insights.append(InsightResponse(**insight))

    return insights

@router.post("/insights/run")
async def run_insights_engine(current_user: User = Depends(get_current_user)):
    """Trigger AI-powered insights generation"""
    campaigns = await db.campaigns.find({}, {"_id": 0}).to_list(1000)
    feedback_list = await db.feedback.find({}, {"_id": 0}).to_list(1000)

    prompt = f"""Analyze this sales platform data and provide actionable insights:

    Total Campaigns: {len(campaigns)}
    Total Feedback: {len(feedback_list)}

    Feedback ratings: {[f['rating'] for f in feedback_list[:10]]}
    Campaign stages: {[c.get('stage') for c in campaigns[:10]]}

    Provide 3 key insights with specific recommendations for improving sales effectiveness."""

    insights_text = await generate_llm_response(prompt)

    return {"insights": insights_text}

# ============== DASHBOARD STATS ==============

@router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    agents_count = await db.agents.count_documents({})
    campaigns_count = await db.campaigns.count_documents({"created_by": current_user.id})
    feedback_count = await db.feedback.count_documents({})
    documents_count = await db.documents.count_documents({"created_by": current_user.id})

    # Get recent activity
    recent_campaigns = await db.campaigns.find(
        {"created_by": current_user.id},
        {"_id": 0}
    ).sort("created_at", -1).limit(5).to_list(5)

    return {
        "agents_count": agents_count,
        "campaigns_count": campaigns_count,
        "feedback_count": feedback_count,
        "documents_count": documents_count,
        "recent_campaigns": recent_campaigns
    }
