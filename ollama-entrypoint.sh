#!/bin/sh

echo "🚀 Запуск сервера Ollama..."

ollama serve &

until ollama list >/dev/null 2>&1; do
  echo "⏳ Очікуємо готовності Ollama..."
  sleep 2
done

if ! ollama list | grep -q 'gemma3:1b'; then
  echo "⬇️  Завантажуємо модель gemma3:1b..."
  ollama pull gemma3:1b
else
  echo "✅ Модель gemma3:1b вже доступна."
fi

wait
