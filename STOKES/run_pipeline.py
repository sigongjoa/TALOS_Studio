import os
from src.style_agent.style_agent import StyleAgent
from src.narration_agent.narration_agent import NarrationAgent
from src.simulation_agent.simulation_agent import SimulationAgent
from src.render_agent.render_agent import RenderAgent
from src.orchestrator.orchestrator import Orchestrator
from src.llm_client import OllamaClient
from gtts import gTTS

# --- Main execution ---
if __name__ == "__main__":
    print("Starting the Effect Stokes + Maimu pipeline demonstration...")

    # Initialize real clients
    ollama_client = OllamaClient(model="llama2") # Assuming 'llama2' is available in Ollama
    # gTTS client is implicitly used within NarrationAgent if not provided

    # Instantiate agents with real clients where applicable
    style_agent = StyleAgent(llm_client=ollama_client)
    narration_agent = NarrationAgent(llm_client=ollama_client, tts_client=gTTS) # Pass gTTS class directly
    simulation_agent = SimulationAgent()
    render_agent = RenderAgent()

    # Instantiate the Orchestrator
    orchestrator = Orchestrator(
        style_agent=style_agent,
        narration_agent=narration_agent,
        simulation_agent=simulation_agent,
        render_agent=render_agent
    )

    # Sample user input
    sample_user_input = "회전하는 물방울 효과를 만들어줘. 푸리에 변환을 사용해서 분석해줘."
    # sample_user_input = "아름다운 파동 효과를 보여줘."

    # Define output directory
    output_dir = os.path.join(os.getcwd(), "outputs", "final_shorts_demo")
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nRunning pipeline with user input: '{sample_user_input}'")
    final_video_path = orchestrator.run_pipeline(sample_user_input, output_dir)

    if final_video_path:
        print(f"\nPipeline completed successfully! Final video at: {final_video_path}")
        print(f"You can find all generated outputs in: {output_dir}")
    else:
        print("\nPipeline failed to complete.")