import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler, ConversationHandler,
    filters, MessageHandler

)

from config import TOKEN, GIT_TOKEN, USER_ID
import requests as req

SENT = 1
BACK_TO_MENU = 2


class RequestedData:
    def __init__(self):
        self.repos = {}
        self.commits = {}
        self.lang_data = {}

    def get_repos(self):
        return self.repos

    def set_repos(self, repos: dict):
        self.repos = repos

    def get_commits(self):
        return self.commits

    def set_commits(self, commits: dict):
        self.commits = commits

    def get_lang_data(self, index=None):
        if index is None:
            return self.lang_data
        else:
            return self.lang_data[index]

    def set_lang_data(self, index, data: str):
        if index not in self.lang_data.keys():
            self.lang_data[index] = []
        self.lang_data[index] += [data]


class Commands:
    def __init__(self):
        self.git_url = "https://github.com/pureheroky"
        self.git_api_url = "https://api.github.com"
        self.query = Update
        self.keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Back to menu", callback_data="menu"), ]])
        self.context = ContextTypes.DEFAULT_TYPE
        self.username = "pureheroky"

    def get_user_repos(self, username):
        url = fr"{self.git_api_url}/users/{username}/repos"
        headers = {"Authorization": f"token {GIT_TOKEN}"}
        response = req.get(url, headers=headers)
        return response.json()

    async def execute_command(self, command, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if command == "git":
            await self.send_user_commits(update, context)
        if command == "lore":
            await self.send_lore(update, context)
        if command == "projects":
            await self.send_projects(update, context)

    def get_user_commits(self):
        repos_names = self.get_projects()
        _return = []
        _data = {}
        for i in repos_names:
            repo = repos_names[i][1]
            url = fr"{self.git_api_url}/repos/{self.username}/{repo}/commits"
            headers = {"Authorization": f"token {GIT_TOKEN}"}

            if rd.get_commits() == {}:
                response = req.get(url, headers=headers)
                data = response.json()
                if repo not in _data.keys():
                    _data[repo] = []
                _data[repo] += data
            else:
                data = rd.get_commits()[repo]

            count = 0
            _return.append(f"<b><i>Title: <code>{repo}</code></i></b>")

            for j in data:
                commit = j["commit"]
                date = commit['committer']['date'].replace("T", " ").replace("Z", "")
                _return.append(f"\nAuthor: <b>{commit['committer']['name']}</b>\n")
                _return.append(f"Date: <b>{date}</b>\n")
                _return.append(f"Message: <b>{commit['message']}</b>\n")
                count += 1
                if count == 5:
                    break

            _return.append(
                f"\n<b><i>Find out more on <a href='https://github.com/0xpure/{repo}'>project page</a></i></b>\n\n\n")

        if rd.get_commits() == {}:
            rd.set_commits(_data)

        return _return

    async def send_user_commits(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        self.query = update
        await query.edit_message_text(
            text="You are on <b>Git</b> page\nThe latest commits will be shown here\n\n\n<b><i>Loading commits...</i></b>",
            parse_mode=ParseMode.HTML,
            reply_markup=self.keyboard,
        )
        data = self.get_user_commits()
        _string = "".join(data)
        _string += "\n\nMore information about the final products can be found <a href='https://0xpure.com'><b>here</b></a>"
        await query.edit_message_text(
            text=_string,
            parse_mode=ParseMode.HTML,
            reply_markup=self.keyboard,
            disable_web_page_preview=True
        )

    def get_projects(self):
        url = fr"{self.git_api_url}/users/{self.username}/repos"
        lang_url = fr"{self.git_api_url}/repos/{self.username}/"
        headers = {"Authorization": f"token {GIT_TOKEN}"}

        if rd.get_repos() == {}:
            response = req.get(url, headers=headers)
            data = response.json()
            rd.set_repos(data)
        else:
            data = rd.get_repos()

        _return = {}

        if not bool(rd.get_lang_data()):
            for i in range(len(data)):
                languages = req.get(lang_url + data[i]["name"] + "/languages")
                languages = languages.json()
                if languages == {}:
                    languages = {"Unknown": 00000}
                for j in languages:
                    rd.set_lang_data(i, j)

        for i in range(len(data)):
            _return[i] = [data[i]["id"], data[i]["name"], data[i]["url"], rd.get_lang_data(i),
                          data[i]["created_at"].replace("T", " ").replace("Z", ""),
                          data[i]['default_branch']]
        return _return

    async def send_projects(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        self.query = update
        await query.edit_message_text(
            text="You are on <b>Projects</b> page\nAll available projects will be shown here\n\n\n<b><i>Loading branches...</i></b>",
            parse_mode=ParseMode.HTML,
            reply_markup=self.keyboard)
        data = self.get_projects()

        _return = []
        for j in data:
            print(data[j])
            _return.append(f"<b><i>Title: <code>{data[j][1]}</code></i></b>\n")
            _return.append(f"<b>ID: {data[j][0]}</b>\n")
            _return.append(f"<b>URL: <a href='https://github.com/pureheroky/{data[j][1]}'>link</a></b>\n")
            _return.append(f"<b>Language: {data[j][3]}</b>\n")
            _return.append(f"<b>Creation date: {data[j][4]}</b>\n")
            _return.append(f"<b>Default branch: {data[j][5]}</b>\n\n\n")

        _string = "".join(_return)
        _string += "\n\nMore information about the projects can be found <a href='https://0xpure.com'><b>here</b></a>"
        await query.edit_message_text(
            text=_string,
            parse_mode=ParseMode.HTML,
            reply_markup=self.keyboard,
            disable_web_page_preview=True
        )

    def get_lore(self):
        skills = [
            "HTML/CSS/JS", "Reactjs", "Redux",
            "Tailwindcss", "Bootstrap", "SCSS(Sass)",
            "Webpack", "Webpack dev server", "Git",
            "OOP", "Express.js", "Postgresql",
            "Sqlite", "Nginx", "Apache",
            "Adaptive layout", "Cross-browser layout", "JSON",
            "Python 3", "Django", "BeautifulSoup4",
            "Requests", "Opencv", "Next",
            "Prisma", "Matplotlib", "Pandas",
            "Numpy", "Requests",
        ]

        data = []
        for i in range(len(skills)):
            skill = skills[i]
            data.append(f"<i>{i + 1}</i>. <b>{skill}</b>\n")

        return data

    async def send_lore(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        self.query = query

        _string = "".join(self.get_lore())
        _string += "\n\nMore information about the knowledge stack can be found <a href='https://0xpure.com'><b>here</b></a>"

        await query.edit_message_text(
            text="You are on <b>Lore</b> page\nAll my knowledge will be shown here\n\n\n<b><i>Loading lore...</i></b>",
            parse_mode=ParseMode.HTML,
            reply_markup=self.keyboard)

        await query.edit_message_text(
            text=_string,
            parse_mode=ParseMode.HTML,
            reply_markup=self.keyboard
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()
    await update.message.reply_text(text="""\n\n<b><i>pureheroky</i></b> was created to help people contact/learn about me.\n
It has a couple of different <strong>buttons</strong> that show any information (knowledge stacks, projects, etc.).\n
Command list:\n\n\n
<code><b>REQUEST:</b> \ncreate a job request</code>\n
<code><b>GIT:</b> \nget last commits/accessible repos</code>\n
<code><b>LORE:</b> \nget knowledge stack</code>\n
<code><b>PROJECTS:</b> \nget list of complete/under development projects\n</code>
\n\nBot will be opensource someday (look on my <a href="https://0xpure.com">website</a> or in the bot description)""",
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=keyboard_menu()
                                    )


async def action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    commands = ["git", "request", "lore", "projects"]
    cmd_system = Commands()

    if query.data not in commands:
        await error(update, context)
    else:
        for cmd in commands:
            if cmd == query.data:
                await cmd_system.execute_command(cmd, update, context)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error occurred at {datetime.datetime.now()}")
    return ConversationHandler.END


def keyboard_menu():
    keyboard = [
        [
            InlineKeyboardButton("Request", callback_data="request"),
            InlineKeyboardButton("Lore", callback_data="lore"),
        ],
        [
            InlineKeyboardButton("Git", callback_data="git"),
            InlineKeyboardButton("Projects", callback_data="projects"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="""\n\n<b><i>pureheroky</i></b> was created to help people contact/learn about me.\n
It has a couple of different <strong>buttons</strong> that show any information (knowledge stacks, projects, etc.).\n
Command list:\n\n\n
<code><b>REQUEST:</b> \ncreate a job request</code>\n
<code><b>GIT:</b> \nget last commits/accessible repos</code>\n
<code><b>LORE:</b> \nget knowledge stack</code>\n
<code><b>PROJECTS:</b> \nget list of complete/under development projects\n</code>
        \n\nBot will be opensource someday (look on my <a href="https://0xpure.com">website</a> or in the bot description)""",
                                  parse_mode=ParseMode.HTML,
                                  reply_markup=keyboard_menu()
                                  )


async def request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Back to menu", callback_data="menu"), ]])
    await update.callback_query.edit_message_text(
        text='You are on <b>Request</b> page.\n\n'
             'If you want to make a job request, please follow the <b>sample</b>:\n\n\n'
             '<b>1. Your name</b>\n'
             '<b>2. Direction of the task (any web-development/python apps etc.)</b>\n'
             '<b>3. Task description</b>\n'
             '<b>4. Ways to contact you</b>\n\n\n'
             'Requests not similar to the sample <span class="tg-spoiler"><b>will be ignored.</b></span>',
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )
    context.user_data['state'] = SENT
    return SENT


async def accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) > 1:
        user = context.args[0]
        message = context.args[1:]
        if update.message.from_user.id == USER_ID:
            await context.bot.send_message(text=f"Accepted {user}", chat_id=USER_ID)
            await context.bot.send_message(
                text=f"Your request was accepted, there is message from pureheroky:\n\n{' '.join(message)}",
                chat_id=user,
            )


async def decline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) > 1:
        user = context.args[0]
        message = context.args[1:]
        if update.message.from_user.id == USER_ID:
            await context.bot.send_message(text=f"Declined {user}", chat_id=USER_ID)
            await context.bot.send_message(
                text=f"Your request was declined, there is message from pureheroky:\n\n{' '.join(message)}",
                chat_id=user,
            )


async def sent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('state') == 1:
        user_input = update.message.text
        chat = update.message.chat

        user = update.message.from_user
        await context.bot.send_message(
            chat_id=USER_ID,
            text=f"New request from someone\n\nBio: {user.first_name} - {user.id}\n\nRequest: \n{user_input}",
        )

        message = await context.bot.send_message(chat_id=chat.id,
                                                 text=f"<b>Request has been sent!</b>\n"
                                                      "Text of request:\n"
                                                      f"{user_input}\n\n\n"
                                                      "This message will be deleted after <b>2 minutes</b>",
                                                 parse_mode=ParseMode.HTML)
        await update.message.delete()
        job_queue.run_once(delete_message_by_id, 60, chat_id=chat.id, data=message.message_id)
        context.user_data['state'] = None
        return BACK_TO_MENU


async def delete_message_by_id(context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(chat_id=context.job.chat_id, message_id=context.job.data)
    except Exception as e:
        print(f"Error deleting message: {e}")


if __name__ == '__main__':
    bot = ApplicationBuilder().token(TOKEN).build()
    job_queue = bot.job_queue
    command_list = {"start": start, "accept": accept, "decline": decline}

    rd = RequestedData()

    for key in command_list:
        bot.add_handler(CommandHandler(key, command_list[key]))

    bot.add_handler(CallbackQueryHandler(menu, pattern="menu"))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, sent))
    bot.add_handler(CallbackQueryHandler(action, pattern='^(|lore|git|projects)$'))
    bot.add_handler(CallbackQueryHandler(request, pattern='request'))

    bot.add_handler(ConversationHandler(
        per_message=False,
        entry_points=[
            CallbackQueryHandler(request, pattern='request')],
        states={
            SENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, sent),
            ],
            BACK_TO_MENU: [
                CallbackQueryHandler(menu, pattern="menu")
            ]
        },
        fallbacks=[CommandHandler("error", error)],

    ))
    bot.run_polling()
