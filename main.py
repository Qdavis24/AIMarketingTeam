import autogen
import os
from dotenv import load_dotenv
from tools import search, reply, wait, store, read
load_dotenv()

CODE_CONFIG = {"use_docker": False}
LLM_CONFIG = {"config_list": [{"model": "gpt-4", "api_key": os.getenv("OPEN_AI_KEY")}], 'cache_seed': None,}

product = """my product 'Yellowstone Expedition Guide' by TravelBrains,
                                  a book that is a collection of all the best locations in yellowstone to visit and hike
                                and also contains lots of historically significant locations."""
link = """https://travelbrains.com/products/yellowstone-expedition-guide"""

user_proxy = autogen.UserProxyAgent("user_proxy",
                                    code_execution_config=CODE_CONFIG,
                                    llm_config=False,
                                    human_input_mode="NEVER",
                                    is_termination_msg=lambda x: x.get("content", "") and x.get("content",
                                                                                                "").rstrip().endswith(
                                        "TERMINATE"),
                                    )

search_guy = autogen.AssistantAgent("filter_agent",
                                    llm_config=LLM_CONFIG,
                                    system_message="""You are a world class marketer, You can make tool calls to search
                                    reddit. You can also make tool calls to store data. When searching reddit use more than
                                    one word. ALWAYS filter and store bests posts when receiving response from redditsearch tool
                                    call""",
                                    is_termination_msg=lambda x: x.get("content", "") and x.get("content",
                                                                                                "").rstrip().endswith(
                                        "TERMINATE"),
                                    )

draft_guy = autogen.AssistantAgent("draft_agent",
                                   llm_config=LLM_CONFIG,
                                   system_message=f"""You are an experienced marketer and redditor, your job is too draft"
                                      a reply to the posts provided, the post should be very human and contain
                                      specific information from the original post.
                                      advertise {product}. The post should advertise my product effectively,
                                      Your job is simply to market the book I am selling.
                                      Limit the length of the drafted reply to 250 words and be sure to include
                                      a direct link using {link}.
                                      """,
                                   is_termination_msg=lambda x: x.get("content", "") and x.get("content",
                                                                                               "").rstrip().endswith(
                                       "TERMINATE"),
                                   )


draft_guy.register_for_llm(name="redditreply", description="reply to a post with a drafted reply")(reply)
draft_guy.register_for_llm(name="wait", description="wait a specified amount of minutes to limit api call rate")(
    wait)
draft_guy.register_for_llm(name="read", description="returns one post from json file and removes that post from file")(read)

search_guy.register_for_llm(name="redditsearch",
                            description="a function that returns a list of reddit posts given a keyword to search for")(
    search)
search_guy.register_for_llm(name="store",
                            description="stores inputed post data in json file and returns the number of currently stored posts")(store)

user_proxy.register_for_execution(name="read")(read)
user_proxy.register_for_execution(name="store")(store)
user_proxy.register_for_execution(name="redditsearch")(search)
user_proxy.register_for_execution(name="wait")(wait)
user_proxy.register_for_execution(name="redditreply")(reply)

chat = user_proxy.initiate_chats(
    [
        {
            "recipient": search_guy,
            "message": f"""search reddit and filter posts to find 5 unique reddit posts that I could use to market {product}
                                
                                
                                If you have received a response from a call to redditsearch, ALWAYS filter the response
                                for the bests posts and save them using store in this format.. list of dicts
                                
                                If there are not 5 posts stored continue to search reddit
                                
                                
                                """,
                               
            "summary_method": "last_msg",
            "max_turns": 10

        },
        {
            "recipient": draft_guy,
            "message": """Draft and post replies to each post in the posts.json file, each time you draft a reply to a post
              it will be removed from the file. continue to draft and post replies until there are no more posts left in the file.
              when you are finished show the replies and their link then TERMINATE""",
            "summary_method": "last_msg"
        },
      
    ]
)
os.remove("./posts.json")
