const fs = require("fs");
const pp = require("path");
const target = pp.join("C:", "Users", "ahmet", "Desktop", ".github",
    "adaptive-math-learning", "backend", "services",
    "enhanced_parent_teacher_service.py");
const DQ = String.fromCharCode(34);
const SQ = String.fromCharCode(39);
const Q3 = DQ + DQ + DQ;
const lines = [];
function L(s) { lines.push(s); }
function B() { lines.push(""); }

B();
L("    def grade_homework(self, homework_id: str) -> Dict[str, Any]:");
L("        " + Q3 + "Odeve ait tum teslimleri otomatik degerlendirir." + Q3);
L("        homework = self.get_homework(homework_id)");
L("        submissions = self._get_homework_submissions(homework_id)");
L("        if not submissions:");
L("            return {" + DQ + "homework_id" + DQ + ": homework_id, " + DQ + "graded_count" + DQ + ": 0,");
L("                    " + DQ + "sinif_ortalamasi" + DQ + ": 0.0, " + DQ + "en_yuksek_puan" + DQ + ": 0.0,");
L("                    " + DQ + "en_dusuk_puan" + DQ + ": 0.0, " + DQ + "submissions" + DQ + ": []}");
L("        scores: List[float] = []");
L("        for submission in submissions:");
L("            self._grade_single_submission(submission, homework)");
L("            if submission.score is not None:");
L("                scores.append(submission.score)");
L("        avg_score = statistics.mean(scores) if scores else 0.0");
L("        homework.sinif_ortalamasi = round(avg_score, 2)");
L("        homework.status = HomeworkStatus.GRADED");
L("        return {" + DQ + "homework_id" + DQ + ": homework_id, " + DQ + "graded_count" + DQ + ": len(submissions),");
L("                " + DQ + "sinif_ortalamasi" + DQ + ": round(avg_score, 2),");
L("                " + DQ + "en_yuksek_puan" + DQ + ": max(scores) if scores else 0.0,");
L("                " + DQ + "en_dusuk_puan" + DQ + ": min(scores) if scores else 0.0,");
L("                " + DQ + "submissions" + DQ + ": submissions}");
B();
L("    def get_homework_results(self, homework_id: str) -> Dict[str, Any]:");
L("        " + Q3 + "Ogretmen icin odev sonuclarini dondurur." + Q3);
L("        homework = self.get_homework(homework_id)");
L("        submissions = self._get_homework_submissions(homework_id)");
L("        student_results: List[Dict[str, Any]] = []");
L("        topic_totals: Dict[str, List[float]] = {}");
L("        for sub in submissions:");
L("            student_results.append({" + DQ + "student_id" + DQ + ": sub.student_id,");
L("                " + DQ + "student_name" + DQ + ": self._store.get_student_name(sub.student_id),");
L("                " + DQ + "score" + DQ + ": sub.score, " + DQ + "dogru_sayisi" + DQ + ": sub.dogru_sayisi,");
L("                " + DQ + "yanlis_sayisi" + DQ + ": sub.yanlis_sayisi, " + DQ + "bos_sayisi" + DQ + ": sub.bos_sayisi,");
L("                " + DQ + "submitted_at" + DQ + ": sub.submitted_at.isoformat(),");
L("                " + DQ + "topic_scores" + DQ + ": sub.topic_scores})");
L("            for topic, score in sub.topic_scores.items():");
L("                topic_totals.setdefault(topic, []).append(score)");
L("        topic_analysis = [{" + DQ + "topic" + DQ + ": t, " + DQ + "ortalama" + DQ + ": round(statistics.mean(v), 2),");
L("             " + DQ + "en_dusuk" + DQ + ": round(min(v), 2), " + DQ + "en_yuksek" + DQ + ": round(max(v), 2)}");
L("            for t, v in topic_totals.items()]");
L("        teslim_orani = (homework.teslim_sayisi / homework.toplam_ogrenci * 100");
L("                        if homework.toplam_ogrenci > 0 else 0.0)");
L("        return {" + DQ + "homework_id" + DQ + ": homework_id, " + DQ + "title" + DQ + ": homework.title,");
L("                " + DQ + "status" + DQ + ": homework.status.value, " + DQ + "sinif_ortalamasi" + DQ + ": homework.sinif_ortalamasi,");
L("                " + DQ + "teslim_orani" + DQ + ": round(teslim_orani, 1), " + DQ + "teslim_sayisi" + DQ + ": homework.teslim_sayisi,");
L("                " + DQ + "toplam_ogrenci" + DQ + ": homework.toplam_ogrenci, " + DQ + "student_results" + DQ + ": student_results,");
L("                " + DQ + "topic_analysis" + DQ + ": topic_analysis}");

fs.appendFileSync(target, lines.join("\n") + "\n", "utf8");
console.log("HW part b appended:", lines.length, "lines");
