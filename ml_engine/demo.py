"""ml_engine demo stub"""
from ml_engine.pipeline import MLPipeline
from ml_engine.schemas import ProjectMetadata, GreenlightPredictRequest

if __name__ == "__main__":
    pipeline = MLPipeline.for_domain("film_tv")
    req = GreenlightPredictRequest(
        project_id="demo-001",
        metadata=ProjectMetadata(project_type="FEATURE", scale_band="_1M_TO_5M", duration=30, headcount=50),
    )
    try:
        result = pipeline.predict_greenlight(req)
        print(f"Predicted: {result.predicted_total_tco2e} tCO2e")
    except RuntimeError as e:
        print(f"Demo requires trained model: {e}")
