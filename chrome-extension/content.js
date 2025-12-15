// Content script for LinkedIn profile data extraction

const API_URL = 'http://localhost:8001/api';

let tarazButton = null;
let sidepanel = null;

// Extract LinkedIn profile data
function extractLinkedInData() {
  const data = {
    name: '',
    title: '',
    company: '',
    location: '',
    bio: '',
    about: '',
    experience: [],
    education: [],
    posts: [],
    skills: [],
    certifications: [],
    languages: [],
    recommendations: [],
    profile_url: window.location.href
  };

  try {
    // Name
    const nameElement = document.querySelector('h1.text-heading-xlarge, h1.inline.t-24.v-align-middle');
    if (nameElement) {
      data.name = nameElement.textContent.trim();
    }

    // Title
    const titleElement = document.querySelector('div.text-body-medium.break-words, div.mt1.t-18');
    if (titleElement) {
      data.title = titleElement.textContent.trim();
    }

    // Company (from title)
    const companyMatch = data.title.match(/at (.+?)$/i);
    if (companyMatch) {
      data.company = companyMatch[1].trim();
    }

    // Location
    const locationElement = document.querySelector('span.text-body-small.inline.t-black--light.break-words');
    if (locationElement) {
      data.location = locationElement.textContent.trim();
    }

    // Bio/Headline (from title)
    data.bio = data.title;

    // About section
    const aboutSection = document.querySelector('div[data-section="about"] div.inline-show-more-text span[aria-hidden="true"]');
    if (aboutSection) {
      data.about = aboutSection.textContent.trim();
    }

    // Experience - Enhanced extraction
    const experienceSection = document.querySelector('#experience');
    if (experienceSection) {
      // Find all company containers (top-level experience items)
      const companyItems = experienceSection.closest('section').querySelectorAll('li.artdeco-list__item');
      console.log('Found', companyItems.length, 'experience items on LinkedIn profile');

      let experienceCount = 0;
      companyItems.forEach((item, index) => {
        if (experienceCount >= 12) return; // Limit to 12 total experiences

        // Check if this is a company with multiple positions
        const companyNameEl = item.querySelector('.hoverable-link-text.t-bold span[aria-hidden="true"]');
        const durationEl = item.querySelector('.t-14.t-normal span[aria-hidden="true"]');

        // Check for sub-positions (nested positions at same company)
        const subPositions = item.querySelectorAll('ul.pvs-list li');

        if (subPositions.length > 0) {
          // Company with multiple positions
          const companyName = companyNameEl ? companyNameEl.textContent.trim() : '';
          const totalDuration = durationEl ? durationEl.textContent.trim() : '';

          subPositions.forEach((subItem, subIndex) => {
            if (experienceCount >= 12) return;

            const positionTitleEl = subItem.querySelector('.hoverable-link-text.t-bold span[aria-hidden="true"]');
            const positionDurationEl = subItem.querySelector('.t-14.t-normal.t-black--light span.pvs-entity__caption-wrapper');
            const positionLocationEl = subItem.querySelectorAll('.t-14.t-normal.t-black--light span[aria-hidden="true"]')[1];
            const descriptionEl = subItem.querySelector('.inline-show-more-text span[aria-hidden="true"]');
            const skillsEl = subItem.querySelector('.hoverable-link-text strong');

            if (positionTitleEl) {
              const experience = {
                company: companyName,
                title: positionTitleEl.textContent.trim(),
                duration: positionDurationEl ? positionDurationEl.textContent.trim() : '',
                location: positionLocationEl ? positionLocationEl.textContent.trim() : '',
                description: descriptionEl ? descriptionEl.textContent.trim() : '',
                skills: skillsEl ? skillsEl.textContent.trim() : '',
                is_current: positionDurationEl && positionDurationEl.textContent.includes('Present')
              };
              data.experience.push(experience);
              experienceCount++;
              console.log('Extracted sub-position:', experience);
            }
          });
        } else {
          // Single position at company
          const titleEl = item.querySelector('.hoverable-link-text.t-bold span[aria-hidden="true"]');
          const companySpans = item.querySelectorAll('.t-14.t-normal span[aria-hidden="true"]');
          const durationSpans = item.querySelectorAll('.t-14.t-normal.t-black--light span[aria-hidden="true"]');
          const descriptionEl = item.querySelector('.inline-show-more-text span[aria-hidden="true"]');
          const skillsEl = item.querySelector('.hoverable-link-text strong');

          if (titleEl) {
            const experience = {
              title: titleEl.textContent.trim(),
              company: companySpans[0] ? companySpans[0].textContent.trim() : '',
              duration: durationSpans[0] ? durationSpans[0].textContent.trim() : '',
              location: durationSpans[1] ? durationSpans[1].textContent.trim() : '',
              description: descriptionEl ? descriptionEl.textContent.trim() : '',
              skills: skillsEl ? skillsEl.textContent.trim() : '',
              is_current: durationSpans[0] && durationSpans[0].textContent.includes('Present')
            };
            data.experience.push(experience);
            experienceCount++;
            console.log('Extracted single position:', experience);
          }
        }
      });

      console.log('Total experiences extracted:', data.experience.length);
    }

    // Education
    const educationItems = document.querySelectorAll('div[data-section="education"] li.artdeco-list__item');
    educationItems.forEach((item, index) => {
      if (index < 3) { // Limit to 3 education entries
        const schoolEl = item.querySelector('span[aria-hidden="true"]');
        const degreeEl = item.querySelector('span.t-14.t-normal span[aria-hidden="true"]');
        
        if (schoolEl) {
          data.education.push({
            school: schoolEl.textContent.trim(),
            degree: degreeEl ? degreeEl.textContent.trim() : ''
          });
        }
      }
    });

    // Skills - Extract from LinkedIn's current structure
    // Skills can be found in multiple locations on the profile
    const skillSelectors = [
      'section[data-section="skills"] li.artdeco-list__item',
      'div[id*="skills"] li.artdeco-list__item',
      'section.artdeco-card li.artdeco-list__item'
    ];

    let skillItems = [];

    // Try to find skills section
    for (const selector of skillSelectors) {
      const items = document.querySelectorAll(selector);
      if (items.length > 0) {
        // Verify these are actually skill items by checking if they have skill-like structure
        const firstItem = items[0];
        const hasSkillStructure = firstItem.querySelector('[data-field="skill_card_skill_topic"]') ||
                                   firstItem.querySelector('.hoverable-link-text.t-bold');

        if (hasSkillStructure) {
          skillItems = items;
          console.log(`Found ${skillItems.length} skill items using: ${selector}`);
          break;
        }
      }
    }

    // Extract skill names
    skillItems.forEach((item, index) => {
      if (index < 15) { // Limit to 15 skills
        // The skill name is in a link with data-field="skill_card_skill_topic"
        const skillLink = item.querySelector('[data-field="skill_card_skill_topic"]');
        if (skillLink) {
          const skillNameEl = skillLink.querySelector('.hoverable-link-text.t-bold span[aria-hidden="true"]');
          if (skillNameEl) {
            const skillText = skillNameEl.textContent.trim();
            if (skillText && !data.skills.includes(skillText)) {
              data.skills.push(skillText);
            }
          }
        }
      }
    });

    console.log(`Extracted ${data.skills.length} skills:`, data.skills.slice(0, 5));

    // Recent posts (activity)
    const postElements = document.querySelectorAll('div.feed-shared-update-v2__description span[dir="ltr"]');
    postElements.forEach((post, index) => {
      if (index < 3) { // Limit to 3 recent posts
        // Posts should be objects/dicts, not strings
        data.posts.push({
          content: post.textContent.trim(),
          engagement: {
            likes: 0,
            comments: 0,
            shares: 0
          }
        });
      }
    });

    // Certifications
    const certificationItems = document.querySelectorAll('div[data-section="certifications"] li.artdeco-list__item, section#certifications li.pvs-list__paged-list-item');
    certificationItems.forEach((item, index) => {
      if (index < 5) { // Limit to 5 certifications
        const nameEl = item.querySelector('div.display-flex.align-items-center span[aria-hidden="true"]');
        const issuerEl = item.querySelector('span.t-14.t-normal span[aria-hidden="true"]');
        const dateEl = item.querySelector('span.t-14.t-normal.t-black--light span[aria-hidden="true"]');

        if (nameEl && nameEl.textContent.trim()) {
          data.certifications.push({
            name: nameEl.textContent.trim(),
            issuer: issuerEl ? issuerEl.textContent.trim() : '',
            date: dateEl ? dateEl.textContent.trim() : ''
          });
        }
      }
    });

    // Languages
    const languageItems = document.querySelectorAll('div[data-section="languages"] li.artdeco-list__item, section#languages li.pvs-list__paged-list-item');
    languageItems.forEach((item, index) => {
      if (index < 10) { // Limit to 10 languages
        const langEl = item.querySelector('div.display-flex.align-items-center span[aria-hidden="true"]');
        const proficiencyEl = item.querySelector('span.t-14.t-normal span[aria-hidden="true"]');

        if (langEl && langEl.textContent.trim()) {
          data.languages.push({
            name: langEl.textContent.trim(),
            proficiency: proficiencyEl ? proficiencyEl.textContent.trim() : ''
          });
        }
      }
    });

    // Recommendations - Extract from LinkedIn's current structure
    // First, try to find the recommendations container within tabs
    const recommendationContainers = document.querySelectorAll('.artdeco-tabpanel');

    let recommendationItems = [];

    // Try multiple selectors for the recommendation list items
    const recommendationSelectors = [
      'li.artdeco-list__item',  // General list items in the recommendations section
      'li.pvs-list__paged-list-item',
      'li.pvs-list__item--line-separated'
    ];

    // First try to get items from the active tab panel (Received recommendations)
    const activeTabPanel = document.querySelector('.artdeco-tabpanel.active');
    if (activeTabPanel) {
      for (const selector of recommendationSelectors) {
        recommendationItems = activeTabPanel.querySelectorAll(selector);
        if (recommendationItems.length > 0) {
          console.log(`Found ${recommendationItems.length} recommendations in active tab using: ${selector}`);
          break;
        }
      }
    }

    // If not found in active tab, search the whole document
    if (recommendationItems.length === 0) {
      for (const selector of recommendationSelectors) {
        // Look specifically within the recommendations section
        const recSection = document.querySelector('section[data-view-name="profile-component-entity"]');
        if (recSection) {
          recommendationItems = recSection.querySelectorAll(selector);
        } else {
          recommendationItems = document.querySelectorAll(selector);
        }

        if (recommendationItems.length > 0) {
          console.log(`Found ${recommendationItems.length} items using: ${selector}`);
          break;
        }
      }
    }

    // Process each recommendation item
    let extractedCount = 0;
    recommendationItems.forEach((item, index) => {
      if (extractedCount >= 5) return; // Limit to 5 recommendations

      // Find the recommendation text - it's in a div with class containing "inline-show-more-text"
      const textContainer = item.querySelector('div[class*="inline-show-more-text"]');
      let textEl = null;
      if (textContainer) {
        textEl = textContainer.querySelector('span[aria-hidden="true"]');
      }

      // Find recommender name - in a div with "hoverable-link-text t-bold"
      const nameContainer = item.querySelector('.hoverable-link-text.t-bold, div[class*="hoverable-link-text"]');
      let recommenderEl = null;
      if (nameContainer) {
        recommenderEl = nameContainer.querySelector('span[aria-hidden="true"]');
      }

      // Find recommender's current title/position
      const titleContainers = item.querySelectorAll('.t-14.t-normal span[aria-hidden="true"]');
      let titleEl = null;
      // The title is usually the first or second span with this class
      if (titleContainers.length > 0) {
        // Look for the one that looks like a job title (contains typical keywords)
        for (let i = 0; i < titleContainers.length; i++) {
          const text = titleContainers[i].textContent.trim();
          if (text && !text.includes('•') && !text.includes('worked with') && text.length > 5) {
            titleEl = titleContainers[i];
            break;
          }
        }
      }

      // Only add if we found the recommendation text
      if (textEl && textEl.textContent.trim()) {
        const recText = textEl.textContent.trim();
        const recommenderName = recommenderEl ? recommenderEl.textContent.trim() : 'LinkedIn Connection';
        const recommenderTitle = titleEl ? titleEl.textContent.trim() : '';

        const recommendation = {
          text: recText,
          recommender: recommenderName,
          recommender_title: recommenderTitle
        };

        data.recommendations.push(recommendation);
        extractedCount++;
        console.log(`Extracted recommendation #${extractedCount}:`, {
          recommender: recommenderName,
          title: recommenderTitle,
          textPreview: recText.substring(0, 100) + '...'
        });
      }
    });

    console.log(`✅ Total recommendations extracted: ${data.recommendations.length}`);

    console.log('Extracted LinkedIn data:', data);
    return data;

  } catch (error) {
    console.error('Error extracting LinkedIn data:', error);
    return data;
  }
}

// Create TaRaZ button
function createTaRazButton() {
  if (tarazButton) return;

  tarazButton = document.createElement('button');
  tarazButton.id = 'taraz-button';
  tarazButton.className = 'taraz-floating-button';

  // Create button structure with icon and text
  tarazButton.innerHTML = `
    <span class="button-icon">⚡</span>
    <span class="button-text">Generate Content</span>
  `;

  tarazButton.addEventListener('click', () => {
    toggleSidepanel();
  });

  document.body.appendChild(tarazButton);
}

// Toggle sidepanel open/close
function toggleSidepanel() {
  if (sidepanel && sidepanel.style.display !== 'none') {
    closeSidepanel();
  } else {
    openSidepanel();
  }
}

// Open sidepanel
function openSidepanel() {
  if (sidepanel) {
    sidepanel.style.display = 'block';
    // Collapse the button
    if (tarazButton) {
      tarazButton.classList.add('collapsed');
    }
    return;
  }

  // Create sidepanel iframe
  const iframe = document.createElement('iframe');
  iframe.id = 'taraz-sidepanel';
  iframe.src = chrome.runtime.getURL('sidepanel.html');
  iframe.className = 'taraz-sidepanel';

  document.body.appendChild(iframe);
  sidepanel = iframe;

  // Collapse the button
  if (tarazButton) {
    tarazButton.classList.add('collapsed');
  }

  // Send profile data to sidepanel
  setTimeout(() => {
    const profileData = extractLinkedInData();
    iframe.contentWindow.postMessage({
      type: 'LINKEDIN_DATA',
      data: profileData
    }, '*');
  }, 500);
}

// Close sidepanel
function closeSidepanel() {
  if (sidepanel) {
    sidepanel.style.display = 'none';
    // Expand the button
    if (tarazButton) {
      tarazButton.classList.remove('collapsed');
    }
  }
}

// Check if we're on a LinkedIn profile page
function isProfilePage() {
  return window.location.pathname.includes('/in/');
}

// Initialize
function init() {
  if (isProfilePage()) {
    createTaRazButton();
  }
}

// Watch for navigation changes (LinkedIn is a SPA)
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    if (tarazButton) {
      tarazButton.remove();
      tarazButton = null;
    }
    if (sidepanel) {
      sidepanel.remove();
      sidepanel = null;
    }
    setTimeout(init, 1000);
  }
}).observe(document, { subtree: true, childList: true });

// Listen for messages from sidepanel
window.addEventListener('message', (event) => {
  // Verify the message is from our extension
  if (event.data.type === 'CLOSE_SIDEPANEL') {
    closeSidepanel();
  } else if (event.data.type === 'OPEN_SETTINGS') {
    // Open settings - for now, we can just alert or open a new tab
    alert('Settings panel coming soon!');
    // Or redirect to extension options page:
    // chrome.runtime.sendMessage({ action: 'openOptions' });
  }
});

// Run on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  setTimeout(init, 2000);
}