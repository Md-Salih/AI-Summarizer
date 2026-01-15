# 🤖 AI Summarizer - Text Summarization

**Production-Grade AI Summarization System** with Modern React UI and Daily Chat History

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org/)
[![FLAN-T5](https://img.shields.io/badge/Model-FLAN--T5-orange.svg)](https://huggingface.co/google/flan-t5-base)

---

## 📋 Overview

A production-ready text summarization system powered by **Google's FLAN-T5** model with a modern ChatGPT-style React frontend. Features real-time streaming generation, customizable summary length, and daily chat history storage with automatic cleanup.

### ✨ Key Features

🚀 **Advanced Backend**
- FLAN-T5 pre-trained model for high-quality summaries
- Real-time token-by-token streaming via Server-Sent Events (SSE)
- Optional AI-generated text detection
- Customizable summary length (50-300 words)
- RESTful API with streaming support

🎨 **Modern Frontend**
- ChatGPT-inspired collapsible sidebar
- Real-time word count and statistics
- Custom/Auto summary length modes
- Daily chat history with auto-save
- Action buttons: Paraphrase, Download, Copy, Toggle Stats
- Smooth animations and transitions
- Responsive split-screen layout

💾 **Smart History Management**
- Auto-saves every summary with meaningful titles
- Stores until 11:59 PM (23:59) daily
- Automatic midnight cleanup
- Click to restore previous conversations
- Empty state guidance for new users

---

## 🏗️ Project Structure

```
AI-Summarizer/
│
├── backend/                       # Flask Backend
│   ├── app.py                     # Main Flask server with streaming API
│   └── inference.py               # FLAN-T5 inference utilities
│
├── frontend/                      # React Frontend
│   ├── src/
│   │   ├── App.jsx                # Main application component
│   │   ├── App.css                # Application styles
│   │   ├── main.jsx               # React entry point
│   │   ├── index.css              # Global styles
│   │   └── components/
│   │       ├── Sidebar.jsx        # Collapsible navigation sidebar
│   │       └── Sidebar.css        # Sidebar styles
│   ├── index.html                 # HTML template
│   ├── package.json               # Frontend dependencies
│   └── vite.config.js             # Vite configuration
│
├── models/                        # AI Models (auto-downloaded)
│   ├── aidetector.model           # AI text detector model
│   └── aidetector.vocab           # AI detector vocabulary
│
├── samples/                       # Example data
│   └── examples.md                # Sample texts for testing
│
├── archive/                       # Development/Legacy files
│   ├── README.md                  # Archive documentation
│   ├── transformer.py             # Custom transformer (legacy)
│   ├── encoder.py, decoder.py     # Custom architecture
│   ├── train.py                   # Training pipeline
│   └── *.csv, *.py                # Data prep and training scripts
│
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Python dependencies
├── start.ps1                      # One-click startup script (Windows)
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (with pip)
- **Node.js 16+** (with npm)
- **Git** (optional, for cloning)
- **8GB RAM** recommended (for model loading)

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/AI-Summarizer.git
cd AI-Summarizer
```

#### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\activate
# Windows CMD:
.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Set Up Frontend
```bash
cd frontend
npm install
cd ..
```

#### 4. Start the Application

**Option A: Automated (Windows)**
```powershell
.\start.ps1
```
This script automatically starts both backend and frontend in separate windows.

**Option B: Manual**
```bash
# Terminal 1 - Backend
.venv\Scripts\activate
python backend\app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

#### 5. Open the Application
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000

---

## 📚 Usage

### Basic Summarization

1. **Enter Text:** Paste or type your document in the input area
2. **Adjust Length:** Use the slider to set summary length (50-300 words)
   - **Custom Mode:** Manual control with real-time word count
   - **Auto Mode:** System-optimized length
3. **Generate:** Click "Summarize" to generate
4. **View Results:** See summary with statistics (word count, reduction %, AI detection)

### Advanced Features

#### Action Buttons
- **Paraphrase** 🔄 - Re-summarize the current summary
- **Toggle Stats** 📊 - Show/hide statistics panel
- **Download** 💾 - Save summary as .txt file
- **Copy** 📋 - Copy to clipboard (shows confirmation)

#### Chat History
- **Auto-Save:** Every summary saves automatically with title (first 5 words)
- **Restore:** Click any history item to restore full conversation
- **Timer:** Shows "History saves until 11:59 PM"
- **Cleanup:** Automatically clears at midnight

#### Sidebar Controls
- **New Chat** - Clear current conversation and start fresh
- **Collapse/Expand** - Toggle sidebar (<</>>) for more space
- **Examples** - Quick-start with pre-made examples

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# AI Detector Configuration (Optional)
AI_DETECTOR_MODEL_FILE=./models/aidetector.model
AI_DETECTOR_VOCAB_FILE=./models/aidetector.vocab
AI_DETECTOR_TOKEN_MODEL=xx_ent_wiki_sm
AI_DETECTOR_DOWNLOAD_SPACY=false
AI_DETECTOR_THRESHOLD=0.5

# Flask Configuration
FLASK_ENV=production
FLASK_PORT=5000

# CORS Configuration
FRONTEND_URL=http://localhost:3000
```

### Summary Length Customization

Edit in `frontend/src/App.jsx`:
```javascript
const [summaryLength, setSummaryLength] = useState(150)  // Default: 150 words
// Slider range: 50-300 words
```

### History Storage Duration

Edit in `frontend/src/App.jsx`:
```javascript
// Change clear time (default: 23:59:59.999)
endOfDay.setHours(23, 59, 59, 999)
```

---

## 🔌 API Documentation

### Endpoints

#### `POST /api/summarize/stream`
**Real-time streaming summarization**

**Request:**
```json
{
  "text": "Your long document text here...",
  "max_length": 150
}
```

**Response:** Server-Sent Events (SSE)
```
data: {"token": "The", "progress": 10}
data: {"token": " quick", "progress": 20}
data: {"token": " brown", "progress": 30}
...
data: {"done": true}
```

#### `POST /api/ai-detect`
**AI-generated text detection**

**Request:**
```json
{
  "text": "Text to analyze..."
}
```

**Response:**
```json
{
  "available": true,
  "ai_percent": 85,
  "is_ai_generated": true,
  "confidence": 0.92
}
```

#### `GET /health`
**Health check endpoint**

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "timestamp": "2026-01-15T10:30:00Z"
}
```

---

## 🛠️ Development

### Tech Stack

**Backend:**
- Python 3.8+
- Flask 2.0+ (Web framework)
- PyTorch 2.0+ (Deep learning)
- Transformers 4.x (Hugging Face)
- FLAN-T5-Base (Google's model)
- aidetector (Optional AI detection)

**Frontend:**
- React 18
- Vite (Build tool)
- Framer Motion (Animations)
- Modern CSS3 (Flexbox, Grid, Transitions)
- localStorage API (History persistence)

### Running in Development Mode

**Backend (with auto-reload):**
```bash
.venv\Scripts\activate
$env:FLASK_ENV="development"
python backend\app.py
```

**Frontend (with hot reload):**
```bash
cd frontend
npm run dev
```

### Building for Production

**Frontend:**
```bash
cd frontend
npm run build
# Output: frontend/dist/
```

**Backend:**
```bash
# Use production WSGI server (e.g., Gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### Code Style

- **Backend:** PEP 8 (Python)
- **Frontend:** ESLint + Prettier
- **Formatting:** 
  - Python: `black` and `isort`
  - JavaScript: `prettier`

---

## 📦 Dependencies

### Backend (requirements.txt)
```
torch>=2.0.0
transformers>=4.30.0
flask>=2.0.0
flask-cors>=4.0.0
aidetector>=0.1.0 (optional)
spacy>=3.5.0 (optional, for AI detector)
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "framer-motion": "^10.0.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.0.0"
  }
}
```

---

## 🐛 Troubleshooting

### Backend Issues

**Model Download Fails:**
```bash
# Manually download FLAN-T5
python -c "from transformers import AutoModelForSeq2SeqLM, AutoTokenizer; AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-base'); AutoTokenizer.from_pretrained('google/flan-t5-base')"
```

**Port 5000 Already in Use:**
```bash
# Find process using port 5000
netstat -ano | findstr :5000
# Kill process (replace PID)
taskkill /PID <PID> /F
```

**AI Detector Not Working:**
```bash
# AI detector is optional - app works without it
# To fix: Ensure model files exist in models/ directory
# Or disable by removing environment variables
```

### Frontend Issues

**Port 3000 Already in Use:**
```bash
# Edit frontend/vite.config.js to change port
export default {
  server: { port: 3001 }
}
```

**History Not Saving:**
- Check browser console for localStorage errors
- Ensure cookies/local storage enabled
- Try incognito mode to test fresh state

**Sidebar Collapse Not Working:**
- Clear browser cache
- Hard refresh (Ctrl+Shift+R)
- Check for JavaScript errors in console

### Common Errors

**CORS Issues:**
```python
# backend/app.py - Ensure CORS is configured
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
```

**Out of Memory:**
- Close other applications
- Reduce batch size in inference.py
- Use smaller model (flan-t5-small instead of base)

---

## 🎯 Features in Detail

### 1. Customizable Summary Length
- **Range:** 50-300 words
- **Modes:**
  - **Custom:** Manual slider control with real-time word count
  - **Auto:** System-optimized (proportional min_length = 30% of max)
- **Backend Calculation:** `min_length = max(30, int(max_length * 0.3))`

### 2. Real-Time Streaming
- Uses Server-Sent Events (SSE) for token-by-token delivery
- Live progress tracking (0-100%)
- No polling - efficient push-based updates
- Smooth UI updates with React state management

### 3. Chat History System
- **Storage:** Browser localStorage (JSON)
- **Persistence:** Until 23:59:59.999 same day
- **Title Generation:** First 5 words of summary
- **Auto-Clear:** setTimeout to midnight
- **Restore:** Full conversation with recalculated stats

### 4. Statistics Dashboard
- Input word count
- Summary word count
- Words reduced (absolute)
- Compression ratio (%)
- AI detection percentage (optional)

### 5. Collapsible Sidebar
- **Expanded:** 260px width, full navigation
- **Collapsed:** 60px width, icon-only strip
- **Transition:** Smooth 0.3s CSS animation
- **Main Content:** Auto-adjusts margin (260px ↔ 60px)

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow existing code style
- Add comments for complex logic
- Update README if adding features
- Test thoroughly before submitting

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/AI-Summarizer/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/AI-Summarizer/discussions)
- **Email:** your.email@example.com

---

## 🙏 Acknowledgments

- **Google** - FLAN-T5 model
- **Hugging Face** - Transformers library
- **React Team** - React framework
- **Vite Team** - Build tooling
- **ChatGPT** - UI/UX inspiration

---

## 🗺️ Roadmap

### Upcoming Features
- [ ] Multi-language support
- [ ] Summary templates (formal, casual, technical)
- [ ] Export history to JSON/CSV
- [ ] Cloud sync for history
- [ ] Batch summarization
- [ ] API key authentication
- [ ] Custom model fine-tuning
- [ ] Mobile-responsive design
- [ ] Dark mode toggle

### Known Limitations
- History limited to single browser/device
- No authentication/user accounts
- Single model (FLAN-T5) only
- Daily history clear (no permanent storage)

---

## 📊 Performance

### Metrics
- **Model Size:** ~892MB (FLAN-T5-Base)
- **Startup Time:** ~5-10 seconds (model loading)
- **Inference Speed:** ~50-100 tokens/second (GPU) / ~10-20 tokens/second (CPU)
- **Memory Usage:** ~2-4GB RAM (during inference)
- **Storage:** ~1GB total (model + dependencies)

### Optimization Tips
- Use GPU for faster inference (`CUDA_VISIBLE_DEVICES=0`)
- Enable model quantization for smaller memory footprint
- Use caching for repeated summaries
- Limit max_length to reduce computation

---

## 📝 Changelog

### v1.0.0 (2026-01-15)
- ✨ Initial release
- 🚀 FLAN-T5 integration
- 🎨 ChatGPT-style UI
- 💾 Daily chat history
- 📊 Real-time statistics
- 🔄 Paraphrase feature
- 📥 Download & copy actions
- 🎛️ Customizable summary length

---

**Made with ❤️ by Your Team** | [Website](https://yoursite.com) | [Twitter](https://twitter.com/yourhandle)
