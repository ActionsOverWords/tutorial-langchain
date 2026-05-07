# %%
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

embedding_function = OpenAIEmbeddings(model = 'text-embedding-3-large')

vector_store = Chroma(
    embedding_function=embedding_function,
    collection_name='imcome_tex_collection',
    persist_directory='./chroma'
)

retriever = vector_store.as_retriever(search_kwargs={'k': 3})

# %%
from typing_extensions import TypedDict
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    query: str
    context: list
    answer: str

graph_builder = StateGraph(AgentState)

# %%
def retrieve(state: AgentState):
    query = state['query']
    docs = retriever.invoke(query)
    return {'context': docs}

# %%
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model='gpt-4o')

# %%
from langsmith import Client

client = Client()
generate_prompt = client.pull_prompt("rlm/rag-prompt")

def generate(state: AgentState):
    query = state['query']
    context = state['context']
    rag_chain = generate_prompt | llm
    response = rag_chain.invoke({'question': query, 'context': context})
    return {'answer': response}

# %%
from typing import Literal

doc_relevance_prompt = client.pull_prompt("langchain-ai/rag-document-relevance")

def check_doc_relevance(state: AgentState) -> Literal['relevant', 'irrelevant']:
    query = state['query']
    context = state['context']
    print(f'context == {context}')

    doc_relevance_rag_chain = doc_relevance_prompt | llm
    response = doc_relevance_rag_chain.invoke({'question': query, 'documents': context})
    print(f'doc relevance response == {response}')

    if response['Score'] == 1:
        return 'relevant'
    return 'irrelevant'

# %%
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

rewrite_prompt = PromptTemplate.from_template("""
사용자의 질문을 보고, 웹 검색에 용이하게 사용자의 질문을 수정해주세요.
질문: {query}
""")

def rewrite(state: AgentState):
    query = state['query']
    rewrite_chain = rewrite_prompt | llm | StrOutputParser()

    response = rewrite_chain.invoke({'query': query})
    print(f"rewrite response: {response}")

    return {'query': response}

# %% [markdown]
# ## [Tavily](https://www.tavily.com/)
# 
# - 웹 검색 시 LangChain에서 많이 사용
# 
# ### [Tavily search integration](https://docs.langchain.com/oss/python/integrations/tools/tavily_search)

# %%
from langchain_tavily import TavilySearch

tavily_search_tool = TavilySearch(
    max_results=3,
    topic="general",
)

def web_search(state: AgentState):
    query = state["query"]
    response = tavily_search_tool.invoke({'query': query})
    print(f"web search response: {response}")
    return {'context': response}

# %%
graph_builder.add_node('retrieve', retrieve)
graph_builder.add_node('generate', generate)
graph_builder.add_node('rewrite', rewrite)
graph_builder.add_node('web_search', web_search)

# %%
from langgraph.graph import START, END

graph_builder.add_edge(START, 'retrieve')
graph_builder.add_conditional_edges(
    'retrieve',
    check_doc_relevance,
    {
        'relevant': 'generate',
        'irrelevant': 'rewrite'
    }
)
graph_builder.add_edge('rewrite', 'web_search')
graph_builder.add_edge('web_search', 'generate')
graph_builder.add_edge('generate', END)

# %%
graph = graph_builder.compile()