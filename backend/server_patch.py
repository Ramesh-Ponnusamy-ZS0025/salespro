# Campaign Model Updates
class FunnelInput(BaseModel):
    type: str  # "tofu", "mofu", "bofu"
    value: str

class CustomInput(BaseModel):
    type: str = "custom"
    value: str

# Update Campaign and CampaignCreate models with new fields:
# funnel_inputs: List[FunnelInput] = []
# custom_inputs: List[CustomInput] = []
# selected_documents: List[str] = []
# auto_pick_documents: bool = False

# Update DocumentFile model with summary field:
# summary: Optional[str] = None
