import importlib

from app import config as config_module


def test_config_reads_environment(monkeypatch):
	monkeypatch.setenv("MONGODB_URI", "mongodb://example:27017")
	monkeypatch.setenv("DATABASE_NAME", "financial_dwh_test")

	module = importlib.reload(config_module)

	assert module.MONGODB_URI == "mongodb://example:27017"
	assert module.DATABASE_NAME == "financial_dwh_test"