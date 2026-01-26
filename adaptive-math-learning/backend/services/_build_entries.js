const fs = require("fs");
const jp = "C:/Users/ahmet/Desktop/.github/adaptive-math-learning/backend/services/_entries.json";
const e = [];
function add(id,tr,en,ku,ar,dtr,den,dku,dar,ex,rel,dl) {
  e.push({id,tr,en,ku,ar,dtr,den,dku,dar,ex,rel,dl});
}
// Entries will be appended below
add("addition","Toplama","Addition","Lêkdan","جمع","İki veya daha fazla sayıyı birleştirerek toplamı bulma işlemi.","The process of combining two or more numbers to find their total.","Pêvajoya kombûna du an jî zêdetir jimaran.","عملية دمج عددين أو أكثر لإيجاد مجموعهما.","3 + 5 = 8",["subtraction","sum"],1);
add("subtraction","Çıkarma","Subtraction","Derxistin","طرح","Bir sayıdan diğerini çıkararak farkı bulma işlemi.","The process of removing one number from another.","Pêvajoya rakirina jimareyêkê ji ya din.","عملية إزالة عدد من عدد آخر.","9 - 4 = 5",["addition","difference"],1);
fs.writeFileSync(jp, JSON.stringify(e), "utf8");
console.log("Saved", e.length, "entries");