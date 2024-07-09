import json
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from apscheduler.schedulers.background import BackgroundScheduler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Replace with your Telegram bot token
# Load environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')


# JSON file path
JSON_FILE = 'quiz_questions.json'

# Function to load quiz questions from JSON file
def load_quiz(filename=JSON_FILE):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Function to save quiz questions to JSON file
def save_quiz(quiz_data, filename=JSON_FILE):
    with open(filename, 'w') as file:
        json.dump(quiz_data, file, indent=4)

# Command handler to add a new question
def add_question(update: Update, context: CallbackContext) -> None:
    message = update.message.text.split(maxsplit=1)
    if len(message) < 2:
        await update.message.reply_text('Please provide at least one valid question in JSON format.')
        return

    try:
        questions = message[1].split('\n')  # Split by newline to get individual JSON questions
        for question_str in questions:
            new_question = json.loads(question_str)
            add_question_to_quiz(new_question)
        await update.message.reply_text('Questions added successfully!')
    except json.JSONDecodeError as e:
        update.message.reply_text(f'Error: Invalid JSON format. {str(e)}')
        
# Function to add a new question to the quiz
def add_question_to_quiz(new_question):
    quiz = load_quiz()
    quiz.append(new_question)
    save_quiz(quiz)

# Command handler to start the quiz
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Quiz is being sent to the channel.')
    await send_quiz(context)

# Function to send the quiz
async def send_quiz(context: CallbackContext):
    quiz = load_quiz()
    for question in quiz:
        await context.bot.send_poll(
            chat_id=CHANNEL_ID,
            question=question["question"],
            options=question["options"],
            type='quiz',
            correct_option_id=question["correct_option_id"]
        )

# Command handler to delete all questions
def delete_questions(update: Update, context: CallbackContext) -> None:
    save_quiz([], JSON_FILE)  # Empty list to clear all questions
    await update.message.reply_text('All previous questions have been deleted.')

async def hello(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hello, Bot is Working.')

def main():
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TOKEN).build()

    # Register the /start, /addquestion, and /deletequestions commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addquestion", add_question))
    application.add_handler(CommandHandler("deletequestions", delete_questions))
    application.add_handler(MessageHandler(filters.Text("hello"), hello))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
