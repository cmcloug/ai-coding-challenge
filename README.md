# Technical Challenge: Getting Started and Submitting

Read `START_HERE_STUDENT_INSTRUCTIONS.md` for the challenge itself. This page covers
the git side: how to get your own copy and how to hand in your work.

## Before the session

1. Make sure **git** and **Python 3.9 or newer** are installed on your laptop.
   Check with `git --version` and `python --version` (or `python3 --version`).
2. **Accept the collaborator invitation** you received from the facilitator on
   GitHub (check your email or the bell icon on github.com). Invitations expire
   after 7 days, so do this early. This only gives you read access to the starter
   materials. You cannot see anyone else's work.

## At the start of the session

### 1. Create your own private copy

1. Open the template repository the facilitator shared with you.
2. Click the green **Use this template** button, then **Create a new repository**.
3. Set **Owner** to your own account.
4. Name it `ai-challenge-<your-github-username>`.
5. Choose **Private**. This matters. Do not make it public.
6. Click **Create repository**.

### 2. Clone it and start working

```
git clone https://github.com/<your-username>/ai-challenge-<your-username>.git
cd ai-challenge-<your-username>
```

Pick your track and open its folder. Follow that folder's README or brief.

## While you work

- **Commit early and often** with short messages, for example
  `Fix list_tasks filter` or `Normalize region labels`. Your commit history shows
  your process, and that is part of what we look at.
- Add a file called `PROMPT_LOG.md` in the top folder. Paste in your AI prompts, or
  a link to your conversation. Rough notes are fine.
- Copy `REFLECTION_TEMPLATE.md` to `REFLECTION.md` and fill it in during the last
  10 minutes.

Suggested commands:

```
git add .
git commit -m "Describe what you changed"
git push
```

## Submitting

Do these in the last 10 minutes of work time:

1. Make sure your final work, `PROMPT_LOG.md`, and `REFLECTION.md` are committed and
   pushed. Open your repo on github.com and confirm you can see them.
2. On your repo page go to **Settings, then Collaborators, then Add people**, and
   add the facilitator's GitHub username (they will tell you what it is).
3. Send the facilitator your repo URL (in the chat they point you to).

Anything pushed after the work period ends will not be reviewed.

## Having trouble with git?

Tell the facilitator right away. If git is the blocker, you can zip your folder and
hand it in that way. Fighting with git is not what we are testing.

## Please keep this private

Do not make your repo public, post the materials elsewhere, or share your solutions
with others. The same challenge may be used again.
