# STOKES Module (VFX Simulation & Rendering)

This module is an agent-based system for generating and rendering fluid-based visual effects (VFX). It uses a simplified Navier-Stokes solver for simulation and Blender for high-quality rendering, with an API-driven and agent-based architecture for control.

## Feature Specification

-   **Agent-based Orchestration:** Uses a multi-agent system (`StyleAgent`, `NarrationAgent`, `SimulationAgent`, `RenderAgent`) orchestrated by a central `Orchestrator` to manage the VFX generation pipeline.
-   **LLM Integration:** Leverages a Large Language Model (e.g., Llama 2 via Ollama) to parse user prompts (e.g., "a swirling vortex") into initial simulation and style parameters (`StyleAgent`).
-   **Fluid Simulation:**
    -   Runs a 2D fluid simulation based on the Navier-Stokes equations.
    -   Supports time-dependent parameters using mathematical expressions (e.g., `viscosity = "0.01 + 0.005 * sin(t * 0.5)"`), which are evaluated at each time step.
    -   Saves the state of the fluid (velocity and pressure fields) as a sequence of `.npz` files.
-   **Blender Visualization:**
    -   Takes the generated fluid data and visualizes it within Blender's Cycles render engine.
    -   Supports GPU rendering (CUDA/OptiX).
    -   Generates geometry (e.g., meshes, arrows) based on the fluid data for each frame.
    -   Animates object visibility and material properties (e.g., color, emission, transparency) over time to create dynamic effects.
-   **Web API & Real-time Feedback:**
    -   Provides a Flask/SocketIO backend (`backend/app.py`).
    -   `/api/run_pipeline`: An endpoint to trigger the full simulation and rendering pipeline with JSON parameters. It provides real-time logging and progress updates via WebSockets.
    -   `/api/run_preview`: A faster endpoint that runs only the simulation and generates a low-fidelity quiver plot preview as a sequence of base64 images, allowing for rapid iteration on simulation parameters.
    -   `/api/stop_pipeline`: An endpoint to terminate a running pipeline process.
-   **Frontend UI:** Includes a React-based frontend for interacting with the backend API.

## Code Description

-   `run_pipeline.py`: A high-level script that demonstrates the agent-based orchestration. It initializes all agents and runs the full pipeline based on a sample text prompt.
-   `run_blender_oneshot.py`: A script designed to be run by Blender from the command line. It handles the entire rendering process in a single go: loading data, creating geometry, setting up materials, animating, and rendering.
-   `backend/app.py`: A Flask server that exposes the simulation and rendering capabilities through a REST API and WebSockets for real-time communication with a frontend.
-   `src/`: Contains the core logic for the agents and simulators.
    -   `orchestrator/`: Manages the overall workflow between agents.
    -   `llm_client.py` / `llm_interface.py`: Handles communication with the LLM.
    -   `simulation_agent.py` / `fluid_simulator.py`: The `SimulationAgent` wraps the `FluidSimulator`, which contains the core logic for solving the fluid equations and saving the data.
    -   `render_agent.py` / `blender_fluid_visualizer.py`: The `RenderAgent` is responsible for calling Blender. The `blender_fluid_visualizer.py` script contains the detailed logic for creating the 3D visualization inside Blender.
-   `frontend/`: A React application for building a user interface to control the pipeline.

## System Flow

There are two primary flows: the full pipeline and the preview flow.

### Full Pipeline Flow (via `backend/app.py`)

1.  **Request:** A frontend sends a JSON object with `simulation_params` and `visualization_params` to the `/api/run_pipeline` endpoint.
2.  **Validation:** The server validates the incoming parameters.
3.  **Execution:** The server starts `src/run_full_pipeline.py` (or a similar script) in a separate thread, passing the parameters.
4.  **Orchestration (`run_pipeline.py`):
    -   The `Orchestrator` coordinates the agents.
    -   **(Simulation):** The `SimulationAgent` calls `fluid_simulator.py` to run the simulation, generating a series of `fluid_data_frame_XXXX.npz` files in a temporary directory.
    -   **(Rendering):** The `RenderAgent` calls Blender as a subprocess, executing `run_blender_oneshot.py` (or `blender_fluid_visualizer.py`).
5.  **Blender Process (`run_blender_oneshot.py`):
    -   Blender starts, clears the scene, and enables GPU rendering.
    -   It reads all the `.npz` fluid data files.
    -   For each frame, it generates a mesh representing the fluid state.
    -   It creates and applies materials based on the `visualization_params`.
    -   It sets up keyframes for the visibility, position, and material properties of the generated meshes.
    -   Finally, it renders the entire animation as a sequence of PNG images.
6.  **Post-processing:** After rendering, a script (likely within the `RenderAgent`) combines the PNG frames into a final video or GIF.
7.  **Response:** The backend sends a "completed" status via WebSocket with a URL to the final output file.

### Preview Flow (via `backend/app.py`)

1.  **Request:** A frontend sends `simulation_params` to the `/api/run_preview` endpoint.
2.  **Simulation:** The server directly instantiates and runs the `FluidSimulator` with the provided parameters for a limited number of frames.
3.  **Image Generation:** For each simulated frame's `.npz` data, the server uses Matplotlib to generate a 2D quiver plot (vector field visualization).
4.  **Response:** The server encodes these plots as base64 image strings and sends them back to the frontend in a single JSON response, allowing for a quick visual preview without involving Blender.
