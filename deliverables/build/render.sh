#!/bin/bash
# Render a .docx/.pptx to PDF with the ONLYOFFICE converter (for visual checks). Usage: render.sh in.docx out.pdf
set -e
IN="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; OUT="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"
F="$HOME/Library/Application Support/asc.onlyoffice.ONLYOFFICE/data/fonts"
XML=$(mktemp /tmp/x2t.XXXXXX.xml)
cat > "$XML" <<X
<?xml version="1.0" encoding="utf-8"?>
<TaskQueueDataConvert xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<m_sFileFrom>$IN</m_sFileFrom><m_sFileTo>$OUT</m_sFileTo><m_nFormatTo>513</m_nFormatTo>
<m_sAllFontsPath>$F/AllFonts.js</m_sAllFontsPath><m_sFontDir>$F</m_sFontDir><m_bIsNoBase64>true</m_bIsNoBase64>
</TaskQueueDataConvert>
X
/Applications/ONLYOFFICE.app/Contents/Resources/converter/x2t "$XML" >/dev/null 2>&1 || true
rm -f "$XML"; ls -la "$OUT"
