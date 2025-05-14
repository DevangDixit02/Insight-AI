# Insight AI

A fast, intelligent chat assistant that combines real-time language generation with live web search. Insight AI offers a clean, modern interface where you can have natural conversations powered by up-to-date information from the internet.

---

## ✨ Key Features

- **Real-Time AI Responses** – Answers stream in smoothly as the AI thinks.
- **Built-in Web Search** – When needed, the AI can fetch fresh info from the web.
- **Ongoing Context Awareness** – Understands and remembers the flow of your conversation.
- **Clear Feedback During Search** – Shows when it's searching, reading, or replying.
- **Responsive Design** – Looks great on mobile, tablets, and desktops.

---

## 🏗️ Project Structure

Insight AI follows a client-server architecture to separate concerns and maximize performance.

### Frontend (Next.js + React)

- Modern interface built using **React** and **Next.js**
- Utilizes **Server-Sent Events (SSE)** to stream chat responses
- Clean component structure for messages, status indicators, and input handling
- Mobile-friendly and fully responsive

### Backend (FastAPI + LangGraph)

- Powered by **FastAPI** for efficient API endpoints
- Uses **LangGraph** for managing the flow of AI conversations and tool use
- Connected to **Google Gemini** for conversational AI
- Uses **Tavily Search API** for retrieving current web data
- Streams updates to the client in real-time with SSE

---

## 🔍 How It Works

1. You send a message through the chat.
2. The backend checks if the AI can respond directly or if it needs to search.
3. If needed, it fetches real-time search results from Tavily.
4. Those results are passed into Gemini to help craft a detailed answer.
5. You get a streaming response, along with visual cues showing what’s happening behind the scenes.
<<<<<<< HEAD

---

## 🙌 Credits & Tech

Built with:

- [Next.js](https://nextjs.org/) & [React](https://reactjs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Google Gemini](https://gemini.google.com/)
- [Tavily Search](https://www.tavily.com/)

---
=======
>>>>>>> 26a88fe2fcc99634af06727c98cfa7bc1732fc60

---

<<<<<<< HEAD
=======
## 🙌 Credits & Tech

Built with:

- [Next.js](https://nextjs.org/) & [React](https://reactjs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Google Gemini](https://gemini.google.com/)
- [Tavily Search](https://www.tavily.com/)

---

## 🚀 Get Started

>>>>>>> 26a88fe2fcc99634af06727c98cfa7bc1732fc60
Clone the repo, install dependencies, run the backend server, and launch the frontend — you're ready to chat with a smart assistant that stays current.
