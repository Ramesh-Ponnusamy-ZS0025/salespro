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

    // Experience
    const experienceItems = document.querySelectorAll('div[data-section="experience"] li.artdeco-list__item');
    experienceItems.forEach((item, index) => {
      if (index < 5) { // Limit to 5 experiences
        const titleEl = item.querySelector('span[aria-hidden="true"]');
        const companyEl = item.querySelector('span.t-14.t-normal span[aria-hidden="true"]');
        const durationEl = item.querySelector('span.t-14.t-normal.t-black--light span[aria-hidden="true"]');
        
        if (titleEl) {
          data.experience.push({
            title: titleEl.textContent.trim(),
            company: companyEl ? companyEl.textContent.trim() : '',
            duration: durationEl ? durationEl.textContent.trim() : ''
          });
        }
      }
    });

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

    // Skills
    const skillsSection = document.querySelectorAll('div[data-section="skills"] span[aria-hidden="true"]');
    skillsSection.forEach((skill, index) => {
      if (index < 10) { // Limit to 10 skills
        const skillText = skill.textContent.trim();
        if (skillText && !data.skills.includes(skillText)) {
          data.skills.push(skillText);
        }
      }
    });

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
  tarazButton.innerHTML = '⚡ Generate Content';
  tarazButton.className = 'taraz-floating-button';
  
  tarazButton.addEventListener('click', () => {
    openSidepanel();
  });

  document.body.appendChild(tarazButton);
}

// Open sidepanel
function openSidepanel() {
  if (sidepanel) {
    sidepanel.style.display = 'block';
    return;
  }

  // Create sidepanel iframe
  const iframe = document.createElement('iframe');
  iframe.id = 'taraz-sidepanel';
  iframe.src = chrome.runtime.getURL('sidepanel.html');
  iframe.className = 'taraz-sidepanel';
  
  document.body.appendChild(iframe);
  sidepanel = iframe;

  // Send profile data to sidepanel
  setTimeout(() => {
    const profileData = extractLinkedInData();
    iframe.contentWindow.postMessage({
      type: 'LINKEDIN_DATA',
      data: profileData
    }, '*');
  }, 500);
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
    if (sidepanel) {
      sidepanel.style.display = 'none';
    }
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