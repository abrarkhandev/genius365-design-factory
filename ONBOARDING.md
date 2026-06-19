# Getting the Design Factory on your computer

This installs all the design profiles (landing pages, Business Information Packs,
LinkedIn banners + carousels, magazines, and more) so they appear in your **Hermes
desktop app**. It takes about 5-10 minutes, once.

---

## Before you start (you probably already have these)
You need three things working. If you already use Hermes day-to-day, you have the first two.

1. **Hermes** — open a terminal and type `hermes --version`. If it shows a number, you're good.
   If not, install it from **hermes-agent.nousresearch.com**.
2. **Your OpenAI sign-in in Hermes** — the profiles run on the OpenAI/Codex setup you already use.
3. **Git** — type `git --version`. If it shows a number, good.
   If it says "not recognized" (Windows), install **Git for Windows** from **git-scm.com**
   (download, run the installer, click Next through it), then reopen your terminal.

---

## Windows (most of the team)

1. Open **PowerShell** (Start menu -> type "PowerShell" -> Enter).
2. Run these **one line at a time** (press Enter after each — do not paste both together):
   ```
   git clone https://github.com/abrarkhandev/genius365-design-factory
   ```
   ```
   cd genius365-design-factory
   ```
3. Install the profiles: **double-click `sync.bat`** inside the new `genius365-design-factory`
   folder (in File Explorer) — or type `.\sync.bat` and press Enter. Let it finish.
4. **Done.** Open your **Hermes desktop app** — the design profiles now appear in the list.
   Pick one (e.g. *landing-page-studio*) and start.

---

## Mac

1. Open **Terminal**.
2. Run:
   ```
   git clone https://github.com/abrarkhandev/genius365-design-factory
   cd genius365-design-factory && ./sync.sh
   ```
3. Open your Hermes desktop app — the profiles appear.

---

## Check it worked
In the desktop app, open **landing-page-studio** and type *"say hello in one line."*
It should reply. (Or in the terminal: `landing-page-studio -z "say hello"`.)

---

## When there is an update
Someone will tell you to update. Then, in the `genius365-design-factory` folder:
- **Windows:** run `git pull`, then double-click `sync.bat` again.
- **Mac:** run `git pull`, then `./sync.sh`.

Your own chats, settings and keys are never touched — only the design profiles refresh.

---

## If something goes wrong
- **"The token '&&' is not a valid statement separator"** -> you pasted two commands on one
  line. Run them **one line at a time**.
- **"running scripts is disabled on this system"** -> use **`sync.bat`** (not `sync.ps1`
  directly). Or run: `powershell -ExecutionPolicy Bypass -File .\sync.ps1`
- **"git is not recognized"** -> install **Git for Windows** (git-scm.com) and reopen PowerShell.
- **Image generation asks for a key** -> add a line `OPENAI_API_KEY=your-key-here` to the file
  `~/.hermes/.env`. (Text/design profiles work without this; only image generation needs it.)

Stuck? Send a screenshot of the error to the team channel.
