# Simple LaTeX presentation

The source file is `semester-3-simple.tex`. It uses the default Beamer style so the slides look like a student-prepared academic presentation rather than a designed template.

## Overleaf

1. Open https://www.overleaf.com/ and create a blank project.
2. Upload `semester-3-simple.tex`.
3. Set the compiler to `pdfLaTeX`.
4. Click **Compile**.
5. Read every slide and replace any sentence that does not sound like our own explanation.
6. Add only our own terminal screenshots if the faculty asks for a live demonstration record.

## Local compilation

On Ubuntu with TeX Live:

```bash
sudo apt install texlive-latex-recommended texlive-fonts-recommended
pdflatex semester-3-simple.tex
```

The output is a PDF. LaTeX Beamer normally creates PDF slides, which is the expected output for this workflow. We should not present the old AI-styled PPTX.

## Before submission

- Check all names, dates and supervisor details.
- Replace the measured values only if we rerun the experiment and save new evidence.
- Do not claim that the random source sequence is optimal.
- Explain that the current setup is a single-machine pseudo-distributed cluster and that true multi-node scaling is future work.
- Both Kumar and Archana should understand every slide and every command mentioned.
