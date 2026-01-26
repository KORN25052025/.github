const fs = require("fs");
const p = require("path");
const target = p.join("C:", "Users", "ahmet", "Desktop", ".github", "adaptive-math-learning", "backend", "services", "spaced_repetition_service.py");
const contentPath = p.join("C:", "Users", "ahmet", "Desktop", ".github", "_srs_content.b64");
const b64 = fs.readFileSync(contentPath, "utf8");
const content = Buffer.from(b64, "base64").toString("utf8");
fs.writeFileSync(target, content, "utf8");
console.log("Written " + content.length + " chars to " + target);