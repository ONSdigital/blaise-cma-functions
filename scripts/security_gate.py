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


def main(file):
    with open(file) as f:
        data = json.load(f)

    image = data.get("ArtifactName", "")

    print("\n==============================")
    print(f"📦 Scanned Image: {image}")
    print("==============================\n")

    fixable = []
    no_fix = []

    # counters for breakdown
    os_count = 0
    lang_count = 0
    unknown_count = 0

    print("🔍 SCANNING CVEs...\n")

    for result in data.get("Results", []):
        for vuln in result.get("Vulnerabilities", []):

            cve = vuln.get("VulnerabilityID")
            pkg = vuln.get("PkgName")
            severity = vuln.get("Severity")
            fixed = vuln.get("FixedVersion")

            category = classify(vuln, result)

            print(f"🔍 {cve} | {pkg} | {severity} | fix={fixed} | {category}")

            # update counters
            if category == "OS":
                os_count += 1
            elif category == "LANG_RUNTIME":
                lang_count += 1
            else:
                unknown_count += 1

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
    # CI DECISION
    # =========================

    # only fail for REAL app vulnerabilities
    real_app_fixable = [item for item in fixable if item[1] == "UNKNOWN"]

    lang_runtime_fixable = [item for item in fixable if item[1] == "LANG_RUNTIME"]

    os_fixable = [item for item in fixable if item[1] == "OS"]

    print("\n📌 Effective CI Counts:", flush=True)
    print(f"   REAL_APP      : {len(real_app_fixable)}", flush=True)
    print(f"   LANG_RUNTIME  : {len(lang_runtime_fixable)}", flush=True)
    print(f"   OS            : {len(os_fixable)}", flush=True)

    # fail ONLY if actual app-layer vulnerabilities exist
    if len(real_app_fixable) > 0:

        print("\n❌ BUILD FAILED - Application vulnerabilities found\n", flush=True)

        for vuln, category in real_app_fixable[:20]:
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
