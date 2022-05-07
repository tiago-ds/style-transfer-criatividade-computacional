import os
import librosa
import soundfile as sf
import shutil
from pydub import AudioSegment

def execute_command(command):
    os.system(command)

def kpopify(sample_file_name):
    # Descobrindo o tempo da música do usuário
    # O warning é normal, pra sinalizar que tá lendo um .mp3 e não um .wav
    sample_y, sample_sr = librosa.load(f'api_files/{sample_file_name}.mp3')
    sample_tempo, beat_frames = librosa.beat.beat_track(y=sample_y, sr=sample_sr)

    # Pequena correção para não ficar um float
    sample_tempo = round(sample_tempo)

    # Aqui, é feita a escolha da música base
    # Ela é escolhida pra ser o mais próximo da escolhida pelo usuário
    musics_tempo = {
        'kingdom_come': (86, '1G0RFXa-M0lwD_K7UYOBlG-a3prhoBXUz'),
        'alcohol_free': (96, '1iLQjt1kwflgHTLheFzgJRRU_1QAtnXtq'),
        'solo': (98, '1TvGqx6FwiK9p7rL6HaZzKEpAciC_9y2u'),
        'dynamite': (112,'1q6wiRbNPRE3nMdtIEUv_fTZ7muXhZpo4'),
        'the_boys': (117, '1YIMwGMaZV9BDNawgcigIcKXwOuDLiubf'),
        'dont_fight_the_feeling': (129, '1yzKPfsrXK_wx0-OrriCjCIzi3Bh6LUOn'),
        'ddu_du_ddu_du': (143, '1DQLWnskeWohL8gQreVRFoq9mdR_w3dnk'),
        'i_cant_stop_me': (151, '1Zz4KUwtAeCixlC0ezunBk6j_MB2C559P'),
        'milkshake': (168, '1TaUBwr1z4hY7qKqmpm9zD1wXTEAT8cu9'),
        'what_is_love': (172, '1EzYHEzszB56A1RUsg4QY5fEXSYV7Qgt5'),
    }

    # Essa linha de código escolhe a música do dicionário musics_tempo com o tempo mais
    # próximo da música escolhida
    base_file_name, file_stats = min(musics_tempo.items(), key=lambda x: abs(sample_tempo - x[1][0]))
    base_tempo, base_file_id = file_stats[0], file_stats[1]

    print("")
    print(f"{sample_file_name}: {sample_tempo} BPM ")
    print(f"Chosen kpop: {base_file_name} ( {base_tempo} BPM )")
    print(f"\n")

    # Agora, baixar a música escolhida pra o mash

    # Exporta o id do arquivo e o nome dele para o ambiente de execução
    os.environ['BASE_FILE_ID'] = base_file_id
    os.environ['CORRECTED_FILE_NAME'] = f"{base_file_name}_corrected.wav"
    # Baixa o arquivo
    gdown_command = f"gdown {base_file_id}"
    execute_command(gdown_command)

    # E carrega ele no librosa
    base_y, base_sr = librosa.load(f'{base_file_name}.mp3')

    # A média do tempo das duas músicas
    mean_tempo = round((base_tempo + sample_tempo) / 2)

    print(f'Mean tempo: {mean_tempo}')

    # O cálculo do fator de multiplicação dos dois tempos
    # Tem um ajuste de duas casas decimais

    base_factor = round((mean_tempo / sample_tempo), 2)
    sample_factor = round((mean_tempo / base_tempo), 2)

    # Condição pra caso um dos tempos for MUITO maior que o outro
    # Basicamente, se um tempo / 2 ainda for maior que o outro, a gente divide
    if abs(base_factor - sample_factor) >= 1:
      if max(base_factor, sample_factor) == sample_factor:
        sample_factor /= 2
      else:
        base_factor /= 2

    # Salva o arquivo escolhido com o tempo corrigido
    corrected_tempo_sample = librosa.effects.time_stretch(sample_y, rate=sample_factor)
    sf.write(f'{sample_file_name}_corrected.wav', corrected_tempo_sample, sample_sr, subtype='PCM_24')
    print(f"Corrected sample tempo file created with size of {os.path.getsize(f'{sample_file_name}_corrected.wav')} bytes as {sample_file_name}_corrected.wav")

    # E agora salva o arquivo base com o tempo corrigido
    corrected_tempo_base = librosa.effects.time_stretch(base_y, rate=base_factor)
    sf.write(f'{base_file_name}_corrected.wav', corrected_tempo_base, base_sr, subtype='PCM_24')
    print(f"Corrected base tempo file created with size of {os.path.getsize(f'{base_file_name}_corrected.wav')} bytes as {base_file_name}_corrected.wav")

    separate_sample = f"spleeter separate -p spleeter:4stems -o output {sample_file_name}_corrected.wav"
    separate_base = f"spleeter separate -p spleeter:4stems -o output {base_file_name}_corrected.wav"

    print("Separating sample file")
    execute_command(separate_sample)

    print("Separating base file")
    execute_command(separate_base)

    print("Successfully separated both files")

    sample_vocals = AudioSegment.from_file(f"./output/{sample_file_name}_corrected/vocals.wav", format="wav")
    base_bass = AudioSegment.from_file(f"./output/{base_file_name}_corrected/bass.wav", format="wav")
    sample_drums = AudioSegment.from_file(f"./output/{sample_file_name}_corrected/drums.wav", format="wav")
    base_other = AudioSegment.from_file(f"./output/{base_file_name}_corrected/other.wav", format="wav")

    # Aumentar um pouco a voz da música
    louder_vocals = sample_vocals + 5 # 5dB mais alto
    base_bass += 8

    # Fazer o overlay das músicas
    result_1 = base_bass.overlay(sample_drums, position=0)
    result_2 = result_1.overlay(base_other, position=0)
    result_3 = result_2 - 10
    result = result_2.overlay(sample_vocals, position=0)

    # Export do resultado final
    result.export(f"./results/{base_file_name}_kpopified.mp3", format="mp3")
    print(f"New file created {sample_file_name}_kpopified.mp3.")

    print(f"{sample_file_name} was successfully kpopified, deleting extra files created...")
    os.remove(f"{base_file_name}.mp3")
    os.remove(f"{base_file_name}_corrected.wav")
    os.remove(f"{sample_file_name}_corrected.wav")
    shutil.rmtree("./output")
    shutil.rmtree("./api_files")


kpopify("tuftuf")