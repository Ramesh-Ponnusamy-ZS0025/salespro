"""
Microsite Component Generators
Creates beautiful, reusable HTML components for microsites
"""

def generate_trust_logos(count=6):
    """Generate trust logo placeholder grid"""
    logos = []
    companies = [
        "TechCorp", "InnovateCo", "Global Solutions", "DataTech",
        "CloudSystems", "SmartBusiness", "FutureWorks", "AgileGroup"
    ]

    for i in range(min(count, len(companies))):
        logos.append(f'''
            <div class="flex items-center justify-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-all grayscale hover:grayscale-0">
                <div class="text-2xl font-bold text-gray-400 hover:text-gray-700">{companies[i]}</div>
            </div>
        ''')

    return '\n'.join(logos)


def generate_pain_point_card(title, description, icon_emoji="⚠️"):
    """Generate a pain point card"""
    return f'''
        <div class="fade-in bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300">
            <div class="text-5xl mb-4">{icon_emoji}</div>
            <h3 class="text-2xl font-bold mb-4 text-gray-900">{title}</h3>
            <p class="text-gray-600 leading-relaxed">{description}</p>
        </div>
    '''


def generate_value_prop_card(title, description, gradient_from="blue", gradient_to="indigo"):
    """Generate a value proposition card"""
    return f'''
        <div class="fade-in bg-gradient-to-br from-{gradient_from}-50 to-{gradient_to}-50 rounded-2xl p-8 shadow-lg hover:shadow-2xl hover:scale-105 transition-all duration-300 border border-{gradient_from}-100">
            <div class="flex items-center gap-3 mb-4">
                <div class="w-12 h-12 bg-gradient-to-br from-{gradient_from}-500 to-{gradient_to}-600 rounded-full flex items-center justify-center text-white text-2xl">
                    ✓
                </div>
                <h3 class="text-2xl font-bold text-gray-900">{title}</h3>
            </div>
            <p class="text-gray-700 leading-relaxed">{description}</p>
        </div>
    '''


def generate_use_case_card(use_case_id, title, description, icon="🚀", theme="blue"):
    """Generate a clickable use case card"""
    return f'''
        <div class="use-case-card cursor-pointer group fade-in" onclick="openModal('{use_case_id}')">
            <div class="bg-gradient-to-br from-{theme}-50 to-purple-50 rounded-2xl p-8 hover:shadow-2xl hover:scale-105 transition-all duration-300">
                <div class="text-5xl mb-4 group-hover:scale-110 transition-transform">{icon}</div>
                <h3 class="text-2xl font-bold mb-3 text-gray-900 group-hover:text-{theme}-600 transition-colors">{title}</h3>
                <p class="text-gray-600 mb-4">{description}</p>
                <div class="text-{theme}-600 font-semibold inline-flex items-center gap-2 group-hover:gap-3 transition-all">
                    Explore Demo
                    <svg class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                    </svg>
                </div>
            </div>
        </div>
    '''


def generate_use_case_modal(use_case_id, title, description, benefit, demo_content):
    """Generate a use case modal with demo"""
    return f'''
        <div id="{use_case_id}-modal" class="modal fixed inset-0 bg-black/50 backdrop-blur-sm hidden z-50 flex items-center justify-center p-4" onclick="closeModal('{use_case_id}')">
            <div class="modal-content bg-white rounded-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto shadow-2xl animate-slide-up" onclick="event.stopPropagation()">
                <div class="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-start justify-between z-10">
                    <h2 class="text-3xl font-bold text-gray-900">{title}</h2>
                    <button onclick="closeModal('{use_case_id}')" class="text-gray-400 hover:text-gray-600 transition-colors">
                        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>

                <div class="p-8 space-y-8">
                    <p class="text-xl text-gray-700">{description}</p>

                    <!-- Demo Content -->
                    <div class="bg-gray-50 rounded-xl p-6">
                        {demo_content}
                    </div>

                    <!-- Benefit Callout -->
                    <div class="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-6">
                        <p class="text-xl font-semibold text-green-900 flex items-center gap-3">
                            <span class="text-3xl">✨</span>
                            {benefit}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    '''


def generate_case_study_card(title, client_name, industry, metrics, description):
    """Generate a case study card with metrics"""
    metrics_html = []
    for metric in metrics[:3]:  # Max 3 metrics
        metrics_html.append(f'''
            <div class="text-center">
                <div class="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">{metric['value']}</div>
                <div class="text-sm text-gray-600">{metric['label']}</div>
            </div>
        ''')

    return f'''
        <div class="fade-in bg-white rounded-2xl shadow-lg p-8 hover:shadow-2xl hover:-translate-y-2 transition-all duration-300">
            <div class="flex items-center justify-between mb-6">
                <div class="text-xl font-bold text-gray-900">{client_name}</div>
                <span class="text-sm text-indigo-600 font-semibold bg-indigo-50 px-3 py-1 rounded-full">{industry}</span>
            </div>
            <h3 class="text-2xl font-bold mb-4 text-gray-900">{title}</h3>
            <div class="grid grid-cols-3 gap-4 mb-6 py-6 border-y border-gray-200">
                {''.join(metrics_html)}
            </div>
            <p class="text-gray-700 mb-6 leading-relaxed">{description}</p>
            <a href="#" class="text-indigo-600 font-semibold inline-flex items-center gap-2 hover:gap-3 transition-all group">
                Read Full Case Study
                <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
            </a>
        </div>
    '''


def generate_metric_card(value, label, description, color="blue"):
    """Generate a metric card"""
    return f'''
        <div class="fade-in bg-gradient-to-br from-{color}-50 to-indigo-50 rounded-2xl p-8 hover:shadow-xl transition-all duration-300">
            <div class="text-6xl font-bold bg-gradient-to-r from-{color}-600 to-purple-600 bg-clip-text text-transparent mb-4">{value}</div>
            <div class="text-2xl font-semibold text-gray-900 mb-3">{label}</div>
            <div class="text-gray-600">{description}</div>
        </div>
    '''


def generate_testimonial_card(quote, name, title, company):
    """Generate a testimonial card"""
    stars = ''.join(['<svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path></svg>' for _ in range(5)])

    return f'''
        <div class="fade-in bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300">
            <div class="flex items-center gap-1 mb-6">
                {stars}
            </div>
            <p class="text-gray-700 italic text-lg mb-6 leading-relaxed">"{quote}"</p>
            <div class="flex items-center gap-4">
                <div class="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white text-xl font-bold">
                    {name[0]}
                </div>
                <div>
                    <div class="font-semibold text-gray-900">{name}</div>
                    <div class="text-sm text-gray-600">{title}, {company}</div>
                </div>
            </div>
        </div>
    '''


def generate_demo_content_simple(steps):
    """Generate simple demo content with steps"""
    steps_html = []
    for i, step in enumerate(steps):
        steps_html.append(f'''
            <div class="flex items-start gap-4 mb-6">
                <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
                    {i + 1}
                </div>
                <div>
                    <h4 class="text-xl font-semibold mb-2 text-gray-900">{step['title']}</h4>
                    <p class="text-gray-600">{step['description']}</p>
                </div>
            </div>
        ''')

    return '<div class="space-y-4">' + ''.join(steps_html) + '</div>'


def get_theme_classes(theme_key):
    """Get CSS classes for a specific theme"""
    themes = {
        "ai_tech": {
            "BODY_CLASS": "bg-slate-900",
            "HERO_BG_CLASS": "bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900",
            "HERO_TEXT_CLASS": "text-white",
            "HERO_SUBTEXT_CLASS": "text-gray-300",
            "TEXT_GRADIENT_CLASS": "bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent",
            "CTA_BUTTON_CLASS": "bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700",
            "GLOW_CLASS": "glow-hover",
            "SECTION_BG_CLASS": "bg-slate-800",
            "SECTION_HEADER_CLASS": "text-white",
            "CUSTOM_CSS": """
                body { color: #e2e8f0; }
                .modal { color: #1f2937; }
            """
        },
        "enterprise": {
            "BODY_CLASS": "bg-white",
            "HERO_BG_CLASS": "bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700",
            "HERO_TEXT_CLASS": "text-white",
            "HERO_SUBTEXT_CLASS": "text-blue-100",
            "TEXT_GRADIENT_CLASS": "bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent",
            "CTA_BUTTON_CLASS": "bg-indigo-600 text-white hover:bg-indigo-700",
            "GLOW_CLASS": "",
            "SECTION_BG_CLASS": "bg-white",
            "SECTION_HEADER_CLASS": "text-gray-900",
            "CUSTOM_CSS": ""
        },
        "fintech": {
            "BODY_CLASS": "bg-white",
            "HERO_BG_CLASS": "bg-gradient-to-br from-green-600 via-blue-600 to-indigo-700",
            "HERO_TEXT_CLASS": "text-white",
            "HERO_SUBTEXT_CLASS": "text-green-100",
            "TEXT_GRADIENT_CLASS": "bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent",
            "CTA_BUTTON_CLASS": "bg-green-600 text-white hover:bg-green-700",
            "GLOW_CLASS": "",
            "SECTION_BG_CLASS": "bg-white",
            "SECTION_HEADER_CLASS": "text-gray-900",
            "CUSTOM_CSS": ""
        },
        "healthcare": {
            "BODY_CLASS": "bg-white",
            "HERO_BG_CLASS": "bg-gradient-to-br from-blue-600 via-cyan-500 to-teal-600",
            "HERO_TEXT_CLASS": "text-white",
            "HERO_SUBTEXT_CLASS": "text-blue-100",
            "TEXT_GRADIENT_CLASS": "bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent",
            "CTA_BUTTON_CLASS": "bg-blue-600 text-white hover:bg-blue-700",
            "GLOW_CLASS": "",
            "SECTION_BG_CLASS": "bg-white",
            "SECTION_HEADER_CLASS": "text-gray-900",
            "CUSTOM_CSS": ""
        }
    }

    return themes.get(theme_key, themes["enterprise"])
