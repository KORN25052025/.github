const fs = require("fs");
const path = "C:\Users\ahmet\Desktop\.github\adaptive-math-learning\backend\services\spaced_repetition_service.py";
const content = fs.readFileSync("C:\Users\ahmet\Desktop\.github\_srs_content.txt", "utf8");
fs.writeFileSync(path, content, "utf8");
console.log("Written: " + content.length + " chars");