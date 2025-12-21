from langgraph.checkpoint.postgres import PostgresSaver

from config import DB_URL 

with PostgresSaver.from_conn_string(DB_URL) as checkpointer:
    checkpointer.setup()