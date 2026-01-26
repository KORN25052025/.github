const fs = require("fs");
const p = "C:/Users/ahmet/Desktop/.github/adaptive-math-learning/backend/services/social_service.py";
const lines = [];
const rl = require("readline").createInterface({input: process.stdin});
rl.on("line", l => lines.push(l));
rl.on("close", () => { fs.writeFileSync(p, lines.join("
"), "utf8"); console.log("Done:", fs.statSync(p).size); });
