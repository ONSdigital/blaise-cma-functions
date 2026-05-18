import json
import sys

# =========================
# CONFIG
# =========================

VENDOR_PREFIXES = [
    "gcr.io",
    "us-docker.pkg.dev",
    "google",
    "cloudfunctions",
    "cloud-run",
]

# =========================
# CLASSIFICATION
# =========================


def classify(vuln, result):
    pkg = (vuln.get("PkgName") or "").lower()
    pkg_type = (result.get("Type") or "").lower()

    # -------------------------
    # 1. OS LAYER
    # -------------------------
    os_keywords = [
        "lib",
        "curl",
        "git",
        "openssl",
        "imagemagick",
        "krb5",
        "ffmpeg",
        "openjpeg",
        "intel",
        "perl",
        "bash",
        "zlib",
        "glib",
        "gcc",
        "gdkpixbuf",
    ]

    if pkg_type in ["os", "debian", "ubuntu", "alpine"]:
        return "OS"

    if any(k in pkg for k in os_keywords):
        return "OS"

    # -------------------------
    # 2. LANGUAGE / RUNTIME ECOSYSTEM
    # -------------------------
    lang_ecosystems = [
        "golang.org",
        "google.golang.org",
        "github.com",
        "gopkg",
        "pkg.go",
        "pip",
        "pypi",
        "poetry",
        "virtualenv",
        "stdlib",
    ]

    if any(k in pkg for k in lang_ecosystems):
        return "LANG_RUNTIME"

    # -------------------------
    # 3. UNKNOWN (possible app layer)
    # -------------------------
    return "UNKNOWN"


# =========================
# MAIN
# =========================

all_os = []
all_lang = []
all_unknown = []


def main(file):
    with open(file) as f:
        data = json.load(f)

    image = data.get("ArtifactName", "")

    print("\n==============================")
    print(f"📦 Scanned Image: {image}")
    print("==============================\n")

    fixable = []
    no_fix = []

    print("🔍 SCANNING CVEs...\n")

    for result in data.get("Results", []):
        for vuln in result.get("Vulnerabilities", []):

            cve = vuln.get("VulnerabilityID")
            pkg = vuln.get("PkgName")
            severity = vuln.get("Severity")
            fixed = vuln.get("FixedVersion")

            category = classify(vuln, result)

            print(f"🔍 {cve} | {pkg} | {severity} | fix={fixed} | {category}")

            if category == "OS":
                all_os.append(vuln)

            elif category == "LANG_RUNTIME":
                all_lang.append(vuln)

            else:
                all_unknown.append(vuln)

            # classification for CI decision
            # =========================
            # CI DECISION RULES
            # =========================

            if fixed and category != "OS":
                fixable.append((vuln, category))

            else:
                no_fix.append((vuln, category))

    # =========================
    # SUMMARY
    # =========================

    # =========================
    # SUMMARY
    # =========================

    print("\n================ SUMMARY ================\n", flush=True)

    # =========================
    # SUMMARY
    # =========================

    print("\n================ SUMMARY ================\n", flush=True)

    print(
        f"📦 TOTAL CVEs: {len(all_os) + len(all_lang) + len(all_unknown)}", flush=True
    )

    print("\n📊 Breakdown by layer:", flush=True)
    print(f"   OS            : {len(all_os)}", flush=True)
    print(f"   LANG_RUNTIME  : {len(all_lang)}", flush=True)
    print(f"   REAL_APP      : {len(all_unknown)}", flush=True)

    # =========================
    # EFFECTIVE CI FAILURES
    # =========================

    real_app_fixable = []

    for vuln in all_unknown:
        if vuln.get("FixedVersion"):
            real_app_fixable.append(vuln)

    print("\n📌 Effective CI Counts:", flush=True)
    print(f"   REAL_APP_FIXABLE : {len(real_app_fixable)}", flush=True)

    # fail ONLY for real app vulnerabilities
    if real_app_fixable:

        print("\n❌ BUILD FAILED - Application vulnerabilities found\n", flush=True)

        for vuln in real_app_fixable[:20]:
            print(
                f"  - {vuln.get('VulnerabilityID')} "
                f"({vuln.get('PkgName')}) "
                f"[{vuln.get('Severity')}]",
                flush=True,
            )

        sys.exit(1)

    print(
        "\n✅ BUILD PASSED - only OS/runtime/vendor vulnerabilities detected",
        flush=True,
    )

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1])
