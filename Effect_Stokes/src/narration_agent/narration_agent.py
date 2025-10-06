import json
import os
import sys
from gtts import gTTS
from src.llm_client import OllamaClient

class NarrationAgent:
    def __init__(self, llm_client: OllamaClient = None, tts_client=None):
        """
        Initializes the NarrationAgent.

        Args:
            llm_client: An OllamaClient instance for script generation.
            tts_client: A gTTS client (or similar) for audio generation.
        """
        self.llm_client = llm_client
        self.tts_client = tts_client if tts_client else gTTS

    def generate_script(self, formula: str, parameters: dict) -> str:
        """
        Generates a narration script based on a mathematical formula and parameters.

        Args:
            formula: The mathematical formula to explain.
            parameters: A dictionary of simulation parameters.

        Returns:
            A string containing the generated narration script.
        """
        if not self.llm_client:
            sys.stdout.write("Warning: LLM client not provided for NarrationAgent. Using placeholder script generation.\n")
            script = (
                f"자네, 이 수식 '{formula}'을 보게나. 이것은 시뮬레이션 파라미터 {json.dumps(parameters)}와 함께 "
                "우주의 신비를 풀어낼 열쇠라네. 마치 무잔의 회전 공격처럼, 이 수식은 복잡한 현상 뒤에 숨겨진 "
                "단순한 패턴을 보여주지. 푸리에 변환을 통해 그 진정한 모습을 드러낼 걸세."
            )
            return script

        prompt = self._create_llm_prompt(formula, parameters)
        response = self.llm_client.generate(prompt)
        return response

    def _create_llm_prompt(self, formula: str, parameters: dict) -> str:
        """
        Creates a prompt for the LLM to generate a narration script.
        """
        prompt = (
            "You are Maimu, a wise and slightly meme-savvy narrator. Your task is to explain "
            "a mathematical formula in an engaging and easy-to-understand way, connecting it "
            "to visual effects (VFX) and using a tone that is both educational and entertaining. "
            "Imagine you are explaining this to an anime fan.\n\n"
            f"Mathematical Formula: {formula}\n"
            f"Simulation Parameters: {json.dumps(parameters)}\n\n"
            "Please generate a short narration script (around 3-5 sentences) that explains "
            "how this formula and these parameters relate to a visual effect. "
            "Use analogies from anime if possible, and maintain a wise, slightly humorous tone."
        )
        return prompt

    def generate_audio(self, script: str, output_path: str = "narration.mp3") -> str:
        """
        Converts the narration script into an audio file.

        Args:
            script: The narration script.
            output_path: The path to save the audio file.

        Returns:
            The path to the generated audio file.
        """
        if not self.tts_client:
            sys.stdout.write("Warning: TTS client not provided. Skipping audio generation.\n")
            return ""

        try:
            tts = self.tts_client(text=script, lang='ko')
            tts.save(output_path)
            print(f"Audio generated successfully to: {output_path}")
            return output_path
        except Exception as e:
            sys.stderr.write(f"Error generating audio with gTTS: {e}\n")
            return ""


    def generate_subtitles(self, script: str, audio_duration: float = None, output_path: str = "subtitles.srt") -> str:
        """
        Generates an SRT subtitle file from the narration script.

        Args:
            script: The narration script.
            audio_duration: The duration of the audio in seconds (for basic synchronization).
            output_path: The path to save the SRT file.

        Returns:
            The path to the generated SRT file.
        """
        # Basic subtitle generation (can be improved with more accurate timing)
        lines = [line.strip() for line in script.split('.') if line.strip()]
        srt_content = ""
        start_time = 0.0
        num_lines = len(lines)
        for i, line in enumerate(lines):
            if line:
                end_time = start_time + (audio_duration / num_lines if audio_duration and num_lines > 0 else 2.0) # Estimate 2 seconds per line
                srt_content += f"{i+1}\n"
                srt_content += f"{self._format_time(start_time)} --> {self._format_time(end_time)}\n"
                srt_content += f"{line}\n\n"
                start_time = end_time

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        return output_path

    def _format_time(self, seconds: float) -> str:
        """Formats seconds into SRT time format (HH:MM:SS,ms)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

    def process_narration(self, formula: str, parameters: dict, output_dir: str = "outputs/narration") -> tuple[str, str]:
        """
        Orchestrates the narration generation process: script, audio, and subtitles.

        Args:
            formula: The mathematical formula.
            parameters: Simulation parameters.
            output_dir: Directory to save output files.

        Returns:
            A tuple containing paths to the generated audio and subtitle files.
        """
        os.makedirs(output_dir, exist_ok=True)

        script = self.generate_script(formula, parameters)
        print(f"Generated Script:\n{script}\n")

        audio_path = os.path.join(output_dir, "narration.mp3")
        generated_audio_path = self.generate_audio(script, audio_path)

        # For now, we'll use a dummy duration for subtitle generation
        # In a real scenario, audio_duration would come from the TTS client.
        num_sentences = len([s.strip() for s in script.split('.') if s.strip()])
        dummy_audio_duration = num_sentences * 2.0 # Estimate 2 seconds per sentence
        subtitle_path = os.path.join(output_dir, "subtitles.srt")
        generated_subtitle_path = self.generate_subtitles(script, dummy_audio_duration, subtitle_path)

        return generated_audio_path, generated_subtitle_path
