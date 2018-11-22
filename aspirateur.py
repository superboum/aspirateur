import os,sys,re
import shutil,tempfile,zipfile
import youtube_dl
from urllib.request import urlopen, Request

def self_install():
  current_file = os.path.realpath(__file__)
  if getattr(sys, 'frozen', False):
    current_file = os.path.realpath(sys.executable)

  current_path = os.path.normcase(os.path.normpath(os.path.dirname(current_file)))
  target_path = os.path.normcase(os.path.normpath(os.path.join(os.path.realpath(os.getenv('APPDATA')), "Microsoft", "Windows", "SendTo")))
  program_path = os.path.join(target_path, os.path.basename(current_file))

  if not os.path.isdir(current_path):
    print("[ERROR] The directory containing our program is not a directory. Houston, we have a logic error")
    return False, current_file, current_path, target_path, program_path

  if not os.path.isdir(target_path):
    print("[ERROR] Our computed destination directory doesn't exist. We need APPDATA/Microsoft/Windows/SendTo to continue...")
    return False, current_file, current_path, target_path, program_path

  if current_path != target_path:
    print("[INFO] We need to install our program as "+program_path)
    shutil.copyfile(current_file, program_path)

  return True, current_file, current_path, target_path, program_path

def ffmpeg_install():
  ffmpeg_url = "https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-4.1-win64-static.zip"
  #ffmpeg_url = "http://127.0.0.1:8000/ffmpeg-4.1-win64-static.zip"
  user_directory = os.path.expanduser("~")
  binaries_path = os.path.join(user_directory, "bin")
  ffmpeg_path = os.path.join(binaries_path, "ffmpeg.exe")
  ffprobe_path = os.path.join(binaries_path, "ffprobe.exe")
  ffplay_path = os.path.join(binaries_path, "ffplay.exe")

  if not os.path.isdir(user_directory):
    print("[ERROR] User has not home directory!")
    return False, user_directory, binaries_path, ffmpeg_path

  if not os.path.isdir(binaries_path):
    print("[INFO] Need to create folder "+binaries_path+" as it doesn't exist yet")
    os.mkdir(binaries_path)

  if not os.path.isfile(ffmpeg_path) or not os.path.isfile(ffprobe_path) or not os.path.isfile(ffplay_path) :
    print("[INFO] We need to download FFMPEG as "+ffmpeg_path)
    with tempfile.TemporaryDirectory() as tmp_dir:
      ffmpeg_zip = os.path.join(tmp_dir, "ffmpeg.zip")
      payload = urlopen(Request(ffmpeg_url, headers={'User-Agent': 'Mozilla'}))

      with open(ffmpeg_zip, "wb") as f:
        f.write(payload.read())

      with zipfile.ZipFile(ffmpeg_zip, 'r') as z:
        z.extractall(tmp_dir)

      ffmpeg_folder = None
      for name, _, _ in os.walk(tmp_dir):
        if "ffmpeg" in name:
          ffmpeg_folder = name
          break

      if ffmpeg_folder == None:
        print("[ERROR] ffmpeg folder has not been found after extraction")
        return False, user_directory, binaries_path, ffmpeg_path

      ffmpeg_binary = os.path.join(tmp_dir, ffmpeg_folder, "bin", "ffmpeg.exe")
      ffprobe_binary = os.path.join(tmp_dir, ffmpeg_folder, "bin", "ffprobe.exe")
      ffplay_binary = os.path.join(tmp_dir, ffmpeg_folder, "bin", "ffplay.exe")
      shutil.copyfile(ffmpeg_binary, ffmpeg_path)
      shutil.copyfile(ffprobe_binary, ffprobe_path)
      shutil.copyfile(ffplay_binary, ffplay_path)

  os.environ["PATH"] += os.pathsep + binaries_path
  return True, user_directory, binaries_path, ffmpeg_path

def download():
  if len(sys.argv) <= 1:
    print("[INFO] No file to parse")
    return True

  target = sys.argv[1]
  folder = os.path.dirname(target)
  if not os.path.isfile(target):
    print("[ERROR] The file does not exist (or you passed a directory)")

  old_wd = os.getcwd()
  os.chdir(folder)

  argv = []
  url = None
  with open(target, 'r') as f:
    for line in f:
      match = re.search('^\s*([^:]+?)\s*:\s*(.*?)\s*$', line)
      if match is not None:
        if match.group(1) == "url": url = match.group(2)
        elif match.group(2) == "true": argv += ["--"+match.group(1)]
        elif match.group(2) == "false": pass
        else: argv += ["--"+match.group(1), match.group(2)]

  if url == None:
    print("[ERROR]: URL is missing. Please add a line with like -> url: https://example.com")

  argv.append(url)
  try:
    youtube_dl._real_main(argv)
  except Exception as inst:
    print(inst)
    print("[ERROR] YoutubeDL encountered an error")
    return False

  os.chdir(old_wd)
  return True

def main():
  ok, _, _, _, _ = self_install()
  if not ok: return False

  ok, _, _, _ = ffmpeg_install()
  if not ok: return False

  ok = download()
  if not ok: return False

try:
  if main(): pass
  else: input("Press [ENTER] to continue...")
except Exception as inst:
  print (inst)
  input("[INFO] Press [ENTER] to quit...")
