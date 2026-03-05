# LaTeX Templates Reference

## Document Shell

```latex
\documentclass[12pt]{article}
\usepackage[margin=1in, top=0.75in, bottom=0.75in]{geometry}
\usepackage{amsmath, amssymb, tikz, pgfplots, enumitem, fancyhdr, multicol, array, booktabs}
\pgfplotsset{compat=1.18}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\textbf{TOPIC Practice}}
\fancyhead[R]{\small Name: \underline{\hspace{4.5cm}}~Date: \underline{\hspace{1.8cm}}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

\newcounter{prob}
\newcommand{\problem}[1]{\stepcounter{prob}\vspace{0.4cm}\noindent\textbf{\large\theprob.}\quad #1\vspace{0.3cm}}

\begin{document}
\begin{center}
  {\LARGE\textbf{TOPIC Practice Worksheet}}\\[0.3cm]
  {\large COURSE \quad $\bullet$ \quad DATE}
\end{center}
\noindent\rule{\linewidth}{0.4pt}\vspace{0.2cm}

% [problems here]

\end{document}
```

## Problem Patterns

### Simple algebraic problem
```latex
\problem{Solve for $x$: \quad $2x^2 - 5x - 3 = 0$}
\vspace{6cm}
```

### Two-column layout (shorter problems)
```latex
\begin{multicols}{2}
\begin{enumerate}[label=\textbf{\arabic*.}, itemsep=4cm]
  \item $3x + 7 = 22$
  \item $-2(x - 5) = 14$
  \item $\dfrac{x}{4} + 3 = 9$
  \item $5x - 3 = 2x + 9$
\end{enumerate}
\end{multicols}
```

### Multi-part problem
```latex
\problem{Given $f(x) = 3x^2 - 2x + 1$, find:}
\begin{enumerate}[label=(\alph*), itemsep=3cm, leftmargin=1.5cm]
  \item $f(0)$
  \item $f(-2)$
  \item $f(x+1)$ — expand and simplify
  \vspace{2cm}
\end{enumerate}
```

### Function table
```latex
\problem{Complete the table for $y = 3x - 2$.}
\vspace{0.3cm}
\begin{center}
\begin{tabular}{|>{\centering\arraybackslash}m{1.5cm}|>{\centering\arraybackslash}m{1.5cm}|}
\hline
\textbf{$x$} & \textbf{$y$} \\
\hline
$-2$ & \rule{1.2cm}{0pt} \\[0.5cm]\hline
$0$  & \\[0.5cm]\hline
$1$  & \\[0.5cm]\hline
$3$  & \\[0.5cm]\hline
\end{tabular}
\end{center}
\vspace{1cm}
```

## Coordinate Planes

### Blank grid (student fills in — algebraic range)
```latex
\begin{center}
\begin{tikzpicture}
\begin{axis}[
    axis lines=center, xmin=-6, xmax=6, ymin=-6, ymax=6,
    xtick={-6,-4,...,6}, ytick={-6,-4,...,6},
    grid=both,
    grid style={line width=0.15pt, draw=gray!30},
    major grid style={line width=0.3pt, draw=gray!50},
    tick label style={font=\small},
    xlabel={$x$}, ylabel={$y$},
    width=9cm, height=9cm, enlargelimits=false
]
\end{axis}
\end{tikzpicture}
\end{center}
```

### Blank grid (full −10 to 10, Pre-Algebra style)
```latex
\begin{axis}[
    axis lines=center, xmin=-10, xmax=10, ymin=-10, ymax=10,
    xtick={-10,-8,...,10}, ytick={-10,-8,...,10},
    minor tick num=1, grid=both,
    grid style={line width=0.12pt, draw=gray!20},
    major grid style={line width=0.3pt, draw=gray!50},
    tick label style={font=\scriptsize},
    xlabel={$x$}, ylabel={$y$}, width=9cm, height=9cm
]
\end{axis}
```

### Completed graph (answer key — plot a function)
```latex
\addplot[blue, thick, domain=-1:5, samples=100] {x^2 - 4*x + 3};
\addplot[only marks, mark=*, mark size=2.5pt, red] coordinates {(1,0)(3,0)};   % x-intercepts
\addplot[only marks, mark=diamond*, mark size=3pt, green!60!black] coordinates {(2,-1)};  % vertex
\draw[dashed, gray] (axis cs:2,-6) -- (axis cs:2,8) node[above] {$x=2$};
```

## Geometric Figures

### Right triangle
```latex
\begin{center}
\begin{tikzpicture}[scale=1.2]
  \coordinate (A) at (0,0);
  \coordinate (B) at (4,0);
  \coordinate (C) at (4,3);
  \draw[thick] (A) -- (B) -- (C) -- cycle;
  \draw (B) ++(-.25,0) -- ++(0,.25) -- ++(.25,0);  % right angle mark
  \node[below left] at (A) {$A$};
  \node[below right] at (B) {$B$};
  \node[above right] at (C) {$C$};
  \node[below] at (2,0) {$8$};
  \node[right] at (4,1.5) {$6$};
  \node[above left] at (2,1.5) {$x$};
\end{tikzpicture}
\end{center}
```

## Answer Key Patterns

### Answer key document header
```latex
\fancyhead[L]{\textbf{TOPIC — Answer Key}}
\fancyhead[R]{\textit{For instructor/parent use}}
```

### Step-by-step solution
```latex
\problem{[Repeat full problem statement]}

\textbf{Solution:}
\begin{align*}
  2x^2 - 5x - 3 &= 0 \\
  \intertext{Factor — find factors of $2(-3)=-6$ summing to $-5$: use $-6,+1$:}
  2x^2 - 6x + x - 3 &= 0 \\
  2x(x - 3) + 1(x - 3) &= 0 \\
  (2x + 1)(x - 3) &= 0 \\
  \intertext{Zero product property:}
  2x + 1 = 0 \quad &\text{or} \quad x - 3 = 0 \\
\end{align*}
\[ \boxed{x = -\tfrac{1}{2} \quad \text{or} \quad x = 3} \]

\vspace{0.3cm}\noindent\rule{\linewidth}{0.2pt}\vspace{0.3cm}
```

### Sign chart (for polynomial graphing)
```latex
\[
\underbrace{+}_{x<-2}\ \Bigl|_{-2}\ \underbrace{-}_{-2<x<0}\ \Bigl|_{0}\ \underbrace{-}_{0<x<2}\ \Bigl|_{2}\ \underbrace{+}_{x>2}
\]
```

---

## Skills Summary / Study Guide Template

This is the **third document** generated alongside every worksheet. It's a one-to-two page reference card the student can use while working or studying.

### Document shell

```latex
\documentclass[12pt]{article}
\usepackage[margin=0.85in, top=0.7in, bottom=0.7in]{geometry}
\usepackage{amsmath, amssymb, tikz, enumitem, fancyhdr, multicol, mdframed, xcolor}

% Color palette
\definecolor{skillblue}{RGB}{30,100,180}
\definecolor{skillbluebg}{RGB}{235,244,255}
\definecolor{warnorange}{RGB}{200,90,0}
\definecolor{warnbg}{RGB}{255,243,230}
\definecolor{exgreen}{RGB}{20,120,60}
\definecolor{exgreenbg}{RGB}{230,248,238}

% Formula/rule box
\newmdenv[
  backgroundcolor=skillbluebg,
  linecolor=skillblue, linewidth=1.5pt,
  innertopmargin=6pt, innerbottommargin=6pt,
  innerleftmargin=10pt, innerrightmargin=10pt,
  skipabove=6pt, skipbelow=4pt
]{formulabox}

% Mini example box
\newmdenv[
  backgroundcolor=exgreenbg,
  linecolor=exgreen, linewidth=1pt,
  innertopmargin=5pt, innerbottommargin=5pt,
  innerleftmargin=10pt, innerrightmargin=10pt,
  skipabove=4pt, skipbelow=4pt
]{examplebox}

% Watch-out box
\newmdenv[
  backgroundcolor=warnbg,
  linecolor=warnorange, linewidth=1pt,
  innertopmargin=5pt, innerbottommargin=5pt,
  innerleftmargin=10pt, innerrightmargin=10pt,
  skipabove=4pt, skipbelow=4pt
]{watchoutbox}

% Skill section heading
\newcommand{\skillheading}[1]{%
  \vspace{0.4cm}
  {\large\textbf{\textcolor{skillblue}{#1}}}
  \vspace{0.1cm}
  \hrule height 1pt
  \vspace{0.2cm}
}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\textbf{Skills Summary: TOPIC}}
\fancyhead[R]{\small\textit{Study Guide \& Reference}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

\begin{document}

\begin{center}
  {\LARGE\textbf{Skills Summary}}\\[0.2cm]
  {\large\textbf{TOPIC}}\\[0.1cm]
  {\small\textit{Use this reference while completing your worksheet or when studying.}}
\end{center}
\vspace{0.1cm}
\noindent\rule{\linewidth}{1.5pt}
\vspace{0.3cm}

% =================== SKILL 1 ===================
\skillheading{Skill 1 Name — e.g. Factoring Trinomials (a = 1)}

\begin{formulabox}
\textbf{Rule / Formula:}\\[4pt]
$x^2 + bx + c = (x + p)(x + q)$ \quad where $p + q = b$ and $p \cdot q = c$
\end{formulabox}

\vspace{0.2cm}

\begin{examplebox}
\textbf{Example:} \quad Factor $x^2 - 7x + 12$\\[4pt]
Find two numbers that \textit{add to} $-7$ and \textit{multiply to} $12$: \quad $-3$ and $-4$ ✓\\[2pt]
$\Rightarrow\quad x^2 - 7x + 12 = \boldsymbol{(x-3)(x-4)}$
\end{examplebox}

\vspace{0.2cm}

\begin{watchoutbox}
\textbf{⚠ Watch out:} Signs matter! If $c > 0$, both factors have the \textit{same sign} as $b$.\par
If $c < 0$, the factors have \textit{opposite signs}.
\end{watchoutbox}

% =================== SKILL 2 ===================
\skillheading{Skill 2 Name — e.g. Quadratic Formula}

\begin{formulabox}
\textbf{Formula:}\\[4pt]
\[
  x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
\]
\textbf{Discriminant:}\quad $\Delta = b^2 - 4ac$\par
\begin{itemize}[leftmargin=1.5cm, itemsep=1pt, topsep=2pt]
  \item $\Delta > 0$: two real solutions
  \item $\Delta = 0$: one real solution (double root)
  \item $\Delta < 0$: no real solutions (complex roots)
\end{itemize}
\end{formulabox}

\vspace{0.2cm}

\begin{examplebox}
\textbf{Example:} \quad Solve $2x^2 - 3x - 5 = 0$\\[4pt]
$a = 2,\ b = -3,\ c = -5$\quad $\Delta = 9 + 40 = 49$\\[2pt]
$x = \dfrac{3 \pm 7}{4}$\quad $\Rightarrow\quad\boldsymbol{x = \tfrac{10}{4} = \tfrac{5}{2}}$ \quad or \quad $\boldsymbol{x = \tfrac{-4}{4} = -1}$
\end{examplebox}

% =================== KEY VOCABULARY ===================
\vspace{0.3cm}
\skillheading{Key Vocabulary}

\begin{multicols}{2}
\begin{description}[leftmargin=0.5cm, itemsep=2pt, font=\normalfont\bfseries]
  \item[Term 1:] Definition here
  \item[Term 2:] Definition here
  \item[Term 3:] Definition here
  \item[Term 4:] Definition here
\end{description}
\end{multicols}

\end{document}
```

### Usage guidance

- Generate **one skill section per distinct skill** tested in the worksheet (typically 2–5 sections)
- Each section should have: a formula/rule box + 1 mini example + optional watch-out
- Keep the whole document to **1–2 pages max** — it's a reference card, not a lesson
- Vocabulary section is optional — include only when there are ≥3 important terms
- The mini examples should be **shorter and simpler** than the worksheet problems, to illustrate the pattern without being distracting
- The watch-out box is optional per skill — only add if there's a genuinely common mistake worth flagging
