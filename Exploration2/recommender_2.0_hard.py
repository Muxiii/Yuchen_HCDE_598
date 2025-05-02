#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
#   FILE: recommender_2.0.py
#   REVISION: April, 2024
#   CREATION DATE: April, 2024
#   AUTHOR: David W. McDonald
#
#   Prototype: 2
#   Version: 1
#
#   Enhanced version that distinguishes among different types of movie releases
#   based on the notes field from MovieNumbers.
#
#   Copyright by Author. All rights reserved. Not for reuse without express permissions.
#

import sys, datetime, json, random
import requests
from rebert.classes.data.KeyManager import KeyManager
from rebert.classes.release.MovieNumbers import MovieNumbers

OAI_HOST = "https://api.openai.com"
OAI_SERVICE_ENDPOINT = "/v1/chat/completions"
OAI_MODEL = "gpt-4-turbo-preview"

MOVIE_RECOMMENDER_PERSONA_PROMPT = '''You are a movie critic who wants to make sure that you make the best movie recommendations. 
Make sure that the movie you recommend satisfies the user across many movie attributes including genre, actors, visuals, music, 
plot line, character development, dialog, mood, and many other movie attributes. 

Pay special attention to the RELEASE TYPE when making recommendations, as different release types often indicate different viewing experiences:
- Wide Releases: Major studio films with broad appeal, typically big-budget productions
- Limited Releases: Often independent or art-house films with more niche appeal
- IMAX Releases: Films optimized for large-format, immersive viewing
- Re-releases: Classic films returning to theaters, often remastered
- Festival Releases: Typically award-contending films with critical acclaim
- Special Engagement: Unique screenings or events around the film

Here is a list of recently released movies. The list contains the MOVIE TITLE, the RELEASE TYPE, and the OPENING DATE for each movie.

{movie_data_str}

Your responses should always focus on making movie recommendations that consider the release type when appropriate.'''

def get_recent_releases(cutoff=0):
    collector = MovieNumbers(name="MovieNumbers-p2.v1")
    movie_list = collector.getRecentReleaseList()
    if cutoff and len(movie_list) > cutoff:
        movie_list = random.sample(movie_list,k=cutoff)
    return movie_list

def create_prompt_data_str(movie_list=[]):
    movie_info_str = ""
    for movie in movie_list:
        # Extract the primary release type from notes
        notes = movie['notes']
        release_type = "General Release"  # default
        
        if notes:
            # Clean up and categorize the release type
            note_parts = [part.strip() for part in notes.split(',')]
            primary_note = note_parts[0].lower()
            
            if 'wide' in primary_note:
                release_type = "Wide Release"
            elif 'limited' in primary_note:
                release_type = "Limited Release"
            elif 'imax' in primary_note:
                release_type = "IMAX Release"
            elif 're-release' in primary_note:
                release_type = "Re-release"
            elif 'festival' in primary_note:
                release_type = "Festival Release"
            elif 'special' in primary_note:
                release_type = "Special Engagement"
        
        data = f"\tMOVIE TITLE: {movie['title']}\n"
        data += f"\tRELEASE TYPE: {release_type}\n"
        data += f"\tOPENING DATE: {movie['opening_date_str']}\n"
        movie_info_str += "\n" + data
    return movie_info_str

def new_chat_turn(role="",content=""):
    turn = dict()
    turn['role'] = role
    turn['content'] = content
    return turn

def new_chat_context(movie_data_str=""):
    chat_context = dict()
    chat_context['model'] = OAI_MODEL
    chat_context['messages'] = list()    
    sprompt = MOVIE_RECOMMENDER_PERSONA_PROMPT.format(movie_data_str=movie_data_str)
    system_turn = new_chat_turn("system",sprompt)
    chat_context['messages'].append(system_turn)
    return chat_context

def make_chat_request(user_text="", chat_context=None, chat_key=None):
    if not chat_context:
        raise Exception("No chat_context has been supplied")
    
    user_turn = new_chat_turn("user",user_text)
    chat_context['messages'].append(user_turn)
    
    payload = json.dumps(chat_context)
    
    header = dict()
    header['Content-Type'] = "application/json"
    header['Authorization'] = f"Bearer {chat_key}"
    
    service_url = OAI_HOST + OAI_SERVICE_ENDPOINT
    
    response = requests.post(service_url,
                             headers=header,
                             data=payload)
    resp_dict = response.json()
    assistant_turn = resp_dict['choices'][0]['message']
    chat_context['messages'].append(assistant_turn)
    return chat_context

def main():
    assistant_name = sys.argv[0].rpartition('.')[0]
    
    key_manager = KeyManager()
    key_list = key_manager.findRecord(domain="api.openai.com")
    chat_key = key_list[0]['key']
    
    movie_releases = get_recent_releases(cutoff=7) 
    movie_info_str = create_prompt_data_str(movie_releases)
    chat_context = new_chat_context(movie_info_str)
    
    print()
    user_text = input(f"You > ").strip()
    print()
    
    while len(user_text)>0 and (user_text.lower() != "quit"):
        chat_context = make_chat_request(user_text, chat_context, chat_key)
        assistant_turn = chat_context['messages'][-1]
        print(f"{assistant_name} > {assistant_turn['content']}")
        print()
        user_text = input(f"You > ").strip()
        print()
    
    return

if __name__ == '__main__':
    main()