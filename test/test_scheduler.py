from app.scheduler import start_scheduler

def test_start_scheduler_runs_without_errors():
    try:
        start_scheduler()
        assert True
    except Exception as e:
        assert False, f"start_scheduler raised an exception: {e}"
