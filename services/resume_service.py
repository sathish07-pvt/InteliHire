import os
import re
from pathlib import Path
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF

# Configurable master skills dictionary categorized by domain
SKILLS_DICTIONARY = {
    "Java": ["java", "jvm", "jdk", "jre", "spring", "spring boot", "hibernate", "maven", "gradle"],
    "Python": ["python", "django", "flask", "fastapi", "pandas", "numpy", "scikit-learn", "pytorch", "tensorflow"],
    "DBMS": ["dbms", "database", "rdbms", "normalization", "acid", "transactions", "er diagram", "indexing", "firebase", "mongodb", "nosql"],
    "SQL": ["sql", "mysql", "postgresql", "oracle", "sqlite", "queries", "joins", "subqueries", "stored procedures"],
    "Data Structures": ["data structures", "dsa", "algorithms", "array", "linked list", "stack", "queue", "binary tree", "bst", "graph", "sorting", "searching", "hashmap", "dynamic programming"],
    "HTML/CSS": ["html", "html5", "css", "css3", "bootstrap", "tailwind", "responsive design", "flexbox", "grid", "sass"],
    "JavaScript": ["javascript", "js", "typescript", "es6", "react", "react.js", "angular", "vue", "node.js", "express", "nodejs"],
    "Spring Boot": ["spring boot", "microservices", "rest api", "jpa", "spring security", "eureka", "actuator"],
    "Cloud & DevOps": ["azure", "aws", "gcp", "docker", "kubernetes", "cloud", "ci/cd", "linux", "git", "github"],
    "Cybersecurity": ["cybersecurity", "cyber security", "cyber risk", "risk analyst", "security", "vulnerability", "encryption", "firewall", "network security"],
    "General Programming": ["oop", "object oriented programming", "git", "github", "docker", "unit testing", "rest", "linux", "ci/cd", "problem solving"],
    "HR": ["communication", "leadership", "teamwork", "problem solving", "time management", "adaptability", "critical thinking"]
}

# Domain mapping based on detected skills
DOMAIN_MAPPING = {
    "Backend Development": ["Java", "Python", "SQL", "DBMS", "Spring Boot"],
    "Frontend Development": ["HTML/CSS", "JavaScript"],
    "Full-Stack Web Development": ["JavaScript", "Python", "Java", "SQL", "HTML/CSS", "Spring Boot"],
    "Data Structures & Problem Solving": ["Data Structures", "General Programming"],
    "Enterprise Software Engineering": ["Java", "Spring Boot", "SQL", "DBMS"],
    "Cloud & Infrastructure": ["Cloud & DevOps", "General Programming"],
    "Cybersecurity & Risk Analysis": ["Cybersecurity", "General Programming", "DBMS"]
}

SUPPORTED_EXTENSIONS = {"pdf", "docx", "doc", "txt", "rtf", "odt"}


class ResumeService:
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> dict:
        """
        Extracts raw text from a PDF file using PyMuPDF (fitz).
        Handles empty or scanned PDFs gracefully.
        Safely captures page_count before document closure to avoid 'document closed' errors.
        """
        if not os.path.exists(pdf_path):
            return {
                "success": False,
                "text": "",
                "error": "The specified resume file was not found on disk."
            }

        try:
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            extracted_text = []

            try:
                for page_num in range(page_count):
                    page = doc.load_page(page_num)
                    page_text = page.get_text("text")
                    if page_text:
                        extracted_text.append(page_text.strip())
            finally:
                doc.close()

            full_text = "\n\n".join(extracted_text).strip()

            if not full_text:
                return {
                    "success": False,
                    "text": "",
                    "is_scanned": True,
                    "page_count": page_count,
                    "error": (
                        "No extractable text was found in this PDF. It appears to be a scanned image "
                        "or contains image-based pages. An OCR (Optical Character Recognition) engine "
                        "is required to process scanned images."
                    )
                }

            return {
                "success": True,
                "text": full_text,
                "is_scanned": False,
                "page_count": page_count,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": f"Failed to parse PDF document: {str(e)}"
            }

    @staticmethod
    def extract_text_from_docx(docx_path: str) -> dict:
        """
        Extracts raw text from Word .docx documents, reading paragraphs and tables.
        """
        if not os.path.exists(docx_path):
            return {"success": False, "text": "", "error": "The specified file was not found on disk."}

        try:
            import docx
            doc = docx.Document(docx_path)
            extracted_text = []

            # Extract paragraphs
            for paragraph in doc.paragraphs:
                cleaned = paragraph.text.strip()
                if cleaned:
                    extracted_text.append(cleaned)

            # Extract table contents (common in resume layouts)
            for table in doc.tables:
                for row in table.rows:
                    row_parts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_parts:
                        extracted_text.append(" | ".join(row_parts))

            full_text = "\n\n".join(extracted_text).strip()
            if not full_text:
                return {
                    "success": False,
                    "text": "",
                    "is_scanned": False,
                    "error": "The Word document (.docx) does not contain extractable text."
                }

            return {
                "success": True,
                "text": full_text,
                "is_scanned": False,
                "page_count": 1,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": f"Failed to parse Word (.docx) document: {str(e)}"
            }

    @staticmethod
    def extract_text_from_doc(doc_path: str) -> dict:
        """
        Extracts text from legacy .doc or multi-format Word documents.
        Attempts docx parser first, falls back to RTF, text encodings, and binary string extraction.
        """
        if not os.path.exists(doc_path):
            return {"success": False, "text": "", "error": "The specified file was not found on disk."}

        # 1. Attempt docx parser (many modern web downloads name docx files as .doc)
        try:
            import docx
            doc = docx.Document(doc_path)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            if paragraphs:
                return {
                    "success": True,
                    "text": "\n\n".join(paragraphs).strip(),
                    "is_scanned": False,
                    "page_count": 1,
                    "error": None
                }
        except Exception:
            pass

        # 2. Attempt RTF decoding or plain text decoding
        try:
            with open(doc_path, "rb") as f:
                content = f.read()

            if content.startswith(b"{\\rtf"):
                cleaned_rtf = ResumeService._strip_rtf(content.decode("latin1", errors="ignore"))
                if cleaned_rtf.strip():
                    return {
                        "success": True,
                        "text": cleaned_rtf.strip(),
                        "is_scanned": False,
                        "page_count": 1,
                        "error": None
                    }

            # 3. Extract readable text strings from binary OLE stream (Word 97-2003)
            # Find contiguous readable ASCII (length >= 4) and UTF-16LE characters
            ascii_strings = re.findall(rb"[\x20-\x7E\t\r\n]{4,}", content)
            utf16_strings = re.findall(rb"(?:[\x20-\x7E][\x00]){4,}", content)

            extracted_parts = []
            for s in ascii_strings:
                text_part = s.decode("latin1", errors="ignore").strip()
                # Exclude internal MS Word stream headers and font table identifiers
                if text_part and not text_part.startswith(("Normal", "Microsoft", "Times", "Courier", "Calibri", "Font", "Word.")):
                    extracted_parts.append(text_part)

            for u in utf16_strings:
                try:
                    text_part = u.decode("utf-16le", errors="ignore").strip()
                    if text_part and not text_part.startswith(("Normal", "Microsoft", "Times", "Courier", "Calibri", "Font", "Word.")):
                        extracted_parts.append(text_part)
                except Exception:
                    pass

            full_text = "\n".join(extracted_parts).strip()
            if full_text and len(full_text) > 40:
                return {
                    "success": True,
                    "text": full_text,
                    "is_scanned": False,
                    "page_count": 1,
                    "error": None
                }

            return {
                "success": False,
                "text": "",
                "error": "Could not extract readable text from the legacy .doc file. Please re-save as .docx or .pdf for optimal extraction."
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": f"Failed to parse Word (.doc) document: {str(e)}"
            }

    @staticmethod
    def extract_text_from_txt(txt_path: str) -> dict:
        """
        Extracts raw text from plain text or rich text format (.txt, .rtf, .md).
        """
        if not os.path.exists(txt_path):
            return {"success": False, "text": "", "error": "The specified file was not found on disk."}

        encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252", "utf-16"]
        for enc in encodings:
            try:
                with open(txt_path, "r", encoding=enc, errors="replace") as f:
                    content = f.read()

                if content.strip().startswith("{\\rtf"):
                    content = ResumeService._strip_rtf(content)

                if content.strip():
                    return {
                        "success": True,
                        "text": content.strip(),
                        "is_scanned": False,
                        "page_count": 1,
                        "error": None
                    }
            except Exception:
                continue

        return {
            "success": False,
            "text": "",
            "error": "Failed to decode the text file content."
        }

    @staticmethod
    def _strip_rtf(text: str) -> str:
        """Helper to strip basic RTF markup."""
        pattern = re.compile(r"\\([a-z]{1,32})(-?\d+)? ?|\\\'([0-9a-f]{2})|\\([^a-z])|([{}])|[\r\n]+|(.)", re.I)
        destinations = frozenset(["fonttbl", "colortbl", "stylesheet", "info"])
        stack = []
        ignorable = False
        out = []
        for match in pattern.finditer(text):
            word, arg, hex_code, char, brace, other = match.groups()
            if brace:
                if brace == "{":
                    stack.append(ignorable)
                elif brace == "}":
                    if stack:
                        ignorable = stack.pop()
            elif word:
                if word in destinations:
                    ignorable = True
                elif word == "par":
                    out.append("\n")
            elif hex_code:
                if not ignorable:
                    out.append(chr(int(hex_code, 16)))
            elif other:
                if not ignorable:
                    out.append(other)
        return "".join(out).strip()

    @classmethod
    def extract_text_from_document(cls, file_path: str) -> dict:
        """
        Universal document extractor that automatically routes to the proper parser
        based on the file extension (.pdf, .docx, .doc, .txt, .rtf, .odt).
        """
        ext = Path(file_path).suffix.lower().lstrip(".")

        if ext == "pdf":
            return cls.extract_text_from_pdf(file_path)
        elif ext == "docx":
            return cls.extract_text_from_docx(file_path)
        elif ext == "doc":
            return cls.extract_text_from_doc(file_path)
        elif ext in ("txt", "rtf", "md", "odt", "text"):
            return cls.extract_text_from_txt(file_path)
        else:
            # Fallback strategy: try PDF first, then docx, then txt
            pdf_attempt = cls.extract_text_from_pdf(file_path)
            if pdf_attempt["success"]:
                return pdf_attempt

            docx_attempt = cls.extract_text_from_docx(file_path)
            if docx_attempt["success"]:
                return docx_attempt

            return cls.extract_text_from_txt(file_path)

    @staticmethod
    def extract_skills_and_recommendations(text: str) -> dict:
        """
        Analyzes the extracted resume text against the configurable skills dictionary.
        Returns identified skills and domain track recommendations.
        """
        if not text:
            return {
                "skills": [],
                "recommendations": []
            }

        cleaned_text = " " + re.sub(r"[^\w\s\+\#\./\-]", " ", text.lower()) + " "
        detected_skills = set()

        for category, keywords in SKILLS_DICTIONARY.items():
            for kw in keywords:
                # Use word boundary matching for safety
                pattern = r"(?:\b|\s)" + re.escape(kw.lower()) + r"(?:\b|\s)"
                if re.search(pattern, cleaned_text):
                    detected_skills.add(category)
                    break

        detected_list = sorted(list(detected_skills))

        # Recommend domains based on matched skills
        recommended_domains = []
        for domain, req_skills in DOMAIN_MAPPING.items():
            matches = [s for s in req_skills if s in detected_list]
            if len(matches) >= 2 or (len(req_skills) == 2 and len(matches) >= 1):
                recommended_domains.append(domain)

        if not recommended_domains and detected_list:
            recommended_domains.append("General Technical Preparation")

        return {
            "skills": detected_list,
            "recommendations": recommended_domains
        }

    @staticmethod
    def save_uploaded_file(file_storage, upload_folder: str, user_id: int, allowed_extensions=None) -> dict:
        """
        Validates, sanitizes, and saves the uploaded resume file securely.
        Supports .pdf, .docx, .doc, .txt, .rtf, .odt formats.
        """
        if allowed_extensions is None:
            allowed_extensions = SUPPORTED_EXTENSIONS

        filename = secure_filename(file_storage.filename)
        if not filename:
            return {"success": False, "error": "Invalid file name provided."}

        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in allowed_extensions:
            formats_str = ", ".join(f".{e}" for e in sorted(allowed_extensions))
            return {
                "success": False,
                "error": f"Unsupported file type (.{ext}). Supported formats: {formats_str}."
            }

        os.makedirs(upload_folder, exist_ok=True)
        safe_name = f"user_{user_id}_{secure_filename(filename)}"
        destination = os.path.join(upload_folder, safe_name)

        try:
            file_storage.save(destination)
            return {
                "success": True,
                "filename": safe_name,
                "filepath": destination,
                "extension": ext
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to save uploaded file: {str(e)}"
            }

    # Backward-compatibility alias
    save_uploaded_pdf = save_uploaded_file
