# Easy azure tts

An easy to use tts (text to speech) using azure.

## Set the secret


In `azure_secret.json` put the following:
```json
{
  "key": "your key",
  "region": "your region"
}
```

## Specify the text
In speech.toml put the following to specify the text to be spoken:

```toml
[output_filename]
text = "I hope you like this."
language_code = "en"
voice = "en-US-JennyNeural"
speed = 1.15
pitch = 0.78

[output_filename2]
text = "Ik hoop dat je dit leuk vindt."
language = "nl"
voice = ""
```
You can put as many of them as you want! The `language` has to be a valid language code. The `voice` has to be a valid voice for that language. 
If you don't specify a voice, it will use the default voice for that language. To get a list of valid voices, run `poetry run voices`. 

Filenames should pass an `.isidentifier()` check meaning only alphanumeric letters (a-z) and (0-9), or underscores (_). A valid identifier cannot start with a number, or contain any spaces. 
If you don't put `speed` or `pitch` we use default values of `1.0` 

## Create the wav files

```bash
poetry install
poetry run tts
```

## Convert to ogg

Use poetry 2ogg to convert the generated wav files in /output to ogg files. Naturally you need to have [ffmpeg](https://ffmpeg.org/) installed.

```bash
poetry run 2ogg
```

## All together

Run `poetry run generate` to run tts, 2ogg and cleanwav in one go.

```bash
poetry run generate
```
