chroma run --path vectordb &
CHROMA_PID=$!
python src/service.py &
LLM_PID=$!

wait $CHROMA_PID $LLM_PID

echo "Chroma and LLM servers have been stopped."