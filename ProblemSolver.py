#!/usr/bin/env python

"""ProblemSolver.py: A program that finds common solutions to technical or programming problems, by searching for a consensus among programming help forums. Uses the Metaphor API"""

__author__ = "Darius Rudominer"

import os
import openai
from metaphor_python import Metaphor
from dotenv import find_dotenv, load_dotenv

#fetches enviornment variables
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

#sets up keys
openai.api_key = os.getenv("OPENAI_API_KEY")
metaphor = Metaphor(os.getenv("METAPHOR_API_KEY"))

#gets the user's question
USER_QUESTION = input("Welcome to ProblemSolver! What seems to be your programming problem?\n")

#the number of page results to search
n = 10

#OpenAI model 1: converts the users problem into a search term
SYSTEM_MESSAGE = "You are a helpful assistant that generates search queries based on users' technical problems. Only generate one search query in order to find people with similar problems to the user."
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": USER_QUESTION},
    ],
)

#Metaphor: uses the search to generate a list of links from reddit and stackOverflow
query = completion.choices[0].message.content
search_response = metaphor.search(
    query, use_autoprompt=True, include_domains=["reddit.com","stackoverflow.com"], num_results=n
)


print("-----------")
print("Searching: \""+ query + "\"")
print("-----------")

#OpenAI models 2-11: summerize the solutions to the user's problem found on each of the web pages returned by metaphor
contents_result = search_response.get_contents()
summaries = []
SYSTEM_MESSAGE = "You are a helpful assistant that determines the most popular solution to a technical problem from a web page in which people discuss that problem. Reply to a web page with a summary of the most popular solutions to the problem discussed within."
for i in range(n):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": contents_result.contents[i].extract},
        ],
    )
    summaries.append(completion.choices[0].message.content)
    print("Summarizing: " + str(i))


#Concatenate together all of the solutions found into one string, to be fed to model 12
sumContent = ""
for i in range(n):
    sumContent += " SOLUTION " + str(i) + ": " + summaries[i] + "\n"


#OpenAI model 12: summarizes the top three most common solutions found among the 10 summaries
SYSTEM_MESSAGE = "You are a helpful assistant that finds the most common solution from among a large list of solutions to a problem. Reply to a long list of solutions with a summary of the top 3 most commonly suggested solutions, as a numbered list."
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": sumContent},
    ],
)

##print the results to the user
print("---------------------")
print(completion.choices[0].message.content)
