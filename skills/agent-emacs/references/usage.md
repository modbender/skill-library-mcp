# Usage Guide: Emacs-Agent Interaction

As an AI agent, you should not interact with this environment like a human. Your interface is the `emacsclient` socket.

## Essential Lisp Patterns for Agents

### 1. High-Speed Buffer Reading
Avoid reading from disk if a buffer exists. It contains the most recent, potentially unsaved state.
```elisp
(with-current-buffer "filename.ext" (buffer-string))
```

### 2. Precise Text Insertion
Use `goto-char` and `point` to manipulate text without full-file rewrites.
```elisp
(with-current-buffer "target.lisp" 
  (save-excursion
    (goto-char (point-max))
    (insert "\n(new-logic)")))
```

### 3. Remote Node Awareness (TRAMP)
When you need to work on a remote machine, do not use manual SSH tools. Use TRAMP paths.
- Local: `/root/file.txt`
- Remote: `/ssh:user@ip-address:/path/to/file.txt`

Once a remote file is opened, the connection is persistent in the daemon. You can run shell commands on that remote node using `(shell-command "...")` while in that buffer.

## Process Management
You can see all active background processes via `(list-processes)`. This is safer than `ps aux` because it shows processes owned by your living image.
