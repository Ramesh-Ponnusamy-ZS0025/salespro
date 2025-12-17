const API_URL = 'http://localhost:8001/api';

// Global state
let currentStep = 1;
let currentProfile = null;
let selectedInsights = [];
let allInsights = [];
let selectedCaseStudies = [];
let selectedContentType = 'email';
let allCaseStudies = [];
let authToken = null;

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', init);

async function init() {
    // Check if user is logged in
    const isLoggedIn = await checkAuthStatus();

    if (isLoggedIn) {
        showMainContent();
        setupEventListeners();
        await loadSavedInstructions();
        await loadValuePropositions();
    } else {
        showLoginPage();
        setupLoginListeners();
    }
}

// Check authentication status
async function checkAuthStatus() {
    try {
        // Get token from chrome storage
        const result = await chrome.storage.local.get(['authToken']);
        if (result.authToken) {
            authToken = result.authToken;

            // Verify token is still valid by making a test API call
            const response = await fetch(`${API_URL}/value-propositions`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });

            if (response.ok) {
                return true;
            } else {
                // Token is invalid, clear it
                await chrome.storage.local.remove('authToken');
                authToken = null;
                return false;
            }
        }
        return false;
    } catch (error) {
        console.error('Error checking auth status:', error);
        return false;
    }
}

// Show login page
function showLoginPage() {
    const loginContainer = document.getElementById('loginContainer');
    const mainContent = document.getElementById('mainContent');

    if (loginContainer) loginContainer.classList.remove('hidden');
    if (mainContent) mainContent.classList.add('hidden');
}

// Show main content
function showMainContent() {
    const loginContainer = document.getElementById('loginContainer');
    const mainContent = document.getElementById('mainContent');

    if (loginContainer) loginContainer.classList.add('hidden');
    if (mainContent) mainContent.classList.remove('hidden');
}

// Setup login event listeners
function setupLoginListeners() {
    const loginForm = document.getElementById('loginForm');
    const signupLink = document.getElementById('signupLink');

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    if (signupLink) {
        signupLink.addEventListener('click', (e) => {
            e.preventDefault();
            // Open signup page in new tab
            chrome.tabs.create({ url: 'http://localhost:3000/signup' });
        });
    }
}

// Handle login form submission
async function handleLogin(e) {
    e.preventDefault();

    const loginBtn = document.getElementById('loginBtn');
    const loginError = document.getElementById('loginError');
    const emailInput = document.getElementById('loginEmail');
    const passwordInput = document.getElementById('loginPassword');

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    // Hide error
    loginError.classList.add('hidden');

    // Show loading state
    loginBtn.classList.add('loading');
    loginBtn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;

            // Save token to chrome storage
            await chrome.storage.local.set({ authToken });

            // Show main content and initialize
            showMainContent();
            setupEventListeners();
            await loadSavedInstructions();
            await loadValuePropositions();

            // Reset form
            emailInput.value = '';
            passwordInput.value = '';
        } else {
            const errorData = await response.json();
            loginError.textContent = errorData.detail || 'Invalid email or password';
            loginError.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Login error:', error);
        loginError.textContent = 'Connection error. Please try again.';
        loginError.classList.remove('hidden');
    } finally {
        loginBtn.classList.remove('loading');
        loginBtn.disabled = false;
    }
}

// Setup all event listeners
function setupEventListeners() {
    // Navigation buttons
    const nextBtn = document.getElementById('nextBtn');
    const backBtn = document.getElementById('backToStep1');
    const closeBtn = document.getElementById('closeBtn');
    const settingsBtn = document.getElementById('settingsBtn');

    if (nextBtn) nextBtn.addEventListener('click', goToStep2);
    if (backBtn) backBtn.addEventListener('click', goToStep1);
    if (closeBtn) closeBtn.addEventListener('click', closeSidepanel);
    if (settingsBtn) settingsBtn.addEventListener('click', openSettings);

    // Content type selection (radio buttons)
    document.querySelectorAll('input[name="contentType"]').forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.checked) {
                selectedContentType = this.value;
                console.log('Content type changed to:', selectedContentType);
            }
        });
    });

    // Case studies modal
    const addAssetsBtn = document.getElementById('addAssetsBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelAssetsBtn = document.getElementById('cancelAssetsBtn');
    const addSelectedAssetsBtn = document.getElementById('addSelectedAssetsBtn');
    const assetSearch = document.getElementById('assetSearch');

    if (addAssetsBtn) addAssetsBtn.addEventListener('click', openCaseStudiesModal);
    if (closeModalBtn) closeModalBtn.addEventListener('click', closeCaseStudiesModal);
    if (cancelAssetsBtn) cancelAssetsBtn.addEventListener('click', closeCaseStudiesModal);
    if (addSelectedAssetsBtn) addSelectedAssetsBtn.addEventListener('click', addSelectedCaseStudies);
    if (assetSearch) assetSearch.addEventListener('input', filterCaseStudies);

    // Custom instructions
    const saveInstructionBtn = document.getElementById('saveInstructionBtn');
    const closeSaveModalBtn = document.getElementById('closeSaveModalBtn');
    const cancelSaveBtn = document.getElementById('cancelSaveBtn');
    const confirmSaveBtn = document.getElementById('confirmSaveBtn');
    const savedInstructionsSelect = document.getElementById('savedInstructionsSelect');

    if (saveInstructionBtn) saveInstructionBtn.addEventListener('click', showSaveInstructionModal);
    if (closeSaveModalBtn) closeSaveModalBtn.addEventListener('click', closeSaveInstructionModal);
    if (cancelSaveBtn) cancelSaveBtn.addEventListener('click', closeSaveInstructionModal);
    if (confirmSaveBtn) confirmSaveBtn.addEventListener('click', saveCustomInstruction);
    if (savedInstructionsSelect) savedInstructionsSelect.addEventListener('change', loadSavedInstruction);

    // Update score when value prop or context changes
    const valuePropSelect = document.getElementById('valuePropositionSelect');
    const additionalInput = document.getElementById('additionalInput');
    if (valuePropSelect) valuePropSelect.addEventListener('change', updateSelectionCounter);
    if (additionalInput) additionalInput.addEventListener('input', updateSelectionCounter);

    // New Agent button
    const newAgentBtn = document.getElementById('newAgentBtn');
    if (newAgentBtn) newAgentBtn.addEventListener('click', openAgentBuilder);

    // Content generation
    const generateContentBtn = document.getElementById('generateContentBtn');
    const copyBtn = document.getElementById('copyBtn');
    const regenerateBtn = document.getElementById('regenerateBtn');

    if (generateContentBtn) generateContentBtn.addEventListener('click', generateContent);
    if (copyBtn) copyBtn.addEventListener('click', copyToClipboard);
    if (regenerateBtn) regenerateBtn.addEventListener('click', generateContent);

    // Custom multi-select dropdown
    setupContentFocusDropdown();

    // Step 3 navigation buttons
    const backToStep2Btn = document.getElementById('backToStep2');
    const generateVariationBtn = document.getElementById('generateVariationBtn');

    if (backToStep2Btn) backToStep2Btn.addEventListener('click', goToStep2FromStep3);
    if (generateVariationBtn) generateVariationBtn.addEventListener('click', () => {
        // Keep all selections, just regenerate with same settings
        showLoading(true);
        generateContent();
    });
}

// Listen for LinkedIn profile data from content script
window.addEventListener('message', (event) => {
    if (event.data.type === 'LINKEDIN_DATA') {
        currentProfile = event.data.data;
        displayProfileInfo(currentProfile);
        generateInsights(currentProfile);
    }
});

// Display profile information in UI
function displayProfileInfo(profile) {
    const elements = {
        name: document.getElementById('profileName'),
        title: document.getElementById('profileTitle'),
        company: document.getElementById('profileCompany'),
        location: document.getElementById('profileLocation'),
        avatar: document.getElementById('profileAvatar')
    };

    if (elements.name) elements.name.textContent = profile.name || 'Unknown';
    if (elements.title) elements.title.textContent = profile.title || '';
    if (elements.company) elements.company.textContent = profile.company ? `🏛️ ${profile.company}` : '';
    if (elements.location) elements.location.textContent = profile.location ? `📍 ${profile.location}` : '';

    // Set avatar initials
    if (elements.avatar && profile.name) {
        const initials = profile.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
        elements.avatar.textContent = initials;
    }
}

// Generate insights from LinkedIn profile data
function generateInsights(profile) {
    allInsights = [];
    let id = 0;

    // ========== LINKEDIN DATA ========== (SELECTED BY DEFAULT)
    // LinkedIn About Me
    if (profile.about) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'LinkedIn Data',
            icon: 'ℹ️',
            title: 'LinkedIn: About Me',
            content: profile.about.substring(0, 200) + (profile.about.length > 200 ? '...' : ''),
            fullContent: profile.about,
            selected: true  // Selected by default
        });
    }

    // LinkedIn Company Description
    if (profile.company_description) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'LinkedIn Data',
            icon: '🏛️',
            title: 'LinkedIn: Company Description',
            content: profile.company_description.substring(0, 200) + (profile.company_description.length > 200 ? '...' : ''),
            fullContent: profile.company_description,
            selected: true  // Selected by default
        });
    }

    // Top Skills from About Section
    if (profile.top_skills_from_about) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'LinkedIn Data',
            icon: '⭐',
            title: 'LinkedIn: Top Skills',
            content: profile.top_skills_from_about,
            selected: true  // Selected by default
        });
    }

    // ========== COMPANY INFORMATION ========== (UNSELECTED BY DEFAULT)
    // Company Name
    if (profile.company) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Company Information',
            icon: '🏢',
            title: 'Company Name',
            content: profile.company,
            selected: false
        });
    }

    // Company Description
    if (profile.company_description) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Company Information',
            icon: '📖',
            title: 'Company Description',
            content: profile.company_description.substring(0, 200) + (profile.company_description.length > 200 ? '...' : ''),
            fullContent: profile.company_description,
            selected: false
        });
    }

    // How Long Working at Company
    if (profile.years_at_company !== undefined && profile.years_at_company !== null) {
        const years = Math.floor(profile.years_at_company);
        const months = Math.round((profile.years_at_company - years) * 12);
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Company Information',
            icon: '📅',
            title: 'How Long Working at Company',
            content: `${years} years, ${months} months at ${profile.company || 'current company'}`,
            selected: false
        });
    }

    // Work Milestones
    if (profile.work_milestones && profile.work_milestones.length > 0) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Company Information',
            icon: '🏆',
            title: 'Work Milestones',
            content: profile.work_milestones.join(' • '),
            selected: false
        });
    }

    // Business Model
    if (profile.business_model) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Company Information',
            icon: '💼',
            title: 'Business Model',
            content: profile.business_model,
            selected: false
        });
    }

    // Company Headcount (bonus)
    if (profile.company_headcount) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Company Information',
            icon: '👥',
            title: 'Company Size',
            content: `~${profile.company_headcount.toLocaleString()} employees`,
            selected: false
        });
    }

    // Number of Roles at Current Company
    if (profile.num_roles_at_company !== undefined) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Company Information',
            icon: '🔄',
            title: 'Number of Roles at Current Company',
            content: `Number of roles at current company: ${profile.num_roles_at_company}`,
            selected: false
        });
    }

    // ========== COMPANY EXPERIENCE ==========
    // Work Experience - Compact view with all details
    console.log('Profile experience data:', profile.experience);
    console.log('Experience length:', profile.experience?.length);

    if (profile.experience && profile.experience.length > 0) {
        console.log('Adding Company Experience insights for', profile.experience.length, 'experiences');

        // Add individual experience entries - one insight per experience
        profile.experience.forEach((exp, index) => {
            if (index < 12) { // Limit to 12 experiences as per requirement
                const companyName = exp.company || 'Unknown Company';
                const jobTitle = exp.title || 'Position';
                const duration = exp.duration || 'Duration not specified';
                const location = exp.location || '';
                const description = exp.description || '';
                const skills = exp.skills || '';

                // Build compact content string with key info
                let content = `${jobTitle} • ${duration}`;
                if (location) content += ` • ${location}`;

                // Build full content with ALL details for backend processing
                let fullContent = `Position: ${jobTitle}\nCompany: ${companyName}\nDuration: ${duration}`;
                if (location) fullContent += `\nLocation: ${location}`;
                if (description) fullContent += `\nDescription: ${description}`;
                if (skills) fullContent += `\nSkills: ${skills}`;

                allInsights.push({
                    id: `insight-${id++}`,
                    category: 'Company Experience',
                    icon: exp.is_current ? '🏢' : '📋',
                    title: `${companyName}${exp.is_current ? ' (Current)' : ''}`,
                    content: content,
                    fullContent: fullContent,
                    selected: false
                });
                console.log(`Added experience insight #${index + 1}:`, companyName);
            }
        });
    } else {
        console.log('No experience data found in profile');
    }

    // ========== BEHAVIORAL & PERSONALITY INSIGHTS ========== (UNSELECTED BY DEFAULT)
    if (profile.personality_type) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Behavioral & Personality Insights',
            icon: '🧠',
            title: 'Personality Type',
            content: `Personality Type: ${profile.personality_type}`,
            selected: false
        });
    }

    // Selling to this Personality Type (Auto-generated based on personality)
    if (profile.personality_type) {
        const sellingTips = generateSellingTips(profile.personality_type);
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Behavioral & Personality Insights',
            icon: '🎯',
            title: 'Selling to this Personality Type',
            content: sellingTips,
            selected: false
        });
    }

    // Top Traits (if available in profile)
    if (profile.top_traits && profile.top_traits.length > 0) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Behavioral & Personality Insights',
            icon: '⭐',
            title: 'Top Traits',
            content: `Top Traits: ${profile.top_traits.join(', ')}`,
            selected: false
        });
    }


    // ========== PSYCHOLOGICAL TRIGGERS ========== (REMOVED)
    // Psychological triggers removed as per user request
    /*
    const triggers = generatePsychTriggers(profile);
    if (triggers) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Psychological Triggers',
            icon: '🧩',
            title: 'Psychological Triggers',
            content: triggers,
            selected: true
        });
    }
    */

    // ========== EMAIL OPTIMIZATION ========== (UNSELECTED BY DEFAULT)
    const emailOpt = generateEmailOptimization(profile);
    if (emailOpt) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Email Optimization',
            icon: '✉️',
            title: 'Email Optimization',
            content: emailOpt,
            selected: false
        });
    }

    // ========== WORK MILESTONES ========== (UNSELECTED BY DEFAULT)
    // Work Anniversary
    if (profile.years_at_company && Math.abs(profile.years_at_company - Math.round(profile.years_at_company)) < 0.1) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Other Insights',
            icon: '🎉',
            title: 'Work Milestones',
            content: `Upcoming work anniversary - Almost ${Math.round(profile.years_at_company)} years at ${profile.company || 'current company'}`,
            selected: false
        });
    }

    // ========== FEATURED CONTENT ========== (HIDDEN)
    // Feature content extraction disabled as per user request
    /*
    if (profile.featured && profile.featured.length > 0) {
        console.log(`Processing ${profile.featured.length} featured items`);

        profile.featured.forEach((item) => {
            // Determine content to display
            let displayContent = '';
            let fullContent = '';
            let title = '';

            if (item.type === 'Article') {
                title = `Article: ${item.title || 'Featured Article'}`;
                displayContent = item.content ? item.content.substring(0, 150) + '...' : item.title;
                fullContent = `${item.title}\n\n${item.content}\n\nEngagement: ${item.reactions} reactions, ${item.comments}`;
            } else {
                title = 'Featured Post';
                displayContent = item.content ? item.content.substring(0, 150) + '...' : '';
                fullContent = `${item.content}\n\nEngagement: ${item.reactions} reactions, ${item.comments}`;
            }

            // Add engagement info to display content
            if (item.reactions !== '0' || item.comments !== '0 comments') {
                displayContent += `\n\n💬 ${item.reactions} reactions • ${item.comments}`;
            }

            if (displayContent) {
                allInsights.push({
                    id: `insight-${id++}`,
                    category: 'Featured Content',
                    icon: item.type === 'Article' ? '📰' : '⭐',
                    title: title,
                    content: displayContent,
                    fullContent: fullContent,
                    selected: true
                });
            }
        });

        console.log(`Total featured insights added: ${allInsights.filter(i => i.category === 'Featured Content').length}`);
    }
    */

    // ========== LINKEDIN ACTIVITY ========== (SELECTED BY DEFAULT)
    if (profile.posts && profile.posts.length > 0) {
        profile.posts.slice(0, 3).forEach((post) => {
            const postText = typeof post === 'string' ? post : (post.text || post.content || '');
            if (postText) {
                allInsights.push({
                    id: `insight-${id++}`,
                    category: 'LinkedIn Activity',
                    icon: '📝',
                    title: 'Recent LinkedIn Post',
                    content: postText.substring(0, 200) + (postText.length > 200 ? '...' : ''),
                    fullContent: postText,
                    selected: true  // Selected by default
                });
            }
        });
    }

    // ========== RECOMMENDATIONS ========== (UNSELECTED BY DEFAULT)
    if (profile.recommendations && profile.recommendations.length > 0) {
        console.log(`Processing ${profile.recommendations.length} recommendations for insights`);

        profile.recommendations.forEach((rec) => {
            let recText = '';
            let recTitle = 'Recommendation';

            if (typeof rec === 'string') {
                recText = rec;
            } else {
                // Build recommendation text from object
                recText = rec.text || rec.content || '';

                // Create title with recommender info
                if (rec.recommender) {
                    recTitle = `Recommendation from ${rec.recommender}`;
                    if (rec.recommender_title) {
                        recTitle += ` (${rec.recommender_title})`;
                    }
                } else if (rec.name) {
                    recTitle = `Recommendation from ${rec.name}`;
                }
            }

            if (recText) {
                const insight = {
                    id: `insight-${id++}`,
                    category: 'Recommendations',
                    icon: '⭐',
                    title: recTitle,
                    content: recText.substring(0, 200) + (recText.length > 200 ? '...' : ''),
                    fullContent: recText,
                    selected: false
                };
                allInsights.push(insight);
                console.log('Added recommendation insight:', insight.title);
            }
        });

        console.log(`Total recommendation insights added: ${allInsights.filter(i => i.category === 'Recommendations').length}`);
    } else {
        console.log('No recommendations found in profile data');
    }

    // ========== SHARED EXPERIENCE ========== (UNSELECTED BY DEFAULT)
    if (profile.location) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Shared Experience',
            icon: '📍',
            title: 'Geographic Location',
            content: `Based in ${profile.location}`,
            selected: false
        });
    }

    // Shared Customers (if available)
    if (profile.shared_customers && profile.shared_customers.length > 0) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Shared Experience',
            icon: '🤝',
            title: 'Shared Customers',
            content: `Shared customers: ${profile.shared_customers.slice(0, 3).join(', ')}`,
            selected: false
        });
    }

    // ========== PROFESSIONAL BACKGROUND ========== (UNSELECTED BY DEFAULT)
    // Skills
    if (profile.skills && profile.skills.length > 0) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Professional Background',
            icon: '🎯',
            title: `${profile.skills.length} Skills Listed`,
            content: `Top skills: ${profile.skills.slice(0, 5).join(', ')}`,
            selected: false
        });
    }

    // Education
    if (profile.education && profile.education.length > 0) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Professional Background',
            icon: '🎓',
            title: 'Education',
            content: `Studied at ${profile.education[0].school || 'university'}`,
            selected: false
        });
    }

    // ========== SUGGESTED NEXT STEPS ========== (UNSELECTED BY DEFAULT)
    const nextSteps = generateNextSteps(profile);
    if (nextSteps) {
        allInsights.push({
            id: `insight-${id++}`,
            category: 'Suggested Next Steps',
            icon: '🚀',
            title: 'Suggested Next Steps',
            content: nextSteps,
            selected: false
        });
    }

    selectedInsights = [...allInsights];
    displayInsights();
    updateSelectionCounter();
}

// Helper function to generate selling tips based on personality type
function generateSellingTips(personalityType) {
    const tips = {
        'DI': 'Focus on results and ROI. Be direct and confident. Emphasize competitive advantages.',
        'D': 'Be concise and results-oriented. Show how your solution drives efficiency and control.',
        'I': 'Build rapport first. Use testimonials and success stories. Be enthusiastic and personable.',
        'S': 'Take time to build trust. Be patient and supportive. Emphasize stability and reliability.',
        'C': 'Provide detailed data and documentation. Be precise and logical. Focus on accuracy and quality.'
    };
    return tips[personalityType] || `Selling to ${personalityType} personality: Tailor your approach based on their communication preferences.`;
}

// Helper function to generate psychological triggers (REMOVED)
// Function removed as per user request
/*
function generatePsychTriggers(profile) {
    const triggers = [];

    // Based on personality and activity
    triggers.push('Use social proof (testimonials, case studies)');
    triggers.push('Balance urgency with reassurance');
    triggers.push('Combine authority with personal stories');

    if (profile.posts && profile.posts.length > 0) {
        triggers.push('Personalization based on recent activities');
    }

    return triggers.join(' • ');
}
*/

// Helper function to generate email optimization tips
function generateEmailOptimization(profile) {
    const tips = [];

    tips.push('Direct CTA like: "30 minutes next Tuesday morning?"');
    tips.push('Keep emails concise');
    tips.push('Use bullet points and bold text');

    return tips.join(' • ');
}

// Helper function to generate next steps
function generateNextSteps(profile) {
    const steps = [];

    if (profile.posts && profile.posts.length > 0) {
        steps.push('Reference their recent LinkedIn post');
    }

    if (profile.company) {
        steps.push(`Research ${profile.company}'s recent initiatives`);
    }

    steps.push('Schedule a brief introductory call');

    return steps.length > 0 ? steps.join(' • ') : null;
}

// Display insights in Step 1
function displayInsights() {
    const container = document.getElementById('insightsContainer');
    if (!container) return;

    if (allInsights.length === 0) {
        container.innerHTML = '<div class="no-insights">No insights detected. Please refresh the LinkedIn page.</div>';
        return;
    }

    // Group insights by category
    const grouped = {};
    allInsights.forEach(insight => {
        if (!grouped[insight.category]) {
            grouped[insight.category] = [];
        }
        grouped[insight.category].push(insight);
    });

    let html = '';
    Object.keys(grouped).forEach(category => {
        html += `<div class="insight-category">
            <h4 class="category-title">${category}</h4>`;

        grouped[category].forEach(insight => {
            const escapedId = insight.id.replace(/'/g, "\\'");
            html += `
                <div class="insight-card ${insight.selected ? 'selected' : ''}" data-id="${insight.id}">
                    <input type="checkbox" class="insight-checkbox" ${insight.selected ? 'checked' : ''}
                           onchange="toggleInsight('${escapedId}')">
                    <div class="insight-icon">${insight.icon}</div>
                    <div class="insight-content">
                        <div class="insight-title">${insight.title}</div>
                        <div class="insight-text">${insight.content}</div>
                    </div>
                </div>`;
        });

        html += '</div>';
    });

    container.innerHTML = html;
}

// Toggle individual insight selection
window.toggleInsight = function(insightId) {
    const insight = allInsights.find(i => i.id === insightId);
    if (!insight) return;

    insight.selected = !insight.selected;
    selectedInsights = allInsights.filter(i => i.selected);
    updateSelectionCounter();

    // Update UI
    const card = document.querySelector(`.insight-card[data-id="${insightId}"]`);
    if (card) {
        card.classList.toggle('selected', insight.selected);
    }
}

// Calculate estimated personalization score
function calculateEstimatedScore() {
    let score = 0;

    // Profile completeness (0-40 points)
    let completeness = 0;
    if (currentProfile?.name) completeness += 10;
    if (currentProfile?.title) completeness += 10;
    if (currentProfile?.company) completeness += 10;
    if (currentProfile?.location) completeness += 10;
    if (currentProfile?.about) completeness += 20;
    if (currentProfile?.experience?.length > 0) completeness += Math.min(20, currentProfile.experience.length * 5);
    if (currentProfile?.posts?.length > 0) completeness += Math.min(20, currentProfile.posts.length * 7);
    score += Math.floor((completeness / 100) * 40);

    // Insights (0-30 points, 3 per insight, max 10)
    score += Math.min(30, selectedInsights.length * 3);

    // Value proposition (+15 points)
    const valueProp = document.getElementById('valuePropositionSelect')?.value;
    if (valueProp) score += 15;

    // Additional context (+14 points)
    const context = document.getElementById('additionalInput')?.value?.trim();
    if (context) score += 14;

    return Math.min(99, score);
}

// Update selection counter and score
function updateSelectionCounter() {
    const selectedCount = document.getElementById('selectedCount');
    const totalCount = document.getElementById('totalCount');
    const finalScore = document.getElementById('finalScore');

    if (selectedCount) selectedCount.textContent = selectedInsights.length;
    if (totalCount) totalCount.textContent = allInsights.length;
    if (finalScore) {
        finalScore.textContent = calculateEstimatedScore();
    }
}

// Setup custom multi-select dropdown for Content Focus
function setupContentFocusDropdown() {
    const button = document.getElementById('contentFocusButton');
    const dropdown = document.getElementById('contentFocusDropdown');
    const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]');

    // Toggle dropdown on button click
    button.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('hidden');
        button.classList.toggle('active');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!button.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.add('hidden');
            button.classList.remove('active');
        }
    });

    // Handle checkbox changes
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            updateContentFocusChips();
            updateContentFocusButtonText();
        });
    });

    // Handle clicking on option div (toggle checkbox)
    dropdown.querySelectorAll('.multi-select-option').forEach(option => {
        option.addEventListener('click', (e) => {
            if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'LABEL') {
                const checkbox = option.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;
                updateContentFocusChips();
                updateContentFocusButtonText();
            }
        });
    });

    // Initialize chips and button text
    updateContentFocusChips();
    updateContentFocusButtonText();
}

// Update the chips display based on selected checkboxes
function updateContentFocusChips() {
    const chipsContainer = document.getElementById('selectedFocusChips');
    const dropdown = document.getElementById('contentFocusDropdown');
    const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]:checked');

    // Clear existing chips
    chipsContainer.innerHTML = '';

    // Add chip for each selected option
    checkboxes.forEach(checkbox => {
        const label = dropdown.querySelector(`label[for="${checkbox.id}"]`);
        const chipText = label.textContent;

        const chip = document.createElement('div');
        chip.className = 'focus-chip';
        chip.innerHTML = `
            <span>${chipText}</span>
            <button type="button" class="focus-chip-remove" data-value="${checkbox.value}">×</button>
        `;

        // Handle chip removal
        const removeBtn = chip.querySelector('.focus-chip-remove');
        removeBtn.addEventListener('click', () => {
            checkbox.checked = false;
            updateContentFocusChips();
            updateContentFocusButtonText();
        });

        chipsContainer.appendChild(chip);
    });
}

// Update button text based on number of selections
function updateContentFocusButtonText() {
    const buttonText = document.getElementById('contentFocusButtonText');
    const dropdown = document.getElementById('contentFocusDropdown');
    const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]:checked');

    if (checkboxes.length === 0) {
        buttonText.textContent = 'Select content focus...';
    } else if (checkboxes.length === 1) {
        const label = dropdown.querySelector(`label[for="${checkboxes[0].id}"]`);
        buttonText.textContent = label.textContent;
    } else {
        buttonText.textContent = `${checkboxes.length} options selected`;
    }
}

// Get selected content focus values
function getSelectedContentFocus() {
    const dropdown = document.getElementById('contentFocusDropdown');
    const checkboxes = dropdown.querySelectorAll('input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// Update Focus Content dropdown based on available insights (multi-select)
function updateContentFocusOptions() {
    const dropdown = document.getElementById('contentFocusDropdown');
    if (!dropdown) return;

    // Check what types of insights are available
    const availableOptions = new Set();

    // Always include "All Profile Data"
    availableOptions.add('all');

    // Check each selected insight and map to focus options
    selectedInsights.forEach(insight => {
        const category = insight.category.toLowerCase();
        const title = insight.title.toLowerCase();

        // Map insights to focus options
        if (category === 'featured content') {
            availableOptions.add('featured');
        }
        if (category === 'linkedin activity' || title.includes('post')) {
            availableOptions.add('recent_posts');
        }
        if (category === 'recommendations' || title.includes('recommendation')) {
            availableOptions.add('recommendations');
        }
        if (title.includes('skill') || title.includes('expertise')) {
            availableOptions.add('skills');
        }
        if (title.includes('education') || title.includes('studied') || title.includes('degree')) {
            availableOptions.add('education');
        }
        if (title.includes('about') || title.includes('about me')) {
            availableOptions.add('about');
        }
        if (title.includes('location') || title.includes('geographic') || category === 'shared experience') {
            availableOptions.add('geography');
        }
        if (category === 'company information' || category === 'company experience' || title.includes('experience') || title.includes('job')) {
            availableOptions.add('experience');
        }
    });

    // Get currently selected values to preserve them
    const currentlySelected = getSelectedContentFocus();

    // Show/hide options based on availability
    const allOptions = dropdown.querySelectorAll('.multi-select-option');
    allOptions.forEach(option => {
        const value = option.dataset.value;
        if (availableOptions.has(value)) {
            option.style.display = 'flex';
        } else {
            option.style.display = 'none';
            // Uncheck if hidden
            const checkbox = option.querySelector('input[type="checkbox"]');
            if (checkbox.checked) {
                checkbox.checked = false;
            }
        }
    });

    // Update chips and button text after changes
    updateContentFocusChips();
    updateContentFocusButtonText();

    console.log('Updated Focus Content dropdown with available options:', Array.from(availableOptions));
}

// Navigation Functions
async function goToStep2() {
    currentStep = 2;
    document.getElementById('step1')?.classList.remove('active');
    document.getElementById('step2')?.classList.add('active');
    document.querySelector('.progress-step[data-step="1"]')?.classList.remove('active');
    document.querySelector('.progress-step[data-step="2"]')?.classList.add('active');

    // Ensure dropdowns are populated before showing Step 2
    await ensureDropdownsLoaded();

    // Update the content focus dropdown based on available insights
    updateContentFocusOptions();

    window.scrollTo(0, 0);
}

// Ensure all dropdowns have data loaded
async function ensureDropdownsLoaded() {
    try {
        // Check if value propositions are loaded
        const valuePropSelect = document.getElementById('valuePropositionSelect');
        if (valuePropSelect && valuePropSelect.options.length <= 1) {
            await loadValuePropositions();
        }

        // Check if saved instructions are loaded
        const savedInstructionsSelect = document.getElementById('savedInstructionsSelect');
        if (savedInstructionsSelect && savedInstructionsSelect.options.length <= 1) {
            await loadSavedInstructions();
        }
    } catch (error) {
        console.error('Error ensuring dropdowns loaded:', error);
    }
}

function goToStep1() {
    currentStep = 1;
    document.getElementById('step2')?.classList.remove('active');
    document.getElementById('step3')?.classList.remove('active');
    document.getElementById('step1')?.classList.add('active');
    document.querySelector('.progress-step[data-step="2"]')?.classList.remove('active');
    document.querySelector('.progress-step[data-step="3"]')?.classList.remove('active');
    document.querySelector('.progress-step[data-step="1"]')?.classList.add('active');
    window.scrollTo(0, 0);
}

function goToStep3() {
    currentStep = 3;
    document.getElementById('step1')?.classList.remove('active');
    document.getElementById('step2')?.classList.remove('active');
    document.getElementById('step3')?.classList.add('active');

    document.querySelector('.progress-step[data-step="1"]')?.classList.remove('active');
    document.querySelector('.progress-step[data-step="2"]')?.classList.remove('active');
    document.querySelector('.progress-step[data-step="3"]')?.classList.add('active');

    window.scrollTo(0, 0);
}

function goToStep2FromStep3() {
    currentStep = 2;
    document.getElementById('step3')?.classList.remove('active');
    document.getElementById('step2')?.classList.add('active');

    document.querySelector('.progress-step[data-step="3"]')?.classList.remove('active');
    document.querySelector('.progress-step[data-step="2"]')?.classList.add('active');

    // Update the content focus dropdown based on available insights
    updateContentFocusOptions();

    window.scrollTo(0, 0);
}

function closeSidepanel() {
    // Send message to content script to close the sidepanel
    window.parent.postMessage({ type: 'CLOSE_SIDEPANEL' }, '*');
}

async function openSettings() {
    // Simple logout confirmation
    const confirmLogout = confirm('Do you want to logout?');
    if (confirmLogout) {
        await handleLogout();
    }
}

function openAgentBuilder() {
    // Open Agent Builder page in new tab
    chrome.tabs.create({ url: 'http://localhost:3000/agents' });
}

async function handleLogout() {
    try {
        // Clear auth token from storage
        await chrome.storage.local.remove('authToken');
        authToken = null;

        // Reset state
        currentProfile = null;
        selectedInsights = [];
        allInsights = [];
        selectedCaseStudies = [];
        allCaseStudies = [];

        // Show login page
        showLoginPage();
        setupLoginListeners();
    } catch (error) {
        console.error('Logout error:', error);
    }
}

// Case Studies Modal Functions
async function openCaseStudiesModal() {
    const modal = document.getElementById('assetModal');
    if (modal) modal.classList.remove('hidden');
    await loadCaseStudies();
}

function closeCaseStudiesModal() {
    const modal = document.getElementById('assetModal');
    if (modal) modal.classList.add('hidden');
}

async function loadCaseStudies() {
    const list = document.getElementById('assetsList');
    if (!list) return;

    list.innerHTML = '<div class="assets-loading"><div class="spinner-small"></div><p>Loading case studies...</p></div>';

    try {
        const storage = await chrome.storage.local.get(['authToken']);
        const authToken = storage.authToken;

        if (!authToken) {
            list.innerHTML = '<div class="error-message">Please login first</div>';
            return;
        }

        const response = await fetch(`${API_URL}/case-studies/relevant`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(currentProfile || {})
        });

        if (response.ok) {
            const data = await response.json();
            allCaseStudies = data.case_studies || [];
            displayCaseStudies(allCaseStudies);
        } else {
            list.innerHTML = '<div class="error-message">Failed to load case studies</div>';
        }
    } catch (error) {
        console.error('Error loading case studies:', error);
        list.innerHTML = '<div class="error-message">Network error. Make sure backend is running.</div>';
    }
}

function displayCaseStudies(studies) {
    const list = document.getElementById('assetsList');
    if (!list) return;

    if (!studies || studies.length === 0) {
        list.innerHTML = '<div class="no-results">No case studies available</div>';
        return;
    }

    list.innerHTML = ''; // Clear existing content

    studies.forEach(study => {
        const isSelected = selectedCaseStudies.some(s => s.title === study.title);

        // Create asset item container
        const assetItem = document.createElement('div');
        assetItem.className = `asset-item ${isSelected ? 'selected' : ''}`;
        assetItem.dataset.title = study.title;

        // Create checkbox
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'asset-checkbox';
        checkbox.checked = isSelected;
        checkbox.addEventListener('change', function() {
            toggleCaseStudy(study.title, study);
        });

        // Create asset info container
        const assetInfo = document.createElement('div');
        assetInfo.className = 'asset-info';

        // Create title
        const title = document.createElement('h4');
        title.textContent = study.title;

        // Create excerpt
        const excerpt = document.createElement('p');
        excerpt.className = 'asset-excerpt';
        excerpt.textContent = study.excerpt;

        // Create tags container
        const tagsContainer = document.createElement('div');
        tagsContainer.className = 'asset-tags';
        study.categories.forEach(cat => {
            const tag = document.createElement('span');
            tag.className = 'asset-tag';
            tag.textContent = cat;
            tagsContainer.appendChild(tag);
        });

        // Create relevance badge if score > 0
        if (study.relevance_score > 0) {
            const relevanceBadge = document.createElement('div');
            relevanceBadge.className = 'relevance-badge';
            // relevance_score is already 0-100 from backend, don't multiply by 100
            relevanceBadge.textContent = `${Math.round(study.relevance_score)}% match`;
            assetInfo.appendChild(relevanceBadge);
        }

        // Append elements
        assetInfo.appendChild(title);
        assetInfo.appendChild(excerpt);
        assetInfo.appendChild(tagsContainer);

        assetItem.appendChild(checkbox);
        assetItem.appendChild(assetInfo);

        // Allow clicking the entire item to toggle
        assetItem.addEventListener('click', function(e) {
            if (e.target !== checkbox) {
                checkbox.checked = !checkbox.checked;
                toggleCaseStudy(study.title, study);
            }
        });

        list.appendChild(assetItem);
    });

    // Update the count display
    updateSelectedCaseStudiesCount();
}

window.toggleCaseStudy = function(title, studyObj = null) {
    // Find study either from parameter or from allCaseStudies
    const study = studyObj || allCaseStudies.find(s => s.title === title);
    if (!study) {
        console.error('Study not found:', title);
        return;
    }

    const index = selectedCaseStudies.findIndex(s => s.title === title);
    if (index > -1) {
        // Remove from selection
        selectedCaseStudies.splice(index, 1);
    } else {
        // Add to selection
        selectedCaseStudies.push(study);
    }

    updateSelectedCaseStudiesCount();

    // Update UI
    const item = document.querySelector(`.asset-item[data-title="${title}"]`);
    if (item) {
        const isSelected = selectedCaseStudies.some(s => s.title === title);
        item.classList.toggle('selected', isSelected);
        const checkbox = item.querySelector('.asset-checkbox');
        if (checkbox) checkbox.checked = isSelected;
    }
}

function updateSelectedCaseStudiesCount() {
    const countEl = document.getElementById('selectedAssetsCount');
    if (countEl) countEl.textContent = selectedCaseStudies.length;
}

function addSelectedCaseStudies() {
    const container = document.getElementById('selectedAssets');
    if (!container) return;

    let html = '';
    selectedCaseStudies.forEach(study => {
        const escapedTitle = study.title.replace(/'/g, "\\'");
        html += `
            <div class="selected-asset-chip">
                <span>${study.title}</span>
                <button class="remove-asset" onclick="removeCaseStudy('${escapedTitle}')">×</button>
            </div>`;
    });

    container.innerHTML = html;
    closeCaseStudiesModal();
}

window.removeCaseStudy = function(title) {
    selectedCaseStudies = selectedCaseStudies.filter(s => s.title !== title);
    addSelectedCaseStudies();
}

function filterCaseStudies(event) {
    const query = event.target.value.toLowerCase();
    if (!allCaseStudies) return;

    const filtered = allCaseStudies.filter(study => {
        const searchText = `${study.title} ${study.excerpt} ${study.categories.join(' ')} ${study.keywords.join(' ')}`.toLowerCase();
        return searchText.includes(query);
    });

    displayCaseStudies(filtered);
}

// Custom Instructions Functions
function showSaveInstructionModal() {
    const text = document.getElementById('additionalInput')?.value.trim();
    if (!text) {
        alert('Please enter instruction text first');
        return;
    }
    const modal = document.getElementById('saveInstructionModal');
    if (modal) modal.classList.remove('hidden');
}

function closeSaveInstructionModal() {
    const modal = document.getElementById('saveInstructionModal');
    if (modal) modal.classList.add('hidden');
    const nameInput = document.getElementById('instructionName');
    if (nameInput) nameInput.value = '';
}

async function saveCustomInstruction() {
    const nameInput = document.getElementById('instructionName');
    const contentInput = document.getElementById('additionalInput');
    const confirmBtn = document.getElementById('confirmSaveBtn');

    const name = nameInput?.value.trim();
    const content = contentInput?.value.trim();

    if (!name || !content) {
        alert('Please provide both name and instruction text');
        return;
    }

    try {
        // Get and validate auth token
        const storage = await chrome.storage.local.get(['authToken']);

        if (!storage.authToken) {
            alert('Please login first from the extension popup');
            closeSaveInstructionModal();
            return;
        }

        // Disable button and show loading state
        if (confirmBtn) {
            confirmBtn.disabled = true;
            confirmBtn.textContent = 'Saving...';
        }

        const response = await fetch(`${API_URL}/custom-instructions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${storage.authToken}`
            },
            body: JSON.stringify({ name, content })
        });

        if (response.ok) {
            alert('Instruction saved successfully!');
            nameInput.value = ''; // Clear name field
            closeSaveInstructionModal();
            await loadSavedInstructions();
        } else {
            // Parse detailed error
            try {
                const error = await response.json();
                const errorMessage = error.detail || error.message || JSON.stringify(error);
                alert(`Error: ${errorMessage}`);
            } catch (e) {
                // If response is not JSON
                alert(`Error: ${response.status} - ${response.statusText}`);
            }
        }
    } catch (error) {
        console.error('Error saving instruction:', error);
        alert(`Network error: ${error.message}. Make sure the backend is running.`);
    } finally {
        // Re-enable button
        if (confirmBtn) {
            confirmBtn.disabled = false;
            confirmBtn.textContent = 'Save';
        }
    }
}

async function loadSavedInstructions() {
    try {
        const storage = await chrome.storage.local.get(['authToken']);
        if (!storage.authToken) {
            console.log('No auth token, skipping load saved instructions');
            return;
        }

        console.log('Loading saved instructions...');
        const response = await fetch(`${API_URL}/custom-instructions`, {
            headers: {
                'Authorization': `Bearer ${storage.authToken}`
            }
        });

        console.log('Saved instructions response status:', response.status);

        if (response.ok) {
            const data = await response.json();
            console.log('Loaded instructions:', data);

            const select = document.getElementById('savedInstructionsSelect');
            if (!select) {
                console.error('savedInstructionsSelect element not found!');
                return;
            }

            select.innerHTML = '<option value="">Load saved instruction...</option>';

            if (data.instructions && data.instructions.length > 0) {
                console.log(`Successfully added ${data.instructions.length} instructions to dropdown`);
                data.instructions.forEach(inst => {
                    const option = document.createElement('option');
                    option.value = inst.content;
                    option.textContent = inst.name;
                    select.appendChild(option);
                });
            } else {
                console.log('No instructions found (empty array)');
            }
        } else {
            console.error('Failed to load saved instructions:', response.status, response.statusText);
            const errorData = await response.text();
            console.error('Error details:', errorData);
        }
    } catch (error) {
        console.error('Error loading saved instructions:', error);
    }
}

function loadSavedInstruction(event) {
    const content = event.target.value;
    const textarea = document.getElementById('additionalInput');
    if (content && textarea) {
        textarea.value = content;
    }
}

// Value Propositions Functions
async function loadValuePropositions() {
    try {
        const storage = await chrome.storage.local.get(['authToken']);
        if (!storage.authToken) {
            console.log('No auth token, skipping load value propositions');
            return;
        }

        console.log('Loading value propositions...');
        const response = await fetch(`${API_URL}/value-propositions`, {
            headers: {
                'Authorization': `Bearer ${storage.authToken}`
            }
        });

        console.log('Value propositions response status:', response.status);

        if (response.ok) {
            const data = await response.json();
            console.log('Loaded value propositions:', data);

            const select = document.getElementById('valuePropositionSelect');
            if (!select) {
                console.error('valuePropositionSelect element not found!');
                return;
            }

            // Clear existing options except the first one (default)
            while (select.options.length > 1) {
                select.remove(1);
            }

            let addedCount = 0;
            const addedAgents = new Set(); // Track added agent names to avoid duplicates

            (data.value_propositions || []).forEach(vp => {
                // Only add each agent once (not per value_prop)
                if (!addedAgents.has(vp.name)) {
                    addedAgents.add(vp.name);

                    const option = document.createElement('option');
                    // Store all value props as JSON in the value for later use
                    option.value = JSON.stringify(vp.value_props);
                    option.dataset.agentName = vp.name;

                    // Display just the agent name
                    let displayName = vp.name;

                    // Add star indicator for leader-configured agents
                    if (vp.is_leader_configured || vp.configured_by_leader || vp.leader) {
                        displayName += ' ⭐';
                    }

                    option.textContent = displayName;
                    option.title = `${vp.name} - ${vp.value_props.length} value proposition(s)`;
                    select.appendChild(option);
                    addedCount++;
                }
            });
            console.log(`Successfully added ${addedCount} agents to dropdown`);
        } else {
            console.error('Failed to load value propositions:', response.status, response.statusText);
            const errorData = await response.text();
            console.error('Error details:', errorData);
        }
    } catch (error) {
        console.error('Error loading value propositions:', error);
    }
}

// Filter insights based on content focus selection (now supports multiple focus types)
function filterInsightsByFocus(insights, focusTypes) {
    // Handle single value (backward compatibility)
    if (typeof focusTypes === 'string') {
        focusTypes = [focusTypes];
    }

    // If "all" is selected, return all insights
    if (focusTypes.includes('all')) {
        return insights;
    }

    // Helper function to match insight against a single focus type
    const matchesFocusType = (insight, focusType) => {
        const title = insight.title.toLowerCase();
        const category = insight.category.toLowerCase();
        const content = (insight.content || '').toLowerCase();

        switch(focusType) {
            case 'featured':
                return category === 'featured content' ||
                       title.includes('featured') ||
                       title.includes('article:');

            case 'recent_posts':
                return category === 'linkedin activity' ||
                       title.includes('post') ||
                       title.includes('linkedin post');

            case 'skills':
                return title.includes('skill') ||
                       title.includes('expertise') ||
                       (category === 'professional background' && title.includes('skills listed'));

            case 'recommendations':
                return category === 'recommendations' ||
                       title.includes('recommendation from');

            case 'geography':
                return title.includes('location') ||
                       title.includes('geographic') ||
                       title.includes('based in') ||
                       category === 'shared experience';

            case 'about':
                return title.includes('about') ||
                       title.includes('about me') ||
                       title.includes('bio') ||
                       (category === 'linkedin data' && title.includes('about'));

            case 'education':
                return title.includes('education') ||
                       title.includes('studied at') ||
                       title.includes('degree') ||
                       title.includes('university');

            case 'experience':
                return title.includes('experience') ||
                       title.includes('job description') ||
                       title.includes('working at') ||
                       title.includes('company') ||
                       title.includes('role') ||
                       category === 'company information' ||
                       category === 'company experience';

            default:
                return false;
        }
    };

    // Filter insights that match ANY of the selected focus types
    const filtered = insights.filter(insight => {
        return focusTypes.some(focusType => matchesFocusType(insight, focusType));
    });

    console.log(`Filtered insights for focus types [${focusTypes.join(', ')}]:`, {
        original: insights.length,
        filtered: filtered.length,
        matchedInsights: filtered.map(i => i.title)
    });

    return filtered;
}

// Content Generation
async function generateContent() {
    try {
        // Get auth token with error handling for extension reload
        const storage = await chrome.storage.local.get(['authToken']);
        const authToken = storage.authToken;

        if (!authToken) {
            alert('Please login first from the extension popup');
            return;
        }

        if (!currentProfile) {
            alert('No profile data available');
            return;
        }

        showLoading(true);
        // Get all selected content focus values from custom dropdown
        const contentFocusArray = getSelectedContentFocus();

        // If no focus selected, default to recent_posts
        if (contentFocusArray.length === 0) {
            contentFocusArray.push('recent_posts');
        }

        // Filter insights based on content focus (now handles multiple)
        const filteredInsights = filterInsightsByFocus(selectedInsights, contentFocusArray);

        // If no insights match the focus, warn the user
        if (filteredInsights.length === 0) {
            alert(`No insights available for the selected focus areas. Please select different content focus or go back to Step 1 to ensure relevant insights are selected.`);
            showLoading(false);
            return;
        }

        // Prepare filtered insights with full details
        const insightsForBackend = filteredInsights.map(insight => ({
            category: insight.category,
            title: insight.title,
            content: insight.fullContent || insight.content,
            icon: insight.icon
        }));

        // Prepare case studies with full data including URLs
        const caseStudiesForBackend = selectedCaseStudies.map(cs => ({
            title: cs.title,
            excerpt: cs.excerpt,
            categories: cs.categories,
            industry: cs.industry,
            keywords: cs.keywords || [],
            relevance_score: cs.relevance_score || 0,
            pdf_url: cs.pdf_url || cs.url || ''
        }));

        // Get value proposition - handle JSON array format
        let valueProposition = '';
        const valuePropSelect = document.getElementById('valuePropositionSelect');
        if (valuePropSelect && valuePropSelect.value) {
            try {
                // Try to parse as JSON (new format with multiple value props)
                const valueProps = JSON.parse(valuePropSelect.value);
                // Use the first value prop
                valueProposition = Array.isArray(valueProps) && valueProps.length > 0 ? valueProps[0] : '';
            } catch (e) {
                // If not JSON, use as-is (backward compatibility)
                valueProposition = valuePropSelect.value;
            }
        }

        const requestData = {
            linkedin_data: currentProfile,
            selected_insights: insightsForBackend,
            content_type: selectedContentType,
            content_focus: contentFocusArray.join(', '),  // Send as comma-separated string for backend
            writing_style: document.getElementById('writingStyle')?.value || 'data-driven',
            value_proposition: valueProposition,
            additional_context: document.getElementById('additionalInput')?.value || '',
            message_length: document.getElementById('messageLength')?.value || '100-200',
            case_studies: caseStudiesForBackend
        };

        console.log('Sending request data:', requestData);

        const response = await fetch(`${API_URL}/generate-content`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(requestData)
        });

        if (response.ok) {
            const data = await response.json();
            displayGeneratedContent(data.generated_text);

            // Copy score to Step 3
            const finalScoreStep3 = document.getElementById('finalScoreStep3');
            if (finalScoreStep3) {
                finalScoreStep3.textContent = data.score || calculateEstimatedScore();
            }

            // Navigate to Step 3
            goToStep3();
        } else {
            const error = await response.json();
            let errorMessage = 'Unknown error';

            // Handle FastAPI validation errors (422)
            if (Array.isArray(error.detail)) {
                errorMessage = error.detail.map(err => {
                    const field = err.loc ? err.loc.join('.') : 'unknown';
                    return `${field}: ${err.msg}`;
                }).join('\n');
            } else if (typeof error.detail === 'string') {
                errorMessage = error.detail;
            } else if (error.message) {
                errorMessage = error.message;
            }

            alert('Failed to generate content:\n' + errorMessage);
            console.error('Backend error:', error);
        }
    } catch (error) {
        console.error('Error generating content:', error);

        // Handle extension context invalidated error
        if (error.message && error.message.includes('Extension context invalidated')) {
            alert('Extension was reloaded. Please refresh this page to continue.');
            window.location.reload();
        } else {
            alert('Network error. Make sure the backend is running on port 8001.');
        }
    } finally {
        showLoading(false);
    }
}

function displayGeneratedContent(text) {
    const contentEl = document.getElementById('generatedContent');

    if (contentEl) contentEl.textContent = text;

    // Content section is now always visible in Step 3
    // No need to toggle hidden class or scroll

    // Update statistics
    const words = text.trim().split(/\s+/).length;
    const chars = text.length;

    const wordCountEl = document.getElementById('wordCount');
    const charCountEl = document.getElementById('charCount');

    if (wordCountEl) wordCountEl.textContent = `${words} words`;
    if (charCountEl) charCountEl.textContent = `${chars} characters`;
}

function copyToClipboard() {
    const contentEl = document.getElementById('generatedContent');
    const btn = document.getElementById('copyBtn');

    if (!contentEl) {
        console.error('Generated content element not found');
        return;
    }

    const text = contentEl.textContent;

    // Validate there's actual content
    if (!text || text.trim().length === 0) {
        alert('No content to copy');
        return;
    }

    // Disable button during copy
    if (btn) btn.disabled = true;

    // Try modern Clipboard API first, with fallback to execCommand
    const copyText = async () => {
        try {
            // Try modern Clipboard API
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.warn('Clipboard API failed, trying fallback method:', err);

            // Fallback: Use the older execCommand method
            try {
                const textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                textarea.style.top = '0';
                textarea.style.left = '0';
                document.body.appendChild(textarea);
                textarea.focus();
                textarea.select();

                const successful = document.execCommand('copy');
                document.body.removeChild(textarea);

                if (successful) {
                    return true;
                } else {
                    throw new Error('execCommand copy failed');
                }
            } catch (fallbackErr) {
                console.error('Fallback copy method also failed:', fallbackErr);
                throw fallbackErr;
            }
        }
    };

    copyText().then(() => {
        if (btn) {
            // Store title instead of innerHTML
            const originalTitle = btn.title;
            btn.title = 'Copied!';
            btn.textContent = '✓ Copied!';

            setTimeout(() => {
                btn.textContent = '📋';
                btn.title = originalTitle;
                btn.disabled = false;
            }, 2000);
        }
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy to clipboard. Please select the text manually and use Ctrl+C (Cmd+C on Mac).');
        if (btn) btn.disabled = false;
    });
}

function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (!overlay) return;

    if (show) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}
