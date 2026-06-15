#!/usr/bin/env zsh
# ElevenLabs voiceover for the Sentinel demo. Brian voice. Idempotent (skips existing).
set -e
cd "$(dirname "$0")"
mkdir -p audio
VOICE="nPczCjzI2devNBz1zQrb"   # Brian
MODEL="eleven_multilingual_v2"

typeset -A CLIPS
CLIPS[money]="Paste a contract into Sentinel. Two engines grade it in seconds, Slither and an AI model. Here it flagged a critical bug. Funds the owner could drain."
CLIPS[onchain]="The verdict is written to Mantle. The report is hashed, so the grade is tamper-proof and anyone can verify it."
CLIPS[registry]="Every contract it grades lives in one on-chain registry. Pass or fail, A through F, read live from the chain."
CLIPS[composable]="Each grade binds to the agent's ERC-8004 identity. One call, isAttestedSafe, lets any contract refuse an agent that never passed."
CLIPS[close]="Sentinel. Audit any agent, and prove it on-chain."

ORDER=(money onchain registry composable close)
for key in $ORDER; do
  out="audio/${key}.mp3"
  if [ -s "$out" ]; then echo "skip $key (exists)"; continue; fi
  text="${CLIPS[$key]}"
  payload=$(python3 -c "import json,sys; print(json.dumps({'text': sys.argv[1], 'model_id': '$MODEL', 'voice_settings': {'stability': 0.82, 'similarity_boost': 0.65, 'style': 0.03, 'use_speaker_boost': True}}))" "$text")
  http=$(curl -s -w "%{http_code}" -o "$out" -X POST \
    "https://api.elevenlabs.io/v1/text-to-speech/${VOICE}" \
    -H "xi-api-key: ${ELEVENLABS_API_KEY}" -H "Content-Type: application/json" \
    --data "$payload")
  # validate: real mp3, not error JSON
  if [ "$http" != "200" ] || head -c 1 "$out" | grep -q "{"; then
    echo "FAIL $key (http $http): $(head -c 160 "$out")"; rm -f "$out"; exit 1
  fi
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out" 2>/dev/null)
  echo "ok $key -> ${dur}s"
done
echo "audio done"
