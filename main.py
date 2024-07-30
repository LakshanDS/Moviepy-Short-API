import os
import random
import asyncio
import zipfile
import edge_tts
#os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick\magick.exe" # for Windows ImageMagick binary
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.VideoClip import TextClip

# Define file paths
Video_path = "Video/"
Audio_path = "Audio/"
Voice_path = "Voice/Audio.mp3"
Youtube_path = "Outputs/Youtube/"
subtitle_path = "Voice/Audio.srt"
font_path = "Font/PassionOne-Bold.ttf"
Tiktok_path = "Outputs/Tiktok/TikTok.mp4"

def get_video_files(folder): #Get Random Video
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    return [os.path.join(folder, f) for f in os.listdir(folder) if os.path.splitext(f)[1] in video_extensions]

def get_audio_files(folder): #Get Random Audio
    audio_extensions = ['.mp3', '.m4a', '.wav']
    return [os.path.join(folder, f) for f in os.listdir(folder) if os.path.splitext(f)[1] in audio_extensions]

def background_video(video_path, total_length=int, subclip_length=int):
    
    raw_videos = get_video_files(video_path)
    final_clips = []
    clip_length = 0

    while clip_length < total_length:

        video = VideoFileClip(random.choice(raw_videos))
        max_start_time = video.duration - subclip_length
        start_time = random.uniform(0, max_start_time)
        next_clip = video.subclip(start_time, start_time + subclip_length)
        final_clips.append(next_clip)
        clip_length += next_clip.duration

    video = concatenate_videoclips(final_clips).subclip(0, total_length)

    video_width, video_height = video.size

    # Determine the maximum width and height for the 16:9 portrait aspect ratio
    target_height = video_height
    target_width = video_height / 16 * 9

    # Calculate the center crop coordinates
    center_x, center_y = video_width // 2, video_height // 2

    # Calculate the cropping box (central portion)
    crop_x1 = center_x - target_width // 2
    crop_x2 = center_x + target_width // 2
    crop_y1 = center_y - target_height // 2
    crop_y2 = center_y + target_height // 2

    # Ensure the cropping box is within the video's dimensions
    crop_x1 = max(0, crop_x1)
    crop_x2 = min(video_width, crop_x2)
    crop_y1 = max(0, crop_y1)
    crop_y2 = min(video_height, crop_y2)

    # Perform the crop
    return video.crop(x1=crop_x1, y1=crop_y1, x2=crop_x2, y2=crop_y2)

def background_audio(audio_path, total_length=int):
    raw_audio = get_audio_files(audio_path)
    final_clips = []
    clip_length = 0

    while clip_length < total_length:
        audio = AudioFileClip(random.choice(raw_audio))
        final_clips.append(audio)
        clip_length += audio.duration

    return concatenate_audioclips(final_clips).subclip(0, total_length).volumex(0.03).audio_fadeout(3)

async def Voice_generator(text: str, voice: str, rate: str, words_in_cue: int) -> tuple:
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    submaker = edge_tts.SubMaker()

    audio_data = bytearray()
    subtitle_content = ""

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

    vtt_file = [submaker.generate_subs(words_in_cue=words_in_cue)]

    for i in vtt_file:
        replaced = i.replace(".", ",")
        lines = replaced.splitlines()

        if len(lines) >= 2:
            text = '\n'.join(lines[1:]).strip()
            subtitle_content += f"{text}\n\n"

    return bytes(audio_data), subtitle_content

def sub_generator(txt):
  main_text = TextClip(txt,
                  font=font_path,
                  fontsize=120,
                  color="yellow",
                  stroke_color=("black"),
                  stroke_width=3,
                  size=(1215, 130))
  shadow_1 = TextClip(txt,
                  font=font_path,
                  fontsize=120,
                  color="black",
                  size=(1215, 130)).set_position((5, 2))
  shadow_2 = TextClip(txt,
                  font=font_path,
                  fontsize=120,
                  color="black",
                  size=(1215, 130)).set_position((6.5, 4.5))
  shadow_3 = TextClip(txt,
                  font=font_path,
                  fontsize=120,
                  color="black",
                  size=(1215, 130)).set_position((8, 7))

  return CompositeVideoClip([shadow_1, shadow_2, shadow_3, main_text])

def split_video(Video, segment_duration: int = 59, overlap:int = 7):

    video_duration = Video.duration
    num_segments = int(video_duration // (segment_duration - overlap)) + (1 if video_duration % (segment_duration - overlap) > 0 else 0)
    output_files = []
    # Split and save each segment
    for i in range(num_segments):
        start_time = i * (segment_duration - overlap)
        end_time = min(start_time + segment_duration, video_duration)
        segment = Video.subclip(start_time, end_time)

        # Create the output file name
        output_file = os.path.join(Youtube_path, f"Part_{i+1}.mp4")

        sub_clip = TextClip(f"PART {i+1}",
            font=font_path,
            fontsize=120, 
            color="yellow", 
            stroke_color=("black"), 
            stroke_width=3, 
            size=(1215, 125)).set_duration(overlap)

        if video_duration > segment_duration:
            final_video = CompositeVideoClip([segment, sub_clip.set_position(("center", 150))])
        else:
            final_video = segment
            output_file = os.path.join(Youtube_path, "Youtube_Short.mp4")

        final_video.write_videofile(output_file, fps=final_video.fps, codec="libx264", audio_codec="aac")

        output_files.append(output_file)
        
        with zipfile.ZipFile(os.path.join(Youtube_path, "Youtube_Shorts.zip"), 'w') as zipf:
            for file in output_files:
                zipf.write(file, os.path.basename(file))

    return os.path.join(Youtube_path, "Youtube_Shorts.zip")
    print("Your videos are ready!")
        
async def editor(text: str, Voice: str, rate: str, words_in_cue: int, subclip_lenth: int, platform: str):

    audio_data, subtitle_content = await Voice_generator(text, Voice, rate, words_in_cue)
    file_path = ""

    # Save audio data to a file
    with open(Voice_path, "wb") as audio_file:
        audio_file.write(audio_data)

    # Save subtitle content to a file
    with open(subtitle_path, "w") as srt_file:
        srt_file.write(subtitle_content)

    video_duration = AudioFileClip(Voice_path).duration

    Voice = AudioFileClip(Voice_path)
    Video = background_video(Video_path, video_duration, subclip_lenth)
    Audio = background_audio(Audio_path, video_duration)
    subtitle = SubtitlesClip(subtitle_path, sub_generator)

    final_audio = CompositeAudioClip([Audio, Voice])
    final_video = CompositeVideoClip([Video, subtitle.set_position("center")]).set_audio(final_audio)

    if platform == "youtube":
        youtube_path = split_video(final_video)
        file_path = youtube_path
    else:
        final_video.write_videofile(Tiktok_path, fps=final_video.fps, codec="libx264", audio_codec="aac")
        file_path = Tiktok_path

    return file_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_text_file>")
        sys.exit(1)

    input_text_file = sys.argv[1]
    
    with open(input_text_file, "r", encoding="utf-8") as file:
        text_content = file.read()
        
    asyncio.run(editor(text_content, "en-US-BrianMultilingualNeural", "+7%", 1, 15, "youtube"))