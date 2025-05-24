
# Newsiee: General & UPSC

Welcome to **Newsiee** – a groundbreaking project designed to revolutionize news consumption with intelligent features for summarization, validity verification, and interactive engagement. We focus not only on the audience who consmue news but also specifically on **UPSC** aspirants who need to be in touch with current affirs. For, them I haved designed a platform to get authentcate news, a deepfake detection system to check its validity, AI Tutor to help them study, make ppts or notes and Quiz section where they can test their knowledge on specific topics. 

## Links:
**Full Product:** https://newsiee-h66l.vercel.app/

**DeepFake Image Detection:** https://deepfakeself-my.streamlit.app/ 

**AI News Anchor:** https://newsaianchor.streamlit.app/

**AI Video Avatar:** https://ai-video-avatar-two.vercel.app/

**AI Tutor:**  https://ai-video-avatar-two.vercel.app/

## Table of Contents

1. [Features of Newsiee ✨](#features-)
   - [News Fetching and Summarization 📰📋](#news-fetching-and-summarization-)
   - [Multimodal Deepfake Detection 🔍🚫](#multimodal-deepfake-detection-)
   - [Audio Feature 🎤🔊](#audio-feature-)
   - [AI_Tutor]
   - [News AI Anchor 🎙️🤖](#news-ai-anchor-)
   - [Newsiee Community 🗣️🌍](#hackinno-community-)
2. [Tech Stack 🛠️](#tech-stack-)
3. [Getting Started 🚀](#getting-started-)
4. [License 📜](#license-)

# Features ✨

## 1. News Fetching and Summarization 📰📋
- **API Integration:** Connects to various news APIs (e.g., NewsAPI, Bing News Search) to fetch the latest news from diverse sources.
- **Machine Learning Summarization:** Utilizes advanced ML models like BERT to summarize articles into concise 60-word summaries.
- **Frontend Display:** Summaries are presented in a user-friendly format using HTML, CSS, jQuery, and Bootstrap. (To be implemented)

## 2. Multimodal Deepfake Detection 🔍🚫
### A. Deepfake Image Detector: 
   #### a. Cross- Domain Method:
   This is associted with **my research paper** titled "A Novel Unified Approach to Deepfake Detection of Images" publised in ISED, 2024 by IEEE. The detailed architecture and novelity can be found in detail in the research paper. This alone is a great area of research and it helps to combat the threats of AI generated media. Despite of researches, development of a single model that is generalised for all types of deepfakes is difficult due to the diversity in images. This model is trained and tested on the **FF++ dataset**.

   - **Detection Model:** Implements a multimodal deepfake detection model combining image analysis to assess news authenticity. The model verifies if the images present along with the news are real or fake.
   - **Automatic Validity Checks:** Flags potentially misleading or false news articles with real-time verification. (Real-time is not currently implemeted, but one can use the model to check manually.)
   - **Validity Indicator:** Provides clear visual indicators of news validity. (We can do this using the deepfake detecton model)

   #### b. GAN Fingerprinting based method:
   The code of this will be added as soon as my other research paper gets published.

### B. Fake News Detector:
This is to verifiy if the text or content of the news are correct or not.

### 3. Audio Feature 🎤🔊
- **Text-to-Speech (TTS) Conversion:** Converts text summaries into audio using advanced TTS services (I have used Google Text-to-Speech (GTTS)).
- **Engaging Visuals:** Includes relevant images or graphics using React components. (This is currently fetched from the news api we are using)
- **Integrated Audio Player:** Features an intuitive audio player built with JavaScript and React. (Not implemented in real-time but present in working stage in jupyter notebook)

### 4. AI Tutor:
This can create a lecture on a specific topic if given with link of an werbsite or a blogpost or a pdf etc. Firstly, AI-Tutor generates a pdf from any of the given format. Then it reads the pdf and develops a contextual understanding of the same. It then creates a ppt of the topic. After the it generates an explaination of each slide not mere reading it. After that both the ppt and explaination are synchronized to get a video explaination or full-fleged presentation of the topic. See AI Tutor/AI-Tutor --> code at create_lecture.ipynb, ppt, video explaination etc are also uploaded there.

### 5. News AI Anchor 🎙️🤖
- **AI-Powered Anchor:** An AI-driven news anchor reads summaries aloud, leveraging Generative AI and advanced NLP techniques.
- **Interactive Feature:** Provides a dynamic and interactive way for users to consume news.

### 6. Newsiee Community 🗣️🌍(On going)
- **Discussion Forum:** A vibrant forum built with React and Node.js where users can share news, comment, and engage in discussions.
- **Profile Management:** Users can create profiles, follow others, and interact with community members.
- **Moderation Tools:** Includes moderation tools to ensure respectful and relevant discussions.

### 7. Quiz Section:
A dummy version of this is added in the website for time being as I am working o this.
### 8. NLP based UPSC Questions:
This is currently under work.


## Tech Stack 🛠️

- **Authentication:** OAuth
- **Machine Learning & NLP:** Transformers, NumPy, pandas, Matplotlib, Seaborn, spaCy, NLTK, BERT
- **Generative AI:** LangChain
- **Visualization & Analysis:** Matplotlib, Seaborn

## Getting Started 🚀

   1. **Clone our hackathon repository:**
      ```bash
      https://github.com/Lord3008/Newsiee.git
      ```
   2. **Install Dependencies:**
      Navigate to the project directory and install the required dependencies.
      ```bash
      cd Newsiee
      pip install -r requirements.txt  # For Python projects with ML models
      ```
   3. **Run the Application:**
      Start the backend and frontend servers as instructed in the documentation.
      ```bash
      npm start  # For Node.js projects
      ```
      Follow additional instructions for setting up the ML models and database.


## License 📜

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
