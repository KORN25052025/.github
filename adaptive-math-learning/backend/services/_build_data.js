const fs = require("fs");
const dataFile = "C:/Users/ahmet/Desktop/.github/adaptive-math-learning/backend/services/_data.json";

// Read existing partial data if any
let lines = [];
try { lines = JSON.parse(fs.readFileSync(dataFile, "utf8")); } catch(e) {}

// Append new lines from stdin or args
const newLines = JSON.parse(process.argv[2] || "[]");
lines = lines.concat(newLines);
fs.writeFileSync(dataFile, JSON.stringify(lines), "utf8");
console.log("Total lines:", lines.length);