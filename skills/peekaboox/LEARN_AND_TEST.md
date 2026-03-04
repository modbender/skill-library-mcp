# Learn and Test the linux-desktop Skill

You have a new skill called `linux-desktop` that lets you control the Linux GUI. Work through each step below to learn how it works. Run all commands from the skill directory.

## Setup

```bash
export DISPLAY=:0
bash install.sh
```

## Test 1: See What's on Screen

Take a screenshot, then look at the image yourself to understand what's on screen:

```bash
SHOT=$(bash capture.sh | tail -1)
# Now read the image file at $SHOT using your vision to see the desktop
```

## Test 2: List Open Windows

```bash
bash inspect.sh
```

Pick a window from the list and get its details:

```bash
bash inspect.sh --window "<name from list>"
```

## Test 3: Click Something

Take a screenshot, look at it to find an element, then click it:

```bash
SHOT=$(bash capture.sh | tail -1)
# Look at the screenshot to find the clock in the panel
# Estimate its coordinates, then click:
bash click.sh --x <X> --y <Y>
```

## Test 4: Type and Use Hotkeys

Open a terminal and type into it:

```bash
bash window.sh --action focus --window "Terminal"
bash type.sh "echo hello from openclaw"
bash hotkey.sh "Return"
```

## Test 5: Window Management

```bash
bash window.sh --action maximize --window "Terminal"
bash capture.sh
bash window.sh --action minimize --window "Terminal"
```

## Test 6: Scroll

```bash
bash scroll.sh --direction down --amount 5
bash scroll.sh --direction up --amount 5
```

## Full Automated Run

Run the built-in test suite to verify everything works:

```bash
bash test.sh
```

If all tests pass, the skill is ready. You can now use it to automate any GUI task by following the capture-look-act-verify loop described in SKILL.md.
