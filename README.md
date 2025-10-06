# 🧠 MindSpace

**MindSpace** — your digital space for **mental well-being** and self-reflection.

This is a Django-based web platform designed to help users track their mental health, write personal reflections, upload media, complete self-reflection surveys, and chat with an AI assistant.

---

## 🚀 Key Features

* ### User Authentication
    * Sign up and log in via email.
    * Password reset via email.
    * **Personal profile** (change password and email).

* ### Diary
    * Save personal thoughts and reflections.
    * Attach a **music track** for a specific day.
    * View entries in the **Calendar**.

* ### Gallery
    * Upload photos and videos.
    * View all media connected to diary entries.

* ### Calendar
    * Based on a **JavaScript** calendar template.
    * Displays diary entries, tracks, gallery media, and **survey results** for each day.

* ### Self-Reflection Surveys
    * Users can evaluate their day (e.g., **good, neutral, or difficult**).
    * Results are visualized directly in the Calendar.

* ### AI Chat Assistant
    * Built with **Django Channels** and **WebSocket**.
    * Provides **real-time, asynchronous** interaction.

* ### Spotify Integration
    * Users can log in with **Spotify**.
    * **Premium users** can play full tracks.
    * **Non-premium users** can listen to 30-second previews and save their favorite songs.

---

## ⚙️ Technologies

| Category | Technologies |
| :--- | :--- |
| **Backend** | Django, Django Channels |
| **Frontend** | HTML, CSS, JavaScript |
| **Database** | PostgreSQL |
| **AI Communication** | WebSocket-based communication |
| **Containerization** | Docker, Docker Compose |
| **Testing** | PyTest |
| **Environment Config** | .env file |
| **Version Control** | GitHub (+ GitHub Actions for CI/CD) |
| **Music Integration** | Spotify API for adding and playing tracks |

---

### Run with Docker Compose

```bash
docker-compose up --build
```

## ℹ️ Site Access

This site is hosted on a personal server with a dynamic URL.  
You can **access it upon request** by contacting the project author.



## 🧪 Tests

To run tests, **PyTest** is used:
```bash
docker-compose run app pytest
```

## 💾 Backups

Saved commands are available for automatically creating backups of the PostgreSQL database.  
Backups are run as needed.

## 🔮 Future Plans

- Optimize the AI model by increasing server memory and replacing it with a more powerful model.
- Improve user data analytics
- Add mood statistics visualization
- Implement push notifications for diary reminders


## 🎨 Site Styles

The website features **light and dark themes**, allowing users to choose the display mode that suits them best.

## 🌍 Localization

* **Supported languages:** Ukrainian 🇺🇦 and English 🇬🇧.
* **Files:** `.po` (manual translation files) and `.mo` (compiled files).


# 🇺🇦 MindSpace — ваш цифровий простір для турботи про психічне здоров’я


**MindSpace** — це веб-платформа, створена на Django, яка допомагає користувачам відслідковувати свій психологічний стан, вести щоденник думок, додавати фотографії, відео, проходити опитування та спілкуватися з помічником штучного інтелекту.

---

## 🚀 Основний функціонал

- **Реєстрація та авторизація користувачів**
  - Реєстрація через email  
  - Відновлення паролю по електронній пошті  
  - Особистий профіль з можливістю змінити пароль або email  

- **Щоденник**
  - Збереження особистих записів і думок  
  - Додавання треків до конкретних днів  
  - Можливість прив’язати записи до календаря  

- **Галерея**
  - Завантаження фото та відео для певного дня  
  - Перегляд матеріалів у зручному інтерфейсі  

- **Календар**
  - Реалізований на основі готового JavaScript-шаблону  
  - Відображає усі записи, треки, зображення, відео та результати опитувань за вибраний день  

- **Опитування (саморефлексія)**
  - Користувач може відповідати на запитання про свій день  
  - Результати автоматично зберігаються та відображаються у календарі  

- **AI-чат**
  - Помічник штучного інтелекту, реалізований через **Django Channels** та **WebSocket**  
  - Асинхронна взаємодія з користувачем у режимі реального часу  

- **Інтеграція з Spotify**
  - Авторизація користувачів через Spotify API  
  - Користувачі з Premium-акаунтом можуть слухати повні треки  
  - Інші користувачі можуть слухати 30-секундні прев’ю та додавати улюблені треки до своїх записів  

---

## ⚙️ Технології

- **Backend:** Django, Django Channels  
- **Frontend:** HTML, CSS, JavaScript  
- **Database:** PostgreSQL  
- **AI integration:** WebSocket (Django Channels)  
- **Containerization:** Docker, Docker Compose  
- **Testing:** PyTest  
- **Environment:** `.env` файл для змінних середовища  
- **Version Control:** GitHub + GitHub Actions (раніше для CI/CD)  
- **Інтеграція музики** Spotify API для додавання та відтворення треків 

---

## 🌍 Локалізація

- Сайт підтримує **українську 🇺🇦** та **англійську 🇬🇧** мови  
- Локалізаційні файли: `.po` (ручний переклад) та `.mo` (скомпільований)  


## 🐳 Розгортання за допомогою Docker

 Запустити додаток:
    ```bash
    docker-compose up --build
    ```
## ℹ️ Доступ до сайту

Сайт запускається на персональному сервері з динамічною URL-адресою.  
Переглянути його можна **за запитом**, звернувшись до автора проекту.

---

## 🧪 Тести

Для запуску тестів використовується **PyTest**:
```bash
docker-compose run app pytest
```
---
## 💾 Бекапи

Збережені команди для автоматичного створення бекапу бази даних PostgreSQL.  
Бекап запускається за потреби. 

## 🔮 Майбутні плани

- Оптимізувати модель штучного інтелекту додавши більший обсяг пам’яті на сервері та замінивши модель на потужнішу.
- Покращити аналітику користувацьких даних
- Додати візуалізацію статистики настрою
- Впровадити push-сповіщення для нагадувань про записи

---

## 🎨 Стилі сайту

Сайт реалізований у **світлій та темній темі**, щоб користувачі могли обирати зручний для себе режим відображення.
---



