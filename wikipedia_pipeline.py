from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
from schemas import OpenAIChatMessage
import requests
import os

proxies = {'http': 'http://172.16.18.121:10809','https': 'http://172.16.18.121:10809'}
class Pipeline:
    class Valves(BaseModel):
        pass

    def __init__(self):
        # Optionally, you can set the id and name of the pipeline.
        # Best practice is to not specify the id so that it can be automatically inferred from the filename, so that users can install multiple versions of the same pipeline.
        # The identifier must be unique across all pipelines.
        # The identifier must be an alphanumeric string that can include underscores or hyphens. It cannot contain spaces, special characters, slashes, or backslashes.
        # self.id = "维基_管道"
        self.name = "维基百科"

        # Initialize rate limits
        self.valves = self.Valves(**{"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "")})

    async def on_startup(self):
        # This function is called when the server is started.
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        print(f"on_shutdown:{__name__}")
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        # This is where you can add your custom pipelines like RAG.

        print(f"pipe:{__name__}")

        if body.get("title", False):
            print("Title Generation")
            return "wikipedia pipeline"
        else:
            titles = []
            for query in [user_message]:
                query = query.replace(" ", "_")
                r = requests.get(f"https://zh.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=1&namespace=0&format=json",proxies=proxies)
                response = r.json()
                titles = titles + response[1]
                print(titles)

            context = None
            if len(titles) > 0:
                r = requests.get(f"https://zh.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles={'|'.join(titles)}",proxies=proxies)
                response = r.json()
                # get extracts
                pages = response["query"]["pages"]
                for page in pages:
                    if context == None:
                        context = pages[page]["extract"] + "\n"
                    else:
                        context = context + pages[page]["extract"] + "\n"

            return context if context else "No information found"
