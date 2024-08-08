from pathlib import Path

import chainlit as cl
from langchain.callbacks.base import BaseCallbackHandler
from langchain.indexes import SQLRecordManager, index
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnableConfig, RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

chunk_size = 1024
chunk_overlap = 50

embeddings_model = OpenAIEmbeddings()

PDF_STORAGE_PATH = "./pdfs"


def process_pdfs(pdf_storage_path: str):
    pdf_directory = Path(pdf_storage_path)
    docs = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    for pdf_path in pdf_directory.glob("*.pdf"):
        loader = PyMuPDFLoader(str(pdf_path))
        documents = loader.load()
        print(len(documents))
        docs += text_splitter.split_documents(documents)
        print(len(docs))

    doc_search = Chroma.from_documents(docs, embeddings_model)

    namespace = "chromadb/my_documents"
    record_manager = SQLRecordManager(
        namespace, db_url="sqlite:///record_manager_cache.sql"
    )
    record_manager.create_schema()

    index_result = index(
        docs, record_manager, doc_search, cleanup="incremental", source_id_key="source"
    )

    print(f"indexing stats: {index_result}")

    return doc_search


doc_search = process_pdfs(PDF_STORAGE_PATH)
model = ChatOpenAI(model_name="gpt-4o-mini", streaming=True)


@cl.on_chat_start
async def on_chat_start():
    template = """以下のコンテキストのみを使用して、質問に答えてください。
    {context}

    質問: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])

    retriever = doc_search.as_retriever()

    runnable = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )

    # chainは起動時に一度だけ作成し、sessionに保存する
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")

    # 出力のメッセージ
    msg = cl.Message(content="")

    class PostMessageHandler(BaseCallbackHandler):
        # RAGで検索したソース文書を保存するためのCallbackハンドラ
        def __init__(self, msg: cl.Message):
            BaseCallbackHandler.__init__(self)
            self.msg = msg
            self.sources = set()

        def on_retriever_end(self, documents, *, run_id, parent_run_id, **kwargs):
            print(f"retrieved {len(documents)} documents")
            for d in documents:
                source_page_pair = (d.metadata["source"], d.metadata["page"])
                self.sources.add(source_page_pair)

        def on_llm_end(self, response, *, run_id, parent_run_id, **kwargs):
            print("on_llm_end")
            if len(self.sources):
                sources_text = "\n".join(
                    [f"{source}#page={page}" for source, page in self.sources]
                )
                self.msg.elements.append(
                    cl.Text(name="Sources", content=sources_text, display="inline")
                )

    async for chunk in runnable.astream(
        message.content,
        config=RunnableConfig(
            callbacks=[cl.LangchainCallbackHandler(), PostMessageHandler(msg)]
        ),
    ):
        await msg.stream_token(chunk)

    await msg.send()
