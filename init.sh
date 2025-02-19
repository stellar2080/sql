chroma run --path vectordb &
CHROMA_PID=$!
python src/llm/service.py &
LLM_PID=$!

wait $CHROMA_PID $LLM_PID

echo "Chroma and LLM servers have been stopped."