#!/usr/bin/env zsh
# Assemble the Sentinel demo: per-segment fades, 0.5s audio lead, 0.3s gaps, music bed, 48kHz out.
set -e
cd "$(dirname "$0")"
COMP=composites; AUD=audio; SEGD=segments
mkdir -p $SEGD
setopt +o nomatch; rm -f $SEGD/*.mp4 concat.txt

ORDER=(hook audit onchain registry dev cta)
VFADE_IN=0.2; AUDIO_DELAY=0.5; BREATH=0.3; VFADE_OUT=0.2; GAP=0.3

# silent black gap (built once, reused)
ffmpeg -y -f lavfi -i "color=c=black:s=1920x1080:r=30:d=${GAP}" \
  -f lavfi -i "anullsrc=r=44100:cl=stereo" -t ${GAP} \
  -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p -c:a aac -b:a 128k "$SEGD/gap.mp4" -loglevel error

first=1
for clip in $ORDER; do
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$AUD/$clip.mp3")
  TOTAL=$(python3 -c "print(round(${dur}+${AUDIO_DELAY}+${BREATH}+${VFADE_OUT},3))")
  FO_START=$(python3 -c "print(round(${TOTAL}-${VFADE_OUT},3))")
  AFO_START=$(python3 -c "print(round(${AUDIO_DELAY}+${dur}-0.25,3))")
  ffmpeg -y -loop 1 -i "$COMP/$clip.png" -i "$AUD/$clip.mp3" -filter_complex "
    anullsrc=r=44100:cl=stereo,atrim=0:${AUDIO_DELAY}[s];
    [s][1:a]concat=n=2:v=0:a=1[j];
    [j]afade=t=in:st=${AUDIO_DELAY}:d=0.15,afade=t=out:st=${AFO_START}:d=0.25,apad=whole_dur=${TOTAL}[a];
    [0:v]scale=1920:1080,fade=t=in:st=0:d=${VFADE_IN},fade=t=out:st=${FO_START}:d=${VFADE_OUT}[v]
  " -map "[v]" -map "[a]" -t ${TOTAL} \
    -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p -c:a aac -b:a 128k -r 30 "$SEGD/$clip.mp4" -loglevel error
  [ $first -eq 0 ] && echo "file 'segments/gap.mp4'" >> concat.txt
  echo "file 'segments/$clip.mp4'" >> concat.txt
  first=0
  echo "segment $clip -> ${TOTAL}s"
done

# concat (re-encode to kill drift), 48kHz audio
ffmpeg -y -f concat -safe 0 -i concat.txt \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -c:a aac -ar 48000 -b:a 192k "$SEGD/narration.mp4" -loglevel error

vidlen=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SEGD/narration.mp4")
mfo=$(python3 -c "print(round(${vidlen}-1.0,3))")

# mix bg music at ~10% under the voiceover, fade out at the end
ffmpeg -y -i "$SEGD/narration.mp4" -stream_loop -1 -i music/bg.mp3 -filter_complex "
  [1:a]volume=0.10,afade=t=in:st=0:d=1,afade=t=out:st=${mfo}:d=1[m];
  [0:a][m]amix=inputs=2:duration=first:dropout_transition=0[a]
" -map 0:v -map "[a]" -t ${vidlen} \
  -c:v copy -c:a aac -ar 48000 -b:a 192k "mantle-sentinel-demo.mp4" -loglevel error

echo "=== final ==="
ffprobe -v error -show_entries format=duration:stream=sample_rate -of default=noprint_wrappers=1 "mantle-sentinel-demo.mp4"
