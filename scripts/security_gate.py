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
            if fixed:
                fixable.append(vuln)
            else:
                no_fix.append(vuln)

    # =========================
    # SUMMARY
    # =========================

    print("\n================ SUMMARY ================\n")

    print(f"🔴 FIXABLE: {len(fixable)}")
    print(f"🟠 NO FIX AVAILABLE: {len(no_fix)}")

    print("\n📊 Breakdown by layer:")
    print(f"   OS           : {os_count}")
    print(f"   LANG_RUNTIME : {lang_count}")
    print(f"   UNKNOWN      : {unknown_count}")

    # =========================
    # CI DECISION
    # =========================

    if fixable:
        print("\n❌ BUILD FAILED - FIXABLE vulnerabilities found")
        sys.exit(1)

    print("\n✅ BUILD PASSED - no fixable vulnerabilities")
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1])
