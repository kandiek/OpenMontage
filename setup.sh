#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------
# System dependencies
# ------------------------------------------------------------
apt-get update -y -qq
apt-get install -y -qq ffmpeg gh git curl

# ------------------------------------------------------------
# Python deps: OpenMontage pipeline + Piper TTS
# ------------------------------------------------------------
if [ -f requirements.txt ]; then
  python -m pip install -r requirements.txt
  fi

  python -m pip install piper-tts

  # ------------------------------------------------------------
  # Node deps for Remotion
  # ------------------------------------------------------------
  if [ -d remotion-composer ]; then
    cd remotion-composer
      npm install
        cd ..
        fi

        # ------------------------------------------------------------
        # Xiaohei skill: repo-scoped primary install
        #
        # This is the source of truth for Codex repo/cloud tasks because
        # it travels with the repository.
        # ------------------------------------------------------------
        XIAOHEI_REPO="https://github.com/helloianneo/ian-xiaohei-illustrations"
        REPO_SKILLS_DIR=".agents/skills"
        XIAOHEI_SKILL_DIR="$REPO_SKILLS_DIR/ian-xiaohei-illustrations"
        TMP_XIAOHEI_DIR="/tmp/xh"

        mkdir -p "$REPO_SKILLS_DIR"

        # Self-healing install:
        # If the skill folder is missing OR exists but has no SKILL.md, reinstall it.
        if [ ! -f "$XIAOHEI_SKILL_DIR/SKILL.md" ]; then
          rm -rf "$XIAOHEI_SKILL_DIR"
            rm -rf "$TMP_XIAOHEI_DIR"

              git clone --depth 1 "$XIAOHEI_REPO" "$TMP_XIAOHEI_DIR"
                cp -R "$TMP_XIAOHEI_DIR/ian-xiaohei-illustrations" "$REPO_SKILLS_DIR/"

                  rm -rf "$TMP_XIAOHEI_DIR"
                  fi

                  # ------------------------------------------------------------
                  # Embed Xiaohei style lock directly into SKILL.md
                  #
                  # This makes the hard style rules travel with the skill itself.
                  # ------------------------------------------------------------
                  STYLE_LOCK_MARKER="<!-- XIAOHEI-STYLE-LOCK -->"
                  SKILL_FILE="$XIAOHEI_SKILL_DIR/SKILL.md"

                  if [ ! -f "$SKILL_FILE" ]; then
                    echo "ERROR: Xiaohei skill installed, but SKILL.md was not found at:"
                      echo "$SKILL_FILE"
                        exit 1
                        fi

                        if ! grep -Fq "$STYLE_LOCK_MARKER" "$SKILL_FILE"; then
                          cat >> "$SKILL_FILE" <<EOF

                          $STYLE_LOCK_MARKER
                          ## Xiaohei Style Lock

                          When the user asks for Xiaohei, Ian Xiaohei, Xiaohei illustration, or xiaohei style, do not invent a new mascot, cartoon style, black creature, or generic hand-drawn illustration language.

                          Use Ian Xiaohei illustration rules only:

                          - pure white background
                          - thin black hand-drawn wobbly line art
                          - lots of whitespace
                          - sparse handwritten Chinese annotations in red, orange, and blue
                          - Xiaohei is a solid black absurd creature
                          - Xiaohei has white dot eyes
                          - Xiaohei has thin stick legs
                          - Xiaohei has a blank neutral expression
                          - Xiaohei must actively perform the core action
                          - one image = one core metaphor, process, structure, state, or judgment
                          - the image should feel clever, absurd, calm, clean, and crisp
                          - Xiaohei is not decoration; Xiaohei performs the concept

                          Forbidden:

                          - cute mascot style
                          - colorful cartoon
                          - anime style
                          - Pixar style
                          - Disney style
                          - glossy vector illustration
                          - polished corporate illustration
                          - PPT infographic style
                          - realistic human figure
                          - shadows
                          - gradients
                          - paper texture
                          - beige background
                          - excessive text
                          - using Xiaohei as decoration only
                          - replacing Xiaohei with a different black character

                          Default aspect ratios:

                          - 16:9 for article illustrations and landscape video
                          - 9:16 for Shorts, TikTok, Reels, Snapchat, and vertical video

                          For Remotion work:

                          - Keep Xiaohei as an imported/generated asset or prompt-driven visual layer.
                          - Do not recreate Xiaohei with generic CSS shapes unless explicitly requested.
                          - If image generation is not configured in the repo, create prompts, templates, and asset folders only.
                          - Do not fake image files.
EOF
                          fi

                          # ------------------------------------------------------------
                          # Optional local fallbacks
                          #
                          # Repo-scoped .agents/skills remains the source of truth.
                          # These are convenience copies for local CLI / IDE sessions.
                          # ------------------------------------------------------------
                          USER_SKILLS_DIR="$HOME/.agents/skills"
                          CODEX_HOME_SKILLS_DIR="${CODEX_HOME:-$HOME/.codex}/skills"

                          mkdir -p "$USER_SKILLS_DIR" "$CODEX_HOME_SKILLS_DIR"

                          rm -rf "$USER_SKILLS_DIR/ian-xiaohei-illustrations"
                          cp -R "$XIAOHEI_SKILL_DIR" "$USER_SKILLS_DIR/"

                          rm -rf "$CODEX_HOME_SKILLS_DIR/ian-xiaohei-illustrations"
                          cp -R "$XIAOHEI_SKILL_DIR" "$CODEX_HOME_SKILLS_DIR/"

                          # ------------------------------------------------------------
                          # Human reference doc
                          # ------------------------------------------------------------
                          mkdir -p docs

                          cat > docs/xiaohei-style-lock.md <<'EOF'
                          # Xiaohei Style Lock

                          The enforced version of these rules is embedded in:

                          .agents/skills/ian-xiaohei-illustrations/SKILL.md

                          This file exists for human reference and manual prompting.

                          ## Core rules

                          - pure white background
                          - thin black hand-drawn wobbly line art
                          - lots of whitespace
                          - sparse handwritten Chinese annotations in red, orange, and blue
                          - Xiaohei is a solid black absurd creature
                          - Xiaohei has white dot eyes
                          - Xiaohei has thin stick legs
                          - Xiaohei has a blank neutral expression
                          - Xiaohei must actively perform the core action
                          - one image = one core metaphor, process, structure, state, or judgment
                          - clever, absurd, calm, clean, and crisp

                          ## Forbidden

                          - cute mascot style
                          - colorful cartoon
                          - anime style
                          - Pixar style
                          - Disney style
                          - glossy vector illustration
                          - polished corporate illustration
                          - PPT infographic style
                          - realistic human figure
                          - shadows
                          - gradients
                          - paper texture
                          - beige background
                          - excessive text
                          - using Xiaohei as decoration only
                          - replacing Xiaohei with a different black character

                          ## Default aspect ratios

                          - 16:9 for article illustrations and landscape video
                          - 9:16 for Shorts, TikTok, Reels, Snapchat, and vertical video
EOF

                          # ------------------------------------------------------------
                          # AGENTS.md project instruction
                          #
                          # Codex reads AGENTS.md before doing work. This reinforces
                          # Xiaohei behavior at the project level. Appends if the file
                          # already exists and does not already contain the Xiaohei rule.
                          # ------------------------------------------------------------
                          AGENTS_MARKER="Xiaohei Illustration Rule"

                          AGENTS_CONTENT=$(cat <<'EOF'

                          # Project Instructions

                          ## Xiaohei Illustration Rule

                          When the user asks for Xiaohei, Ian Xiaohei, Xiaohei illustration, or xiaohei style:

                          1. Use the skill:

                             $ian-xiaohei-illustrations

                             2. Do not invent a new mascot, cartoon, black creature, or generic hand-drawn style.

                             3. Follow the embedded style lock in:

                                .agents/skills/ian-xiaohei-illustrations/SKILL.md

                                4. Xiaohei image prompts must preserve:

                                   - pure white background
                                      - thin black wobbly hand-drawn line art
                                         - lots of whitespace
                                            - solid black Xiaohei creature
                                               - white dot eyes
                                                  - thin stick legs
                                                     - blank neutral expression
                                                        - sparse red/orange/blue handwritten Chinese annotations
                                                           - one metaphor per image
                                                              - Xiaohei actively performs the core action

                                                              5. For vertical social video, default to 9:16.

                                                              6. For landscape article/video, default to 16:9.

                                                              7. If the task involves Remotion, keep Xiaohei as an imported/generated asset or prompt-driven visual layer. Do not recreate Xiaohei with generic CSS shapes unless explicitly requested.

                                                              8. If image generation is not configured in the repo, create prompts, templates, and asset folders only. Do not fake image files.

                                                              9. Any generated prompt for Xiaohei must say explicitly that Xiaohei is the solid black absurd creature with white dot eyes, thin stick legs, and a blank neutral expression.
EOF
                                                              )

                                                              if [ -f AGENTS.md ]; then
                                                                if ! grep -Fq "$AGENTS_MARKER" AGENTS.md; then
                                                                    printf "%s\n" "$AGENTS_CONTENT" >> AGENTS.md
                                                                      fi
                                                                      else
                                                                        printf "%s\n" "$AGENTS_CONTENT" > AGENTS.md
                                                                        fi

                                                                        echo "Setup complete."
                                                                        echo "Xiaohei skill primary: $XIAOHEI_SKILL_DIR"
                                                                        echo "Xiaohei skill user fallback: $USER_SKILLS_DIR/ian-xiaohei-illustrations"
                                                                        echo "Xiaohei skill CODEX_HOME fallback: $CODEX_HOME_SKILLS_DIR/ian-xiaohei-illustrations"
                                                                        echo "Style lock: embedded in $SKILL_FILE"
                                                                        echo "Human reference: docs/xiaohei-style-lock.md"
                                                                        echo "Codex project instructions: AGENTS.md"