import os
import json
import pytest
from src.simulation_agent.simulation_agent import SimulationAgent

@pytest.fixture
def simulation_agent():
    return SimulationAgent()

def test_run_simulation(simulation_agent, tmp_path):
    parameters = {"type": "rotation", "speed": 10}
    formula = "f(t) = A * cos(omega * t)"
    output_dir = tmp_path / "sim_output"
    
    output_file = simulation_agent.run_simulation(parameters, formula, str(output_dir))
    
    assert os.path.exists(output_file)
    assert "simulation_data.json" in output_file
    
    with open(output_file, "r") as f:
        data = json.load(f)
        assert data["simulation_type"] == "rotation"
        assert data["formula_used"] == formula
        assert len(data["frames"]) == 10
        assert "particles" in data["frames"][0]
        assert "metadata" in data["frames"][0]
