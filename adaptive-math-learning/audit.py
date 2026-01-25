#!/usr/bin/env python3
"""
Adaptive Math Learning - Comprehensive Project Audit Script
============================================================
Bu script projedeki sorunları tespit eder ve revizyon raporu oluşturur.

Kullanım:
    python audit.py [--fix] [--verbose] [--category CATEGORY]

Kategoriler:
    all, api, security, imports, quality, deps, tests, config, types, db
"""

import ast
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ANSI renk kodları
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

@dataclass
class Issue:
    """Tespit edilen sorun."""
    category: str
    severity: str  # critical, high, medium, low, info
    file: str
    line: Optional[int]
    message: str
    suggestion: Optional[str] = None
    auto_fixable: bool = False

@dataclass
class AuditReport:
    """Audit raporu."""
    issues: List[Issue] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)

    def add_issue(self, issue: Issue):
        self.issues.append(issue)
        key = f"{issue.category}_{issue.severity}"
        self.stats[key] = self.stats.get(key, 0) + 1

class ProjectAuditor:
    """Ana audit sınıfı."""

    def __init__(self, project_root: Path, verbose: bool = False):
        self.root = project_root
        self.verbose = verbose
        self.report = AuditReport()

        # Proje dizinleri
        self.backend_dir = self.root / "backend"
        self.frontend_dir = self.root / "frontend"
        self.mobile_dir = self.root / "mobile"
        self.tests_dir = self.root / "tests"
        self.question_engine_dir = self.root / "question_engine"
        self.adaptation_dir = self.root / "adaptation"
        self.ai_dir = self.root / "ai_integration"

    def log(self, msg: str, color: str = Colors.WHITE):
        """Verbose logging."""
        if self.verbose:
            print(f"{color}{msg}{Colors.RESET}")

    def add_issue(self, category: str, severity: str, file: str,
                  line: Optional[int], message: str,
                  suggestion: Optional[str] = None, auto_fixable: bool = False):
        """Sorun ekle."""
        issue = Issue(category, severity, file, line, message, suggestion, auto_fixable)
        self.report.add_issue(issue)

    # =========================================================================
    # 1. API UYUMLULUK KONTROLÜ
    # =========================================================================

    def audit_api_compatibility(self):
        """Frontend/Backend API uyumluluğunu kontrol et."""
        self.log("\n[1/10] API Uyumluluk Kontrolü...", Colors.CYAN)

        # Backend endpoint'lerini topla
        backend_endpoints = self._collect_backend_endpoints()

        # Frontend API çağrılarını kontrol et
        self._check_frontend_api_calls(backend_endpoints)

        # Response format uyumsuzluklarını kontrol et
        self._check_response_format_mismatches()

    def _collect_backend_endpoints(self) -> Dict[str, dict]:
        """Backend endpoint'lerini topla."""
        endpoints = {}
        routes_dir = self.backend_dir / "api" / "routes"

        if not routes_dir.exists():
            return endpoints

        for py_file in routes_dir.glob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.AsyncFunctionDef) or isinstance(node, ast.FunctionDef):
                        # Decorator'ları kontrol et
                        for decorator in node.decorator_list:
                            if isinstance(decorator, ast.Call):
                                if isinstance(decorator.func, ast.Attribute):
                                    method = decorator.func.attr.upper()
                                    if method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                                        # Endpoint path'ini bul
                                        if decorator.args:
                                            path_arg = decorator.args[0]
                                            if isinstance(path_arg, ast.Constant):
                                                path = path_arg.value
                                                endpoints[f"{method} {path}"] = {
                                                    "file": str(py_file),
                                                    "function": node.name,
                                                    "line": node.lineno
                                                }
            except Exception as e:
                self.log(f"  Parse error in {py_file}: {e}", Colors.YELLOW)

        return endpoints

    def _check_frontend_api_calls(self, backend_endpoints: Dict[str, dict]):
        """Frontend API çağrılarını kontrol et."""
        frontend_files = list(self.frontend_dir.rglob("*.py"))

        api_call_pattern = re.compile(
            r'api_request\s*\(\s*["\'](\w+)["\']\s*,\s*["\']([^"\']+)["\']'
        )

        for py_file in frontend_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                for match in api_call_pattern.finditer(content):
                    method = match.group(1).upper()
                    path = match.group(2)
                    endpoint_key = f"{method} {path}"

                    # Endpoint backend'de var mı?
                    if endpoint_key not in backend_endpoints:
                        # Dinamik path olabilir
                        if "{" not in path and not any(
                            re.match(ep.replace("{", ".*").replace("}", ".*"), endpoint_key)
                            for ep in backend_endpoints.keys()
                        ):
                            line_no = content[:match.start()].count('\n') + 1
                            self.add_issue(
                                "api", "medium",
                                str(py_file.relative_to(self.root)),
                                line_no,
                                f"API endpoint bulunamadı: {endpoint_key}",
                                "Backend'de endpoint tanımlı mı kontrol edin"
                            )
            except Exception as e:
                self.log(f"  Error reading {py_file}: {e}", Colors.YELLOW)

    def _check_response_format_mismatches(self):
        """Response format uyumsuzluklarını kontrol et."""
        # .get() kullanımlarını kontrol et
        patterns = [
            (r'result\.get\(["\'](\w+)["\']', "result.get kullanımı - API response format kontrolü gerekli"),
            (r'response\.json\(\)\.get\(["\'](\w+)["\']', "Response parsing - format kontrolü gerekli"),
        ]

        for py_file in self.frontend_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                lines = content.split('\n')

                for i, line in enumerate(lines, 1):
                    # isinstance kontrolü olmadan .get() kullanımı
                    if '.get(' in line and 'isinstance' not in line:
                        # Önceki satırda isinstance kontrolü var mı?
                        prev_lines = '\n'.join(lines[max(0, i-3):i-1])
                        if 'isinstance' not in prev_lines and 'if result:' in prev_lines:
                            self.add_issue(
                                "api", "medium",
                                str(py_file.relative_to(self.root)),
                                i,
                                "Tip kontrolü olmadan .get() kullanımı",
                                "isinstance(result, dict) kontrolü ekleyin",
                                auto_fixable=True
                            )
            except Exception:
                pass

    # =========================================================================
    # 2. GÜVENLİK KONTROLÜ
    # =========================================================================

    def audit_security(self):
        """Güvenlik açıklarını kontrol et."""
        self.log("\n[2/10] Güvenlik Kontrolü...", Colors.CYAN)

        # Hardcoded credentials
        self._check_hardcoded_secrets()

        # CORS konfigürasyonu
        self._check_cors_config()

        # SQL Injection riskleri
        self._check_sql_injection()

        # Güvensiz fonksiyon kullanımı
        self._check_unsafe_functions()

    def _check_hardcoded_secrets(self):
        """Hardcoded secret'ları kontrol et."""
        secret_patterns = [
            (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\'][a-zA-Z0-9_-]{20,}["\']', "Hardcoded API key"),
            (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\'][^"\']{4,}["\']', "Hardcoded password"),
            (r'(?i)(secret|token)\s*[=:]\s*["\'][a-zA-Z0-9_-]{20,}["\']', "Hardcoded secret/token"),
            (r'sk-[a-zA-Z0-9]{20,}', "OpenAI API key"),
            (r'sk-ant-[a-zA-Z0-9-]{20,}', "Anthropic API key"),
        ]

        exclude_patterns = ['.env.example', 'test', 'mock', 'example', 'sample']

        for py_file in self.root.rglob("*.py"):
            if any(ex in str(py_file).lower() for ex in exclude_patterns):
                continue
            if '.git' in str(py_file) or '__pycache__' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                for pattern, desc in secret_patterns:
                    for match in re.finditer(pattern, content):
                        line_no = content[:match.start()].count('\n') + 1
                        self.add_issue(
                            "security", "critical",
                            str(py_file.relative_to(self.root)),
                            line_no,
                            f"{desc} tespit edildi",
                            "Ortam değişkeni kullanın (os.getenv)"
                        )
            except Exception:
                pass

    def _check_cors_config(self):
        """CORS konfigürasyonunu kontrol et."""
        for py_file in self.backend_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")

                # allow_origins = ["*"] kontrolü
                if 'allow_origins' in content and '"*"' in content:
                    line_no = None
                    for i, line in enumerate(content.split('\n'), 1):
                        if 'allow_origins' in line and '*' in line:
                            line_no = i
                            break

                    self.add_issue(
                        "security", "high",
                        str(py_file.relative_to(self.root)),
                        line_no,
                        "CORS tüm origin'lere açık (allow_origins = [\"*\"])",
                        "Sadece güvenilir domain'lere izin verin"
                    )
            except Exception:
                pass

    def _check_sql_injection(self):
        """SQL injection risklerini kontrol et."""
        risky_patterns = [
            r'execute\s*\(\s*f["\']',
            r'execute\s*\(\s*["\'].*%s.*["\'].*%',
            r'\.raw\s*\(\s*f["\']',
            r'text\s*\(\s*f["\'].*SELECT',
        ]

        for py_file in self.root.rglob("*.py"):
            if '__pycache__' in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                for pattern in risky_patterns:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        line_no = content[:match.start()].count('\n') + 1
                        self.add_issue(
                            "security", "critical",
                            str(py_file.relative_to(self.root)),
                            line_no,
                            "Potansiyel SQL injection riski",
                            "Parametreli sorgular kullanın"
                        )
            except Exception:
                pass

    def _check_unsafe_functions(self):
        """Güvensiz fonksiyon kullanımlarını kontrol et."""
        unsafe = [
            (r'\beval\s*\(', "eval() kullanımı - güvenlik riski"),
            (r'\bexec\s*\(', "exec() kullanımı - güvenlik riski"),
            (r'\bpickle\.loads?\s*\(', "pickle kullanımı - güvensiz deserialize"),
            (r'subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True', "shell=True - command injection riski"),
        ]

        for py_file in self.root.rglob("*.py"):
            if '__pycache__' in str(py_file) or 'audit.py' in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                for pattern, desc in unsafe:
                    for match in re.finditer(pattern, content):
                        line_no = content[:match.start()].count('\n') + 1
                        self.add_issue(
                            "security", "high",
                            str(py_file.relative_to(self.root)),
                            line_no,
                            desc
                        )
            except Exception:
                pass

    # =========================================================================
    # 3. IMPORT KONTROLÜ
    # =========================================================================

    def audit_imports(self):
        """Import sorunlarını kontrol et."""
        self.log("\n[3/10] Import Kontrolü...", Colors.CYAN)

        for py_file in self.root.rglob("*.py"):
            if '__pycache__' in str(py_file) or 'audit.py' in str(py_file):
                continue
            if '.git' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)

                imports = set()
                used_names = set()

                for node in ast.walk(tree):
                    # Import'ları topla
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            name = alias.asname if alias.asname else alias.name
                            imports.add((name, node.lineno))
                    elif isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            if alias.name != '*':
                                name = alias.asname if alias.asname else alias.name
                                imports.add((name, node.lineno))
                    # Kullanılan isimleri topla
                    elif isinstance(node, ast.Name):
                        used_names.add(node.id)
                    elif isinstance(node, ast.Attribute):
                        if isinstance(node.value, ast.Name):
                            used_names.add(node.value.id)

                # Kullanılmayan import'ları bul
                for name, line_no in imports:
                    base_name = name.split('.')[0]
                    if base_name not in used_names:
                        # Bazı false positive'leri filtrele
                        if base_name not in ['typing', 'annotations', '__future__', 'TYPE_CHECKING']:
                            self.add_issue(
                                "imports", "low",
                                str(py_file.relative_to(self.root)),
                                line_no,
                                f"Kullanılmayan import: {name}",
                                "Import'u kaldırın",
                                auto_fixable=True
                            )
            except SyntaxError as e:
                self.add_issue(
                    "imports", "critical",
                    str(py_file.relative_to(self.root)),
                    e.lineno,
                    f"Syntax hatası: {e.msg}"
                )
            except Exception as e:
                self.log(f"  Error parsing {py_file}: {e}", Colors.YELLOW)

    # =========================================================================
    # 4. KOD KALİTESİ KONTROLÜ
    # =========================================================================

    def audit_code_quality(self):
        """Kod kalitesi sorunlarını kontrol et."""
        self.log("\n[4/10] Kod Kalitesi Kontrolü...", Colors.CYAN)

        for py_file in self.root.rglob("*.py"):
            if '__pycache__' in str(py_file) or 'audit.py' in str(py_file):
                continue
            if '.git' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                lines = content.split('\n')

                for i, line in enumerate(lines, 1):
                    # Çok uzun satırlar
                    if len(line) > 120:
                        self.add_issue(
                            "quality", "low",
                            str(py_file.relative_to(self.root)),
                            i,
                            f"Satır çok uzun ({len(line)} karakter)",
                            "120 karakterin altına indirin"
                        )

                    # Boş except
                    if re.match(r'\s*except\s*:\s*$', line):
                        self.add_issue(
                            "quality", "medium",
                            str(py_file.relative_to(self.root)),
                            i,
                            "Boş except bloğu - tüm hataları yakalar",
                            "Spesifik exception türü belirtin"
                        )

                    # pass ile biten except
                    if re.match(r'\s*except.*:\s*$', line):
                        if i < len(lines) and lines[i].strip() == 'pass':
                            self.add_issue(
                                "quality", "medium",
                                str(py_file.relative_to(self.root)),
                                i,
                                "Sessizce geçilen exception",
                                "En azından logging ekleyin"
                            )

                    # TODO/FIXME/HACK yorumları
                    for marker in ['TODO', 'FIXME', 'HACK', 'XXX']:
                        if marker in line:
                            self.add_issue(
                                "quality", "info",
                                str(py_file.relative_to(self.root)),
                                i,
                                f"{marker} bulundu: {line.strip()[:80]}"
                            )

                    # print() debug ifadeleri
                    if re.match(r'\s*print\s*\(', line) and 'debug' not in py_file.name.lower():
                        # String içinde değilse
                        stripped = line.strip()
                        if not stripped.startswith('#') and not stripped.startswith('"') and not stripped.startswith("'"):
                            self.add_issue(
                                "quality", "low",
                                str(py_file.relative_to(self.root)),
                                i,
                                "print() ifadesi - production'da logging kullanın",
                                "logging modülünü kullanın"
                            )

                # Fonksiyon karmaşıklığı (basit satır sayısı kontrolü)
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                            if func_lines > 50:
                                self.add_issue(
                                    "quality", "medium",
                                    str(py_file.relative_to(self.root)),
                                    node.lineno,
                                    f"Fonksiyon çok uzun: {node.name} ({func_lines} satır)",
                                    "Daha küçük fonksiyonlara bölün"
                                )
                except Exception:
                    pass

            except Exception as e:
                self.log(f"  Error analyzing {py_file}: {e}", Colors.YELLOW)

    # =========================================================================
    # 5. BAĞIMLILIK KONTROLÜ
    # =========================================================================

    def audit_dependencies(self):
        """Bağımlılık sorunlarını kontrol et."""
        self.log("\n[5/10] Bağımlılık Kontrolü...", Colors.CYAN)

        # requirements.txt kontrolü
        req_file = self.root / "requirements.txt"
        if req_file.exists():
            self._check_requirements(req_file)
        else:
            self.add_issue(
                "deps", "high",
                "requirements.txt",
                None,
                "requirements.txt dosyası bulunamadı"
            )

        # package.json kontrolü (mobile)
        pkg_file = self.mobile_dir / "package.json"
        if pkg_file.exists():
            self._check_package_json(pkg_file)

    def _check_requirements(self, req_file: Path):
        """requirements.txt dosyasını kontrol et."""
        try:
            content = req_file.read_text(encoding="utf-8")
            lines = content.strip().split('\n')

            pinned = 0
            unpinned = 0

            deprecated_packages = {
                'sklearn': 'scikit-learn olarak yeniden adlandırıldı',
                'pycrypto': 'pycryptodome kullanın',
                'imp': 'importlib kullanın',
            }

            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Paket adını çıkar
                match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                if match:
                    pkg_name = match.group(1).lower()

                    # Deprecated paket kontrolü
                    if pkg_name in deprecated_packages:
                        self.add_issue(
                            "deps", "medium",
                            "requirements.txt",
                            i,
                            f"Deprecated paket: {pkg_name}",
                            deprecated_packages[pkg_name]
                        )

                    # Versiyon pinleme kontrolü
                    if '==' in line:
                        pinned += 1
                    elif '>=' in line or '~=' in line:
                        unpinned += 1
                    else:
                        unpinned += 1
                        self.add_issue(
                            "deps", "low",
                            "requirements.txt",
                            i,
                            f"Versiyon belirtilmemiş: {pkg_name}",
                            "Tekrarlanabilir build'ler için versiyon pinleyin"
                        )

            # Özet
            if unpinned > pinned:
                self.add_issue(
                    "deps", "info",
                    "requirements.txt",
                    None,
                    f"Bağımlılıkların çoğu pinlenmemiş ({unpinned}/{pinned + unpinned})",
                    "pip freeze > requirements.txt ile versiyonları kilitleyin"
                )

        except Exception as e:
            self.add_issue(
                "deps", "medium",
                "requirements.txt",
                None,
                f"Dosya okunamadı: {e}"
            )

    def _check_package_json(self, pkg_file: Path):
        """package.json dosyasını kontrol et."""
        try:
            content = json.loads(pkg_file.read_text(encoding="utf-8"))

            # Missing scripts kontrolü
            scripts = content.get('scripts', {})
            recommended_scripts = ['test', 'lint', 'build']
            for script in recommended_scripts:
                if script not in scripts:
                    self.add_issue(
                        "deps", "low",
                        "mobile/package.json",
                        None,
                        f"Önerilen script eksik: {script}"
                    )

            # Outdated Expo SDK kontrolü
            deps = {**content.get('dependencies', {}), **content.get('devDependencies', {})}
            if 'expo' in deps:
                version = deps['expo'].replace('^', '').replace('~', '')
                try:
                    major = int(version.split('.')[0])
                    if major < 50:
                        self.add_issue(
                            "deps", "medium",
                            "mobile/package.json",
                            None,
                            f"Eski Expo SDK ({version})",
                            "Expo SDK 50+ sürümüne güncelleyin"
                        )
                except ValueError:
                    pass

        except Exception as e:
            self.add_issue(
                "deps", "medium",
                "mobile/package.json",
                None,
                f"Dosya parse edilemedi: {e}"
            )

    # =========================================================================
    # 6. TEST KONTROLÜ
    # =========================================================================

    def audit_tests(self):
        """Test coverage sorunlarını kontrol et."""
        self.log("\n[6/10] Test Kontrolü...", Colors.CYAN)

        # Test dosyalarını bul
        test_files = list(self.tests_dir.rglob("test_*.py")) if self.tests_dir.exists() else []
        test_files += list(self.root.rglob("*_test.py"))

        if not test_files:
            self.add_issue(
                "tests", "high",
                "tests/",
                None,
                "Test dosyası bulunamadı",
                "pytest ile testler ekleyin"
            )
            return

        # Test edilmesi gereken modüller
        modules_to_test = [
            ("backend/api/routes", "API routes"),
            ("backend/services", "Services"),
            ("question_engine/generators", "Question generators"),
            ("adaptation", "Adaptation algorithms"),
        ]

        test_content = ""
        for tf in test_files:
            try:
                test_content += tf.read_text(encoding="utf-8") + "\n"
            except Exception:
                pass

        for module_path, module_name in modules_to_test:
            module_dir = self.root / module_path
            if module_dir.exists():
                # Bu modül için test var mı?
                module_short = module_path.split('/')[-1]
                if module_short not in test_content and module_name.lower() not in test_content.lower():
                    self.add_issue(
                        "tests", "medium",
                        module_path,
                        None,
                        f"Test coverage eksik: {module_name}",
                        f"test_{module_short}.py ekleyin"
                    )

        # Fixture ve mock kullanımı kontrolü
        for test_file in test_files:
            try:
                content = test_file.read_text(encoding="utf-8")

                # Database testi yapılıyor ama mock yok
                if 'database' in content.lower() or 'session' in content.lower():
                    if 'mock' not in content.lower() and 'fixture' not in content.lower():
                        self.add_issue(
                            "tests", "medium",
                            str(test_file.relative_to(self.root)),
                            None,
                            "Database testi mock/fixture olmadan",
                            "pytest-mock veya fixtures kullanın"
                        )
            except Exception:
                pass

    # =========================================================================
    # 7. KONFİGÜRASYON KONTROLÜ
    # =========================================================================

    def audit_config(self):
        """Konfigürasyon sorunlarını kontrol et."""
        self.log("\n[7/10] Konfigürasyon Kontrolü...", Colors.CYAN)

        # .env dosyası kontrolü
        env_file = self.root / ".env"
        env_example = self.root / ".env.example"

        if not env_file.exists():
            self.add_issue(
                "config", "info",
                ".env",
                None,
                ".env dosyası yok (bu normal olabilir)",
                ".env.example'dan kopyalayın"
            )

        if env_example.exists():
            self._check_env_example(env_example)

        # alembic.ini kontrolü
        alembic_ini = self.root / "alembic.ini"
        if alembic_ini.exists():
            try:
                content = alembic_ini.read_text(encoding="utf-8")
                if 'sqlalchemy.url' in content:
                    # Hardcoded connection string kontrolü
                    match = re.search(r'sqlalchemy\.url\s*=\s*(.+)', content)
                    if match:
                        url = match.group(1).strip()
                        if '@' in url and 'env' not in url.lower() and '%(DB' not in url:
                            self.add_issue(
                                "config", "high",
                                "alembic.ini",
                                None,
                                "Hardcoded database URL",
                                "Ortam değişkeni kullanın"
                            )
            except Exception:
                pass

        # Docker konfigürasyonu
        docker_compose = self.root / "docker-compose.yml"
        if docker_compose.exists():
            self._check_docker_compose(docker_compose)

    def _check_env_example(self, env_file: Path):
        """Environment örnek dosyasını kontrol et."""
        try:
            content = env_file.read_text(encoding="utf-8")

            required_vars = [
                'DATABASE_URL',
                'SECRET_KEY',
            ]

            for var in required_vars:
                if var not in content:
                    self.add_issue(
                        "config", "medium",
                        ".env.example",
                        None,
                        f"Önemli ortam değişkeni eksik: {var}"
                    )

            # Örnek değerler gerçek değerlere benziyor mu?
            if re.search(r'sk-[a-zA-Z0-9]{20,}', content):
                self.add_issue(
                    "config", "high",
                    ".env.example",
                    None,
                    "Gerçek API key örnek dosyada",
                    "Placeholder değer kullanın"
                )

        except Exception:
            pass

    def _check_docker_compose(self, compose_file: Path):
        """Docker compose dosyasını kontrol et."""
        try:
            content = compose_file.read_text(encoding="utf-8")

            # Hardcoded password kontrolü
            if re.search(r'(POSTGRES_PASSWORD|MYSQL_PASSWORD)\s*:\s*["\']?[^$\n]+["\']?', content):
                if '${' not in content or 'password' in content.lower():
                    for i, line in enumerate(content.split('\n'), 1):
                        if 'PASSWORD' in line and '${' not in line:
                            self.add_issue(
                                "config", "high",
                                "docker-compose.yml",
                                i,
                                "Hardcoded database password",
                                "Ortam değişkeni kullanın: ${DB_PASSWORD}"
                            )
                            break

            # Health check kontrolü
            if 'healthcheck' not in content:
                self.add_issue(
                    "config", "low",
                    "docker-compose.yml",
                    None,
                    "Health check tanımlanmamış",
                    "Servislere healthcheck ekleyin"
                )

        except Exception:
            pass

    # =========================================================================
    # 8. TYPE HINTING KONTROLÜ
    # =========================================================================

    def audit_types(self):
        """Type hinting sorunlarını kontrol et."""
        self.log("\n[8/10] Type Hinting Kontrolü...", Colors.CYAN)

        for py_file in self.root.rglob("*.py"):
            if '__pycache__' in str(py_file) or 'audit.py' in str(py_file):
                continue
            if '.git' in str(py_file) or 'migrations' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Constructor ve magic method'ları atla
                        if node.name.startswith('_'):
                            continue

                        # Return type annotation kontrolü
                        if node.returns is None and node.name not in ['main', 'setup', 'teardown']:
                            # Fonksiyon bir değer döndürüyor mu?
                            has_return = any(
                                isinstance(n, ast.Return) and n.value is not None
                                for n in ast.walk(node)
                            )
                            if has_return:
                                self.add_issue(
                                    "types", "low",
                                    str(py_file.relative_to(self.root)),
                                    node.lineno,
                                    f"Return type eksik: {node.name}()",
                                    "Return type annotation ekleyin"
                                )

                        # Parametre type annotation kontrolü
                        for arg in node.args.args:
                            if arg.arg not in ['self', 'cls'] and arg.annotation is None:
                                self.add_issue(
                                    "types", "low",
                                    str(py_file.relative_to(self.root)),
                                    node.lineno,
                                    f"Parametre type eksik: {node.name}({arg.arg})",
                                    "Type annotation ekleyin"
                                )
                                break  # Sadece ilk eksik için uyar

            except Exception:
                pass

    # =========================================================================
    # 9. VERİTABANI KONTROLÜ
    # =========================================================================

    def audit_database(self):
        """Veritabanı sorunlarını kontrol et."""
        self.log("\n[9/10] Veritabanı Kontrolü...", Colors.CYAN)

        # Model dosyalarını bul
        models_dir = self.backend_dir / "models"
        if not models_dir.exists():
            self.add_issue(
                "db", "high",
                "backend/models",
                None,
                "Models dizini bulunamadı"
            )
            return

        # Model-Schema uyumluluğu
        self._check_model_schema_consistency()

        # N+1 query potansiyeli
        self._check_n_plus_one_queries()

        # Migration dosyaları
        self._check_migrations()

    def _check_model_schema_consistency(self):
        """Model ve schema uyumluluğunu kontrol et."""
        models = {}
        schemas = {}

        # Model'leri topla
        models_dir = self.backend_dir / "models"
        if models_dir.exists():
            for py_file in models_dir.glob("*.py"):
                try:
                    content = py_file.read_text(encoding="utf-8")
                    # class ModelName(Base): pattern
                    for match in re.finditer(r'class\s+(\w+)\s*\([^)]*Base[^)]*\)', content):
                        models[match.group(1)] = str(py_file)
                except Exception:
                    pass

        # Schema'ları topla
        schemas_dir = self.backend_dir / "schemas"
        if schemas_dir.exists():
            for py_file in schemas_dir.glob("*.py"):
                try:
                    content = py_file.read_text(encoding="utf-8")
                    # class SchemaName(BaseModel): pattern
                    for match in re.finditer(r'class\s+(\w+)\s*\([^)]*BaseModel[^)]*\)', content):
                        schemas[match.group(1)] = str(py_file)
                except Exception:
                    pass

        # Model için schema var mı?
        for model_name in models:
            expected_schemas = [
                f"{model_name}Schema",
                f"{model_name}Response",
                f"{model_name}Create",
                f"{model_name}Base",
            ]
            if not any(s in schemas for s in expected_schemas):
                self.add_issue(
                    "db", "medium",
                    models[model_name],
                    None,
                    f"Model için schema eksik: {model_name}",
                    f"{model_name}Schema, {model_name}Response vb. oluşturun"
                )

    def _check_n_plus_one_queries(self):
        """N+1 query potansiyelini kontrol et."""
        routes_dir = self.backend_dir / "api" / "routes"
        if not routes_dir.exists():
            return

        for py_file in routes_dir.glob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                lines = content.split('\n')

                for i, line in enumerate(lines, 1):
                    # Loop içinde query
                    if 'for ' in line and ('query(' in line or '.filter(' in line):
                        self.add_issue(
                            "db", "medium",
                            str(py_file.relative_to(self.root)),
                            i,
                            "Loop içinde query - N+1 potansiyeli",
                            "joinedload veya batch query kullanın"
                        )

                    # .all() sonrası loop içinde ilişki erişimi
                    if '.all()' in line:
                        # Sonraki satırlarda for loop var mı?
                        for j in range(i, min(i + 5, len(lines))):
                            if 'for ' in lines[j-1] and '.' in lines[j-1]:
                                self.add_issue(
                                    "db", "low",
                                    str(py_file.relative_to(self.root)),
                                    i,
                                    ".all() sonrası iteration - lazy loading kontrolü",
                                    "İlişkiler için eager loading düşünün"
                                )
                                break
            except Exception:
                pass

    def _check_migrations(self):
        """Migration dosyalarını kontrol et."""
        alembic_dir = self.root / "alembic" / "versions"
        if not alembic_dir.exists():
            self.add_issue(
                "db", "medium",
                "alembic/versions",
                None,
                "Migration dosyaları bulunamadı",
                "alembic revision --autogenerate ile migration oluşturun"
            )
            return

        migrations = list(alembic_dir.glob("*.py"))
        if not migrations:
            self.add_issue(
                "db", "medium",
                "alembic/versions",
                None,
                "Migration dosyası yok"
            )

    # =========================================================================
    # 10. PROJE YAPISI KONTROLÜ
    # =========================================================================

    def audit_structure(self):
        """Proje yapısı sorunlarını kontrol et."""
        self.log("\n[10/10] Proje Yapısı Kontrolü...", Colors.CYAN)

        # Gerekli dosyalar
        required_files = [
            ("README.md", "Proje dokümantasyonu"),
            ("requirements.txt", "Python bağımlılıkları"),
            (".gitignore", "Git ignore dosyası"),
        ]

        for file_name, description in required_files:
            if not (self.root / file_name).exists():
                self.add_issue(
                    "structure", "medium",
                    file_name,
                    None,
                    f"Eksik dosya: {description}"
                )

        # __init__.py kontrolü
        for package_dir in [self.backend_dir, self.question_engine_dir, self.adaptation_dir]:
            if package_dir.exists():
                init_file = package_dir / "__init__.py"
                if not init_file.exists():
                    self.add_issue(
                        "structure", "low",
                        str(package_dir.relative_to(self.root)),
                        None,
                        "__init__.py eksik - paket olarak import edilemez"
                    )

        # Boş dizinler
        for dir_path in self.root.rglob("*"):
            if dir_path.is_dir():
                if not list(dir_path.iterdir()) and '.git' not in str(dir_path):
                    self.add_issue(
                        "structure", "info",
                        str(dir_path.relative_to(self.root)),
                        None,
                        "Boş dizin"
                    )

    # =========================================================================
    # RAPOR OLUŞTURMA
    # =========================================================================

    def run_all_audits(self, categories: Optional[List[str]] = None):
        """Tüm audit'leri çalıştır."""
        audit_map = {
            'api': self.audit_api_compatibility,
            'security': self.audit_security,
            'imports': self.audit_imports,
            'quality': self.audit_code_quality,
            'deps': self.audit_dependencies,
            'tests': self.audit_tests,
            'config': self.audit_config,
            'types': self.audit_types,
            'db': self.audit_database,
            'structure': self.audit_structure,
        }

        if categories is None or 'all' in categories:
            categories = list(audit_map.keys())

        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
        print("   ADAPTIVE MATH LEARNING - PROJECT AUDIT")
        print(f"{'='*60}{Colors.RESET}\n")

        for category in categories:
            if category in audit_map:
                try:
                    audit_map[category]()
                except Exception as e:
                    self.add_issue(
                        category, "critical",
                        "audit.py",
                        None,
                        f"Audit hatası: {e}"
                    )

    def generate_report(self) -> str:
        """Rapor oluştur."""
        lines = []

        # Özet
        severity_counts = defaultdict(int)
        category_counts = defaultdict(int)

        for issue in self.report.issues:
            severity_counts[issue.severity] += 1
            category_counts[issue.category] += 1

        lines.append(f"\n{Colors.BOLD}{'='*60}")
        lines.append("   AUDIT SONUÇLARI")
        lines.append(f"{'='*60}{Colors.RESET}\n")

        # Severity özeti
        lines.append(f"{Colors.BOLD}Önem Derecesine Göre:{Colors.RESET}")
        severity_colors = {
            'critical': Colors.RED,
            'high': Colors.RED,
            'medium': Colors.YELLOW,
            'low': Colors.BLUE,
            'info': Colors.WHITE,
        }
        severity_icons = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🔵',
            'info': 'ℹ️ ',
        }

        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            count = severity_counts.get(severity, 0)
            color = severity_colors[severity]
            icon = severity_icons[severity]
            lines.append(f"  {icon} {color}{severity.upper():10} {count:3}{Colors.RESET}")

        lines.append(f"\n{Colors.BOLD}Kategoriye Göre:{Colors.RESET}")
        category_names = {
            'api': 'API Uyumluluk',
            'security': 'Güvenlik',
            'imports': 'Import',
            'quality': 'Kod Kalitesi',
            'deps': 'Bağımlılıklar',
            'tests': 'Testler',
            'config': 'Konfigürasyon',
            'types': 'Type Hinting',
            'db': 'Veritabanı',
            'structure': 'Proje Yapısı',
        }

        for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            name = category_names.get(category, category)
            lines.append(f"  📁 {name:20} {count:3}")

        # Detaylı sorunlar
        lines.append(f"\n{Colors.BOLD}{'='*60}")
        lines.append("   DETAYLI SORUNLAR")
        lines.append(f"{'='*60}{Colors.RESET}")

        # Severity'e göre sırala
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        sorted_issues = sorted(
            self.report.issues,
            key=lambda x: (severity_order.get(x.severity, 5), x.category, x.file)
        )

        current_category = None
        for issue in sorted_issues:
            if issue.category != current_category:
                current_category = issue.category
                cat_name = category_names.get(issue.category, issue.category)
                lines.append(f"\n{Colors.BOLD}{Colors.MAGENTA}── {cat_name.upper()} ──{Colors.RESET}")

            color = severity_colors.get(issue.severity, Colors.WHITE)
            icon = severity_icons.get(issue.severity, '•')

            location = issue.file
            if issue.line:
                location += f":{issue.line}"

            lines.append(f"\n{icon} {color}[{issue.severity.upper()}]{Colors.RESET} {location}")
            lines.append(f"   {issue.message}")
            if issue.suggestion:
                lines.append(f"   {Colors.GREEN}💡 {issue.suggestion}{Colors.RESET}")
            if issue.auto_fixable:
                lines.append(f"   {Colors.CYAN}🔧 Otomatik düzeltilebilir{Colors.RESET}")

        # Özet
        total = len(self.report.issues)
        critical_high = severity_counts.get('critical', 0) + severity_counts.get('high', 0)

        lines.append(f"\n{Colors.BOLD}{'='*60}")
        lines.append("   ÖZET")
        lines.append(f"{'='*60}{Colors.RESET}")
        lines.append(f"\nToplam sorun: {total}")

        if critical_high > 0:
            lines.append(f"{Colors.RED}⚠️  {critical_high} kritik/yüksek öncelikli sorun var!{Colors.RESET}")
        elif total == 0:
            lines.append(f"{Colors.GREEN}✅ Harika! Sorun bulunamadı.{Colors.RESET}")
        else:
            lines.append(f"{Colors.YELLOW}📝 {total} düşük/orta öncelikli sorun bulundu.{Colors.RESET}")

        return '\n'.join(lines)

    def export_json(self, output_file: Path):
        """JSON formatında export et."""
        data = {
            "summary": {
                "total_issues": len(self.report.issues),
                "by_severity": {},
                "by_category": {},
            },
            "issues": []
        }

        for issue in self.report.issues:
            data["summary"]["by_severity"][issue.severity] = \
                data["summary"]["by_severity"].get(issue.severity, 0) + 1
            data["summary"]["by_category"][issue.category] = \
                data["summary"]["by_category"].get(issue.category, 0) + 1

            data["issues"].append({
                "category": issue.category,
                "severity": issue.severity,
                "file": issue.file,
                "line": issue.line,
                "message": issue.message,
                "suggestion": issue.suggestion,
                "auto_fixable": issue.auto_fixable,
            })

        output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n{Colors.GREEN}📄 JSON rapor kaydedildi: {output_file}{Colors.RESET}")


def main():
    """Ana fonksiyon."""
    import argparse
    import io

    # Windows terminal encoding fix
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description="Adaptive Math Learning - Project Audit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Kategoriler:
  all        Tüm kontroller
  api        API uyumluluk kontrolü
  security   Güvenlik kontrolü
  imports    Import kontrolü
  quality    Kod kalitesi kontrolü
  deps       Bağımlılık kontrolü
  tests      Test kontrolü
  config     Konfigürasyon kontrolü
  types      Type hinting kontrolü
  db         Veritabanı kontrolü
  structure  Proje yapısı kontrolü

Örnekler:
  python audit.py                    # Tüm kontroller
  python audit.py -c security api    # Sadece güvenlik ve API
  python audit.py -v                 # Verbose mod
  python audit.py --json report.json # JSON export
        """
    )

    parser.add_argument(
        '-c', '--category',
        nargs='+',
        default=['all'],
        help='Kontrol edilecek kategoriler'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Detaylı çıktı'
    )
    parser.add_argument(
        '--json',
        type=str,
        help='JSON formatında export dosyası'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Otomatik düzeltilebilir sorunları düzelt (henüz desteklenmiyor)'
    )

    args = parser.parse_args()

    # Proje kök dizini
    project_root = Path(__file__).parent

    # Auditor oluştur
    auditor = ProjectAuditor(project_root, verbose=args.verbose)

    # Audit'leri çalıştır
    auditor.run_all_audits(args.category)

    # Rapor oluştur
    report = auditor.generate_report()
    print(report)

    # JSON export
    if args.json:
        auditor.export_json(Path(args.json))

    # Exit code
    critical_high = sum(
        1 for i in auditor.report.issues
        if i.severity in ['critical', 'high']
    )
    sys.exit(1 if critical_high > 0 else 0)


if __name__ == "__main__":
    main()
