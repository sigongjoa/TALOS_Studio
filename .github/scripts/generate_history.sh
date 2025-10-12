#!/bin/bash

# Exit on error and print commands
set -ex

HISTORY_FILE="docs/manga_distribution_research/deployment_history.json"
OUTPUT_DIR="output_for_deployment"

# Always create a clean output directory
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# --- Create current deployment assets ---
SHORT_SHA=$(echo $GITHUB_SHA | cut -c1-7)
mkdir -p "$OUTPUT_DIR/$SHORT_SHA"
cp -a ./output_visualizations/* "$OUTPUT_DIR/$SHORT_SHA/" 2>/dev/null || echo "No visualization output to copy."

# --- Check for [publish] flag and update history file ---
if [[ "$COMMIT_MSG" == *"[publish]"* ]]; then
  echo "[publish] flag detected. Updating history file..."
  
  COMMIT_MSG_CLEAN=$(echo "$COMMIT_MSG" | sed 's/"/\"/g' | sed 's/\\[publish\\]//g' | xargs)
  TIMESTAMP=$(git log -1 --format=%ct -- "$GITHUB_SHA")

  # Create a new JSON object for the current entry
  NEW_ENTRY=$(jq -n \
                --arg hash "$SHORT_SHA" \
                --arg msg "$COMMIT_MSG_CLEAN" \
                --arg ts "$TIMESTAMP" \
                '{hash: $hash, message: $msg, timestamp: $ts}')

  # Add new entry to the history file (prepend to the array)
  jq --argjson new_entry "$NEW_ENTRY" '[$new_entry] + .' "$HISTORY_FILE" > tmp.json && mv tmp.json "$HISTORY_FILE"

  # --- Commit and push the updated history file ---
  git config --global user.name 'github-actions[bot]'
  git config --global user.email 'github-actions[bot]@users.noreply.github.com'
  git add "$HISTORY_FILE"
  # Check if there are changes to commit
  if ! git diff-index --quiet HEAD; then
    git commit -m "Docs: Update deployment history [skip ci]"
    git push
  else
    echo "History file is already up to date."
  fi
fi

# --- Generate index.html from the latest history file ---
echo "Generating index.html from $HISTORY_FILE..."

# 1. Write top part of the HTML
cat <<'EOF' > "$OUTPUT_DIR/index.html"
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

# 2. Generate the <ul> list dynamically from JSON
LATEST_SHA=$(jq -r '.[0].hash // ""' "$HISTORY_FILE")
jq -c '.[]' "$HISTORY_FILE" | while read -r entry; do
    HASH=$(echo "$entry" | jq -r '.hash')
    MSG=$(echo "$entry" | jq -r '.message')
    cat <<EOT >> "$OUTPUT_DIR/index.html"
<li class="p-4 bg-background-light dark:bg-background-dark rounded-md flex items-center justify-between hover:shadow-lg transition-shadow duration-300">
<div class="flex items-center">
<span class="material-icons text-green-500 mr-3">check_circle</span>
<div>
<a class="font-mono text-lg text-primary hover:underline" href="./$HASH/">$HASH</a>
<p class="text-sm text-subtle-light dark:text-subtle-dark">$MSG</p>
</div>
</div>
</li>
EOT
done

# 3. Write middle part of HTML
cat <<'EOF' >> "$OUTPUT_DIR/index.html"
</ul>
</div>
<div class="mt-12">
<h2 class="text-3xl font-bold font-display mb-6">Latest Visualization Result</h2>
<div class="bg-card-light dark:bg-card-dark p-1 sm:p-2 rounded-lg shadow-md border border-border-light dark:border-border-dark">
EOF

# 4. Add the iframe for the latest result
if [ -n "$LATEST_SHA" ]; then
  echo "<iframe src=\"./$LATEST_SHA/\"></iframe>" >> "$OUTPUT_DIR/index.html"
else
  echo "<p class=\"text-center text-subtle-light dark:text-subtle-dark\">No published deployments to show yet.</p>" >> "$OUTPUT_DIR/index.html"
fi

# 5. Write the final part of the HTML
cat <<'EOF' >> "$OUTPUT_DIR/index.html"
</div>
</div>
</main>
</div>
</body></html>
EOF