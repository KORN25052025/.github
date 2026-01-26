const fs = require("fs");
const jp = "C:/Users/ahmet/Desktop/.github/adaptive-math-learning/backend/services/_pylines.json";
const existing = JSON.parse(fs.readFileSync(jp, "utf8"));
const newLines = JSON.parse(process.argv[2]);
const combined = existing.concat(newLines);
fs.writeFileSync(jp, JSON.stringify(combined), "utf8");
console.log("Total:", combined.length, "lines");