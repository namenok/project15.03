#!/bin/sh

echo "Server startup Ollama..."

ollama serve &

until ollama list >/dev/null 2>&1; do
  echo "Waiting for readiness Ollama..."
  sleep 2
done

if ! ollama list | grep -q 'gemma3:1b'; then
  echo "Loading the model gemma3:1b..."
  ollama pull gemma3:1b
else
  echo "The gemma3:1b model is now available"
fi

wait
