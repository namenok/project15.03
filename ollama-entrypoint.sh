#!/bin/sh

echo "🚀 Запуск сервера Ollama..."

# Запуск сервера у фоновому режимі
ollama serve &

# Очікування готовності Ollama (CLI може отримати список моделей)
until ollama list >/dev/null 2>&1; do
  echo "⏳ Очікуємо готовності Ollama..."
  sleep 2
done

# Перевірка: чи модель вже присутня. Якщо ні — завантажуємо
if ! ollama list | grep -q 'gemma3:1b'; then
  echo "⬇️  Завантажуємо модель gemma3:1b..."
  ollama pull gemma3:1b
else
  echo "✅ Модель gemma3:1b вже доступна."
fi

# Очікування завершення всіх фонових процесів (щоб сервер залишався активним)
wait
