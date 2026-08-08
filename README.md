Models Used:
-LLM: Gemini 1.5 Flash
   Chosen for fast response time, good quality answers, and cost efficiency for RAG applications.
-Embedding Model: text-embedding-004
   Chosen for strong semantic search performance, accurate vector embeddings, and compatibility with Gemini ecosystem.



API Key Setup:

-Get your API key from Google AI Studio.
-Create a .env file in the project root:
   GOOGLE_API_KEY=your_api_key_here
-Install dotenv:
  pip install python-dotenv
-Load in Python:
  from dotenv import load_dotenv
  load_dotenv()