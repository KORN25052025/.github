const fs = require("fs");
const jp = "C:/Users/ahmet/Desktop/.github/adaptive-math-learning/backend/services/_entries_all.json";
const existing = JSON.parse(fs.readFileSync(jp, "utf8"));

const more = [
  {id:"percentage",tr:"Yüzde",en:"Percentage",ku:"Ji Sedî",ar:"نسبة مئوية",dtr:"Yüzde oranı.",den:"Fraction of 100.",dku:"Rêje ji 100.",dar:"نسبة من مئة.",ex:"%50 = 1/2",rel:["fraction","decimal","ratio"],dl:2},
  {id:"equation",tr:"Denklem",en:"Equation",ku:"Hevkêşe",ar:"معادلة",dtr:"Eşitlik cümlesi.",den:"Equality statement.",dku:"Wekheviya bêjan.",dar:"تساوي تعبيرين.",ex:"2x + 3 = 7",rel:["variable","expression","inequality"],dl:3},
];

const combined = existing.concat(more);
fs.writeFileSync(jp, JSON.stringify(combined), "utf8");
console.log("Total:", combined.length);