# 🧠 The AI Engine

This document explains the intelligence layers integrated into the **HopOn** platform. We utilize a hybrid approach, combining local embedding models for privacy-preserving, fast search with cloud-based Large Language Models (LLMs) for complex reasoning and summarization.

---

## 1. Semantic Search & Recommendations

**Goal:** To find projects based on *meaning* and *context*, not just exact keyword matches.

### ⚙️ How It Works

Instead of looking for the word "Eco-friendly" (which might miss "Sustainable" or "Green"), we convert project descriptions into mathematical vectors (lists of numbers) that represent their conceptual meaning.

### 🤖 The Model

* **Model:** [`sentence-transformers/all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
* **Type:** Local Transformer (running on your machine/server).
* **Why we chose it:**
  * **Speed:** It is incredibly fast and lightweight.
  * **Privacy:** No data leaves the server; embeddings are generated locally.
    * **Performance:** It maps sentences & paragraphs to a 384-dimensional dense vector space, ideal for semantic search.
  
  ### 🔍 Deep Dive: What is "Vectorization"?

  When we say "vectorizing," we mean translating human language into a language computers understand: **numbers**.
  
  1. **The Input:** We take the unique text fingerprint of a project (Title + Objective + Topics).
  2. **The Magic:** The model (`all-MiniLM-L6-v2`) processes this text and outputs a list of 384 specific decimal numbers (e.g., `[0.12, -0.45, 0.88, ...]`). This list is the **"Embedding"** or **"Vector"**.
  3. **The Meaning:** These numbers represent the *semantic meaning* of the project. Projects with similar meanings will have vectors that are mathematically close to each other, even if they don't share the same keywords.
  4. **Storage:**
      * **Location:** Currently, these vectors are stored **in-memory (RAM)** for maximum speed and privacy. They are re-calculated when the app starts.
          * **Future:** If the dataset grows to millions of projects, we would store them in a persistent **Vector Database** (like ChromaDB or FAISS) to save startup time.

     ### 🆚 Why Local AI (MiniLM) vs. Cloud AI (OpenRouter) for Search?

      You might ask: *"Why not use OpenRouter for the search embeddings too?"*

      We deliberately chose a **Local Model (`all-MiniLM`)** for search and a **Cloud Model (OpenRouter)** for summarization. Here is why:

      | Feature | Local Model (MiniLM) | Cloud API (OpenRouter) |
      | :--- | :--- | :--- |
      | **Cost** | **Free** (Runs on your CPU) | **Pay-per-token** (or rate limited) |
      | **Speed** | **Instant** (Zero network latency) | Slower (Network round-trip) |
      | **Privacy** | **High** (Data stays on device) | Data sent to external server |
      | **Stability** | **Always works** (Offline capable) | Dependent on API uptime |
      | **Use Case** | Perfect for *matching* & *sorting* | Perfect for *reasoning* & *writing* |

      For **Search**, we need to compare thousands of numbers instantly. Doing this locally is standard engineering practice because it makes the search bar feel "snappy" and responsive.

      For **One-Pagers**, we need "creativity" and "reasoning," which is too heavy for a typical laptop to run well. That's why we outsource that specific task to the Cloud.

     ### ❓ FAQ: Project IDs vs. Multiple Projects

  You might be wondering: *"Does one Project ID represent multiple projects?"*
  
  **No.** In our system:
  * **1 Project ID = 1 Unique Project** (Grant Agreement).
  * *Example:* ID `101226563` is specifically for the "M-CARE" project.
  * **Confusion Source:** A single project *does* have multiple **Organizations** (Participants) and usually belongs to a broader **Call for Proposals** (which contains many other projects). But the "AI One-Pager" is generating a summary for that single, specific Grant Agreement (Project ID).
  
  ### 🔄 The Process

  1. **Ingestion:** When the app loads, we combine the Project Title, Objective, and Topics into a single text block.
  2. **Vectorization:** The `ProjectMatcher` converts this text into a vector (embedding).

1. **Search:** When you type a query (e.g., *"How to reduce urban pollution"*), we convert your query into a vector.
2. **Similarity:** We calculate the **Cosine Similarity** between your query vector and all project vectors.
3. **Ranking:** Projects are sorted by their similarity score (0 to 1), bringing the most relevant concepts to the top.

---

## 2. AI One-Pager Generation

**Goal:** To turn complex, technical, and lengthy EU project descriptions into a concise, readable, and structured executive summary ("One-Pager").

### ⚙️ How It Works

We send the raw project data (Title, Description, Objective) to an external LLM via an API. The LLM acts as an expert technical analyst, reading the text and extracting key insights.

### 🤖 The Model

* **Provider:** [OpenRouter](https://openrouter.ai/) (Unified API gateway).
* **Current Model:** `xiaomi/mimo-v2-flash:free`
* **Why we chose it:**
  * **Cost-Effective:** It is currently available on the free tier.
  * **Performance:** "Flash" models are optimized for speed and low latency while maintaining high reasoning capabilities.
  * **Flexibility:** Using OpenRouter allows us to switch models (e.g., to Google Gemini, DeepSeek, or GPT-4) by changing a single line of configuration, without rewriting code.

### 🔄 The Process

1. **Trigger:** User clicks "✨ Generate AI One-Pager".
2. **Prompt Engineering:** We construct a strict prompt:
    > "You are an expert technical analyst. Create a concise 'One-Pager' project brief... Provide output in Markdown format: Summary, Key Technologies, Potential Impact."
3. **API Call:** The prompt + project data is sent securely to the OpenRouter API.
4. **Streaming/Response:** The model generates the text.
5. **Display:** The result is rendered immediately in the UI and cached for the session.

---

## 🔒 Data Privacy & Security

* **Search Data:** NEVER leaves your machine. All vector operations happen locally.
* **Generation Data:** Only the specific project details you choose to summarize are sent to the OpenRouter API.
* **API Keys:** Your `OPENROUTER_API_KEY` is stored in a `.env` file and is never committed to version control.
