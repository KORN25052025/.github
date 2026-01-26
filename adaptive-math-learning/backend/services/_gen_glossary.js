const fs = require("fs");
const t = "C:/Users/ahmet/Desktop/.github/adaptive-math-learning/backend/services/accessibility_service.py";
const e = JSON.parse(fs.readFileSync("C:/Users/ahmet/Desktop/.github/adaptive-math-learning/backend/services/_entries.json","utf8"));
const L = fs.readFileSync(t,"utf8");
let o = L;
o += "

# ---------------------------------------------------------------------------
";
o += "# Glossary data - 35 mathematical terms in four languages
";
o += "# ---------------------------------------------------------------------------

";
o += "_MATH_GLOSSARY: List[GlossaryEntry] = [
";
for(const x of e){
  o+="    GlossaryEntry(
";
  o+="        term_id=""+x.id+"", term_tr=""+x.tr+"", term_en=""+x.en+"",
";
  o+="        term_ku=""+x.ku+"", term_ar=""+x.ar+"",
";
  o+="        definition_tr=""+x.dtr+"",
";
  o+="        definition_en=""+x.den+"",
";
  o+="        definition_ku=""+x.dku+"",
";
  o+="        definition_ar=""+x.dar+"",
";
  o+="        example=""+x.ex+"", related_terms="+JSON.stringify(x.rel)+", difficulty_level="+x.dl+",
";
  o+="    ),
";
}
o += "]

";
o += "# Quick lookup by term_id
";
o += "_GLOSSARY_MAP: Dict[str, GlossaryEntry] = {entry.term_id: entry for entry in _MATH_GLOSSARY}
";
fs.writeFileSync(t, o, "utf8");
console.log("Written", o.length, "chars");