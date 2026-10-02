# Track 2: Code Review Template

An AI assistant wrote `order_utils.py`. It runs, it has docstrings, and it looks
professional. Your job is to review it the way you would review a teammate's pull
request before it ships to production.

**Run it first:** `python order_utils.py`

Use any tools you like, including AI. Make a note of what you used and how.

---

## Part 1: Findings

Copy the block below once per issue you find. Aim for quality over quantity.
A clearly explained issue is worth more than a vague one.

```
### Issue #
Function / line:
What is wrong:
Why it matters (what could actually happen):
Severity (Critical / High / Medium / Low):
How I verified it (ran code, wrote a test, read docs, etc.):
Suggested fix (a code snippet is welcome):
```

---

## Part 2: Fix at least two

Pick the **two issues you think matter most** and fix them directly in
`order_utils.py`. For each, write one or two sentences on why you chose it.

---

## Part 3: Verify your fixes

Show proof that your fixes work. A short script, a few asserts, or a pasted
terminal output all count.

---

## Part 4: Your summary for the team (3 to 5 sentences)

Imagine you are telling your team lead whether this code is ready to merge.
What is your recommendation, and what are your top concerns?

---

## Part 5: AI reflection

1. Which AI tool(s) did you use, and for what?
2. Did the AI miss anything, or say something that turned out to be wrong?
3. How did you decide whether to trust its feedback?
4. Which issue did you find without AI help?
