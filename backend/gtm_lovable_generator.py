"""
GTM Lovable Prompt Generator
Generates interactive, personalized Lovable prototypes like ChatGPT workflow
"""

import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime


class LovablePromptGenerator:
    """
    Generates structured Lovable prompts with 7 interconnected sections:
    1. Landing Page (with prospect's photo/name)
    2. Dashboard (KPIs specific to their pain)
    3. AI Copilot (chat interface)
    4. Simulation/Workspace
    5. Client Impact (case studies + Figma)
    6. Insights & Roadmap
    7. Next Steps (CTA)
    """
    
    def __init__(self):
        self.demo_templates = {
            "mortgage_underwriting": {
                "title": "AI Underwriting Copilot",
                "kpis": ["Time-to-Decision ↓65%", "Exceptions ↓30%", "Manual Rework ↓25%", "Analyst Hours Saved 400+/mo"],
                "copilot_questions": [
                    "Summarize today's broker pipeline and flag risky cohorts.",
                    "Explain decision for Application #CMI-2025-01928.",
                    "Simulate: raise FICO cutoff by 10 pts & extend max LTV by 2%."
                ],
                "simulation_params": [
                    {"name": "Credit Score Cutoff", "min": 580, "max": 760, "default": 650},
                    {"name": "Max LTV (%)", "min": 60, "max": 95, "default": 80},
                    {"name": "Max TDS (%)", "min": 30, "max": 50, "default": 42}
                ]
            },
            "credit_risk": {
                "title": "Agentic AI Copilot for Credit Risk",
                "kpis": ["Approval Rate ↑40%", "Loss Ratio ↓25%", "Decision Time ↓80%", "Portfolio Health 92/100"],
                "copilot_questions": [
                    "Show me top 3 risk segments deteriorating this quarter.",
                    "Compare model accuracy vs. manual underwriting.",
                    "Simulate impact if we relax credit cutoff by 20 points."
                ],
                "simulation_params": [
                    {"name": "Interest Rate (%)", "min": 8, "max": 20, "default": 12},
                    {"name": "Loan Term (months)", "min": 24, "max": 72, "default": 48},
                    {"name": "Credit Score Cutoff", "min": 580, "max": 720, "default": 650}
                ]
            },
            "payments_reconciliation": {
                "title": "AI Reconciliation Copilot",
                "kpis": ["Reconciliation Time ↓70%", "Match Rate ↑95%", "Manual Exceptions ↓80%", "Cost per Transaction ↓60%"],
                "copilot_questions": [
                    "Show today's reconciliation mismatches and root causes.",
                    "Identify high-risk transactions requiring manual review.",
                    "Simulate: automate rule-based matching for low-risk transactions."
                ],
                "simulation_params": [
                    {"name": "Auto-Match Threshold (%)", "min": 80, "max": 99, "default": 95},
                    {"name": "Review Queue Size", "min": 10, "max": 500, "default": 100}
                ]
            },
            "real_estate_closing": {
                "title": "Connected Closings Platform",
                "kpis": ["Closing Time ↓55%", "Document Errors ↓70%", "Title Verification ↓80%", "Customer NPS ↑25%"],
                "copilot_questions": [
                    "Which closings are delayed and why?",
                    "Summarize today's funding-ready files.",
                    "Simulate: what if title verification were automated via LAC?"
                ],
                "simulation_params": [
                    {"name": "Doc Validation Threshold (%)", "min": 85, "max": 100, "default": 95},
                    {"name": "Auto-Approval Limit ($)", "min": 100000, "max": 1000000, "default": 500000}
                ]
            }
        }
    
    def generate_landing_section(self, prospect: Dict[str, Any]) -> str:
        """Generate Landing Page section with prospect's profile"""
        return f"""## 🏁 Landing Page (Hero Section)

Full-screen hero section:
- **Background**: Gradient blend of {prospect['company_name']} brand colors and Zuci blue (#009CDE)
- **Layout**: Split-screen with prospect photo on left, content on right

### Content:
**Photo Section (Left 40%)**:
- Large professional photo of {prospect['name']}
- Subtle animation (fade-in + slight zoom)
- Overlay badge: "{prospect['title']}"

**Hero Content (Right 60%)**:
- **Main Headline**: "{prospect['company_name']} × Zuci Systems"
- **Subheadline**: "Co-creating the Future of {prospect['industry']}"
- **Tagline**: "{prospect.get('tagline', 'Empowering Teams with Agentic Intelligence')}"

### Animated KPI Counters (fade in sequentially):
{self._format_kpi_counters(prospect)}

### Call-to-Action Buttons:
- Primary: "Experience the Copilot" → (scrolls to Dashboard)
- Secondary: "View Client Impact" → (jumps to Case Studies section)

### Design Details:
- Font: Inter/Nunito Sans, modern sans-serif
- Colors: White text on gradient background
- Micro-animations: Counters count up from 0, fade-in effects
- Responsive: Mobile-friendly with stacked layout
"""

    def generate_dashboard_section(self, prospect: Dict[str, Any], demo_type: str) -> str:
        """Generate Dashboard with KPIs specific to prospect's industry"""
        template = self.demo_templates.get(demo_type, self.demo_templates["credit_risk"])
        
        return f"""## 📊 Dashboard (Executive Overview)

**Header**: "{template['title']} – Real-Time Intelligence"

### KPI Tiles (4 cards, animate on scroll):
{self._format_kpi_tiles(template['kpis'])}

### Interactive Chart:
**Title**: "{prospect['industry']} Performance Trends (Last 12 Months)"
**Type**: Line chart with 3 metrics
- **Line 1**: Applications (blue)
- **Line 2**: Approvals (green)  
- **Line 3**: Pull-Through Rate (orange)
**Interaction**: Hover shows exact values, click filters by region

### Alert Banner (top-right):
**Icon**: ⚠️ Warning badge
**Messages** (rotate every 5 seconds):
- "Pipeline surge in {prospect.get('region', 'GTA')} – review capacity"
- "Appraisal turn-times rising +12%"
- "VOI verification delays detected"

### Quick Actions (bottom):
- **Button 1**: "Open AI Copilot" → (navigates to Copilot section)
- **Button 2**: "Run Policy Simulation" → (navigates to Simulation section)
- **Button 3**: "Generate Report (PDF)" → (downloads mock report)

### Design:
- Modern dashboard UI with glassmorphism effects
- Cards have subtle shadows and hover lift effects
- Color palette: White background, blue accents (#0A66C2), green for positive metrics
"""

    def generate_copilot_section(self, prospect: Dict[str, Any], demo_type: str) -> str:
        """Generate AI Copilot chat interface"""
        template = self.demo_templates.get(demo_type, self.demo_templates["credit_risk"])
        
        return f"""## 🤖 AI Copilot (Chat + Insights)

**Layout**: Two-panel split (40% chat / 60% visualization)

### Left Panel: Chat Interface
**Title**: "Ask Zuci Copilot"
**Subtitle**: "Your AI Assistant for {prospect['industry']}"

**Preset User Prompts** (clickable buttons):
{self._format_copilot_questions(template['copilot_questions'])}

**Example AI Response** (after user clicks first question):
```
🤖 Copilot Response:

Based on today's pipeline analysis:

📊 Risk Segments Flagged:
- Portfolio C (Western Region): Early risk signals detected
  • Delinquency trending ↑8% vs last month
  • Avg FICO declining from 652 → 638
  • Recommendation: Tighten underwriting criteria or increase pricing

- Segment B (Small Business Loans): Payment delays increasing
  • 14 accounts showing 30+ day late payments
  • Industry: Retail/Hospitality (macro headwinds)
  • Action: Proactive outreach, restructuring offers

💡 Model Insight: 
Approval probability for Portfolio C: 68% (down from 74%)
Key drivers: Income stability ↓, DTI ratio ↑, thin credit history

[Generate Detailed Report] [Send Alert to Risk Team]
```

### Right Panel: Visualization Area
**Dynamic Charts Based on Query**:
- Risk band distribution (A-E segments) - Bar chart
- Geographic heatmap - Regional risk intensity
- Trend line - Delinquency rate over time

**Interactive Elements**:
- Click segments to drill down
- Hover for detailed tooltips
- Export chart as PNG

### Bottom Action Bar:
- Button: "Generate Risk Report (PDF)"
- Button: "Send to Portfolio Manager"
- Button: "Schedule Follow-up Analysis"

### Design:
- Chat bubbles: User (right, blue), AI (left, gray)
- Typing indicator animation when "thinking"
- Smooth scroll, auto-scroll to latest message
- Charts render with animation (bars grow, lines draw)
"""

    def generate_simulation_section(self, prospect: Dict[str, Any], demo_type: str) -> str:
        """Generate interactive simulation workspace"""
        template = self.demo_templates.get(demo_type, self.demo_templates["credit_risk"])
        
        simulation_ui = self._format_simulation_sliders(template['simulation_params'])
        
        return f"""## 🧮 Policy Simulation Workspace

**Header**: "{prospect['company_name']} Simulation Concept"
**Subtitle**: "Test credit policy changes before implementation"

### Layout: Three-Column Design

#### Left Column (30%): Input Parameters
{simulation_ui}

**Big Action Button**: "🚀 Run Simulation"

#### Middle Column (40%): Loan File Preview (for context)
**Sample Borrower Profile**:
```
Application: #{prospect['company_name'][:3].upper()}-2025-01473
Borrower: Jane Smith
Co-Borrower: John Smith
Property: $450,000 (Toronto, ON)
Loan Amount: $360,000
LTV: 80%
Credit Score: 658
Income: $95,000 (verified)
DTI: 38%
Employment: 3 years (stable)
```

**Current Status**: ⏳ Pending Review
**Risk Band**: B (Moderate Risk)

#### Right Column (30%): Simulation Results

**Before Simulation**:
"Adjust parameters and click 'Run Simulation'"

**After Simulation** (animated results):
```
✅ Simulation Complete

Impact Analysis:

📈 Approvals: +9%
   Expected: 156 → 170 approvals/month

📊 Expected Loss: +1.6%
   Portfolio loss rate: 2.3% → 2.39%

💰 Net Yield: +2.8%
   Avg yield: 8.2% → 8.43%

⏱️ Ops Efficiency: -12 min/file
   Avg processing: 45 min → 33 min

🎯 Net Impact: POSITIVE
   Incremental revenue: +$180K/month
   Incremental loss provision: -$24K/month
   Net gain: +$156K/month
```

**AI Insight Box**:
```
💡 Copilot Recommendation:

"{prospect['name']}, adjusting the credit cutoff from 650 → 620 
would increase your approval rate by 9% while keeping expected 
loss within tolerance (+1.6%).

The net yield improvement (+2.8%) suggests this policy change 
is favorable for {prospect['company_name']}'s growth objectives.

Recommend: Implement for 60-day trial period, monitor cohort 
performance, adjust if delinquency exceeds 3.5%."
```

### Bottom Action Bar:
- "📄 Generate Policy Change Memo"
- "📧 Send to Risk Committee"
- "🔄 Reset to Defaults"

### Design:
- Sliders have real-time preview values
- Results animate in with count-up effects
- Color-coded metrics (green=positive, red=negative, blue=neutral)
- Professional financial dashboard aesthetic
"""

    def generate_impact_section(self, case_studies: List[Dict], figma_urls: List[str]) -> str:
        """Generate Client Impact section with case studies and Figma embeds"""
        case_study_html = ""
        
        for idx, cs in enumerate(case_studies, 1):
            case_study_html += f"""
### {idx}. {cs['title']}
**Industry**: {cs.get('category', 'Financial Services')}

**Outcomes**:
- **Time Efficiency**: {cs.get('metric_time', 'Decision time ↓65%')}
- **Quality Improvement**: {cs.get('metric_quality', 'Exceptions ↓30%')}
- **Cost Savings**: {cs.get('savings', '$250-500K annually')}
- **ROI**: {cs.get('roi', '10× in 9-12 months')}

**What We Built**:
{cs.get('summary', 'Application modernization, AI-assisted underwriting, and portfolio visibility platform')}

"""
        
        figma_section = ""
        if figma_urls:
            figma_section = f"""
### 🎨 Visual Concepts (Figma Prototypes)

**Interactive Prototypes** (click to explore):
{chr(10).join([f'- [View {url.split("/")[-1][:20]}... Prototype]({url})' for url in figma_urls])}

**Embed Options**:
```html
<iframe 
  src="{figma_urls[0] if figma_urls else 'https://figma.com/...'}" 
  width="100%" 
  height="600px" 
  frameborder="0"
  allowfullscreen>
</iframe>
```
"""
        
        return f"""## 💼 Client Impact (Proven Results)

**Header**: "Relevant Experience – Real Results in {chr(10).join([cs.get('category', 'Financial Services') for cs in case_studies[:2]])}"

**Layout**: Two-column grid

### Left Column: Case Study Metrics
{case_study_html}

### Right Column: ROI Visualization
**Chart**: Bar chart comparing metrics
- Time Savings (hours/month)
- Cost Reduction ($K/year)
- Accuracy Improvement (%)

**Summary Tiles**:
```
┌─────────────────────────────────┐
│  Average ROI: 10-15×            │
│  Typical Timeline: 6-12 months  │
│  Analyst Hours Saved: 300-500/mo│
│  Customer Satisfaction: +25%    │
└─────────────────────────────────┘
```

{figma_section}

### Credibility Statement:
**Footer**: "The same automation and explainability framework can transform {'{company_name}'}'s operations."

### Design:
- Professional case study cards with hover effects
- Metrics displayed as animated counters
- Figma embeds with loading states
- Trust badges/logos of client companies
"""

    def generate_insights_section(self, prospect: Dict[str, Any]) -> str:
        """Generate Insights & Roadmap section"""
        return f"""## 🚀 Insights & Next Steps

### Evolution Roadmap
**Animated Timeline** (horizontal scroll):

```
Phase 1              Phase 2              Phase 3              Phase 4
─────────────────────────────────────────────────────────────────────
📄 Document          🤖 AI Decisioning    🧠 Agentic Copilot   📊 Portfolio
   Automation           (6-9 months)        (9-12 months)        Optimization
   (3-6 months)                                                  (12-18 months)
   
✓ OCR, extraction    ✓ Predictive models  ✓ Chat interface     ✓ Risk monitoring
✓ Validation rules   ✓ Auto-decisions     ✓ Policy simulation  ✓ Early warnings
✓ Workflow           ✓ Explainability     ✓ Audit trails       ✓ Strategy insights
```

### Integration Architecture
**Diagram**: System integration map

```
┌─────────────────────────────────────────────────┐
│          {prospect['company_name']} Ecosystem   │
├─────────────────────────────────────────────────┤
│                                                 │
│  LOS/CRM          Credit Bureau      Banking    │
│  (Filogix/Finmo)  (Equifax/TU)      (Plaid)    │
│       ↓                ↓                ↓       │
│       └────────────────┴────────────────┘       │
│                       │                         │
│              ┌────────▼─────────┐               │
│              │  Zuci AI Layer   │               │
│              │  - Data Pipeline │               │
│              │  - ML Models     │               │
│              │  - Copilot API   │               │
│              └────────┬─────────┘               │
│                       │                         │
│       ┌───────────────┼───────────────┐         │
│       ↓               ↓               ↓         │
│  Underwriting    Portfolio       Compliance     │
│  Dashboard       Monitoring      Reporting      │
└─────────────────────────────────────────────────┘
```

### Deployment Options:
- **API-First**: RESTful APIs for easy integration
- **Microservices**: Modular, scalable architecture
- **Private Cloud**: Secure VPC deployment (AWS/Azure)
- **Compliance-Ready**: Audit logs, explainability, data governance

### Key Differentiators:
✅ **No Black Box**: Full explainability with reason codes
✅ **Team Empowerment**: Augments analysts, doesn't replace them
✅ **Rapid ROI**: Measurable impact in 6-9 months
✅ **Flexible Integration**: Works with existing systems

### Pilot Proposal:
**Suggested Approach**:
```
Week 1-2:  Discovery & Data Assessment
Week 3-4:  Integration & Model Setup
Week 5-6:  Testing & Validation
Week 7-8:  Pilot Launch (one product line)
Week 9-12: Monitor, Measure, Optimize
```

**Success Metrics**:
- Time-to-decision reduction: Target 50%+
- Exception rate reduction: Target 25%+
- Analyst productivity: Target 30%+ hours saved

### Design:
- Clean, modern infographic style
- Interactive timeline (click to expand phases)
- Architecture diagram with hover tooltips
- Professional B2B aesthetic
"""

    def generate_cta_section(self, prospect: Dict[str, Any]) -> str:
        """Generate Call-to-Action section"""
        return f"""## 🎯 Next Steps & Call-to-Action

**Header**: "Ready to Transform {prospect['company_name']}'s Operations?"

### Primary CTA:
```
┌─────────────────────────────────────────────┐
│                                             │
│   📅 Book a 45-Minute Deep Dive with       │
│      {prospect['name']}                     │
│                                             │
│   [Schedule Meeting] →                     │
│                                             │
│   Available slots:                          │
│   • Tomorrow at 2:00 PM                     │
│   • Thursday at 10:00 AM                    │
│   • Friday at 3:00 PM                       │
│                                             │
└─────────────────────────────────────────────┘
```

### Secondary CTAs:
**Three-column layout**:

```
┌──────────────┬──────────────┬──────────────┐
│ 📄 Download  │ 🎨 Explore   │ 💬 Contact   │
│ Concept Deck │ More Demos   │ Sales Team   │
│              │              │              │
│ 2-page PDF   │ Interactive  │ Direct line  │
│ summary      │ prototypes   │ to experts   │
│              │              │              │
│ [Download]   │ [View More]  │ [Contact]    │
└──────────────┴──────────────┴──────────────┘
```

### Trust Signals:
**Footer Section**:
```
Trusted by leading financial institutions:

[MCAN Logo]  [Mariner Logo]  [MAPS CU Logo]  [Numerica Logo]

"We've delivered $2M+ in efficiency savings across 15+ clients"
```

### Contact Information:
```
📧 Email: tamil.bharathi@zuci.com
📞 Phone: +1 647 404 2503
🌐 Web: www.zucisystems.com
📍 Location: Toronto, ON
```

### Final Tagline:
**Large, bold text**:
> "From {prospect['industry']} Pain Points to Proven Performance"
> 
> "{prospect['company_name']} × Zuci Systems – Let's Build Together"

### Design:
- High-contrast CTA buttons with hover animations
- Calendar integration (if possible)
- Trust badges/social proof
- Professional contact card design
- Mobile-responsive layout
"""

    def assemble_full_prompt(
        self,
        prospect: Dict[str, Any],
        demo_type: str,
        case_studies: List[Dict],
        figma_urls: List[str] = []
    ) -> str:
        """Assemble complete Lovable prompt with all sections"""
        
        company_name = prospect['company_name']
        demo_title = self.demo_templates.get(demo_type, {}).get('title', 'AI-Powered Platform')
        
        header = f"""# {company_name} × Zuci – {demo_title}

**Created for**: {prospect['name']}, {prospect['title']}
**Meeting**: {prospect.get('meeting_date', 'TBD')} | {prospect.get('meeting_duration', '15 min')}
**Location**: {prospect.get('meeting_location', 'Virtual')}

---

## 🎯 Objective
Create a clickable, interactive web prototype that demonstrates how Zuci's {demo_title} 
can transform {company_name}'s operations through AI-powered automation, explainability, 
and seamless integration.

**Tone**: Professional, CIO-friendly, pragmatic, and visually stunning
**Style**: Modern fintech/proptech design with micro-animations
**Output**: Production-ready prototype ready for live demo

---

## 🎨 Branding & Design System

### Color Palette:
- **Primary**: Zuci Blue `#009CDE`
- **Secondary**: {company_name} Brand Colors (research and apply)
- **Accent**: Green for positive metrics `#10B981`, Red for alerts `#EF4444`
- **Background**: White `#FFFFFF`, Light gray sections `#F9FAFB`
- **Text**: Dark gray `#1F2937`, Medium gray `#6B7280`

### Typography:
- **Headings**: Inter Bold, 32px-48px
- **Body**: Inter Regular, 16px-18px
- **Labels**: Inter Medium, 14px
- **Code**: Fira Code, 14px

### Design Elements:
- Rounded corners (8px-16px)
- Subtle shadows on cards
- Smooth transitions (300ms ease)
- Hover effects (lift, scale, glow)
- Loading states and animations
- Glassmorphism effects on hero sections

---

## 📐 Navigation Structure

**Top Navigation Bar** (sticky):
```
[{company_name} Logo]  Dashboard  |  AI Copilot  |  Simulation  |  Client Impact  |  Insights  |  Next Steps  [Zuci Logo]
```

**Mobile**: Hamburger menu with same sections

---

"""
        
        sections = [
            header,
            self.generate_landing_section(prospect),
            self.generate_dashboard_section(prospect, demo_type),
            self.generate_copilot_section(prospect, demo_type),
            self.generate_simulation_section(prospect, demo_type),
            self.generate_impact_section(case_studies, figma_urls),
            self.generate_insights_section(prospect),
            self.generate_cta_section(prospect)
        ]
        
        footer = f"""
---

## ✨ Interactive Behaviors

### Must-Have Interactions:
1. **Smooth Scroll**: All navigation links scroll smoothly to sections
2. **Hover Effects**: Cards lift on hover, buttons scale slightly
3. **Click Animations**: Success toasts, loading spinners
4. **Chart Animations**: Bars grow, lines draw, counters count up
5. **Modal Windows**: For detailed views (click charts, case studies)
6. **Form Validation**: Real-time validation on input fields
7. **Responsive**: Mobile-first design, works on all devices

### Data Handling:
- Use **synthetic/demo data** (no real customer info)
- Make charts **interactive** (hover, click, zoom)
- Add **audit logs** visible on demand
- Include **export options** (PDF, CSV) as mockups

---

## 🚀 Deliverable

A fully functional, clickable prototype where:
- Every section is navigable
- Every button triggers an appropriate action (even if mocked)
- Charts and visualizations are interactive
- The experience feels like a real product demo
- {prospect['name']} can click through during the meeting

**Quality Bar**: Production-ready, not wireframes. Should look like a real SaaS product.

---

## 📝 Sample Data Suggestions

### For {company_name}:
- Use Canadian geography (Toronto, Vancouver, Calgary, Ottawa)
- Use realistic {prospect['industry']} metrics
- Reference actual market trends (2024-2025)
- Include competitor benchmarks

### For Zuci Case Studies:
- MCAN Financial (Mortgage)
- Mariner Finance (Consumer Lending)
- MAPS Credit Union (Automation)
- Numerica Credit Union (Fraud Prevention)

---

**End of Prompt** – Paste this into Lovable.dev or similar prototype builder.

Generated by Zuci GTM Generator on {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        
        return "\n\n".join(sections) + footer

    # Helper methods
    def _format_kpi_counters(self, prospect: Dict) -> str:
        kpis = prospect.get('kpis', [
            "Decision Speed ↑65%",
            "Accuracy ↑40%",
            "Cost Savings $500K+/year",
            "Customer Satisfaction ↑25%"
        ])
        return "\n".join([f"- **{kpi}**" for kpi in kpis])
    
    def _format_kpi_tiles(self, kpis: List[str]) -> str:
        tiles = []
        icons = ["📈", "✅", "⏱️", "💰"]
        for i, kpi in enumerate(kpis):
            icon = icons[i % len(icons)]
            tiles.append(f"""
**Card {i+1}**: {icon} {kpi}
- Large number display (e.g., "65%" or "400+")
- Small label below
- Subtle gradient background
- Animate on scroll (count up from 0)""")
        return "\n".join(tiles)
    
    def _format_copilot_questions(self, questions: List[str]) -> str:
        return "\n".join([f'{i+1}. "{q}"' for i, q in enumerate(questions)])
    
    def _format_simulation_sliders(self, params: List[Dict]) -> str:
        sliders = []
        for param in params:
            sliders.append(f"""
**{param['name']}**
- Slider: {param['min']} ←→ {param['max']}
- Default: {param['default']}
- Live preview value display
""")
        return "\n".join(sliders)


# Factory function
def create_lovable_prompt(
    prospect_data: Dict[str, Any],
    demo_type: str,
    case_studies: List[Dict],
    figma_urls: List[str] = []
) -> str:
    """
    Main entry point for generating Lovable prompts
    
    Args:
        prospect_data: Dict with prospect info (name, title, company, etc.)
        demo_type: One of the template keys (e.g., 'mortgage_underwriting')
        case_studies: List of relevant case study dicts
        figma_urls: List of Figma prototype URLs to embed
    
    Returns:
        Complete Lovable prompt as string
    """
    generator = LovablePromptGenerator()
    return generator.assemble_full_prompt(prospect_data, demo_type, case_studies, figma_urls)
