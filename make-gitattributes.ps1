$path = "I:\Legal Repository\.gitattributes"

$content = @"
###############################################################################
# .gitattributes for a legal / litigation / investigations repository
###############################################################################

* text=auto

# Windows scripts
*.bat  text eol=crlf
*.cmd  text eol=crlf
*.ps1  text eol=crlf
*.psm1 text eol=crlf
*.psd1 text eol=crlf

# Unix / code / text
*.sh   text eol=lf
*.bash text eol=lf
*.zsh  text eol=lf
*.py   text eol=lf
*.txt        text
*.md         text
*.markdown   text
*.csv        text
*.tsv        text
*.json       text
*.jsonl      text
*.xml        text
*.yml        text
*.yaml       text
*.ini        text
*.cfg        text
*.conf       text
*.log        text
*.sql        text
*.html       text
*.htm        text
*.css        text
*.js         text
*.ts         text
*.jsx        text
*.tsx        text
*.tex        text
*.bib        text
*.vcf        text
*.srt        text

# Legal documents / office files
*.pdf   filter=lfs diff=lfs merge=lfs -text
*.doc   filter=lfs diff=lfs merge=lfs -text
*.docx  filter=lfs diff=lfs merge=lfs -text
*.docm  filter=lfs diff=lfs merge=lfs -text
*.dot   filter=lfs diff=lfs merge=lfs -text
*.dotx  filter=lfs diff=lfs merge=lfs -text
*.dotm  filter=lfs diff=lfs merge=lfs -text
*.rtf   filter=lfs diff=lfs merge=lfs -text
*.odt   filter=lfs diff=lfs merge=lfs -text

*.xls   filter=lfs diff=lfs merge=lfs -text
*.xlsx  filter=lfs diff=lfs merge=lfs -text
*.xlsm  filter=lfs diff=lfs merge=lfs -text
*.xlt   filter=lfs diff=lfs merge=lfs -text
*.xltx  filter=lfs diff=lfs merge=lfs -text
*.xltm  filter=lfs diff=lfs merge=lfs -text
*.ods   filter=lfs diff=lfs merge=lfs -text

*.ppt   filter=lfs diff=lfs merge=lfs -text
*.pptx  filter=lfs diff=lfs merge=lfs -text
*.pptm  filter=lfs diff=lfs merge=lfs -text
*.pot   filter=lfs diff=lfs merge=lfs -text
*.potx  filter=lfs diff=lfs merge=lfs -text
*.potm  filter=lfs diff=lfs merge=lfs -text
*.odp   filter=lfs diff=lfs merge=lfs -text

# Email / discovery
*.msg   filter=lfs diff=lfs merge=lfs -text
*.eml   filter=lfs diff=lfs merge=lfs -text
*.pst   filter=lfs diff=lfs merge=lfs -text
*.ost   filter=lfs diff=lfs merge=lfs -text
*.mbox  filter=lfs diff=lfs merge=lfs -text
*.olm   filter=lfs diff=lfs merge=lfs -text
*.nsf   filter=lfs diff=lfs merge=lfs -text

# Images / scans / exhibits
*.jpg   filter=lfs diff=lfs merge=lfs -text
*.jpeg  filter=lfs diff=lfs merge=lfs -text
*.png   filter=lfs diff=lfs merge=lfs -text
*.gif   filter=lfs diff=lfs merge=lfs -text
*.bmp   filter=lfs diff=lfs merge=lfs -text
*.tif   filter=lfs diff=lfs merge=lfs -text
*.tiff  filter=lfs diff=lfs merge=lfs -text
*.heic  filter=lfs diff=lfs merge=lfs -text
*.webp  filter=lfs diff=lfs merge=lfs -text
*.raw   filter=lfs diff=lfs merge=lfs -text
*.dng   filter=lfs diff=lfs merge=lfs -text
*.psd   filter=lfs diff=lfs merge=lfs -text
*.ai    filter=lfs diff=lfs merge=lfs -text
*.eps   filter=lfs diff=lfs merge=lfs -text

# Audio / video
*.wav   filter=lfs diff=lfs merge=lfs -text
*.mp3   filter=lfs diff=lfs merge=lfs -text
*.m4a   filter=lfs diff=lfs merge=lfs -text
*.aac   filter=lfs diff=lfs merge=lfs -text
*.flac  filter=lfs diff=lfs merge=lfs -text
*.wma   filter=lfs diff=lfs merge=lfs -text
*.mp4   filter=lfs diff=lfs merge=lfs -text
*.mov   filter=lfs diff=lfs merge=lfs -text
*.avi   filter=lfs diff=lfs merge=lfs -text
*.mkv   filter=lfs diff=lfs merge=lfs -text
*.wmv   filter=lfs diff=lfs merge=lfs -text
*.m4v   filter=lfs diff=lfs merge=lfs -text

# Archives / exports
*.zip   filter=lfs diff=lfs merge=lfs -text
*.7z    filter=lfs diff=lfs merge=lfs -text
*.rar   filter=lfs diff=lfs merge=lfs -text
*.tar   filter=lfs diff=lfs merge=lfs -text
*.gz    filter=lfs diff=lfs merge=lfs -text
*.bz2   filter=lfs diff=lfs merge=lfs -text
*.xz    filter=lfs diff=lfs merge=lfs -text
*.cab   filter=lfs diff=lfs merge=lfs -text
*.iso   filter=lfs diff=lfs merge=lfs -text

# Databases / containers
*.db      filter=lfs diff=lfs merge=lfs -text
*.sqlite  filter=lfs diff=lfs merge=lfs -text
*.sqlite3 filter=lfs diff=lfs merge=lfs -text
*.mdb     filter=lfs diff=lfs merge=lfs -text
*.accdb   filter=lfs diff=lfs merge=lfs -text
*.parquet filter=lfs diff=lfs merge=lfs -text
*.feather filter=lfs diff=lfs merge=lfs -text
*.avro    filter=lfs diff=lfs merge=lfs -text

# Certificates / encrypted / packaged
*.p7s   filter=lfs diff=lfs merge=lfs -text
*.pfx   filter=lfs diff=lfs merge=lfs -text
*.p12   filter=lfs diff=lfs merge=lfs -text
*.cer   filter=lfs diff=lfs merge=lfs -text
*.crt   filter=lfs diff=lfs merge=lfs -text
*.key   filter=lfs diff=lfs merge=lfs -text
*.gpg   filter=lfs diff=lfs merge=lfs -text
*.pgp   filter=lfs diff=lfs merge=lfs -text

# CAD / maps
*.dwg   filter=lfs diff=lfs merge=lfs -text
*.dxf   filter=lfs diff=lfs merge=lfs -text
*.kml   filter=lfs diff=lfs merge=lfs -text
*.kmz   filter=lfs diff=lfs merge=lfs -text
"@

Set-Content -Path $path -Value $content -Encoding UTF8
Write-Host "Created $path"
