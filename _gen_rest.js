const fs = require("fs");
const p = require("path");
const target = p.join("C:", "Users", "ahmet", "Desktop", ".github", "adaptive-math-learning", "backend", "services", "enhanced_parent_teacher_service.py");
const q3 = '"""';

// Read the rest from a data file
const dataPath = p.join("C:", "Users", "ahmet", "Desktop", ".github", "_pydata.txt");
const data = fs.readFileSync(dataPath, "utf8");
fs.appendFileSync(target, data, "utf8");
console.log("Appended", data.length, "chars");