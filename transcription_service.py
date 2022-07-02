import os
from pydub import AudioSegment 
import speech_recognition as sr
from threading import Thread
import shutil
import queue
from pydub.silence import split_on_silence
import wave


############################################

#FUNCTIONS

############################################
############################################
def create_dirs(working_dir_path,unique_id):
    dirName0 = working_dir_path+'/tempo'+unique_id
    dirName1 = working_dir_path+'/channels'+unique_id
    dirName2 = working_dir_path+'/tempo'+unique_id+'/c1'
    dirName3 = working_dir_path+'/tempo'+unique_id+'/c2'
    dirName4 = working_dir_path+'/tempo'+unique_id+'/c3'
    dirName5 = working_dir_path+'/channels'+unique_id+'/multi_channels'

    os.mkdir(dirName0)
    os.mkdir(dirName1)
    os.mkdir(dirName2)
    os.mkdir(dirName3)
    os.mkdir(dirName4)
    os.mkdir(dirName5)

def delete_dirs(working_dir_path,path_to_recording,unique_id):
    # location
    
  
    # directory
    dir1 = "tempo"+unique_id
    dir2=  "channels"+unique_id
    # path
    path1 = os.path.join(working_dir_path, dir1)
    path2 = os.path.join(working_dir_path, dir2)
    # removing directory
    shutil.rmtree(path1)
    shutil.rmtree(path2)
    os.remove(path_to_recording)

def extract_channels(path_to_racording,working_dir_path,unique_id):
    # Import stereo audio file and check channels
    stereo_phone_call = AudioSegment.from_file(path_to_racording, "wav")

    # Split stereo phone call and check channels
    channels = stereo_phone_call.split_to_mono()


    # Save new channels separately
    phone_call_channel_1 = channels[0]
    phone_call_channel_2 = channels[1]

    #augment the volume of calls
    phone_call_channel_1 = phone_call_channel_1 +7.5
    phone_call_channel_2 = phone_call_channel_2 +7.5

    #save the phone call channels to directory
    phone_call_channel_1.export(working_dir_path+"/channels"+unique_id+"/channel1.wav",format="wav") 
    phone_call_channel_2.export(working_dir_path+"/channels"+unique_id+"/channel2.wav",format="wav") 




def splitOnSilence(path_to_channel,path_to_save_chunks,list_of_files):
  audio_chunks = split_on_silence( AudioSegment.from_file(path_to_channel), min_silence_len=1500, silence_thresh=-55)
  for i, chunk in enumerate(audio_chunks):
   out_file = path_to_save_chunks+"/chunk{0}.wav".format(i)
   list_of_files.append(out_file)
   chunk.export(out_file, format="wav")

def split_mono_channel(path_to_channel,path_to_save_chunks,listoffiles):
    audio = AudioSegment.from_wav(path_to_channel)
    n = len(audio)
    counter = 1
    interval = 6000
    overlap = 1000
    start = 0
    end = 0
    flag = 0
    for i in range(0, n, interval):
        
        if i == 0:
            start = 0
            end = interval
        else:
            start = end - overlap
            end = start + interval + overlap 
        if end >= n:
            end = n
            flag = 1
        chunk = audio[start:end]
        chunk_name = path_to_save_chunks+"/chunk{}.wav".format(counter)
        listoffiles.append(chunk_name)
        chunk.export(chunk_name, format ="wav")
        counter = counter + 1


def transcribe(listoffiles):


  r=sr.Recognizer()
  ts1 = ""
  for filename in listoffiles :
    with sr.AudioFile(filename) as source:
      audio=r.record(source)
            
      try:
              
        text = r.recognize_google(audio, language="en-US")
              
        ts1 =ts1 + text
        ts1 =ts1 + ' '
      except :
        pass

  return ts1



############################################

#PROGRAM

############################################




#paths to change
def start_transcription(recording_dir,unique_id):
    working_dir="tempdir"
    print("############ working directory######## ",working_dir)
    path_to_racording=recording_dir#working_dir+"/1257253568.wav"
    path_to_save_chunks1=working_dir+"/tempo"+unique_id+"/c1"
    path_to_save_chunks2=working_dir+"/tempo"+unique_id+"/c2"
    path_to_save_chunks3=working_dir+"/tempo"+unique_id+"/c3"
    path_to_channel_1=working_dir+"/channels"+unique_id+"/channel1.wav"
    path_to_channel_2=working_dir+"/channels"+unique_id+"/channel2.wav"
    path_to_mono_channel=working_dir+"/channels"+unique_id+"/mono_channel.wav"
    

    

    #variables we need

    listoffiles1=list()
    listoffiles2=list()
    listoffiles3=list()


    #begin
    
    create_dirs(working_dir,unique_id)

    R = wave.open(path_to_racording, "r")

    if(R.getnchannels()==2):
        n_channels=2
        
    elif(R.getnchannels()==1): 
        n_channels=1
  


    
    if(n_channels==2):
        extract_channels(path_to_racording,working_dir,unique_id)
        

        t1 = Thread(target=splitOnSilence,args=(path_to_channel_1,path_to_save_chunks1,listoffiles1))
        t2 = Thread(target=splitOnSilence,args=(path_to_channel_2,path_to_save_chunks2,listoffiles2))

        t1.start()
        t2.start()

        t1.join()
        t2.join()


        que = queue.Queue()
        x = Thread(target=lambda  q ,arg1: q.put(transcribe(arg1)),args=(que,listoffiles1))
        que2 = queue.Queue()
        y = Thread(target=lambda  a ,arg2: a.put(transcribe(arg2)),args=(que2,listoffiles2))
        
        

        x.start()
        y.start()

        x.join()
        y.join()
        speakers=list()
        speakers.append(que.get()) 
        speakers.append(que2.get())
        #print("$$$$$$$",speakers)
        try:
            delete_dirs(working_dir,path_to_racording,unique_id)
        except:pass
      
        return speakers


    elif (n_channels==1):
        mono_phone_call = AudioSegment.from_file(path_to_racording, "wav")
        mono_phone_call=mono_phone_call+7.5
        mono_phone_call.export(path_to_mono_channel, format="wav")
        split_mono_channel(path_to_mono_channel,path_to_save_chunks3,listoffiles3)
        speakers=list()
        speakers.append(transcribe(listoffiles3))
        speakers.append("")
        try:
            delete_dirs(working_dir,path_to_racording,unique_id)
        except:pass
        return speakers
    