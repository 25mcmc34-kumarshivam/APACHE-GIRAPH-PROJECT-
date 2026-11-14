import fs from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = fileURLToPath(new URL("./", import.meta.url));
const OUT = `${ROOT}semester-3-evaluation-2026.pptx`;
const PREVIEW = `${ROOT}preview/`;
await fs.mkdir(PREVIEW, { recursive: true });

const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const C = {
  navy: "#12304A", blue: "#1769AA", teal: "#0C7C86", orange: "#E87522",
  ink: "#17212B", muted: "#536273", pale: "#F4F7FA", white: "#FFFFFF",
  green: "#218739", red: "#B42318", line: "#D7E0E8",
};

function shape(slide, geometry, left, top, width, height, fill = "transparent", lineFill = "transparent") {
  for (const [label, value] of [["fill", fill], ["line", lineFill]]) {
    if (typeof value !== "string" || !(value === "transparent" || /^#[0-9A-Fa-f]{6,8}$/.test(value))) {
      console.log(`BAD SHAPE COLOR ${geometry} ${label}:`, value);
    }
  }
  // Artifact-tool treats line geometry as a stroke; keeping its fill transparent
  // avoids passing a fill colour to a line primitive.
  const actualFill = geometry === "line" ? "transparent" : fill;
  if (geometry === "line") {
    if (width < 0) { left += width; width = Math.abs(width); }
    if (height < 0) { top += height; height = Math.abs(height); }
  }
  return slide.shapes.add({ geometry, position: { left, top, width, height }, fill: actualFill, line: { style: "solid", fill: lineFill, width: lineFill === "transparent" ? 0 : 1 } });
}
function text(slide, value, left, top, width, height, size = 22, color = C.ink, bold = false, align = "left") {
  if (typeof color !== "string" || !(color === "transparent" || /^#[0-9A-Fa-f]{6,8}$/.test(color))) console.log("BAD TEXT COLOR", color, value);
  const fontSize = typeof size === "number" && Number.isFinite(size) ? size : 20;
  const s = shape(slide, "textbox", left, top, width, height);
  s.text = value;
  s.text.style = { fontSize: `${fontSize}px`, color, bold, alignment: align };
  return s;
}
function title(slide, heading, sub = "") {
  text(slide, heading, 64, 42, 1080, 58, 34, C.navy, true);
  shape(slide, "line", 64, 108, 1152, 1, C.orange, C.orange);
  if (sub) text(slide, sub, 66, 124, 1100, 32, 16, C.muted, false);
}
function footer(slide, n) {
  text(slide, "Apache Giraph project | MCA Semester III | Group A", 64, 684, 850, 20, 12, C.muted);
  text(slide, String(n).padStart(2, "0"), 1150, 684, 60, 20, 12, C.muted, true, "right");
}
function bullet(slide, value, yOrLeft, colorOrY = C.ink, sizeOrColor = 21, maybeSize, maybeWidth) {
  const customPosition = maybeSize !== undefined;
  const left = customPosition ? yOrLeft : 78;
  const y = customPosition ? colorOrY : yOrLeft;
  const color = customPosition ? sizeOrColor : colorOrY;
  const size = customPosition ? maybeSize : sizeOrColor;
  text(slide, "•", left, y, 22, 26, size, C.orange, true);
  text(slide, value, left + 28, y, maybeWidth ?? (customPosition ? 430 : 1070), 32, size, color);
}
function addSlide(heading, sub = "") {
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  title(slide, heading, sub);
  footer(slide, presentation.slides.items.length);
  return slide;
}

// 1. Cover
{
  const s = presentation.slides.add(); s.background.fill = C.navy;
  shape(s, "rect", 0, 0, 1280, 18, C.orange, C.orange);
  const coverBytes = await fs.readFile(`${ROOT}graph-network-cover.png`);
  s.images.add({ blob: coverBytes, contentType: "image/png", alt: "Distributed graph network illustration", fit: "cover", position: { left: 680, top: 44, width: 570, height: 600 } });
  text(s, "IMPLEMENTATION OF DISTRIBUTED GRAPH ALGORITHMS", 76, 116, 560, 48, 23, "#BFD8EA", true);
  text(s, "for Social Network Problems using Apache Giraph", 76, 178, 560, 110, 37, C.white, true);
  text(s, "Semester III academic project evaluation", 80, 318, 560, 38, 22, "#D9E7F2");
  text(s, "Kumar Shivam  |  Archana Kumari", 80, 402, 700, 36, 23, C.white, true);
  text(s, "MCA, School of Computer and Information Sciences\nUniversity of Hyderabad", 80, 452, 800, 66, 20, "#D9E7F2");
  text(s, "Supervisor: Dr. Anjeneya Swami Kare", 80, 590, 800, 32, 18, "#BFD8EA");
  text(s, "11 December 2026", 950, 620, 220, 28, 17, C.white, true, "right");
}

// 2. Problem definition
{
  const s = addSlide("Problem definition", "Why we started with a distributed graph-processing framework");
  bullet(s, "Social-network data is naturally represented as vertices and edges.", 190);
  bullet(s, "Large graphs make repeated, vertex-to-vertex computation difficult on a single ordinary program.", 240);
  bullet(s, "We needed a reproducible framework to load split graph files, execute vertex-centric algorithms, and verify results.", 290);
  bullet(s, "Our approved project problem is to implement distributed graph algorithms for social-network problems using Apache Giraph.", 340);
  shape(s, "roundRect", 86, 440, 1080, 132, "#EAF3FA", "#B9D5E8");
  text(s, "Research question for this semester", 112, 468, 400, 28, 18, C.blue, true);
  text(s, "Can we build, run, check and explain graph algorithms on a Hadoop/YARN/Giraph setup, from a tiny graph to a real large graph?", 112, 504, 1000, 62, 22, C.navy, true);
}

// 3. Aim and scope
{
  const s = addSlide("Aim and scope", "What we planned to establish in the first project phase");
  shape(s, "roundRect", 80, 180, 520, 350, "#F0F7FC", "#C7DDEA");
  text(s, "Aim", 112, 210, 420, 40, 28, C.blue, true);
  bullet(s, "Set up Apache Giraph on the lab server.", 112, 274, C.ink, 20, 430);
  bullet(s, "Understand vertex-centric computation.", 112, 328, C.ink, 20, 430);
  bullet(s, "Run baseline graph algorithms.", 112, 382, C.ink, 20, 430);
  bullet(s, "Implement and verify Graph Burning.", 112, 436, C.ink, 20, 430);
  shape(s, "roundRect", 680, 180, 520, 350, "#FFF6ED", "#F2D1B1");
  text(s, "Scope reached", 712, 210, 420, 40, 28, C.orange, true);
  bullet(s, "JSON and plain-text graph input.", 712, 274, C.ink, 20, 430);
  bullet(s, "Multiple HDFS input parts as one graph.", 712, 328, C.ink, 20, 430);
  bullet(s, "Python reference prediction.", 712, 382, C.ink, 20, 430);
  bullet(s, "Giraph verification up to 348,087 vertices.", 712, 436, C.ink, 20, 430);
}

// 4. Literature / existing work
{
  const s = addSlide("Literature and existing work", "Concepts that guided our implementation");
  const rows = [
    ["Pregel", "Vertex-centric graph processing model; computation proceeds in supersteps."],
    ["Apache Giraph", "Open-source Pregel-style framework integrated with Hadoop."],
    ["HDFS and YARN", "Distributed storage and resource management used by the lab execution."],
    ["Graph algorithms", "PageRank, degree, BFS and shortest paths provided baseline checks."],
    ["Graph Burning", "A supplied source sequence spreads through graph neighbourhoods over rounds."],
  ];
  rows.forEach((r, i) => {
    const y = 178 + i * 76;
    shape(s, "rect", 80, y, 245, 56, i % 2 ? "#F4F7FA" : "#EAF3FA", C.line);
    shape(s, "rect", 325, y, 875, 56, i % 2 ? "#F4F7FA" : C.white, C.line);
    text(s, r[0], 102, y + 15, 200, 25, 20, C.navy, true);
    text(s, r[1], 350, y + 13, 825, 32, 18, C.ink);
  });
  text(s, "Sources used: Apache Giraph documentation and repository study notes; see the References slide and GitHub study roadmap.", 82, 590, 1080, 28, 15, C.muted);
}

// 5. Semester progress
{
  const s = addSlide("Progress through the semester", "From environment setup to a verified large-graph run");
  const milestones = [
    ["Jul–Aug", "Understand project\nLinux, Java, Hadoop"],
    ["Aug–Sep", "Shared SSH server\nHDFS, YARN, Giraph build"],
    ["Sep", "PageRank, degree\nBFS, shortest path"],
    ["Sep–Oct", "Graph Burning\ninput-driven schedule"],
    ["Oct–Nov", "Python preview\n348k Giraph verification"],
  ];
  shape(s, "line", 130, 350, 1010, 1, C.blue, C.blue);
  milestones.forEach((m, i) => {
    const x = 110 + i * 230;
    shape(s, "ellipse", x, 326, 48, 48, i === 4 ? C.orange : C.blue, i === 4 ? C.orange : C.blue);
    text(s, m[0], x - 50, 246, 140, 28, 16, C.navy, true, "center");
    text(s, m[1], x - 70, 400, 190, 58, 17, C.ink, false, "center");
  });
  shape(s, "roundRect", 160, 535, 960, 62, "#EEF8F0", "#C5E1CA");
  text(s, "Semester outcome: a repeatable Python-to-Giraph workflow with saved evidence and exact output comparison.", 190, 552, 900, 28, 20, C.green, true, "center");
}

// 6. Architecture
{
  const s = addSlide("System architecture", "How a graph moves from our laptop to Giraph");
  const boxes = [
    ["Input parts", "part-01.txt … part-N.txt", 80, 260, C.blue],
    ["HDFS", "logical input directory", 350, 260, C.teal],
    ["YARN", "ResourceManager + NodeManager", 620, 260, C.orange],
    ["Giraph", "vertex-centric supersteps", 890, 260, C.green],
    ["Result", "B/NB + first burn round", 890, 490, C.navy],
  ];
  boxes.forEach(b => { shape(s, "roundRect", b[2], b[3], 220, 105, "#F7FAFC", b[4]); text(s, b[0], b[2]+18, b[3]+20, 185, 28, 22, b[4], true, "center"); text(s, b[1], b[2]+18, b[3]+58, 185, 32, 15, C.ink, false, "center"); });
  [[300,312,350,312],[570,312,620,312],[840,312,890,312],[1000,365,1000,490]].forEach(a => shape(s, "line", a[0], a[1], a[2]-a[0], a[3]-a[1], C.muted, C.muted));
  text(s, "The two-account arrangement is operational: hduser runs Hadoop services; mca2025 builds Giraph and submits experiments.", 100, 620, 1080, 30, 18, C.muted, false, "center");
}

// 7. Baseline algorithms
{
  const s = addSlide("Baseline graph algorithms", "We built confidence on small graphs before Graph Burning");
  const algos = [
    ["PageRank", "importance score from incoming links"],
    ["In-degree", "number of incoming edges"],
    ["Out-degree", "number of outgoing edges"],
    ["BFS", "fewest-edge distance from a source"],
    ["Shortest path", "lowest total weight from a source"],
  ];
  algos.forEach((a, i) => {
    const y = 172 + i * 72;
    shape(s, "rect", 100, y, 260, 52, i % 2 ? "#F4F7FA" : "#EAF3FA", C.line);
    text(s, a[0], 122, y + 13, 220, 25, 20, C.navy, true);
    text(s, a[1], 420, y + 12, 680, 28, 19, C.ink);
  });
  shape(s, "roundRect", 100, 545, 1050, 66, "#FFF6ED", "#F2D1B1");
  text(s, "Key takeaway: these baseline jobs taught us the input format, HDFS paths, YARN execution, supersteps and output interpretation.", 130, 559, 990, 42, 17, C.orange, true, "center");
}

// 8. Burning model
{
  const s = addSlide("Graph Burning model", "The current implementation evaluates a supplied schedule");
  text(s, "Example source sequence", 90, 178, 330, 28, 18, C.muted, true);
  text(s, "3 : 8 : 6", 90, 218, 360, 72, 45, C.orange, true);
  text(s, "Round 1", 520, 180, 160, 26, 18, C.blue, true, "center");
  text(s, "Round 2", 720, 180, 160, 26, 18, C.teal, true, "center");
  text(s, "Round 3", 920, 180, 160, 26, 18, C.green, true, "center");
  [520,720,920].forEach((x,i)=>{ shape(s,"ellipse",x,245,70,70,[C.blue,C.teal,C.green][i],[C.blue,C.teal,C.green][i]); text(s,["3","8","6"][i],x,264,70,30,24,C.white,true,"center"); });
  shape(s, "line", 590, 280, 130, 1, C.muted, C.muted); shape(s, "line", 790, 280, 130, 1, C.muted, C.muted);
  bullet(s, "The source for a round ignites in that round.", 380, C.ink, 20);
  bullet(s, "Existing fire spreads one hop per round.", 430, C.ink, 20);
  bullet(s, "Each vertex records its first burn round.", 480, C.ink, 20);
  bullet(s, "NB -1 means the vertex stayed unburned within the configured rounds.", 530, C.ink, 20);
}

// 9. Data pipeline
{
  const s = addSlide("Input, prediction and verification", "The same scheduled graph goes through two implementations");
  const steps = [
    ["1", "Graph parts", "plain text adjacency"],
    ["2", "Schedule", "source round in each line"],
    ["3", "Python", "expected.tsv + round files"],
    ["4", "Giraph", "HDFS/YARN execution"],
    ["5", "Compare", "cmp exit code 0"],
  ];
  steps.forEach((st,i)=>{
    const x = 74 + i*232;
    shape(s,"roundRect",x,255,190,150,"#F7FAFC",i===4?C.green:C.line);
    shape(s,"ellipse",x+70,215,50,50,i===4?C.green:C.blue,i===4?C.green:C.blue);
    text(s,st[0],x+70,226,50,24,20,C.white,true,"center");
    text(s,st[1],x+18,286,154,28,20,C.navy,true,"center");
    text(s,st[2],x+18,330,154,42,16,C.ink,false,"center");
    if(i<4) shape(s,"line",x+190,330,42,1,C.muted,C.muted);
  });
  text(s, "Python is the independent reference calculation. Giraph is the distributed implementation being checked.", 130, 520, 1020, 34, 22, C.navy, true, "center");
}

// 10. Results table
{
  const s = addSlide("Experiments completed", "Growth from teaching graphs to a real Web-Google subgraph");
  const rows = [
    ["9-node path", "9", "3", "All rows match"],
    ["30-node graph", "30", "4", "All rows match"],
    ["120-node grid", "120", "8", "119 B, 1 NB"],
    ["Web-Google sample", "9,625", "6", "131 B, 9,494 NB"],
    ["Web-Google sample", "348,087", "8", "243,095 B, 104,992 NB"],
  ];
  const heads=["Experiment","Vertices","Rounds","Verified result"];
  const widths=[350,160,160,450];
  let x=70; heads.forEach((h,i)=>{shape(s,"rect",x,160,widths[i],50,C.navy,C.navy);text(s,h,x+10,175,widths[i]-20,22,17,C.white,true,"center");x+=widths[i];});
    rows.forEach((r,j)=>{let x=70; r.forEach((v,i)=>{shape(s,"rect",x,210+j*58,widths[i],58,j%2?"#F4F7FA":C.white,C.line);text(s,v,x+10,228+j*58,widths[i]-20,25,17,C.ink,i===0);x+=widths[i];});});
  text(s,"All claims above refer to saved inputs, outputs and comparison evidence in the repository.",80,560,1100,28,16,C.muted,false,"center");
}

// 11. Large result
{
  const s = addSlide("348,087-vertex verification", "Largest successful Graph Burning run completed this semester");
  const vals = [243095,104992];
  // Keep the quantitative comparison editable and robust across PowerPoint
  // viewers by drawing two native bars with their exact values as labels.
  const chartLeft = 140, chartBottom = 520, chartHeight = 300, chartWidth = 420;
  const maxVal = Math.max(...vals);
  ["Burned", "Unburned"].forEach((label, i) => {
    const barH = chartHeight * vals[i] / maxVal;
    const x = chartLeft + i * 250;
    shape(s, "rect", x, chartBottom - barH, 100, barH, C.blue, C.blue);
    text(s, String(vals[i]), x - 20, chartBottom - barH - 28, 140, 22, 14, C.muted, false, "center");
    text(s, label, x - 35, chartBottom + 12, 170, 24, 16, C.muted, false, "center");
  });
  [0, 0.25, 0.5, 0.75, 1].forEach((fraction) => {
    const y = chartBottom - chartHeight * fraction;
    shape(s, "line", chartLeft - 20, y, chartWidth + 20, 1, C.line, C.line);
  });
  shape(s,"roundRect",730,188,430,322,"#F0F7FC","#C7DDEA");
  text(s,"Measured configuration",760,218,350,28,20,C.blue,true);
  bullet(s,"348,087 vertices",760,274,C.ink,19,350);
  bullet(s,"1,128,693 undirected connections",760,320,C.ink,19,350);
  bullet(s,"8 random eligible source rounds",760,366,C.ink,19,350);
  text(s,"Python and Giraph produced 348,087 identical rows.",760,438,350,50,20,C.green,true);
  text(s,"Source selection was a reproducible baseline, not an optimization result.",90,590,1080,28,18,C.muted,false,"center");
}

// 12. Verification and runtime
{
  const s = addSlide("Verification and runtime", "What we can defend in front of the panel");
  shape(s,"roundRect",90,180,500,330,"#EEF8F0","#C5E1CA");
  text(s,"Correctness check",120,215,420,35,26,C.green,true);
  text(s,"Python expected rows",130,285,300,25,19,C.ink); text(s,"348,087",440,285,110,25,21,C.navy,true,"right");
  text(s,"Giraph actual rows",130,335,300,25,19,C.ink); text(s,"348,087",440,335,110,25,21,C.navy,true,"right");
  text(s,"Comparison",130,385,300,25,19,C.ink); text(s,"exit code 0",410,385,140,25,21,C.green,true,"right");
  text(s,"Burned / unburned",130,435,300,25,19,C.ink); text(s,"243,095 / 104,992",370,435,180,25,18,C.navy,true,"right");
  shape(s,"roundRect",660,180,500,330,"#FFF6ED","#F2D1B1");
  text(s,"Timing",690,215,420,35,26,C.orange,true);
  text(s,"Python preview",700,285,260,25,19,C.ink); text(s,"about 20 min",1010,285,120,25,21,C.orange,true,"right");
  text(s,"Giraph run (real)",700,345,260,25,19,C.ink); text(s,"54.887 s",1010,345,120,25,21,C.green,true,"right");
  text(s,"Why different?",700,405,360,25,19,C.ink); text(s,"Python wrote every round table",700,445,390,26,17,C.muted);
}

// 13. Contributions
{
  const s = addSlide("Our contribution", "Group A: Kumar Shivam and Archana Kumari");
  shape(s,"roundRect",90,180,490,360,"#EAF3FA","#B9D5E8");
  text(s,"Kumar Shivam",125,218,420,35,27,C.blue,true);
  bullet(s,"Shared-server access, Hadoop/YARN checks and Giraph builds.",125,290,C.ink,19,420);
  bullet(s,"Input-driven Graph Burning Java integration and runners.",125,348,C.ink,19,420);
  bullet(s,"Large-graph conversion, HDFS upload and measured jobs.",125,406,C.ink,19,420);
  bullet(s,"Repository, weekly evidence and reproducibility record.",125,464,C.ink,19,420);
  shape(s,"roundRect",700,180,490,360,"#FFF6ED","#F2D1B1");
  text(s,"Archana Kumari",735,218,420,35,27,C.orange,true);
  bullet(s,"Shared study of graph models and distributed processing.",735,290,C.ink,19,410);
  bullet(s,"Review and understanding of algorithms and outputs.",735,348,C.ink,19,410);
  bullet(s,"Presentation preparation and explanation of the workflow.",735,406,C.ink,19,410);
  bullet(s,"Joint validation of the project direction and results.",735,464,C.ink,19,410);
}

// 14. Demo
{
  const s = addSlide("Demonstration plan", "A short, reliable demo for the panel");
  const steps = ["Show scheduled input parts", "Run validator", "Show YARN node", "Run Giraph runner", "Display B/NB output", "Compare with Python"];
  steps.forEach((v,i)=>{const y=175+i*62;shape(s,"ellipse",90,y,38,38,i===5?C.green:C.blue,i===5?C.green:C.blue);text(s,String(i+1),90,y+8,38,20,16,C.white,true,"center");text(s,v,155,y+5,700,28,22,C.ink,i===5);});
  shape(s,"roundRect",830,210,330,230,"#F4F7FA",C.line);
  text(s,"Demo evidence",865,240,260,30,22,C.navy,true);
  text(s,"• HDFS input path\n• RUNNING YARN node\n• Giraph output path\n• comparison exit code 0",865,300,260,110,19,C.ink);
  text(s,"If network or YARN fails, use saved repository evidence instead of improvising.",110,590,1060,28,18,C.muted,false,"center");
}

// 15. Conclusion and future
{
  const s = addSlide("Conclusion and future work", "What this semester established");
  text(s,"Completed",100,180,430,32,25,C.green,true);
  bullet(s,"Built and operated a reproducible Giraph/Hadoop workflow.",100,236,C.ink,20,500);
  bullet(s,"Implemented and explained baseline graph algorithms.",100,288,C.ink,20,500);
  bullet(s,"Implemented Graph Burning with scheduled input rounds.",100,340,C.ink,20,500);
  bullet(s,"Verified Python predictions against Giraph at 348k vertices.",100,392,C.ink,20,500);
  text(s,"Next phase",690,180,430,32,25,C.orange,true);
  bullet(s,"Confirm the faculty-approved burning model and constraints.",690,236,C.ink,20,470);
  bullet(s,"Study larger graphs and true multi-node execution.",690,288,C.ink,20,470);
  bullet(s,"Compare source-selection strategies and optimization methods.",690,340,C.ink,20,470);
  bullet(s,"Extend the Group A implementation after the faculty review.",690,392,C.ink,20,470);
  shape(s,"roundRect",170,520,940,65,"#EAF3FA","#B9D5E8");
  text(s,"Our current result is a verified foundation, not the final optimization study.",200,540,880,28,21,C.navy,true,"center");
}

// 16. References
{
  const s = addSlide("References and evidence", "All evidence is maintained in the project repository");
  const refs = [
    "Apache Giraph: https://giraph.apache.org/",
    "Apache Hadoop: https://hadoop.apache.org/",
    "Stanford SNAP datasets: https://snap.stanford.edu/data/",
    "Project repository: https://github.com/25mcmc34-kumarshivam/APACHE-GIRAPH-PROJECT-",
    "Week reports, source code, datasets and result comparisons are linked from the repository README.",
  ];
  refs.forEach((r,i)=>bullet(s,r,190+i*62,C.ink,19));
  shape(s,"roundRect",110,535,820,62,"#F4F7FA",C.line);
  text(s,"Thank you\nQuestions and discussion",145,548,750,42,22,C.navy,true,"center");
  text(s,"Scan for the repository",982,505,190,24,15,C.muted,true,"center");
  const qrBytes = await fs.readFile(`${ROOT}repo-qr.png`);
  s.images.add({ blob: qrBytes, contentType: "image/png", alt: "QR code linking to the project repository", position: { left: 1015, top: 530, width: 110, height: 110 } });
}

for (const [i, slide] of presentation.slides.items.entries()) {
  console.log(`Rendering slide ${i + 1}`);
  const png = await presentation.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(`${PREVIEW}slide-${String(i + 1).padStart(2, "0")}.png`, new Uint8Array(await png.arrayBuffer()));
}
const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(OUT);
console.log(`Wrote ${OUT}`);
