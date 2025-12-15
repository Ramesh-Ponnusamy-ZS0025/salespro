# TaRaZ Chrome Extension

AI-powered sales assistant that generates hyper-personalized outreach content from LinkedIn profiles.

## Features

- 🔍 **Auto-extract LinkedIn profile data** - Name, title, company, experience, skills, and recent posts
- 🤖 **AI-powered content generation** - Uses GPT-4 to create personalized emails, LinkedIn messages, and openers
- 📊 **Insight analysis** - Identifies key signals and calculates relevance scores
- 🎨 **Multiple content types** - Email, LinkedIn DM, or conversation openers
- 🎭 **Tone customization** - Professional, casual, or friendly tone options
- 💾 **History tracking** - All generated content is saved to your account

## Installation

### Development Mode (Local Testing)

1. **Start the backend server** (must be running):
   ```bash
   cd /app/backend
   sudo supervisorctl restart backend
   ```

2. **Open Chrome** and navigate to:
   ```
   chrome://extensions/
   ```

3. **Enable Developer Mode** (toggle in top-right corner)

4. **Click "Load unpacked"** and select:
   ```
   /app/chrome-extension
   ```

5. The TaRaZ extension should now appear in your Chrome toolbar!

## Usage

### First Time Setup

1. Click the **TaRaZ extension icon** in your Chrome toolbar
2. Click **"Create Account"** 
3. Enter your email and password
4. Click **"Create Account"** to register

### Generating Content

1. Visit any **LinkedIn profile page** (e.g., https://www.linkedin.com/in/[username])
2. Wait for the page to load completely
3. Click the **"⚡ Generate Content"** button (floating on the right side)
4. The TaRaZ sidepanel will open showing:
   - Profile information
   - Detected insights
   - Relevance score

5. **Customize your content**:
   - Select content type (Email, LinkedIn DM, or Opener)
   - Choose tone (Professional, Casual, or Friendly)
   - Add optional value proposition

6. Click **"✨ Generate Personalized Content"**

7. Wait for AI to generate your content (5-10 seconds)

8. **Copy and use** the generated content!

## How It Works

### 1. Data Extraction
The extension reads publicly visible information from LinkedIn profiles:
- Name and headline
- Current job title and company
- Location
- About section
- Work experience
- Education
- Skills
- Recent posts/activity

**Note:** The extension only reads data that's already visible in your browser. It uses your logged-in LinkedIn session but doesn't access LinkedIn's API directly.

### 2. AI Processing
The extracted data is sent to the TaRaZ backend API, which:
- Analyzes the profile data
- Identifies key insights (job changes, company news, social activity)
- Generates personalized content using GPT-4
- Calculates a relevance score (0-99)

### 3. Content Delivery
The generated content is displayed in the sidepanel where you can:
- Review and edit
- Copy to clipboard
- Regenerate with different settings
- View in your content history

## API Configuration

The extension connects to:
```
Backend API: http://localhost:8001/api
```

To use in production, update the `API_URL` in:
- `popup.js`
- `content.js`
- `sidepanel.js`

## File Structure

```
chrome-extension/
├── manifest.json           # Extension configuration
├── popup.html              # Extension popup UI
├── popup.js                # Popup logic (auth)
├── content.js              # LinkedIn data extraction
├── content.css             # Floating button styles
├── sidepanel.html          # Content generation UI
├── sidepanel.js            # Sidepanel logic
├── sidepanel.css           # Sidepanel styles
├── background.js           # Service worker
├── icons/                  # Extension icons
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md               # This file
```

## Permissions

The extension requires:
- `storage` - Save auth tokens and settings
- `activeTab` - Access current LinkedIn tab
- `https://www.linkedin.com/*` - Extract profile data
- `http://localhost:8001/*` - Connect to backend API

## Troubleshooting

### Extension not loading
- Make sure Developer Mode is enabled in Chrome
- Check that all files are present in /app/chrome-extension
- Look for errors in chrome://extensions/

### Button not appearing on LinkedIn
- Make sure you're on a profile page (/in/[username])
- Wait 2-3 seconds for the page to fully load
- Refresh the LinkedIn page
- Check the browser console for errors (F12)

### "Please login first" error
- Click the extension icon in toolbar
- Create account or sign in
- Try generating content again

### "Network error" when generating
- Make sure backend is running: `sudo supervisorctl status backend`
- Check backend is accessible: `curl http://localhost:8001/api/health`
- Look at backend logs: `tail -f /var/log/supervisor/backend.*.log`

### Content not generating
- Ensure you're logged into the extension
- Check that the LinkedIn profile has sufficient data
- Look at browser console for errors (F12)
- Check backend logs for AI service errors

## Development

### Testing Changes

After modifying any file:

1. Go to `chrome://extensions/`
2. Click the **refresh icon** on the TaRaZ extension card
3. Reload the LinkedIn page
4. Test your changes

### Debugging

**Content Script:**
- Open LinkedIn profile page
- Press F12 to open DevTools
- Check Console tab for errors
- Look for "Extracted LinkedIn data" log

**Popup:**
- Right-click extension icon → "Inspect popup"
- Check Console for errors

**Background:**
- Go to chrome://extensions/
- Click "service worker" under TaRaZ
- Check Console for errors

## Privacy & Security

- ✅ Extension only reads publicly visible LinkedIn data
- ✅ Uses your logged-in LinkedIn session (no separate login)
- ✅ All data is sent securely to your TaRaZ backend
- ✅ Auth tokens are stored locally in Chrome storage
- ✅ No data is shared with third parties
- ❌ Extension does NOT store or log your LinkedIn password

## Known Limitations

1. **LinkedIn SPA Navigation** - Sometimes the button doesn't appear after navigating between profiles. Refresh the page to fix.

2. **Profile Data Completeness** - Some LinkedIn profiles have limited public information. The quality of generated content depends on available data.

3. **Rate Limiting** - LinkedIn may rate-limit if you extract data too quickly. Use responsibly.

4. **API Keys** - The backend uses the Emergent LLM key. Monitor your usage to avoid hitting limits.

## Future Enhancements

- [ ] Support for LinkedIn company pages
- [ ] Bulk content generation for multiple profiles
- [ ] A/B testing different content variations
- [ ] Integration with CRM systems
- [ ] Browser notifications for job changes
- [ ] Chrome extension publishing to Web Store

## Support

For issues or questions:
1. Check backend logs: `tail -f /var/log/supervisor/backend.*.log`
2. Check browser console (F12)
3. Verify backend is running: `sudo supervisorctl status`

## License

Part of the TaRaZ platform.
