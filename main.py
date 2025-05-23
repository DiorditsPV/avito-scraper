from src.orchestration.pipeline import run_pipeline

if __name__ == "__main__":
    result_key = run_pipeline()
    print(f"Пайплайн завершен. Ключ результата: {result_key}")

