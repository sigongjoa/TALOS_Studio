#!/bin/bash
set -x # Enable Debug Mode

# Exit on error
set -e

# Ensure the gh-pages directory exists
mkdir -p ./gh-pages

# --- Create current deployment ---
SHORT_SHA=$(echo $GITHUB_SHA | cut -c1-7)
mkdir -p ./gh-pages/$SHORT_SHA
# Use cp -a to preserve attributes, and handle case where output_visualizations might be empty
cp -a ./output_visualizations/* ./gh-pages/$SHORT_SHA/ 2>/dev/null || echo "No visualization output to copy."


# --- Find all valid deployments ---
# Create an array of valid commit hash directories
DEPLOYMENTS=()
for dir in ./gh-pages/*; do
  if [ -d "$dir" ]; then
    COMMIT_HASH=$(basename "$dir")
    # Check if the directory name is a 7-char hex string
    if [[ "$COMMIT_HASH" =~ ^[a-f0-9]{7}$ ]]; then
      # Check if this hash exists in the git history to be sure
      if git cat-file -e "$COMMIT_HASH" 2>/dev/null;
        then
        DEPLOYMENTS+=("$COMMIT_HASH")
      fi
    fi
  fi
done

# --- Determine latest deployment ---
LATEST_SHA=""
LATEST_TIMESTAMP=0
for HASH in "${DEPLOYMENTS[@]}"; do
  TIMESTAMP=$(git log -1 --format=%ct -- "$HASH")
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
# Create a temporary file to hold sortable data
SORTABLE_FILE=$(mktemp)
for HASH in "${DEPLOYMENTS[@]}"; do
    # format: <timestamp>:<hash> 
    echo "$(git log -1 --format=%ct:%H -- "$HASH")" >> "$SORTABLE_FILE"
done

# Sort numerically in reverse (newest first) and read just the hash
cat "$SORTABLE_FILE" | sort -t: -k1 -nr | cut -d: -f2 | while read -r FULL_HASH; do
    HASH=$(echo $FULL_HASH | cut -c1-7)
    COMMIT_MSG=$(git log -1 --format=%s -- "$HASH")
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