const fs = require("fs");
const t = "C:/Users/ahmet/Desktop/.github/adaptive-math-learning/backend/services/accessibility_service.py";
let py = fs.readFileSync(t, "utf8");

py += String.fromCharCode(10,10);
py += "# ---------------------------------------------------------------------------" + String.fromCharCode(10);
py += "# Glossary data - 35 mathematical terms in four languages" + String.fromCharCode(10);
py += "# ---------------------------------------------------------------------------" + String.fromCharCode(10,10);
py += "_MATH_GLOSSARY: List[GlossaryEntry] = [" + String.fromCharCode(10);

var NL = String.fromCharCode(10);
var DQ = String.fromCharCode(34);

function ge(id,tr,en,ku,ar,dtr,den,dku,dar,ex,rel,dl) {
  py += "    GlossaryEntry(" + NL;
  py += "        term_id=" + DQ + id + DQ + ", term_tr=" + DQ + tr + DQ + ", term_en=" + DQ + en + DQ + "," + NL;
  py += "        term_ku=" + DQ + ku + DQ + ", term_ar=" + DQ + ar + DQ + "," + NL;
  py += "        definition_tr=" + DQ + dtr + DQ + "," + NL;
  py += "        definition_en=" + DQ + den + DQ + "," + NL;
  py += "        definition_ku=" + DQ + dku + DQ + "," + NL;
  py += "        definition_ar=" + DQ + dar + DQ + "," + NL;
  var r = "[" + rel.map(function(x){return DQ + x + DQ}).join(", ") + "]";
  py += "        example=" + DQ + ex + DQ + ", related_terms=" + r + ", difficulty_level=" + dl + "," + NL;
  py += "    )," + NL;
}

// Entries will be added by append

// Read entries from JSON
var entries = JSON.parse(fs.readFileSync("C:/Users/ahmet/Desktop/.github/adaptive-math-learning/backend/services/_entries_all.json", "utf8"));
entries.forEach(function(e) { ge(e.id,e.tr,e.en,e.ku,e.ar,e.dtr,e.den,e.dku,e.dar,e.ex,e.rel,e.dl); });

py += "]" + NL + NL;
py += "# Quick lookup by term_id" + NL;
py += "_GLOSSARY_MAP: Dict[str, GlossaryEntry] = {entry.term_id: entry for entry in _MATH_GLOSSARY}" + NL;

// Read rest of file content
var restB64 = fs.readFileSync("C:/Users/ahmet/Desktop/.github/adaptive-math-learning/backend/services/_rest.b64", "utf8");
py += Buffer.from(restB64, "base64").toString("utf8");

fs.writeFileSync(t, py, "utf8");
console.log("Written", py.length, "chars to", t);
