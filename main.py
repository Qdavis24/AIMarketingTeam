import autogen
import os
from tools import search, reply, wait, store

CODE_CONFIG = {"use_docker": False}
LLM_CONFIG = {"config_list": [{"model": "gpt-4", "api_key": os.environ.get("OPEN_AI_KEY")}]}

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
                                      a reply to the posts provided, the post should be very human.
                                      advertise {product}. The post should advertise my product effectively,
                                      Your job is simply to market the book I am selling.
                                      Limit the length of the drafted reply to 250 words and be sure to include
                                      a direct link using {link}.
                                      When you have drafted the replies return them in this format,
                                      a list with each drafted reply as a dictionary element in the list, 
                                      reply: reply, post_id: post id""",
                                   is_termination_msg=lambda x: x.get("content", "") and x.get("content",
                                                                                               "").rstrip().endswith(
                                       "TERMINATE"),
                                   )
reply_guy = autogen.AssistantAgent("reply_agent",
                                   llm_config=LLM_CONFIG,
                                   system_message=""" Given a reply and post id, make a tool call using redditreply
                                      to post the reply to the corrosponding post id. In between each reply make a tool
                                      call too wait to limit api request rate""",
                                   is_termination_msg=lambda x: x.get("content", "") and x.get("content",
                                                                                               "").rstrip().endswith(
                                       "TERMINATE"),
                                   )

reply_guy.register_for_llm(name="redditreply", description="reply to a post with a drafted reply")(reply)
reply_guy.register_for_llm(name="wait", description="wait a specified amount of minutes to limit api call rate")(
    wait)
search_guy.register_for_llm(name="redditsearch",
                            description="a function that returns a list of reddit posts given a keyword to search for")(
    search)
search_guy.register_for_llm(name="store",
                            description="input data to store in json file returns all currently stored posts")(store)
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
                                
                                Otherwise send the exact Response from calling tool store back to user proxy including
                                the full title, full body of the post, and post id
                                  and include TERMINATE at end of message
                               """,
            "summary_method": "last_msg"

        },
        {
            "recipient": draft_guy,
            "message": """Use the provided context which contains reddit posts and draft replies to them""",
            "max_turns": 1,
            "summary_method": "last_msg"
        },
        {
            "recipient": reply_guy,
            "message": 'Use the provided context to alternate from posting a reddit reply to the post id in context using'
                       'redditreply and sleep to limit api call rate using wait. post all the drafted replies then return a link'
                       'to each and TERMINATE'
        }
    ]
)
print(chat.summary)
