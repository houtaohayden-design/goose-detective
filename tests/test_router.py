import pytest
from unittest.mock import patch, MagicMock
from analysis.router import AnalysisRouter, AnalysisResult
from analysis.prompts import build_analysis_prompt

def test_build_prompt_contains_player_speech():
    records = [
        {"player": "玩家1", "time": "00:12", "text": "我在发电室"},
        {"player": "玩家2", "time": "00:18", "text": "我看到玩家5"},
    ]
    prompt = build_analysis_prompt(records)
    assert "玩家1" in prompt
    assert "我在发电室" in prompt
    assert "逻辑漏洞" in prompt

def test_analysis_result_dataclass():
    r = AnalysisResult(
        player="玩家1",
        suspicion_score=72,
        contradictions=["第2轮声称在走廊，与第1轮矛盾"],
        summary="存在明显矛盾",
    )
    assert r.suspicion_score == 72
    assert len(r.contradictions) == 1

def test_router_calls_openai_client():
    router = AnalysisRouter.__new__(AnalysisRouter)
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = '''[
        {"player": "玩家1", "suspicion_score": 80,
         "contradictions": ["矛盾1"], "summary": "高度可疑"}
    ]'''
    mock_client.chat.completions.create.return_value = mock_resp
    router._client = mock_client
    router._model = "test-model"

    records = [{"player": "玩家1", "time": "00:12", "text": "test"}]
    results = router.analyze(records)
    assert len(results) == 1
    assert results[0].player == "玩家1"
    assert results[0].suspicion_score == 80
