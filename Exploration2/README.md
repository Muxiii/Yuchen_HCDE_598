### Prototype2 - Mid ###

---
## **1. Modified the System Prompt (`MOVIE_RECOMMENDER_PERSONA_PROMPT`)**
**Change:**  
Rewrote the prompt to explicitly separate **new releases** from **re-releases** and guide the AI on handling them differently.

**Old Prompt:**
```python
MOVIE_RECOMMENDER_PERSONA_PROMPT = '''You are a movie critic... 
{movie_data_str}
Your responses should always focus on making movie recommendations.'''
```

**New Prompt:**
```python
MOVIE_RECOMMENDER_PERSONA_PROMPT = '''You are a movie critic... 
NEW RELEASES:
{new_releases_str}

RE-RELEASES:
{rereleases_str}

When recommending movies, consider whether the user might prefer a brand new movie or a classic...'''
```
---
### **2. Updated `create_prompt_data_str()`**
**Change:**  
Split the function to categorize movies into **new releases** or **re-releases** based on the `notes` field.

**Old Behavior:**  
- Combined all movies into a single string with uniform formatting.

**New Behavior:**
```python
def create_prompt_data_str(movie_list=[]):
    new_releases = []
    rereleases = []
    
    for movie in movie_list:
        if 're-release' in movie['notes'].lower():  # Detect re-releases
            data = f"\tMOVIE TITLE: {movie['title']}\n"
            data += f"\tRELEASE TYPE: {movie['notes'].partition(',')[0]}\n"
            data += f"\tORIGINAL RELEASE DATE: {movie.get('original_date_str', 'Unknown')}\n"
            data += f"\tRE-RELEASE DATE: {movie['opening_date_str']}\n"
            rereleases.append(data)
        else:  # New releases
            data = f"\tMOVIE TITLE: {movie['title']}\n"
            data += f"\tRELEASE TYPE: {movie['notes'].partition(',')[0]}\n"
            data += f"\tOPENING DATE: {movie['opening_date_str']}\n"
            new_releases.append(data)
    
    return "\n".join(new_releases), "\n".join(rereleases)  # Return two strings
```

---

### **3. Refactored `new_chat_context()`**
**Change:**  
Updated to accept **two separate strings** (new releases and re-releases) instead of one.

**Old Version:**
```python
def new_chat_context(movie_data_str=""):
    sprompt = MOVIE_RECOMMENDER_PERSONA_PROMPT.format(movie_data_str=movie_data_str)
```

**New Version:**
```python
def new_chat_context(new_releases_str="", rereleases_str=""):
    sprompt = MOVIE_RECOMMENDER_PERSONA_PROMPT.format(
        new_releases_str=new_releases_str,
        rereleases_str=rereleases_str
    )
```

---

### **4. Updated `main()` to Handle Dual Data Streams**
**Change:**  
Modified the workflow to process and pass two separate movie lists.

**Old Code:**
```python
movie_info_str = create_prompt_data_str(movie_releases)
chat_context = new_chat_context(movie_info_str)
```

**New Code:**
```python
new_releases_str, rereleases_str = create_prompt_data_str(movie_releases)
chat_context = new_chat_context(new_releases_str, rereleases_str)
```
