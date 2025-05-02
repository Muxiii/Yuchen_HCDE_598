#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
#   FILE: recommender_2.0.py
#   REVISION: April, 2024
#   CREATION DATE: April, 2024
#   AUTHOR: David W. McDonald
#
#   Prototype: 2
#   Version: 0
#
#   This is the code for a very simple chat prototype of a movie recommender. The primary 
#   enhancement for this version is the addition of release information. The release
#   information is provided by the MovieNumbers object
#   
#   Copyright by Author. All rights reserved. Not for reuse without express permissions.
#

#   These are standard python modules/packages
import sys, datetime, json, random
#
#   If you got any version of Protype 1 working then you should have
#   this available on your machine
import requests
#
#   This comes from the rebert class library and manages API keys
#   You should use it to store your OpenAI API key locally, so your
#   key is not stored as a constant in the code.
from rebert.classes.data.KeyManager import KeyManager
#
#   This is a class that collects data from a website called
#   The Numbers: https://www.the-numbers.com/movies/release-schedule
from rebert.classes.release.MovieNumbers import MovieNumbers
#
#
#
#   CONSTANTS
#
#   This example will use an OpenAI service
OAI_HOST = "https://api.openai.com"
OAI_SERVICE_ENDPOINT = "/v1/chat/completions"
OAI_MODEL = "gpt-4-turbo-preview"
#
#   Updated prompt to distinguish between new releases and re-releases
#
MOVIE_RECOMMENDER_PERSONA_PROMPT = '''You are a movie critic who wants to make sure that you make the best movie recommendations. Make sure that the movie you recommend satisfies the user across many movie attributes including genre, actors, visuals, music, plot line, character development, dialog, mood, and many other movie attributes. 

Here is information about current movies in theaters:

NEW RELEASES:
{new_releases_str}

RE-RELEASES:
{rereleases_str}

When recommending movies, consider whether the user might prefer a brand new movie or a classic that's been re-released in theaters. Your responses should always focus on making appropriate movie recommendations based on the user's preferences.'''
#
#
#
#   Request data on recently released movies
#   returns a string of KEY:value release information
def get_recent_releases(cutoff=0):
    #
    #   Use a MovieNumbers object to get some movie data
    #   MovieNumbers does not use an API key. The data is
    #   collected from public web pages and uses screen
    #   scraping to parse the HTML and collect data
    collector = MovieNumbers(name="MovieNumbers-p2.v0")
    movie_list = collector.getRecentReleaseList()
    #
    #   Create a subset if there is a lot of releases
    #   If cutoff is set to 0 (zero) then it returns 
    #   the whole list of movies
    if cutoff and len(movie_list) > cutoff:
        # randomly select a subset of movies
        movie_list = random.sample(movie_list,k=cutoff)
    return movie_list
#
#   Generate separate strings for new releases and re-releases
def create_prompt_data_str(movie_list=[]):
    new_releases = []
    rereleases = []
    
    for movie in movie_list:
        # Check if this is a re-release (notes contain "re-release")
        if 're-release' in movie['notes'].lower():
            data = f"\tMOVIE TITLE: {movie['title']}\n"
            note = movie['notes'].partition(',')[0]
            data += f"\tRELEASE TYPE: {note}\n"
            data += f"\tORIGINAL RELEASE DATE: {movie.get('original_date_str', 'Unknown')}\n"
            data += f"\tRE-RELEASE DATE: {movie['opening_date_str']}\n"
            rereleases.append(data)
        else:
            data = f"\tMOVIE TITLE: {movie['title']}\n"
            note = movie['notes'].partition(',')[0]
            data += f"\tRELEASE TYPE: {note}\n"
            data += f"\tOPENING DATE: {movie['opening_date_str']}\n"
            new_releases.append(data)
    
    # Join all entries with double newlines
    new_releases_str = "\n".join(new_releases)
    rereleases_str = "\n".join(rereleases)
    
    return new_releases_str, rereleases_str
#
#   Create a new chat turn.
#   Each chat turn is a dictionary with a 'role' and 'content'
def new_chat_turn(role="",content=""):
    turn = dict()
    turn['role'] = role
    turn['content'] = content
    return turn
#
#   The program needs to maintain the status of the chat. This status 
#   will include parameters that tell the model how it should respond
#   as well as all of the user questions and the responses.
#   This procedure creates a chat context to maintain that status.
def new_chat_context(new_releases_str="", rereleases_str=""):
    chat_context = dict()
    chat_context['model'] = OAI_MODEL
    chat_context['messages'] = list()    
    sprompt = MOVIE_RECOMMENDER_PERSONA_PROMPT.format(
        new_releases_str=new_releases_str,
        rereleases_str=rereleases_str
    )
    system_turn = new_chat_turn("system", sprompt)
    chat_context['messages'].append(system_turn)
    return chat_context
#
#   Making a request is about modifying the growing chat_context,
#   setting up the HTTP request URL and request headers, and making
#   the request.
def make_chat_request(user_text="", chat_context=None, chat_key=None):
    #   If there is no chat context, raise an error
    if not chat_context:
        raise Exception("No chat_context has been supplied")
    
    #   We use the text we got from the user to create a user turn
    user_turn = new_chat_turn("user",user_text)
    #   Add that user turn to the list of messages in the context
    chat_context['messages'].append(user_turn)
    
    #   The whole context is payload for the request - a request body
    payload = json.dumps(chat_context)
    
    #   Create header information for the request - this must include
    #   the 'Content-Type' key set to 'application/json' and the
    #   'Authorization' key set to include your API key
    header = dict()
    header['Content-Type'] = "application/json"
    header['Authorization'] = f"Bearer {chat_key}"
    
    #   The service URL is the host and the service endpoint
    service_url = OAI_HOST + OAI_SERVICE_ENDPOINT
    
    #   Make this as a POST request
    response = requests.post(service_url,
                             headers=header,
                             data=payload)
    #   The response should be 'application/json' so extract the JSON
    resp_dict = response.json()
    #   There is a lot in the response - just extract the message
    assistant_turn = resp_dict['choices'][0]['message']
    #   Add the response to our chat context
    chat_context['messages'].append(assistant_turn)
    return chat_context

#
#   The main is called from the command line and just loops asking
#   for user ask a question.
def main():
    #   Initialize some variables
    assistant_name = sys.argv[0].rpartition('.')[0]
    
    #   Create a key manager object - it automatically loads
    #   the available key information - if you added a key    
    key_manager = KeyManager()
    #
    #   Returns a list of keys - should only be one
    key_list = key_manager.findRecord(domain="api.openai.com")
    #
    #   Extract just the api key from the key record
    chat_key = key_list[0]['key']
    #
    #   Get some recent release information
    movie_releases = get_recent_releases(cutoff=7) 
    #
    #   Convert the movie data to separate strings for new releases and re-releases
    new_releases_str, rereleases_str = create_prompt_data_str(movie_releases)
    #
    #   Create the chat context with separate sections for new releases and re-releases
    chat_context = new_chat_context(new_releases_str, rereleases_str)
    
    print()
    #   A rather simple chat loop
    user_text = input(f"You > ").strip()
    print()
    #   While the user enters some text - not 'quit'
    while len(user_text)>0 and (user_text.lower() != "quit"):
        
        #   Use that user text to make the request
        chat_context = make_chat_request(user_text, chat_context, chat_key)
        
        #   Get the last message - it should be the text response
        assistant_turn = chat_context['messages'][-1]
        
        #   Show that response
        print(f"{assistant_name} > {assistant_turn['content']}")
        print()
        
        #   Get the next user turn
        user_text = input(f"You > ").strip()
        print()
    
    return

if __name__ == '__main__':
    main()