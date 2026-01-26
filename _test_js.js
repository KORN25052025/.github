const DQ = String.fromCharCode(34);
const SQ = String.fromCharCode(39);
const Q3 = DQ + DQ + DQ;
const lines = [];
function L(s) { lines.push(s); }
L("        weak_topics = [t for t, s in topic_scores.items() if s < 50]");
L("        if weak_topics:");
L("            feedback += f" + DQ + " Ozellikle su konulara calis: {" + SQ + ", " + SQ + ".join(weak_topics)}." + DQ);
L("        return feedback");
console.log(lines.join("\n"));
