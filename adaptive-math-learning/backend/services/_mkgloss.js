const fs = require("fs");
const gp = "C:/Users/ahmet/Desktop/.github/adaptive-math-learning/backend/services/_gen_all.js";
let c = "";
function ge(o) {
  c += "    GlossaryEntry(
        term_id=\"" + o.id + "\", term_tr=\"" + o.tr + "\", term_en=\"" + o.en + "\",
";
  c += "        term_ku=\"" + o.ku + "\", term_ar=\"" + o.ar + "\",
";
  c += "        definition_tr=\"" + o.dtr + "\",
";
  c += "        definition_en=\"" + o.den + "\",
";
  c += "        definition_ku=\"" + o.dku + "\",
";
  c += "        definition_ar=\"" + o.dar + "\",
";
  c += "        example=\"" + o.ex + "\", related_terms=[" + o.rel.map(function(r){return "\"" + r + "\""}).join(", ") + "], difficulty_level=" + o.dl + ",
";
  c += "    ),
";
}