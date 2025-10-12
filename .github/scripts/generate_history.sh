#!/bin/bash

# Exit on error and print commands
set -ex

# --- Pre-fetch all commit data ---
GIT_LOG_DATA=$(mktemp)
git log --all --pretty=format:"%h|%ct|%s" > "$GIT_LOG_DATA"

# Ensure the gh-pages directory exists
mkdir -p ./gh-pages

# --- Create current deployment ---
SHORT_SHA=$(echo $GITHUB_SHA | cut -c1-7)
mkdir -p ./gh-pages/$SHORT_SHA
cp -a ./output_visualizations/* ./gh-pages/$SHORT_SHA/ 2>/dev/null || echo "No visualization output to copy."

# --- Find all valid deployments ---
DEPLOYMENTS=()
for dir in ./gh-pages/*; do
  if [ -d "$dir" ]; then
    COMMIT_HASH=$(basename "$dir")
    # Check if the hash from the directory name exists in our pre-fetched log
    if grep -q "^$COMMIT_HASH|" "$GIT_LOG_DATA"; then
      DEPLOYMENTS+=("$COMMIT_HASH")
    fi
  fi
done

# --- Determine latest deployment ---
LATEST_SHA=""
LATEST_TIMESTAMP=0
for HASH in "${DEPLOYMENTS[@]}"; do
  TIMESTAMP=$(grep "^$HASH|" "$GIT_LOG_DATA" | cut -d'|' -f2)
  if [ "$TIMESTAMP" -gt "$LATEST_TIMESTAMP" ]; then
    LATEST_TIMESTAMP=$TIMESTAMP
    LATEST_SHA=$HASH
  fi
done

# --- Generate index.html ---

# 1. Write top part of the HTML
cat <<'EOF' > ./gh-pages/index.html
<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Research Deployment History</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,typography"></script>
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"/>
<script>
    tailwind.config = {
      darkMode: "class",
      theme: {
        extend: {
          colors: {
            primary: "#4f46e5",
            "background-light": "#f8fafc",
            "background-dark": "#0f172a",
            "card-light": "#ffffff",
            "card-dark": "#1e293b",
            "text-light": "#1e293b",
            "text-dark": "#e2e8f0",
            "subtle-light": "#64748b",
            "subtle-dark": "#94a3b8",
            "border-light": "#e2e8f0",
            "border-dark": "#334155",
          },
          fontFamily: {
            display: ["Inter", "sans-serif"],
          },
          borderRadius: {
            DEFAULT: "0.5rem",
          },
        },
      },
    };
  </script>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    body { font-family: 'Inter', sans-serif; }
    iframe { width: 100%; height: 800px; border: none; border-radius: 0.5rem; }
</style>
</head>
<body class="bg-background-light dark:bg-background-dark text-text-light dark:text-text-dark antialiased">
<div class="container mx-auto px-4 py-8">
<header class="mb-8">
<h1 class="text-4xl font-bold font-display text-text-light dark:text-text-dark">Research Deployment History</h1>
<p class="text-lg text-subtle-light dark:text-subtle-dark mt-2">A versioned archive of all research deployments for the "Manga Image Distribution" project.</p>
</header>
<main>
<div class="bg-card-light dark:bg-card-dark p-6 rounded-lg shadow-md border border-border-light dark:border-border-dark">
<h2 class="text-2xl font-semibold font-display mb-4 flex items-center">
<span class="material-icons mr-2 text-primary">history</span>
          Deployment Log
        </h2>
<ul class="space-y-3">
EOF

# 2. Generate the <ul> list dynamically
SORTABLE_FILE=$(mktemp)
for HASH in "${DEPLOYMENTS[@]}"; do
    grep "^$HASH|" "$GIT_LOG_DATA" | awk -F'|' '{print $2 ":" $1}' >> "$SORTABLE_FILE"
done

cat "$SORTABLE_FILE" | sort -t: -k1 -nr | cut -d: -f2 | while read -r HASH;
do
    COMMIT_DATA=$(grep "^$HASH|" "$GIT_LOG_DATA")
    COMMIT_MSG=$(echo "$COMMIT_DATA" | cut -d'|' -f3)
    cat <<EOT >> ./gh-pages/index.html
<li class="p-4 bg-background-light dark:bg-background-dark rounded-md flex items-center justify-between hover:shadow-lg transition-shadow duration-300">
<div class="flex items-center">
<span class="material-icons text-green-500 mr-3">check_circle</span>
<div>
<a class="font-mono text-lg text-primary hover:underline" href="./$HASH/">$HASH</a>
<p class="text-sm text-subtle-light dark:text-subtle-dark">$COMMIT_MSG</p>
</div>
</div>
</li>
EOT
done
rm "$SORTABLE_FILE"
rm "$GIT_LOG_DATA"

# 3. Write middle part of HTML
cat <<'EOF' >> ./gh-pages/index.html
</ul>
</div>
<div class="mt-12">
<h2 class="text-3xl font-bold font-display mb-6">Latest Visualization Result</h2>
<div class="bg-card-light dark:bg-card-dark p-1 sm:p-2 rounded-lg shadow-md border border-border-light dark:border-border-dark">
EOF

# 4. Add the iframe for the latest result
if [ -n "$LATEST_SHA" ]; then
  echo "<iframe src=\"./$LATEST_SHA/\"></iframe>" >> ./gh-pages/index.html
else
  echo "<p class=\"text-center text-subtle-light dark:text-subtle-dark\">No deployments to show yet.</p>" >> ./gh-pages/index.html
fi

# 5. Write the final part of the HTML
cat <<'EOF' >> ./gh-pages/index.html
</div>
</div>
</main>
</div>
</body></html>
EOF
