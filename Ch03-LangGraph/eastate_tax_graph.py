# %%
from typing_extensions import TypedDict
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    query: str
    answer: str
    tax_base_equation: str # 과세표준 계산 수식
    tax_deduction: str # 공제액
    market_ratio: str # 공정시장가액비율
    tax_base: str # 과세표준 계산
    # 세율 계산 = answer

graph_builder = StateGraph(AgentState)

# %% [markdown]
# ### Embedding

# %%
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

embedding_function = OpenAIEmbeddings(model='text-embedding-3-large')

#vector_store = Chroma.from_documents(
#    documents=text_document_list,
#    embedding = embedding_function,
#    collection_name='estate_tax_collection',
#    persist_directory='./estate_tax'
#)

vector_store = Chroma(
    embedding_function=embedding_function,
    collection_name='estate_tax_collection',
    persist_directory='./estate_tax'
)

retriever = vector_store.as_retriever(search_kwargs={'k': 3})

# %%
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model='gpt-4o')
mini_llm = ChatOpenAI(model='gpt-4o-mini')

# %%
from langsmith import Client

client = Client()
rag_prompt = client.pull_prompt("rlm/rag-prompt")

# %% [markdown]
# ## 과세표준

# %%
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

tax_base_equation_chain = (
    {'context': retriever, 'question': RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

def get_tax_base_equation(state: AgentState):
    tax_base_equation_question = '주택에 대한 종합부동산세 계산 시 과세표준을 계산하는 방법을 알려주세요.'
    tax_base_equation = tax_base_equation_chain.invoke(tax_base_equation_question)
    return {'tax_base_equation': tax_base_equation}


# %%
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

tax_base_retrieval_chain = (
    {'context': retriever, 'question': RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

tax_base_equation_prompt = ChatPromptTemplate.from_messages([
    ('system', '사용자의 질문에서 과세표준을 계산하는 방법을 수식으로 나타내주세요. 부연설명 없이 수식만 리턴해주세요.'),
    ('user', '{tax_base_equation_information}')
])

tax_base_equation_chain = (
    {'tax_base_equation_information': RunnablePassthrough()}
    | tax_base_equation_prompt
    | llm
    | StrOutputParser()
)

tax_base_chain = {'tax_base_equation_information': tax_base_retrieval_chain} | tax_base_equation_chain

def get_tax_base_equation(state: AgentState):
    tax_base_equation_question = '주택에 대한 종합부동산세 계산 시 과세표준을 계산하는 방법을 알려주세요.'
    tax_base_equation = tax_base_chain.invoke(tax_base_equation_question)
    print(f"tax_base_equation: {tax_base_equation}")
    return {'tax_base_equation': tax_base_equation}


# %% [markdown]
# ## 공제액

# %%
tax_deduction_chain = (
    {'context': retriever, 'question': RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

def get_tax_deduction(state: AgentState):
    tax_deduction_question = '주택에 대한 종합부동산세 계산 시 공제금액을 알려주세요.'
    tax_deduction = tax_deduction_chain.invoke(tax_deduction_question)
    return {'tax_deduction': tax_deduction}


# %% [markdown]
# ## 공정시장가액비율

# %%
from langchain_tavily import TavilySearch
from datetime import date

tax_market_ratio_prompt = ChatPromptTemplate.from_messages([
    ('system', '아래 정보를 기반으로 공정시장 가액비율을 계산해주세요.\n\nContext:{context}'),
    ('user', '{query}')
])

tavily_search_tool = TavilySearch(
    max_results=3,
    topic="general",
    include_images=True,
    include_raw_content=True,
    include_answer=True,
)

tax_market_ratio_chain = (
    tax_market_ratio_prompt
    | llm
    | StrOutputParser()
)

def get_market_ratio(state: AgentState):
    query = f'오늘 날짜({date.today()})에 해당하는 주택 공시가격 공정시장가액비율은 몇 %인가요?'
    context = tavily_search_tool.invoke({'query': query})
    print(f"tax_market_ratio web search: {context}")

    market_ratio = tax_market_ratio_chain.invoke({'context': context, 'query': query})
    print(f"market ratio: {market_ratio}")

    return {'market_ratio': market_ratio}


# %% [markdown]
# ## 과세표준 계산

# %%
from langchain_core.prompts import PromptTemplate

tax_base_calculation_prompt = ChatPromptTemplate.from_messages([
    ('system', """주어진 내용을 기반으로 과세표준을 계산해주세요.
                                                           
    과세표준 게산 공식: {tax_base_equation}
    공제금액: {tax_deduction}
    공정시장가액비율: {market_ratio}"""),
    ('human', '사용자 주택 공시가격 정보: {query}')
])

tax_base_calculation_chain = (
    tax_base_calculation_prompt
    | llm
    | StrOutputParser()
)

def calculate_tax_base(state: AgentState):
    query = state['query']
    market_ratio = state['market_ratio']
    tax_deduction = state['tax_deduction']
    tax_base_equation = state['tax_base_equation']

    tax_base = tax_base_calculation_chain.invoke({
        'query': query,
        'market_ratio': market_ratio,
        'tax_deduction': tax_deduction ,
        'tax_base_equation': tax_base_equation
    })
    print(f'tax_base: {tax_base}')

    return {'tax_base': tax_base}


# %% [markdown]
# ## 세율 계산

# %%
tax_calculation_rate_prompt = ChatPromptTemplate.from_messages([
    ('system', """당신은 종합부동산세 계산 전문가입니다. 아래 문서를 참고해서 사용자의 질문에 대한 종합부동산세를 계산해주세요.
     
     종합부동산 세율: {context}"""),
     ('human', """과세표준과 사용자가 소지한 주택의 수가 아래와 같을 때 종합부동산세를 계산해주세요.
      
      과세표준: {tax_base}
      주택 수: {query}""")
])

tax_calculation_rate_chain = (
    tax_calculation_rate_prompt
    | llm
    | StrOutputParser()
)

def calculate_tax_rate(state: AgentState):
    query = state['query']
    tax_base = state['tax_base']
    context = retriever.invoke(query)
    tax_rate = tax_calculation_rate_chain.invoke({
        'context': context,
        'tax_base': tax_base,
        'query': query
    })
    print(f'tax_rate: {tax_rate}')
    return {'answer': tax_rate}


# %% [markdown]
# ## Add Node

# %%
graph_builder.add_node('get_tax_deduction', get_tax_deduction)
graph_builder.add_node('get_tax_base_equation', get_tax_base_equation)
graph_builder.add_node('get_market_ratio', get_market_ratio)
graph_builder.add_node('calculate_tax_base', calculate_tax_base)
graph_builder.add_node('calculate_tax_rate', calculate_tax_rate)

# %% [markdown]
# ## Add Edge

# %%
from langgraph.graph import START, END

"""병렬 실행"""
graph_builder.add_edge(START, 'get_tax_base_equation') 
graph_builder.add_edge(START, 'get_tax_deduction') 
graph_builder.add_edge(START, 'get_market_ratio') 

"""fan-in"""
#graph_builder.add_edge('get_tax_base_equation', 'calculate_tax_base')
#graph_builder.add_edge('get_tax_deduction', 'calculate_tax_base')
#graph_builder.add_edge('get_market_ratio', 'calculate_tax_base')

graph_builder.add_edge(
    ['get_tax_base_equation', 'get_tax_deduction', 'get_market_ratio'],
    'calculate_tax_base'
)

graph_builder.add_edge('calculate_tax_base', 'calculate_tax_rate')
graph_builder.add_edge('calculate_tax_rate', END)

# %%
graph = graph_builder.compile()
