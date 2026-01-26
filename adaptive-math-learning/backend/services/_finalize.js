const fs = require("fs");
const jp = "C:/Users/ahmet/Desktop/.github/adaptive-math-learning/backend/services/_pylines.json";
const tp = "C:/Users/ahmet/Desktop/.github/adaptive-math-learning/backend/services/accessibility_service.py";
const lines = JSON.parse(fs.readFileSync(jp, "utf8"));
fs.writeFileSync(tp, lines.join("
"), "utf8");
console.log("Written", lines.length, "lines,", lines.join("
").length, "chars");