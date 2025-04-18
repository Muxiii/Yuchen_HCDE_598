# 📘 Yuchen_HCDE_598 - Exploration 1

This repository contains my work for **Exploration 1** in HCDE 598. The goal of this task was to build on a basic movie recommender prototype powered by a large language model (LLM), and enhance it with better control over token usage and generation behavior.

---

## 🔍 Project File

- **Code File**: `recommender_1.1.py`
- **Prototype Base**: Prototype 1 (as provided)
- **Tasks Completed**:  
  ✅ Medium — Track API token usage  
  ✅ Hard — Add temperature and max token parameters to control generation

---

## 🧠 Explore 1.2 — Track API Usage (Medium)

In this task, I modified the prototype to track the total number of tokens used in a chat session. This helps visualize and estimate the cost of API usage.

### ✔️ Code Changes:
- `make_chat_request()` now extracts `total_tokens` from the OpenAI response and returns it.
- `main()` accumulates usage via a new variable `total_usage` and prints the total after the session ends.

### 🧩 Key Code Snippets:
```python
# In make_chat_request():
usage = resp_dict.get("usage", {}).get("total_tokens", 0)
return chat_context, usage

# In main():
total_usage = 0
chat_context, usage = make_chat_request(user_text, chat_context, API_KEY)
total_usage += usage
print(f"\n🔢 Total token usage in this session: {total_usage} tokens.\n")
