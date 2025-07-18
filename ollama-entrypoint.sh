#!/bin/sh

echo "🚀 Starting Ollama server..."

# Start the Ollama server in the background
ollama serve &

# Wait until ollama CLI can list models (server ready)
until ollama list >/dev/null 2>&1; do
  echo "⏳ Waiting for Ollama to be ready..."
  sleep 2
done

# Check and pull model if needed
if ! ollama list | grep -q 'gemma.*2b'; then
  echo "⬇️  Pulling gemma:2b model..."
  ollama pull gemma:2b
else
  echo "✅ gemma:2b model already exists."
fi

# Wait for background processes to finish (keeps server running)
wait
