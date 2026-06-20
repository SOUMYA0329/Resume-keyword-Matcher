## AI RESUME & CARRER-MATCH ANALYZER:-

* Upload a resume +parse a job description -> get an instant semantic maytch score,missing keyword gaps,and Ai-rewritten bullet points.
* A small end-to-end NLP project that goes beyound simple keyword matching - it uses a sentence embeddings to understand meaning,not 
  just word overlap, then uses Claude to help you close the gaps .

## FEATURES:-

* **semantic match scoring** -compares resume and job description using Sentence-Bert embeddings (not just keyword overlap)
* **Missing Keyword detection** -extracts the highest-value skills/requirements from a job ppost and flags what's missing from your resume
* **Ai-powered bullet rewriting** -Sends weak bullet points to Claude ,which rewrits them to be stronger and incorporate missing keywords
  (without investing fake experience)
* **Simple web UI**- drag-and-drop resume upload + paste job description, built with streamlit
* Supports PDF,DOCX,and TXT resumes.

 ## TECH STACK

  * ### |LAYER|______________________ |TOOL LIBRARY|
 * Language ____________________________ python
 * Resume parshing ____________________ pdfplumber,python-docx
 * Keyword extraction __________________ Sentence-transformers(all-MiniLM-L6-v2)
 * Bullet rewriting ______________________ Claude API(Antropic)
 * Frontend _____________________________ Streamlit
   

## PROJECT STRUCTURE

### Resume-matcher/
```
├── app.py                             # Streamlit UI - ties the whole pipeline together

├── resume_parser.py                   # Extracts plain text from PDF/DOCX/TXT resumes

├── keyword_extractor.py               # Pulls key skills/requirements from a job description

├── similarity.py                      # Embeds text + computes match score & keyword gaps

├── rewriter.py                        # Claude-powered bullet point rewriting

├── requirements.txt                   # Python dependencies

└── README.md
```

## SETUP GUIDE
### 1. Clone the repo
```
git clone https://githib.com/YOUR_USERNAME/Resume-Keyword-Matcher.git
cd Resume-keyword-Matcher
```
### 2. Create a Virtual Environment
```
python -m venv venv

#Windows
venv\Scripts\activate

#macOS/Linux
Source venv/bin/activate
```

### 3. Install Dependecies
```
pip install requirement.txt
python -m spacydownload en_core_web_sm
```

### 4. Set your Claude API Key
* Required only for the AI bullet rewriting features,Get a key from
  console.anthropic.com
```
#windows(powershell)
$env:ANTHROPIC_API_KEY="your-key-here"

#macOS/Linux
export ANTHROPIC_API_KEY="your-key-here"
```

### 5. Run the app
```
streamlit run app.py
```
* Then open the url it prints-usually 
http://localhost:8501.

## HOW IT WORKS

1. **Praise** the uploaded resume in to plain text
2. **Extract keywords** from the praised job description using keyBERT + spaCy
3. **Embed** both texts with sentence-BERT and compute a semantic similarity score(0-100)
4. **Detectgaps** - keywords from the job description not present(even semantically) in the resume
5. **Rewrite** - optionally send weak bullet points + missing keywords to Claude for stronger,targetwd rewrites

## ROADMAP

* [ ] Export results as a downloadable PDF report
* [ ] Support scoring against multiple job postings at once
* [ ] Add a cleaner keyword-extraction filter (skills only, no phrase fragments)
* [ ] Resume formatting/ATS-layout checker

## NOTES

* Match scores are heuristic, not a guarantee of ATS pass/fail — use them as directional feedback, not gospel.
* Never commit your ANTHROPIC_API_KEY to the repo. It's read from an environment variable only.

## LICENSE

This project is open source under the MIT LICENSE 

## AUTHOR 

Built by **SOUMYA RANJAN NAYAK**.
Feel free to open an issue or PR if you'd like to contribute






